import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}@{}/{}".format('student', 'localhost:5432', self.database_name)
        
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path
        })

        self.client = self.app.test_client

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #region app.route('/categories', methods=['GET'])
    def test_retrieve_categories_success(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])
        
    def test_retrieve_categories_failed(self):
        res = self.client().get('/categories/x')
        data = json.loads(res.data)
    
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
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["categories"]))
        self.assertEqual(data["currentCategory"], 0)
        
    def test_get_questions_failed(self):
        res = self.client().get("/questions/aa")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    #endregion
    
    #region @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def test_delete_questions_success(self):
        res = self.client().delete("/questions/67")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        
    def test_delete_questions_failed(self):
        res = self.client().delete("/questions/1000")
        # data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
    # #endregion
    
    # #region @app.route('/questions', methods=['POST']) #! 4 case for both "search" and "create" Question
    # # case seach Question
    def test_seach_question_success(self):
        res = self.client().post('/questions', json={"searchTerm": "How"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])
        self.assertEqual(data["currentCategory"], 0)

    def test_seach_question_failed(self):
        res = self.client().get('/categories/x')
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
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
        data = json.loads(res.data)
        
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
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
    #end region
    
    #region @app.route('/categories/<int:category_id>/questions')
    def test_get_question_by_category_success(self):
        request_category_id = 5
        res = self.client().get('/categories/5/questions')
        data = json.loads(res.data)
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
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()