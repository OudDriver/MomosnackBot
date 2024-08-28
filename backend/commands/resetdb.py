from discord.ext import commands
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

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

@commands.hybrid_command(name='resetdb', help='Resets the database (admin only)', with_app_command=True)
@commands.has_permissions(administrator=True)  # Restrict to admins
async def reset_database(ctx: commands.Context):
    with Session() as session:
        try:
            session.query(Message).delete()
            session.commit()
            await ctx.send("Database reset successfully!")
        except Exception as e:
            await ctx.send(f"Error resetting database: {e}")