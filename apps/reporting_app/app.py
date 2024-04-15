import logging
import pytz

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from src.db_model import db, Scores, Criteria
from src.config import Config
from pathlib import Path
from datetime import datetime


LOG_LEVEL = logging.DEBUG
CWD = Path.cwd()
MODULE_NAME = 'horeca_db_business_app'
BAD_REQUEST_CODE = 400
UNAUTHORIZED_CODE = 401
OK_STATUS_CODE = 200
INTERNAL_SERVER_ERROR = 500


log = logging.getLogger(MODULE_NAME)
log_handler = logging.FileHandler(CWD / f'logs/{MODULE_NAME}.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log_handler.setLevel(LOG_LEVEL)
log_handler.setFormatter(formatter)
log.addHandler(log_handler)
logging.basicConfig(level=LOG_LEVEL)


# Инициализация Flask-приложения
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)  # Инициализируем объект db


# Главная страница
@app.route('/')
def index():
	return 'Hello from Horeca App!'


@app.route('/api/scores', methods=['POST'])
def scores_handler():
	# Получение данных из JSON запроса
	data = request.json
	_, token = request.headers.get('Authorization').split(' ')

	if token != Config.TOKEN:
		return jsonify({"error": "Unauthorized"}), UNAUTHORIZED_CODE

	if request.method == 'POST':
		if (data is None or 'scores' not in data):
			return jsonify({"error": "Invalid JSON data"}), BAD_REQUEST_CODE

		try:
			for score_data in data.get('scores'):
				new_score = Scores(
					employee_id = score_data.get('employee_id'),
					criteria_id = score_data.get('criteria_id'),
					score = score_data.get('score'),
					timestamp = datetime.now(pytz.utc)  # Установка значения timestamp в UTC
				)
				db.session.add(new_score)
			db.session.commit()
		except:
			db.session.rollback()
			log.error("Error with inserting data into `scores` table", exc_info=True)
			return jsonify({"error": "Error inserting scores data"}), INTERNAL_SERVER_ERROR

	return jsonify({"success": "Success inserted the data into a db"}), OK_STATUS_CODE


@app.route('/api/criteria', methods=['GET','POST'])
def criteria_handler():
	_, token = request.headers.get('Authorization').split(' ')

	if token != Config.TOKEN:
		return jsonify({"error": "Unauthorized"}), UNAUTHORIZED_CODE

	if request.method == 'GET':
		try:
			criteria = Criteria.query.all()
			criteria_list = [{'id': crit.id, 'name': crit.name} for crit in criteria]
			return jsonify(criteria_list), OK_STATUS_CODE
		except:
			log.error("Error with getting data from `criteria` table", exc_info=True)
			return jsonify({"error": "Internal server error"}), INTERNAL_SERVER_ERROR


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)
