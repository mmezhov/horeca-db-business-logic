from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db_model import Criteria
from src.config import Config


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)


def print_five_criteria_rows():
    with Session() as session:
        criteria_list = session.query(Criteria).limit(5).all()

        for criteria in criteria_list:
            print(criteria.id, criteria.name)


if __name__ == "__main__":
    print_five_criteria_rows()
