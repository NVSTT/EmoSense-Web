from flask import Flask
from routes.main_routes import bp

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True)
