from discord.ext import commands
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import discord
import queue
import re
import json
import time
from utils.leaderboardOps import *

# Database setup
engine = create_engine('sqlite:///messages.db') 
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
cooldowns = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message: discord.message.Message):
    thankedUsers = []
    
    if message.author == bot.user:
        return

    with Session() as session:
        if re.search(r"thank|thx", message.content, re.IGNORECASE): 
            if message.mentions:
                for mentionedUser in message.mentions:
                    if message.author == mentionedUser:
                        # User is mentioning themselves
                        await message.reply("You can't thank yourself!")
                        return
                    
                    update_message_count(session, mentionedUser.name, message.created_at, True)
                    
                    thankedUsers.append(mentionedUser.name)
                    print(thankedUsers)
                    
            if message.author.id in cooldowns and time.time() - cooldowns[message.author.id] < 150:
                await message.reply(f"You're thanking too much! You have to wait {time.time() - cooldowns[message.author.id]} seconds before you can thank again.")
                return
            else:
                cooldowns[message.author.id] = time.time()
                
            finalMessage = ""
            
            if thankedUsers:
                if len(thankedUsers) == 1:
                    finalMessage = f"{thankedUsers[0]} got thanked!"
                else:
                    finalMessage = ", ".join(thankedUsers[:-1]) + f", and {thankedUsers[-1]} got thanked!"
                    
                await message.reply(finalMessage)
                    
            message_queue.put({'leaderboard': get_leaderboard_data(session)})
                
        elif message.content.startswith("!eat"):
            existing_message = session.query(Message).filter_by(author=str(message.author)).first()
            if not existing_message or existing_message.amount == 0:
                await message.reply("You don't have any momosnacks 😦")
                return

            update_message_count(session, message, increment=False)
            message_queue.put({'leaderboard': get_leaderboard_data(session)})

1
def run_bot():
    global bot_running
    if bot_running:
        print("Bot is already running!")
        return
    bot_running = True
    bot.run(DISCORD_BOT_TOKEN['BotToken'])