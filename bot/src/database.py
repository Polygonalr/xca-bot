from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import dotenv_values

config = dotenv_values(".env")
engine = create_engine(f"sqlite:///{ config['DATABASE_FILE'] }")
db_session = scoped_session(
    sessionmaker(autocommit=False,autoflush=False,bind=engine)
)

def init_db():
    from models import Base
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()