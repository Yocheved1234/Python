from flask import Flask, request, jsonify, make_response , abort
# from flask_cors import CORS
from functools import wraps
from user import User
import json
import random
app = Flask(__name__)

# CORS(app, supports_credentials=True)

def isConnected(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        name = request.cookies.get('user')
        if name:
            return func(*args, **kwargs)
        else:
            return abort(401)
    return wrapper

def find_word(num):
        try:
            with open('Words.txt', 'r') as file:
                words = file.read().splitlines()
        except FileNotFoundError:
            return jsonify({"error": "Words file not found."}), 500
        random.shuffle(words)
        selected_word = words[(num%len(words))-1]
        return selected_word

def all_user():
    try:
        with open('json.json', 'r') as file:
            u = json.load(file)
    except FileNotFoundError:
        u = []
    except json.JSONDecodeError:
        u = []
    return u

@app.route('/add_win', methods=['POST'])
@isConnected
def add_win():
    data = request.json

    if not data:
        return make_response(jsonify({"error": "No data provided."}), 400)
    name = data.get('name')
    password = data.get('password')
    word = data.get('word')

    if not name or not password or not word:
        return make_response(jsonify({"error": "Missing fields in request."}), 400)

    filename = 'json.json'
    try:
        with open(filename, 'r') as file:
            players = json.load(file)
    except FileNotFoundError:
        players = []
    except json.JSONDecodeError:
        return make_response(jsonify({"error": "Invalid JSON format in file."}), 500)

    for player in players:
        if player['name'] == name and player['password'] == password:
            if word not in player['words']:
                player['words'].append(word)
            player['win'] = player.get('win', 0) + 1
            with open(filename, 'w') as file:
                json.dump(players, file)
            return jsonify(player)

    return make_response(jsonify({"error": "Player not found or incorrect password."}), 404)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    name = data.get('name')
    password = data.get('password')

    players = all_user()
    if any(player['name'] == name and player['password'] == password for player in players):
        response = make_response(f"Wellcome {name}!!!", 400)
        response.set_cookie("user", name, max_age=600, httponly=True, secure=False, samesite='None')
        return response

    new_user = User(name, password, len(players) + 1)
    players.append(new_user.to_dict())

    try:
        with open('json.json', 'w') as file:
            json.dump(players, file)
    except Exception as e:
        return make_response(f"Error saving user: {str(e)}", 500)

    response = make_response("Welcome - for your first time!")
    response.set_cookie("user", name, max_age=600, httponly=True, secure=False, samesite='None')
    return response

if __name__ == '__main__':
    app.run(debug=True)

    app.run(host='127.0.0.1', port=5000, debug=True)
