from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from schema.db_main import db, User
from werkzeug.exceptions import BadRequest

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Username, email and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=str(user.id))
    response = jsonify({'access_token': access_token, 'message': 'Login successful'})
    response.set_cookie('access_token_cookie', access_token, httponly=True, secure=False, samesite='Lax', path='/')
    return response, 200

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    return jsonify({'message': f'Hello, {user.username}!'}), 200

@auth_bp.route('/update_profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    data = request.get_json()
    new_username = data.get('username')
    new_email = data.get('email')

    if not new_username or not new_email:
        return jsonify({'message': 'Username and email are required'}), 400

    # Проверка уникальности
    if User.query.filter_by(username=new_username).first() and new_username != user.username:
        return jsonify({'message': 'Username already exists'}), 400

    if User.query.filter_by(email=new_email).first() and new_email != user.email:
        return jsonify({'message': 'Email already exists'}), 400

    user.username = new_username
    user.email = new_email
    db.session.commit()

    return jsonify({'message': 'Profile updated successfully'}), 200

@auth_bp.route('/delete_account', methods=['DELETE'])
@jwt_required()
def delete_account():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    db.session.delete(user)
    db.session.commit()

    response = jsonify({'message': 'Account deleted successfully'})
    response.set_cookie('access_token_cookie', '', expires=0, path='/')
    return response, 200