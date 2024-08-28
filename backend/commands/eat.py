from discord.ext import commands
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.leaderboardOps import update_message_count, get_leaderboard_data

engine = create_engine('sqlite:///messages.db') 
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    author = Column(String)
    amount = Column(Integer)
    latestTimeStamp = Column(DateTime)
    
@commands.hybrid_command(name="eat", help="Eats a momosnack", with_app_command=True)
async def eat(ctx: commands.Context):
    from bot import message_queue
    with Session() as session:
        existing_message = session.query(Message).filter_by(author=str(ctx.author)).first()
        if not existing_message or existing_message.amount == 0:
            await ctx.reply("You don't have any momosnacks 😦")
            return
        
        update_message_count(session, ctx.author, ctx.message.created_at, increment=False)
        message_queue.put({'leaderboard': get_leaderboard_data(session)})