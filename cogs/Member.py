import discord
from discord.ext import commands
from discord.ext.commands.core import command
import requests
import _db
from datetime import datetime, timedelta
import json
import random
from . import _helper

with open('config.json') as f:
  config = json.load(f)

prefix = config["prefix"]

class Member(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='daily', aliases=['dl'])
  async def daily(self, ctx):
    isNewMember = _helper.isNewPlayer(ctx)
    if (isNewMember):
      await ctx.send(embed=isNewMember)

    try:
      discordID = ctx.message.author.id
      member = _db.select_one_from('bot_member', 'discordID=?', (discordID,))
      lastDailyReward = datetime.strptime(member[2], '%Y-%m-%d %H:%M:%S.%f') 
      if (lastDailyReward.day < datetime.now().day):
        dailyCoins = random.randint(10000, 50000)
        _db.add_coins_to(discordID, dailyCoins)
        set_cond = 'lastDailyReward=?'
        where_cond = 'discordID=?'
        data = (datetime.now(), discordID)
        _db.update('bot_member', set_cond, where_cond, data)
        embed = discord.Embed()
        embed.title = "Daily reward!"
        embed.description = f'Bạn nhận được **{dailyCoins}** coins.\nChúc bạn chơi game vui vẻ'
        embed.colour = discord.Color.green()
        embed.set_footer(text=f'Requested by {ctx.message.author.name}')
        await ctx.send(embed=embed)
        return

      embed = discord.Embed()
      embed.title = "Daily reward!"
      embed.description = f'Bạn đã nhận phần thưởng ngày hôm nay'
      embed.colour = discord.Color.red()
      embed.set_footer(text=f'Requested by {ctx.message.author.name}')
      await ctx.send(embed=embed)
      
    except Exception as e:
      embed = discord.Embed()
      embed.title = "Daily reward!"
      embed.description = f'Nhận thưởng hàng ngày lỗi.\nTìm Devil nhé'
      embed.colour = discord.Color.green()
      embed.set_footer(text=f'Requested by {ctx.message.author.name}')
      await ctx.send(embed=embed)
      raise e

  @commands.command(name='coins')
  async def coins(self, ctx):
    isNewMember = _helper.isNewPlayer(ctx)
    if (isNewMember):
      await ctx.send(embed=isNewMember)
      return

    discordID = ctx.message.author.id
    conditions = f'discordID=?'
    data = (discordID,)
    sumMoney = _db.select_one_from('bot_member', conditions, data)[1]
    
    embed = discord.Embed()
    embed.title = "Coins!"
    embed.description = f'Bạn có **{sumMoney}** coins trong tài khoản.\nChúc bạn chơi game vui vẻ'
    embed.colour = discord.Color.green()
    embed.set_footer(text=f'Requested by {ctx.message.author.name}')
    await ctx.send(embed=embed)
    
  @commands.command(name='commit', aliases=['cm', 'CM'])
  async def commit(self, ctx, betType:str, *arg):

    isNewMember = _helper.isNewPlayer(ctx)
    if (isNewMember):
      await ctx.send(embed=isNewMember)
      sumMoney = 50000
    else:
      discordID = ctx.message.author.id
      conditions = f'discordID=?'
      data = (discordID,)
      sumMoney = _db.select_one_from('bot_member', conditions, data)[1]

    betType = betType.upper()
    
    if not _db.isCorrect(betType, arg):
      embed = discord.Embed()
      embed.title = "Sai cú pháp!"
      embed.description = f'Cú pháp đúng: {prefix}commit betType num_1 coins_1 num_2 coins_2...\nChúc bạn chơi game vui vẻ'
      embed.colour = discord.Color.red()
      embed.set_footer(text=f'Requested by {ctx.message.author.name}')
      await ctx.send(embed=embed)
      return

    end = datetime.now()
    if (end.hour == 18):
      embed = discord.Embed()
      embed.title = "BTC đang chấm thi, quay lại sau 19h bạn nhé!"
      embed.colour = discord.Color.purple()
      embed.set_footer(text=f'Requested by {ctx.message.author.name}')
      await ctx.send(embed=embed)
      return

    commited = {
      'SH' : [],
      'GT' : []
    }

    noMoney = []

    await ctx.send('*Xin chờ...*')
    try:
      for i in range(0, len(arg)-1, 2):
        money = int(float(arg[i+1]))

        if (money > sumMoney):
          noMoney.append(arg[i])
          continue

        if end.hour in range(19, 24):
          start = datetime(end.year, end.month, end.day, 19, 0, 0, 0)
        else:
          yesterday = end + timedelta(days=-1)
          start = datetime(yesterday.year, yesterday.month, yesterday.day, 19, 0, 0, 0)
            
        played_cond = 'discordID=? and betType=? and number=? and datetime BETWEEN ? and ?'
        played_data = (discordID, betType, arg[i], start, end)

        played = _db.select_one_from('bot_bet', played_cond, played_data)
        if played:
          commited[betType].append(arg[i])
          continue

        data = (discordID, betType, arg[i], money, end)
        _db.insert_into('bot_bet', data)
        sumMoney -= money

      if ((not commited['SH']) and (not commited['GT']) and (not noMoney)):
        embed = discord.Embed()
        embed.title = "Dự thi thành công!"
        embed.colour = discord.Color.green()
        embed.set_footer(text=f'Requested by {ctx.message.author.name}')
        await ctx.send(embed=embed)
      else:
        msg = ''
        if commited['SH']:
          msg += 'Trùng mã số học: *{}*\n'.format(' '.join(commited['SH']))
        if commited['GT']:
          msg += 'Trùng mã giải tích: *{}*\n'.format(' '.join(commited['GT']))
        if noMoney:
          msg += 'Không đủ coins dự thi các mã: *{}*\n'.format(' '.join(noMoney))
        msg += 'Các mã còn lại (nếu có) đã dự thi thành công'
        embed = discord.Embed()
        embed.title = "Kết quả dự thi:"
        embed.description = msg
        embed.colour = discord.Color.green()
        embed.set_footer(text=f'Requested by {ctx.message.author.name}')
        await ctx.send(embed=embed)

      set_cond = 'money=?'
      where_cond = 'discordID=?'
      data = (sumMoney, discordID)
      _db.update('bot_member', set_cond, where_cond, data)

    except Exception as e:
      embed = discord.Embed()
      embed.title = "Dự thi thất bại!"
      embed.colour = discord.Color.green()
      embed.set_footer(text=f'Requested by {ctx.message.author.name}')
      await ctx.send(embed=embed)
      raise e

  @commands.command(name='getres', aliases=['gr'])
  async def getres(self, ctx):
      await ctx.send('Loading...')

      URL = 'http://api.xoso.me/app/homepage'
      res = requests.get(URL)

      msg_db = """```prolog
      {}```""".format('-' if (len(res.json()['data']['lottery']['mb']['lotData']['DB']) == 0) else res.json()['data']['lottery']['mb']['lotData']['DB'][0][-2:])

      msg_sh = """```prolog
      0: {}
      1: {}
      2: {}
      3: {}
      4: {}
      5: {}
      6: {}
      7: {}
      8: {}
      9: {}```""".format(
          '-' if (len(res.json()['data']['lottery']['mb']['dau']['0']) == 0) else '0{}'.format(' 0'.join(res.json()['data']['lottery']['mb']['dau']['0'])),
          '-' if (len(res.json()['data']['lottery']['mb']['dau']['1']) == 0) else '1{}'.format(' 1'.join(res.json()['data']['lottery']['mb']['dau']['1'])),
          '-' if (len(res.json()['data']['lottery']['mb']['dau']['2']) == 0) else '2{}'.format(' 2'.join(res.json()['data']['lottery']['mb']['dau']['2'])),
          '-' if (len(res.json()['data']['lottery']['mb']['dau']['3']) == 0) else '3{}'.format(' 3'.join(res.json()['data']['lottery']['mb']['dau']['3'])),
          '-' if (len(res.json()['data']['lottery']['mb']['dau']['4']) == 0) else '4{}'.format(' 4'.join(res.json()['data']['lottery']['mb']['dau']['4'])),
          '-' if (len(res.json()['data']['lottery']['mb']['dau']['5']) == 0) else '5{}'.format(' 5'.join(res.json()['data']['lottery']['mb']['dau']['5'])),
          '-' if (len(res.json()['data']['lottery']['mb']['dau']['6']) == 0) else '6{}'.format(' 6'.join(res.json()['data']['lottery']['mb']['dau']['6'])),
          '-' if (len(res.json()['data']['lottery']['mb']['dau']['7']) == 0) else '7{}'.format(' 7'.join(res.json()['data']['lottery']['mb']['dau']['7'])),
          '-' if (len(res.json()['data']['lottery']['mb']['dau']['8']) == 0) else '8{}'.format(' 8'.join(res.json()['data']['lottery']['mb']['dau']['8'])),
          '-' if (len(res.json()['data']['lottery']['mb']['dau']['9']) == 0) else '9{}'.format(' 9'.join(res.json()['data']['lottery']['mb']['dau']['9']))
      )

      embed = discord.Embed()
      embed.title = '__**Kết quả mới nhất của BTC**__'
      embed.colour = discord.Color.blue()
      embed.set_footer(text=f'Requested by {ctx.author.name}')
      embed.add_field(name='GT', value=msg_db, inline=False)
      embed.add_field(name='SH', value=msg_sh)
      
      await ctx.send(embed=embed)

  @commands.command(name='show')
  async def show(self, ctx):
      end = datetime.now()
      
      if (end.hour == 18 and end.minute < 35):
          await ctx.send('BTC đang chấm thi, quay lại sau 18h35 bạn nhé')
          return

      if end.hour in range(19, 24):
          start = datetime(end.year, end.month, end.day, 18, 30, 0, 0)
      else:
          yesterday = end + timedelta(days=-1)
          start = datetime(yesterday.year, yesterday.month, yesterday.day, 18, 30, 0, 0)

      conditions = 'datetime BETWEEN ? and ?'
      data = (start, end)
      winners = _db.select_all_from('bot_winner', conditions, data)
      if winners:
          embed = discord.Embed()
          embed.title = 'Danh sách các thí sinh trúng tuyển ngày gần nhất'
          embed.set_footer(text=f'Requested by {ctx.message.author.name}')
          msg = ''
          i = 0
          for winner in winners:
              member = ctx.message.guild.get_member(int(winner[0]))
              i += 1
              msg += f'{i}. {member.name} trúng giải {winner[1]} xu\n'
          embed.description = msg
          await ctx.send(embed=embed)
      else:
          await ctx.send('Ngày gần nhất không có thí sinh trúng tuyển')

  @commands.command(name='get')
  async def getpp(self, ctx, member: discord.Member = None):

    member = member if member else ctx.message.author

    discordID = member.id

    conditions = f'discordID=?'
    data = (discordID,)
    signed = _db.select_one_from('bot_member', conditions, data)
    if (not signed):
      embed = discord.Embed()
      embed.title = f"Thí sinh {member.name} chưa tham dự kỳ thi"
      embed.colour = discord.Color.green()
      embed.set_footer(text=f"Requested by {ctx.message.author.name}")
      await ctx.send(embed=embed)
      return

    end = datetime.now()
    if end.hour in range(19, 24):
      start = datetime(end.year, end.month, end.day, 19, 0, 0, 0)
    else:
      yesterday = end + timedelta(days=-1)
      start = datetime(yesterday.year, yesterday.month, yesterday.day, 19, 0, 0, 0)

    conditions = 'discordID=? and datetime BETWEEN ? and ?'
    data = (discordID, start, end)
    played = _db.select_all_from('bot_bet', conditions, data)

    if played:
      p = {
        'SH' : [],
        'GT' : []
      }

      for item in played:
        p[item[1]].append((item[2], item[3]))

      embed = discord.Embed()
      embed.title = f'Người chơi {member.name} đã dự thi như sau'
      embed.colour = discord.Color.green()
      embed.set_footer(text = f'Requested by {ctx.message.author.name}')
      
      if p['SH']:
        msg_sh = ''
        for ele in p['SH']:
          msg_sh += f'{ele[0]}  -  {ele[1]} coins\n'
        embed.add_field(name='Số học', value=msg_sh)
      
      if p['GT']:
        msg_gt = ''
        for ele in p['GT']:
          msg_gt += f'{ele[0]}  -  {ele[1]} coins\n'
        embed.add_field(name='Giải tích', value=msg_gt)

      await ctx.send(embed=embed)
    else:
      embed = discord.Embed()
      embed.title = f'Người chơi {member.name} không dự thi'
      embed.colour = discord.Color.green()
      embed.set_footer(text = f'Requested by {ctx.message.author.name}')
      await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Member(bot))