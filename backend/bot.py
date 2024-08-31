from discord.ext import commands
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import discord
import queue
import re
import json

from utils.leaderboardOps import handle_thank_you_message
from utils.rulesOp import rule_trigger

from commands.resetdb import reset_database
from commands.addrule import add_rule
from commands.sync import sync
from commands.eat import eat
from commands.removerule import remove_rule

DATABASE_URL = 'sqlite:///messages.db'
CONFIG_FILE = 'config.json'
COOLDOWN_SECONDS = 150

# Database setup
engine = create_engine(DATABASE_URL) 
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
with open(CONFIG_FILE) as f:
    DISCORD_BOT_TOKEN = json.loads(f.read())


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
message_queue = queue.Queue()
bot_running = False
cooldowns = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    


@bot.event
async def on_message(message: discord.message.Message):
    if message.author == bot.user:
        return

    with Session() as session:
        if re.search(r"thank|thx", message.content, re.IGNORECASE):
            await handle_thank_you_message(message, session, COOLDOWN_SECONDS)

        await rule_trigger(message)
        await bot.process_commands(message)
        
bot.add_command(reset_database)
bot.add_command(add_rule)
bot.add_command(sync(bot))
bot.add_command(eat)
bot.add_command(remove_rule)

def run_bot():
    bot.run(DISCORD_BOT_TOKEN['BotToken'])