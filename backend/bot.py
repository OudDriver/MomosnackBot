from discord.ext import commands
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import discord
import queue
import re
import json

# Database setup
engine = create_engine('sqlite:///messages.db')  # Choose your preferred database
Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    author = Column(String)
    amount = Column(Integer)
    latestTimeStamp = Column(DateTime)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Discord bot setup
with open("config.json") as f:
    DISCORD_BOT_TOKEN = json.loads(f.read())

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

message_queue = queue.Queue()

bot_running = False

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message: discord.message.Message):
    if message.author == bot.user:
        return
    
    if not re.search("thanks", message.content, re.IGNORECASE):
        return

    session = Session()
    try:
        existing_message = session.query(Message).filter_by(author=str(message.author)).first()
        if existing_message:
            existing_message.amount += 1
            existing_message.latestTimeStamp = message.created_at
        else:
            new_message = Message(amount=1, author=str(message.author), latestTimeStamp=message.created_at)
            session.add(new_message)

        session.commit()

        # Emit updated leaderboard data
        leaderboard = session.query(Message).order_by(Message.amount.desc()).all()
        leaderboard_data = [{'author': msg.author, 'amount': msg.amount, 'latestTimeStamp': msg.latestTimeStamp.isoformat()} for msg in leaderboard]
        message_queue.put({'leaderboard': leaderboard_data})
    finally:
        session.close()


def run_bot():
    global bot_running
    if bot_running:
        print("Bot is already running!")
        return
    bot_running = True
    bot.run(DISCORD_BOT_TOKEN['BotToken'])