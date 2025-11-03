from flask import Flask, redirect, url_for, render_template
from flask_jwt_extended import JWTManager
from routes.main_routes import bp
from routes.auth_routes import auth_bp
from schema.db_main import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key_here'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
jwt = JWTManager(app)

# Обработчик ошибок JWT
@jwt.unauthorized_loader
def unauthorized_callback(callback):
    return render_template('login.html'), 401

@jwt.invalid_token_loader
def invalid_token_callback(callback):
    return render_template('login.html'), 401

app.register_blueprint(bp)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
