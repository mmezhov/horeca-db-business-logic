from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src.db_model import db, Criteria
from src.config import Config


# Инициализация Flask-приложения
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)  # Инициализируем объект db


# Главная страница
@app.route('/')
def index():
	return 'Hello from Horeca App!'


@app.route('/api/scores', methods=['POST'])
def api_insert_score():
	...



if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)
