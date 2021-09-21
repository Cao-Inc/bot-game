import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta
import requests
import _db
import json

with open('config.json') as f:
    config = json.load(f)

rate = {
  "SH": config["rateSH"],
  "GT": config["rateGT"]
}

guildId = config["guildId"]
channelId = config["channelId"]

class Calc(commands.Cog):
  
  def __init__(self, bot):
      self.bot = bot
      self.index = 0
      self.is15h = True
      self.is18h = True
      self.is18h32 = True
      self.sol.start()

  @tasks.loop(seconds=2)
  async def sol(self):
    end = datetime.now()

    if (self.is15h and end.hour == 15 and end.minute == 00):
      self.is15h = False
      guild = self.bot.get_guild(guildId)
      channel = guild.get_channel(channelId)
      await channel.send('Hello 15h')

    if (self.is18h and end.hour == 18 and end.minute == 0):
      self.is18h = False
      guild = self.bot.get_guild(guildId)
      channel = guild.get_channel(channelId)
      await channel.send(f'Cuộc thi ngày {end.day}-{end.month}-{end.year} kết thúc')

    if (self.is18h32 and end.hour == 18 and end.minute == 32):
      self.is18h32 = False
      guild = self.bot.get_guild(guildId)
      channel = guild.get_channel(channelId)
      URL = 'http://api.xoso.me/app/homepage'
      res_json = requests.get(URL)
      res = {
        "SH": res_json.json()['data']['lottery']['mb']['loto'],
        "GT": [res_json.json()['data']['lottery']['mb']['lotData']['DB'][0][-2:]]
      }

      yesterday = end + timedelta(days=-1)
      start = datetime(yesterday.year, yesterday.month, yesterday.day, 19, 00, 0, 0)
      
      winners = {}

      conditions = 'datetime BETWEEN ? and ?'
      data = (start, end)

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
            
            member = await guild.fetch_member(int(discordID))
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
          await channel.send(embed=embed)
        except Exception as e:
          await channel.send('Something wrong!!! Pls call Devil')
      else:
          await channel.send('Ngày gần nhất không có thí sinh trúng tuyển')

    if (end.hour == 19 and end.minute == 0):
      self.is15h = True
      self.is18h = True
      self.is18h32 = True

  @sol.before_loop
  async def before_sol(self):
    await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Calc(bot))