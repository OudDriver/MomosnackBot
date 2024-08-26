from discord.ext import commands
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import discord
import queue
import re
import json
import time
from utils.leaderboardOps import update_message_count, get_leaderboard_data

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

@bot.command(name='leaderboard', help='Displays the leaderboard')
async def leaderboard(ctx: commands.Context):
    with Session() as session:
        leaderboard_data = get_leaderboard_data(session)
        
        if not leaderboard_data:
            await ctx.send("The leaderboard is currently empty.")
            return
        
        leaderboard_message = "🏆 **Leaderboard** 🏆\n\n"
        for idx, entry in enumerate(leaderboard_data, start=1):
            leaderboard_message += f"{idx}. {entry['author']} - {entry['amount']} momosnacks\n"
        
        await ctx.send(leaderboard_message)

@bot.command(name='resetdb', help='Resets the database (admin only)')
@commands.has_permissions(administrator=True)  # Restrict to admins
async def reset_database(ctx: commands.Context):
    with Session() as session:
        try:
            session.query(Message).delete()
            session.commit()
            await ctx.send("Database reset successfully!")
        except Exception as e:
            await ctx.send(f"Error resetting database: {e}")
            
@bot.command(name="eat", help="Eats a momosnack")
async def eat(ctx: commands.Context):
    with Session() as session:
        existing_message = session.query(Message).filter_by(author=str(ctx.author)).first()
        if not existing_message or existing_message.amount == 0:
            await ctx.reply("You don't have any momosnacks 😦")
            return
        
        update_message_count(session, ctx.author, ctx.message.created_at, increment=False)
        message_queue.put({'leaderboard': get_leaderboard_data(session)})

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

        await bot.process_commands(message)

def run_bot():
    global bot_running
    if bot_running:
        print("Bot is already running!")
        return
    bot_running = True
    bot.run(DISCORD_BOT_TOKEN['BotToken'])