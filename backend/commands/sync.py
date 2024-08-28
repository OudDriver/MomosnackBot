from discord.ext import commands

def sync(bot):
    @commands.hybrid_command(name="sync", help="Syncs command (admin only)", with_app_command=True)
    async def command(ctx: commands.Context):
        await bot.tree.sync()
        await ctx.send("Synced!")
        
    return command