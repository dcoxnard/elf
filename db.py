from sqlalchemy import create_engine

db_path = "sqlite:///db.sqlite"

engine = create_engine(db_path)
