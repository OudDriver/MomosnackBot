from discord.ext import commands
from utils.rulesOp import *
from utils.generalUtils import fixSkippedKey

@commands.hybrid_command(name='removerule', help='Removes the latest rule (admin only)', with_app_command=True)
@commands.has_permissions(administrator=True)
async def remove_rule(ctx: commands.Context):
    ruleDict = load_rules()

    if ruleDict:  # Check if there are any rules
        latest_rule_key = max(ruleDict, key=lambda k: int(k.split('-')[1]))
        del ruleDict[latest_rule_key]
        newData = fixSkippedKey(ruleDict)  # You'll still need fixSkippedKey

        save_rules(newData)
        await ctx.reply(f"Removed rule {latest_rule_key}!")
    else:
        await ctx.reply("There are no rules to remove.")