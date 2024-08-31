from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import Session
import time

Base = declarative_base()
cooldowns = {}

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    author = Column(String)
    amount = Column(Integer)
    latestTimeStamp = Column(DateTime)

def get_leaderboard_data(session):
    """Retrieves and formats leaderboard data."""
    leaderboard = session.query(Message).order_by(Message.amount.desc()).all()
    return [{'author': msg.author, 'amount': msg.amount, 'latestTimeStamp': msg.latestTimeStamp.isoformat() + "Z"} for msg in leaderboard]

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

async def handle_thank_you_message(message, session: Session, cooldownTime):
    from bot import message_queue
    thanked_users = []

    if message.mentions:
        for mentioned_user in message.mentions:
            if message.author == mentioned_user:
                await message.reply("You can't thank yourself!")
                return

            update_message_count(session, mentioned_user.name, message.created_at, True)
            thanked_users.append(mentioned_user.name)

    if message.author.id in cooldowns and time.time() - cooldowns[message.author.id] < cooldownTime:
        remaining_cooldown = round(cooldownTime - (time.time() - cooldowns[message.author.id]))
        await message.reply(f"You're thanking too much! You have to wait {remaining_cooldown} seconds before you can thank again.")
        return

    cooldowns[message.author.id] = time.time()

    if thanked_users:
        if len(thanked_users) == 1:
            final_message = f"{thanked_users[0]} got thanked!"
        else:
            final_message = ", ".join(thanked_users[:-1]) + f", and {thanked_users[-1]} got thanked!"
        await message.reply(final_message)
        
    message_queue.put({'leaderboard': get_leaderboard_data(session)})