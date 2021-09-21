import discord
from discord.ext import commands

class Mod(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='clear')
  @commands.has_role('Admin')
  async def clear(self, ctx, amount:int=0):
    await ctx.channel.purge(limit = amount+1)

def setup(bot):
  bot.add_cog(Mod(bot))