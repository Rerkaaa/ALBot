from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from decouple import config

# Direct PostgreSQL connection string
DATABASE_URL = f"postgresql+psycopg2://{config('DB_USER')}:{config('DB_PASSWORD')}@localhost:5432/mydb"

# Create the engine
engine = create_engine(DATABASE_URL)

# Set up session and base
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define the Conversation model
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    message = Column(String)
    response = Column(String)

# Create the tables
Base.metadata.create_all(engine)

print("Tables created successfully")