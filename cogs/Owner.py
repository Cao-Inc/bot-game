import discord
from discord.ext import commands
import _db
import json
from datetime import datetime
import requests

with open('config.json') as f:
    config = json.load(f)

rate = {
  "SH": config["rateSH"],
  "GT": config["rateGT"]
}

guildId = config["guildId"]
channelId = config["channelId"]

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='gift')
    @commands.is_owner()
    async def gift(self, ctx, member: discord.Member = None, coins: int = 0):
      member = member if member else ctx.message.author
      coins = coins if coins else 10000
      try:
        discordID = member.id
        print(discordID, coins)
        _db.add_coins_to(discordID, coins)
        await ctx.send('Ok.')
      except Exception as e:
        await ctx.send('Failed.')
        raise e

    @commands.command(name='ts')
    @commands.is_owner()
    async def ts(self, ctx):
      guild = self.bot.get_guild(guildId)
      print(guild)
      channel = guild.get_channel(channelId)
      print(channel)
      await channel.send('ok')

    @commands.command(name='loto')
    @commands.is_owner()
    async def loto(self, ctx):
      URL = 'http://api.xoso.me/app/homepage'
      res_json = requests.get(URL)
      res = {
        "SH": res_json.json()['data']['lottery']['mb']['loto'],
        "GT": [res_json.json()['data']['lottery']['mb']['lotData']['DB'][0][-2:]]
      }

      now = datetime.now()
      winners = {}

      conditions = f'datetime < ?'
      data = (now,)
      allplayed = _db.select_all_from('bot_bet', conditions, data)

      for played in allplayed:
        winnerDiscordId = played[0]
        betType = played[1]
        number = played[2]
        money = played[3]

        winners.setdefault(winnerDiscordId, 0)
        winners[winnerDiscordId] += float(money) * rate[betType] * res[betType].count(number)

      if winners:
        try:
          embed = discord.Embed()
          embed.title = 'Danh sách các thí sinh trúng tuyển ngày gần nhất'
          embed.set_footer(text=f'Xin chúc mừng tất cả các bạn')
          msg = ''
          i = 0
          for discordID, wonMoney in winners.items():
            if wonMoney <= 0:
              continue
            
            member = await ctx.message.guild.fetch_member(int(discordID))
            i += 1
            msg += f'{i}. {member.mention} trúng giải **{int(wonMoney)}** coins\n'
            
            conditions = f'discordID=?'
            data = (discordID,)
            player = _db.select_one_from('bot_member', conditions, data)

            set_cond = 'money=?'
            where_cond = 'discordID=?'
            data = (wonMoney+player[1], discordID)
            _db.update('bot_member', set_cond, where_cond, data)

          embed.description = msg
          await ctx.send(embed=embed)
        except Exception as e:
          await ctx.send('Something wrong!!! Pls call Devil')
      else:
          await ctx.send('Ngày gần nhất không có thí sinh trúng tuyển')

      await ctx.send('Done!')

    @commands.command(name='reload')
    @commands.is_owner()
    async def reload(self, ctx, cog):
        try:
            cog = f'cogs.{cog}'
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
            await ctx.send(f'{cog} has been reloaded!')
        except Exception as e:
            raise e

    @commands.command(name='cldb')
    @commands.is_owner()
    async def cleardb(self, ctx):
      tables = ['bot_member', 'bot_bet', 'bot_winner']
      for table in tables:
        try:
          _db.delete_tables_content(table)  
          await ctx.send(f'{table} - Ok.')
        except Exception as e:
          await ctx.send(f'{table} - Failed.')
          raise e

    @commands.command(name='erase')
    @commands.is_owner()
    async def erase(self, ctx, member: discord.Member):
        
        conditions = 'discordID=?'
        data = (member.id,)
        
        signed = _db.select_one_from('bot_member', conditions, data)
        
        if not signed:
            await ctx.send(f'{member.name} chưa đăng ký')
            return
        
        try:
            _db.delete_from('bot_member', conditions, data)
            await ctx.send('Done!')
        except Exception as e:
            await ctx.send('Failed!')
            raise e

def setup(bot):
    bot.add_cog(Owner(bot))