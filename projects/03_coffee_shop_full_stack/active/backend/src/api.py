import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()


# ROUTES
@app.route('/drinks')
def get_drinks():
    selection = Drink.query.order_by(Drink.id).all()
    selection_short = []
    if len(selection) == 0:
        abort(404)

    for drink in selection:
        selection_short.append(drink.short())

    return jsonify({'success':True,
                    'drinks':selection_short
                    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    selection = Drink.query.order_by(Drink.id).all()
    selection_long = []
    if len(selection) == 0:
        abort(404)

    for drink in selection:
        selection_long.append(drink.long())

    return jsonify({'success':True,
                    'drinks':selection_long
                    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = json.dumps(body.get('recipe', None))

    try:
        drink = Drink(title=new_title,
                      recipe=new_recipe)
        drink.insert()

        selection = Drink.query.order_by(Drink.id).all()
        selection_long = []
        for drink in selection:
            selection_long.append(drink.long())

        return jsonify({
            'success': True,
            'drinks': selection_long
        })
    except Exception as e:
        abort(422, str(e))


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):

    selected_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not selected_drink:
        abort(404, "Specified Drink not found")

    body = request.get_json()
    try:
        if 'title' in body:
            selected_drink.title = body.get('title')

        if 'recipe' in body:
            selected_drink.recipe = body.get('recipe')

        selected_drink.update()

        selection = Drink.query.order_by(Drink.id).all()
        selection_long = []
        for drink in selection:
            selection_long.append(drink.long())

        return jsonify({
            'success': True,
            'drinks': selection_long
        })
    except:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
          abort(404)

        drink.delete()

        return jsonify({
          'success': True,
          'deleted': drink_id
        })

    except:
      abort(422)

# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable: " + str(error)
    }), 422

@app.errorhandler(AuthError)
def Unauthorized(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), 401


@app.errorhandler(404)
def notfound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404
