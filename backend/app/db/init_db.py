from app.db.session import Base, engine
import app.models  # noqa: F401  (registers the tables on Base)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("Tables created:", ", ".join(Base.metadata.tables))

if __name__ == "__main__":
    init_db()