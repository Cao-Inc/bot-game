import discord
from discord.ext import commands
import random
import _db
from . import _helper

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send('Pong')

    @commands.command(name='coinflip', aliases=['coinf', 'cf', 'cflip'])
    async def coinflip(self, ctx, coins: int = 0, side: str = 'h'):
      isNewMember = _helper.isNewPlayer(ctx)
      if (isNewMember):
        await ctx.send(embed = isNewMember)

      discordID = ctx.message.author.id
      embed = discord.Embed()
      embed.title = "Coin Flip!"
      embed.set_footer(text=f'Requested by {ctx.message.author.name}')

      member = _db.select_one_from('bot_member', 'discordID=?', (discordID,))
      memberCoins = member[1]
      if (coins <= 0) or (coins > memberCoins):
        embed.description = f'Không chơi với người ít tiền nhớ'
        embed.colour = discord.Color.red()
        await ctx.send(embed = embed)
        return

      res = random.choice(['t', 'h'])
      if (res == side):
        embed.description = f'Chúc mừng bạn đã thắng {coins} coins.'
        embed.colour = discord.Color.gold()
        memberCoins += coins
      else:
        embed.description = f'Chúc mừng bạn đã thua {coins} coins.'
        embed.colour = discord.Color.red()
        memberCoins -= coins

      try:
        set_cond = 'money=?'
        where_cond = 'discordID=?'
        data = (memberCoins, discordID)
        _db.update('bot_member', set_cond, where_cond, data)
        await ctx.send(embed = embed)
      except Exception as e:
        await ctx.send('Failed to update your coins. Pls try again later!')
        raise e


    @commands.command(name='8b')
    async def _8ball(self, ctx, *arg):
        answers = [
            'Tất nhiên là có',
            'Chắc con mẹ nó luôn bạn êi',
            'Đùa đấy',
            'Đang đói...',
            'UwU tự chọn...',
            'Tất nhiên là không',
            'Không chắc đâu',
            'Chỉ hôm nay, chắc zl...',
            'Có thể',
            'Noooo...',
            'Ngủ rồi zzz...',
            'Chỉ hôm nay, nhưng mà ko chắc',
            '<liec:759389970649055252>',
            '<liec:759389970649055252>'
        ]
        msg = 'Question: {}\n'.format(' '.join(arg))
        msg += f'Answer: {random.choice(answers)}\n'
        msg += f'Requested by {ctx.message.author.name}'
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(Fun(bot))