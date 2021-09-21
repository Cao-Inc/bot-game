import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'logged in {self.bot.user}')
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you!!!"))

def setup(bot):
    bot.add_cog(Events(bot))