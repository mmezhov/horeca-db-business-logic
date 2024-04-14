import requests
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db_model import Scores
from src.config import Config


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)


def print_five_scores_rows():
    with Session() as session:
        scores_list = session.query(Scores).limit(5).all()
        if len(scores_list) > 0:
            for score in scores_list:
                print("id:", score.id,
                    "timestamp:", score.timestamp,
                    "employee_id:", score.employee_id,
                    "criteria_id:", score.criteria_id,
                    "score:", score.score)
        else:
            print("Данных пока нет")

def insert_scores():
    # Data to insert
    data = {
        "scores":[
            {"employee_id": 1, "criteria_id": 1, "score": 0},
            {"employee_id": 1, "criteria_id": 2, "score": 1},
            {"employee_id": 1, "criteria_id": 3, "score": 1}
        ]
    }

    # Отправка POST запроса с данными в формате JSON
    response = requests.post(
        Config.API_URL +'/scores',
        json=data,
        headers={'Authorization': f'Bearer {Config.TOKEN}'}
    )

    # Проверка статуса ответа
    if response.status_code == 200:
        print("Запрос успешно отправлен на сервер БД")
    else:
        print("Произошла ошибка при отправке запроса на сервер БД")
        print("response.status_code: ", response.status_code)


if __name__ == "__main__":
    insert_scores()
    print_five_scores_rows()
