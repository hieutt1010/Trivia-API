import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
Curent_category_global = None

def pagination_question(request, questions):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    format_question = [question.format() for question in questions]
    return format_question[start : end]  

def get_list_categories():
    selections = Category.query.order_by(Category.id).all()
    return selections

def create_question(body):
    new_question_description =  body.get("question", None)
    new_answer = body.get("answer", None)
    new_dificulty = body.get("difficulty", None)
    new_category = body.get("category", None)
    
    new_question = Question(new_question_description, new_answer, new_category, new_dificulty)
    new_question.insert()
    
    return jsonify({
        'success': True
    })
        
def search_question(search_term):
    question_filter = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    format_question_filter = [question.format() for question in question_filter]

    return jsonify({
        'questions' : format_question_filter,
        'totalQuestions' : len(format_question_filter),
        'currentCategory' : Curent_category_global
    })  

        
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    CORS(app, resources={r"*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
    # CORS(app)
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization, true")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response
    
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def retrive_categories():
        try:
            selections = get_list_categories()
            # format_categories = [category.format() for category in selections]
            format_categories = {str(category.id): category.type for category  in selections}
            return jsonify({
                'categories': format_categories,
            })
        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def retrive_question():
        try: 
            selections = Question.query.order_by(Question.id).all()
            current_question = pagination_question(request, selections)
            # if len(current_question) == 0: 
            #     abort(404)
            list_categories = get_list_categories()
        
            format_categories = {str(category.id): category.type for category  in list_categories}
            return jsonify({
                'questions': current_question,
                'totalQuestions' : len(selections),
                'categories': format_categories,
                'currentCategory' : Curent_category_global
            })
        except:
            abort(404)
            
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try: 
            question = Question.query.filter(Question.id == question_id).one_or_none()
            # if question is None:
            #     abort(404)
                
            question.delete()
            
            return jsonify({
                'success': True
            })
        except:
            abort(404)
            
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions', methods=['POST'])
    def questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        try:
            if search_term is None:
                return create_question(body)
            else:
                return search_question(search_term)
        except: 
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def retrive_question_by_category(category_id):
        try:
            questions = Question.query.filter(Question.category == category_id).all()
            format_questions = [question.format() for question in questions]
            currentCategory = Category.query.filter(Category.id == category_id).one_or_none()
            global Curent_category_global
            
            if currentCategory is None:
                categoryName = ''
                Curent_category_global = 0
            else:
                categoryName = currentCategory.type
                # global Curent_category_global
                Curent_category_global = currentCategory.id
            return jsonify({
                'questions':format_questions,
                'totalQuestions' : len(format_questions),
                'currentCategory' : categoryName,
            })
        except:
            abort(404)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """ 
    @app.route('/quizzes', methods=['POST'])
    def play():
        try:
            body= request.get_json()
            previous_questions = body.get('previous_questions', [])
            quiz_category = body.get('quiz_category', None)
            question_query = Question.query
            
            if quiz_category is not None:
                category = Category.query.filter(Category.type == quiz_category["type"]).one_or_none()
                if category is not None:
                    question_query = question_query.filter(Question.category == category.id)
            
            if previous_questions is not []:
                question_query = question_query.filter(Question.id.notin_(previous_questions))
            
            questions = question_query.all()
            
            if len(questions) == 0: 
                return jsonify({
                    'questions': None,
                })

            next_question = random.choice(questions)
            format_question = next_question.format()
            
            return jsonify({
                'question' : format_question
            })
        except:
            abort(422) 
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )
    return app

