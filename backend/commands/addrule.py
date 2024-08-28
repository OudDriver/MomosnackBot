from discord.ext import commands
from utils.rulesOp import *

@commands.hybrid_command(name='addrule', help='Adds a rule (admin only)', with_app_command=True)
@commands.has_permissions(administrator=True)
async def add_rule(ctx: commands.Context, *, new_rule: str):
    ruleDict = load_rules()
    
    nextKeyN = len(ruleDict) + 1
    nextKey = f"rule-{nextKeyN}"
    
    ruleDict[nextKey] = new_rule
    
    save_rules(ruleDict)
        
    await ctx.reply(f"Added {nextKey}!")