from src.db.setup import Base, engine


def create_tables():
    Base.metadata.create_all(engine)


def drop_tables():
    Base.metadata.drop_all(engine)


if __name__ == "__main__":
    drop_tables()
    create_tables()
