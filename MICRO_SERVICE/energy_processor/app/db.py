from sqlmodel import create_engine, SQLModel, Session
import os

import time
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:0823@db:5432/microservicios")

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    retries = 5
    while retries > 0:
        try:
            SQLModel.metadata.create_all(engine)
            print("Database initialized successfully.")
            break
        except OperationalError as e:
            retries -= 1
            print(f"Database not ready. Retrying in 2 seconds... ({retries} retries left)")
            time.sleep(2)
    if retries == 0:
        print("Could not connect to the database. Exiting.")
        raise OperationalError("Failed to connect to DB after retries", params=None, orig=None)

def get_session():
    with Session(engine) as session:
        yield session
