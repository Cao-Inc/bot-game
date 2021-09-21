import discord
import _db
from datetime import datetime, timedelta

def isNewPlayer(ctx):
  discordID = ctx.message.author.id
  conditions = f'discordID=?'
  data = (discordID,)
  signed = _db.select_one_from('bot_member', conditions, data)

  if (not signed):
    try:
      before_yesterday = datetime.now() + timedelta(days=-2)
      data = (discordID, 50000, before_yesterday)
      _db.insert_into('bot_member', data)

      embed = discord.Embed()
      embed.title = "Welcome!"
      embed.description = f'Bạn được tặng **50000** coins.\nChúc bạn chơi game vui vẻ'
      embed.colour = discord.Color.green()
      embed.set_footer(text=f'Requested by {ctx.message.author.name}')
      return embed
    except Exception as e:
      raise e

  return False