import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db as database
from dotenv  import load_dotenv

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""


    load_dotenv()
    database_path = os.getenv('database_path_test')
    
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path
        })
        
        self.client = self.app.test_client
        self.connection = database.engine.connect()
        self.trans = self.connection.begin()

        # Bind a session to the connection
        database.session.bind = self.connection
    def tearDown(self):
        """Executed after reach test"""
        self.trans.rollback()
        self.connection.close()
        database.session.remove()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #region app.route('/categories', methods=['GET'])
    def test_retrieve_categories_success(self):
        res = self.client().get('/categories')
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])
        
    def test_retrieve_categories_failed(self):
        res = self.client().get('/categories/x')
        data = res.get_json()
    
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    #endregion
    
    #region @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def test_delete_question_success(self):
        question = Question(question="question", answer="answer", category="1", difficulty=1)
        question.insert()
        question_id = question.id

        res = self.client().delete(f'/questions/{question_id}')
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        deleted_question = Question.query.filter(Question.id == question_id).one_or_none()
        self.assertIsNone(deleted_question)
        
    def test_delete_question_failed(self):
        res = self.client().delete('/questions/200')
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    #endregion
    
    #region @app.route('/questions', methods=['GET'])
    def test_get_questions_success(self):
        res = self.client().get("/questions")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(data["currentCategory"])
        
    def test_get_questions_failed(self):
        res = self.client().get("/questions/aa")
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    #endregion
    

    
    # #region @app.route('/questions', methods=['POST']) #! 4 case for both "search" and "create" Question
    def test_search_question_success(self):
        res = self.client().post('/questions', json={"searchTerm": "How"})
        data = res.get_json()
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(data["currentCategory"])

    def test_search_question_failed(self):
        res = self.client().post('/questions', json={"searchTerm": "xyz123"})
        data = res.get_json()
    
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["questions"], [])
        self.assertEqual(data["totalQuestions"], 0)
        self.assertTrue(data["currentCategory"])
    
    #case create Question
    def test_create_question_success(self):
        json_data = {
            "questions": [
                {
                    "id": 1,
                    "question": "This is a question",
                    "answer": "This is an answer",
                    "difficulty": 5,
                    "category": 5
                }
            ],
            "totalQuestions": 100,
            "currentCategory": "Entertainment"
        }
        res = self.client().post('/questions', json= json_data)
        data = res.get_json()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        
    def test_create_question_failed(self):
        json_data = {
            "question": [
                {
                    "id": 1,
                    "question": "This is a question",
                    "answer": "This is an answer",
                    "difficulty": 5,
                    "category": 5
                }
            ],
            "totalQuestions": 100,
            "currentCategory": "Entertainment"
        }
        res = self.client().post('/questions', json = json_data)
        data = res.get_json()
    
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
    #end region
    
    # #region @app.route('/categories/<int:category_id>/questions')
    def test_get_question_by_category_success(self):
        request_category = Category.query.first()
        request_category_id = request_category.id
        res = self.client().get(f'/categories/{request_category_id}/questions')
        data = res.get_json()
        all_questions = Question.query.filter(Question.category == request_category_id).all()
        format_questions = [question.format() for question in all_questions]
        currentCategory = Category.query.filter(Category.id == request_category_id).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['questions'], format_questions)
        self.assertEqual(data['totalQuestions'], len(format_questions))
        self.assertEqual(data['currentCategory'], currentCategory.type)
    
    def test_get_question_by_category_failed(self):
        res = self.client().get('/categories/999/questions')
        data = res.get_json()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['questions'], [])
        self.assertEqual(data['totalQuestions'], 0)
        self.assertEqual(data['currentCategory'], "")
    #endregion
    
    #region @app.route('/quizzes', methods=['POST'])
    def test_get_quizzes_success(self):
        request_data = {
            'previous_questions': [1, 4, 20, 15],
            'quiz_category': 'Science'
        }
        res = self.client().post('/quizzes', json=request_data)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
    
    def test_get_quizzes_failed(self):
        request_data = {
            'previous_questions': [],
            'quiz_category': 'abc'
        }
        res = self.client().post('/quizzes', json='request_data')
        data = res.get_json()
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
    #endregion
    
    #region @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def test_delete_questions_success(self):
        question = Question(question="question", answer="answer", category="1", difficulty=1)
        question.insert()
        question_id = question.id

        res = self.client().delete(f"/questions/{question_id}")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        
    def test_delete_questions_failed(self):
        res = self.client().delete("/questions/1000")

        self.assertEqual(res.status_code, 404)
    #endregion
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()