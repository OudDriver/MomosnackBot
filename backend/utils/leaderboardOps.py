from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    author = Column(String)
    amount = Column(Integer)
    latestTimeStamp = Column(DateTime)

def get_leaderboard_data(session):
    """Retrieves and formats leaderboard data."""
    leaderboard = session.query(Message).order_by(Message.amount.desc()).all()
    return [{'author': msg.author, 'amount': msg.amount, 'latestTimeStamp': msg.latestTimeStamp.isoformat()} for msg in leaderboard]

def update_message_count(session, user, timestamp, increment=True):
    """Updates the message count for a user."""
    existing_message = session.query(Message).filter_by(author=str(user)).first()
    if existing_message:
        existing_message.amount += 1 if increment else -1
        existing_message.latestTimeStamp = timestamp
    else:
        new_message = Message(amount=1, author=str(user), latestTimeStamp=timestamp)
        session.add(new_message)
    session.commit()
    