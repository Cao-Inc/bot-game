import discord
from discord.ext import commands
import requests
import _db
from . import _dbgame
from datetime import datetime, timedelta

class Member(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='commit')
  async def commit(self, ctx, betType:str, *arg):

    betType = betType.upper()
    discordID = ctx.message.author.id
    conditions = f'discordID=?'
    data = (discordID,)
    signed = _db.select_one_from('bot_member', conditions, data)

    sumMoney = 50000

    if (signed):
      sumMoney = signed[1]

    if (not signed):
      try:
        data = (discordID, sumMoney)
        _db.insert_into('bot_member', data)

        embed = discord.Embed()
        embed.title = "Welcome!"
        embed.description = f'Bạn được tặng {sumMoney} coins.'
        embed.colour = discord.Color.green()
        embed.set_footer(text="Chúc bạn chơi game vui vẻ")
        await ctx.send(embed=embed)
      except Exception as e:
        raise e
        return

    if not _db.isCorrect(betType, arg):
        msg = "Sai cú pháp"
        await ctx.send(msg)
        return

    end = datetime.now()
    if (end.hour == 18):
        await ctx.send('BTC đang chấm thi, quay lại sau 19h bạn nhé')
        return

    commited = {
        'SH' : [],
        'GT' : []
    }

    noMoney = []

    await ctx.send('Xin chờ...')
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
            await ctx.send('Dự thi thành công')
        else:
            msg = ''
            if commited['SH']:
                msg += 'Trùng mã số học: {}\n'.format(' '.join(commited['SH']))
            if commited['GT']:
                msg += 'Trùng mã giải tích: {}\n'.format(' '.join(commited['GT']))
            if noMoney:
              msg += 'Không đủ coins dự thi các mã: {}\n'.format(' '.join(noMoney))
            msg += 'Các mã số còn lại (nếu có) đã dự thi thành công'
            await ctx.send(msg)

        set_cond = 'money=?'
        where_cond = 'discordID=?'
        data = (sumMoney, discordID)
        _db.update('bot_member', set_cond, where_cond, data)

    except Exception as e:
        await ctx.send('Dự thi thất bại')
        raise e

    @commands.command(name='edit')
    async def edit(self, ctx, betType:str, number:str, newMoney:float):
        
        discordID = ctx.message.author.id
        betType = betType.upper()

        conditions = f'discordID=?'
        data = (discordID,)
        signed = _db.select_one_from('bot_member', conditions, data)
        if (not signed):
            embed = discord.Embed()
            embed.title = "Bạn chưa đăng ký ingame"
            embed.description = f'Đăng ký ingame để dự thi nhé bạn'
            embed.add_field(name='Cú pháp:', value='sign <ingame>',inline=True)
            embed.colour = discord.Color.green()
            embed.set_footer(text="Chúc bạn chơi game vui vẻ")
            await ctx.send(embed=embed)
            return

        if signed[2]:
            await ctx.send(f'{ctx.message.author.mention} Bạn bị ban con mẹ nó rồi')
            return

        if (not _db.isCorrect(betType,(number, newMoney))):
            msg = "Sai cú pháp"
            await ctx.send(msg)
            return

        end = datetime.now()
        if end.hour in range(19, 24):
            start = datetime(end.year, end.month, end.day, 19, 0, 0, 0)
        else:
            yesterday = end + timedelta(days=-1)
            start = datetime(yesterday.year, yesterday.month, yesterday.day, 19, 0, 0, 0)

        conditions = 'discordID=? and betType=? and number=? and datetime BETWEEN ? and ?'
        data = (discordID, betType, number, start, end)

        signed = _db.select_one_from('bot_bet', conditions, data)
        if (not signed):
            embed = discord.Embed()
            embed.title = "Cung cấp thông tin sai lệch"
            embed.description = f'Không có bài dự thi này'
            embed.colour = discord.Color.red()
            embed.set_footer(text="Ăn xiên bây giờ")
            await ctx.send(embed=embed)
            return

        try:
            newMoney = int(newMoney*1000)
            set_cond = 'money=?'
            where_cond = 'discordID=? and betType=? and number=? and datetime BETWEEN ? and ?'
            data = (newMoney, discordID, betType, number, start, end)
            _db.update('bot_bet', set_cond, where_cond, data)
            await ctx.send('Sửa bài thi thành công')
        except Exception as e:
            await ctx.send('Sửa bài thi thất bại')
            raise e

    @commands.command(name='delete')
    async def delete(self, ctx, betType:str, number:str):
        
        discordID = ctx.message.author.id
        betType = betType.upper()

        conditions = f'discordID=?'
        data = (discordID,)
        signed = _db.select_one_from('bot_member', conditions, data)
        if (not signed):
            embed = discord.Embed()
            embed.title = "Bạn chưa đăng ký ingame"
            embed.description = f'Đăng ký ingame để dự thi nhé bạn'
            embed.add_field(name='Cú pháp:', value='sign <ingame>',inline=True)
            embed.colour = discord.Color.green()
            embed.set_footer(text="Chúc bạn chơi game vui vẻ")
            await ctx.send(embed=embed)
            return

        if signed[2]:
            await ctx.send(f'{ctx.message.author.mention} Bạn bị ban con mẹ nó rồi')
            return

        if (not _db.isCorrect(betType,(number, '2'))):
            msg = "Sai cú pháp"
            await ctx.send(msg)
            return

        end = datetime.now()
        if end.hour in range(19, 24):
            start = datetime(end.year, end.month, end.day, 19, 0, 0, 0)
        else:
            yesterday = end + timedelta(days=-1)
            start = datetime(yesterday.year, yesterday.month, yesterday.day, 19, 0, 0, 0)

        conditions = 'discordID=? and betType=? and number=? and datetime BETWEEN ? and ?'
        data = (discordID, betType, number, start, end)

        signed = _db.select_one_from('bot_bet', conditions, data)
        if (not signed):
            embed = discord.Embed()
            embed.title = "Cung cấp thông tin sai lệch"
            embed.description = f'Không có bài dự thi này'
            embed.colour = discord.Color.red()
            embed.set_footer(text="Ăn xiên bây giờ")
            await ctx.send(embed=embed)
            return

        try:
            _db.delete_from('bot_bet', conditions, data)
            await ctx.send('Xóa bài thi thành công')
        except Exception as e:
            await ctx.send('Xóa bài thi thất bại')
            raise e

    @commands.command(name='getres')
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

    @commands.command(name='getpp')
    async def getpp(self, ctx, member: discord.Member = None):

        member = member if member else ctx.message.author

        discordID = member.id

        conditions = f'discordID=?'
        data = (discordID,)
        signed = _db.select_one_from('bot_member', conditions, data)
        if (not signed):
            embed = discord.Embed()
            embed.title = f"Thí sinh {member.name} chưa đăng ký ingame"
            embed.description = f'Đăng ký ingame để dự thi'
            embed.add_field(name='Cú pháp:', value='sign <ingame>',inline=True)
            embed.colour = discord.Color.green()
            embed.set_footer(text=f"Requested by {ctx.message.author.name}")
            await ctx.send(embed=embed)
            return

        if signed[2]:
            await ctx.send(f'{member.name} bị ban con mẹ nó rồi')
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
            embed.set_footer(text = f'Requested by {ctx.message.author.name}')
            
            if p['SH']:
                msg_sh = ''
                for ele in p['SH']:
                    msg_sh += f'{ele[0]}    {ele[1]}\n'
                embed.add_field(name='Số học', value=msg_sh)
            
            if p['GT']:
                msg_gt = ''
                for ele in p['GT']:
                    msg_gt += f'{ele[0]}    {ele[1]}\n'
                embed.add_field(name='Giải tích', value=msg_gt)

            await ctx.send(embed=embed)
        else:
            await ctx.send(f'Người chơi {member.mention} không dự thi')

def setup(bot):
    bot.add_cog(Member(bot))