from discord.ext import commands
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import discord
import queue
import re
import json
import time

from utils.leaderboardOps import update_message_count, get_leaderboard_data
from utils.rulesOp import *

from commands.resetdb import reset_database
from commands.addrule import add_rule
from commands.sync import sync
from commands.eat import eat
from commands.removerule import remove_rule

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
                        await message.reply("You can't thank yourself!")
                        return
                    
                    update_message_count(session, mentionedUser.name, message.created_at, True)
                    
                    thankedUsers.append(mentionedUser.name)
                    print(thankedUsers)
                    
            if message.author.id in cooldowns and time.time() - cooldowns[message.author.id] < 150:
                await message.reply(f"You're thanking too much! You have to wait {round(150 - (time.time() - cooldowns[message.author.id]))} seconds before you can thank again.")
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
        
        regexContent = re.finditer(r"rule-\d+", message.content, re.IGNORECASE)
        if re.search(r"rule-\d+", message.content, re.IGNORECASE): 
            RULE_DICT = load_rules()
                
            ruleMessage = ""
            for rule in regexContent:
                ruleString = rule.group()
                for key in RULE_DICT:
                    if ruleString in key:
                        ruleMessage += f"{RULE_DICT[ruleString]}\n\n"
                        
            if ruleMessage != "" :
                await message.reply(ruleMessage)
            
        await bot.process_commands(message)
        
bot.add_command(reset_database)
bot.add_command(add_rule)
bot.add_command(sync(bot))
bot.add_command(eat)
bot.add_command(remove_rule)

def run_bot():
    global bot_running
    if bot_running:
        print("Bot is already running!")
        return
    bot_running = True
    bot.run(DISCORD_BOT_TOKEN['BotToken'])