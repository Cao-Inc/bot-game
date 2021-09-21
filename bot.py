import discord
from discord.ext import commands
import os
import json

with open('config.json') as f:
    config = json.load(f)

bot_prefix = config['prefix']
token = config['token']

bot = commands.Bot(command_prefix=bot_prefix)

@bot.command(name='rel')
@commands.is_owner()
async def rel(ctx):
    for cog in os.listdir('./cogs'):
        if (cog.endswith('.py') and (not cog.startswith('_'))):
            try:
                cog = f'cogs.{cog[:-3]}'
                bot.unload_extension(cog)
                bot.load_extension(cog)
            except Exception as e:
                print(f'{cog} can not be loaded!')
                raise e
    await ctx.send('Done!')

for cog in os.listdir('./cogs'):
    if (cog.endswith('.py') and (not cog.startswith('_'))):
        try:
            cog = f'cogs.{cog[:-3]}'
            bot.load_extension(cog)
        except Exception as e:
            print(f'{cog} can not be loaded!')
            raise e

bot.run(token)

