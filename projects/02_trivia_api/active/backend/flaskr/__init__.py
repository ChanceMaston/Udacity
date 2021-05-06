import os
from flask import Flask, request, abort, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
CATEGORIES_PER_PAGE = 10


def paginate_categories(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * CATEGORIES_PER_PAGE
    end = start + CATEGORIES_PER_PAGE

    current_category_list = selection[start:end]
    current_category = {category.id:category.type for category in current_category_list}

    return current_category


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all()
        current_category = paginate_categories(request, selection)

        if len(current_category) == 0:
            abort(404)

        return jsonify({'success':True,
                        'categories':current_category,
                        'total_categories': len(Category.query.all())
                        })

    @app.route('/questions')
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_question = paginate_questions(request, selection)
        categories = Category.query.all()
        categories_formatted = {category.id:category.type for category in categories}
        if len(current_question) == 0:
            abort(404)

        return jsonify({'success': True,
                        'questions': current_question,
                        'total_questions': len(Question.query.all()),
                        'categories': categories_formatted,
                        'current_category': 'ALL'
                        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

    @app.route('/questions', methods=['POST', 'PUT'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        search = body.get('searchTerm', None)

        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(selection.all()),
                    'current_category': 'ALL'
                })
            else:
               question = Question(question=new_question,
                                   answer=new_answer,
                                   category=new_category,
                                   difficulty=new_difficulty)
               question.insert()

               selection = Question.query.order_by(Question.id).all()
               current_questions = paginate_questions(request, selection)

               return jsonify({
                   'success': True,
                   'created': question.id,
                   'questions': current_questions,
                   'total_questions': len(Question.query.all())
           })
        except:
            abort(422)

    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_by_category(category_id):
        selection = Question.query.filter_by(category=str(category_id)).all()
        current_question = paginate_questions(request, selection)
        category = Category.query.filter_by(id=category_id).first()
        if len(current_question) == 0:
            abort(404)

        return jsonify({'questions': current_question,
                        'total_questions': len(selection),
                        'current_category': category.type
                        })

    @app.route('/quizzes', methods=['POST'])
    def play_quizzes():
        body = request.get_json()
        #  page = request.args.get('page', 1, type=int)
        all_category = {'id':0, 'type': 'ALL'}
        category = body.get('quiz_category', all_category)
        previous_questions = body.get('previous_questions', [])

        # Get a list of questions based on the category
        if category['id'] == 0:
            # All categories chosen
            selection = Question.query.all()
        else:
            selection = Question.query.filter_by(category=str(category['id'])).all()

        # Make new list based on selection that does not overlap with previous questions:
        new_selection = []
        for question_ins in selection:
            if question_ins.id in previous_questions:
                pass
            else:
                new_selection.append(question_ins)

        if len(new_selection) == 0:
            new_question = False
            return jsonify({'question': new_question})
        else:
            # Now, pick a random question from the remaining questions.
            question_index = random.randint(0, (len(new_selection)-1))
            new_question = new_selection[question_index]
            return jsonify({'question': new_question.format()})


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422
  
    return app

    