import discord
import requests
from datetime import datetime, timedelta
from cmath import log
from distutils.sysconfig import PREFIX
from dotenv import load_dotenv
from discord.ext import commands
import os
import asyncio
load_dotenv()


TOKEN = os.environ['TOKEN']
KEY = os.environ['KEY']



intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='$', intents=intents)


sc_info = "https://open.neis.go.kr/hub/schoolInfo"
meal_info = "https://open.neis.go.kr/hub/mealServiceDietInfo"


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    game = discord.Game("나이스 대국민서비스 일시 중단 및 지능형 나이스 전환에 따라 나이스 급식 시스템 연계가 잠시 중단됨을 알려드립니다.")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    if message.author.bot:
        return

    await client.process_commands(message)

@client.command(name='급식찾기')
async def find_school_info(ctx, *, school_name):
    params = {
        'KEY': KEY,
        'Type': 'json',
        'pIndex': '1',
        'pSize': '100',
        'SCHUL_NM': school_name
    }

    response = requests.get(sc_info, params=params)
    json_data = response.json()

    if 'schoolInfo' in json_data and len(json_data['schoolInfo']) > 1 and 'row' in json_data['schoolInfo'][1]:
        for item in json_data['schoolInfo'][1]['row']:
            atpt_ofcdc_sc_code = item['ATPT_OFCDC_SC_CODE']
            sd_schul_code = item['SD_SCHUL_CODE']

            emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
            days = ['월요일', '화요일', '수요일', '목요일', '금요일']

            message = await ctx.send('날짜를 선택하세요! (1 = 월요일, 2 = 화요일, 3 = 수요일, 4 = 목요일, 5 = 금요일)')
            for emoji in emojis:
                await message.add_reaction(emoji)
            
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in emojis
            
            try:
                reaction, _ = await client.wait_for('reaction_add', timeout=60.0, check=check)

                index = emojis.index(str(reaction.emoji))

                today = datetime.today()
                weekday_offset = (index - today.weekday() + 7) % 7
                selected_day = today + timedelta(days=weekday_offset)
                selected_day_str = selected_day.strftime('%Y%m%d')

                params1 = {
                    'KEY': KEY,
                    'Type': 'json',
                    'pIndex': '1',
                    'pSize': '100',
                    'ATPT_OFCDC_SC_CODE': atpt_ofcdc_sc_code,
                    'SD_SCHUL_CODE': sd_schul_code,
                    'MLSV_YMD': selected_day_str
                }

                response = requests.get(meal_info, params=params1)
                json_data = response.json()

                if 'mealServiceDietInfo' in json_data and len(json_data['mealServiceDietInfo']) > 1 and 'row' in json_data['mealServiceDietInfo'][1]:
                    meals = []
                    for item in json_data['mealServiceDietInfo'][1]['row']:
                        ddish_nm = item['DDISH_NM']
                        cleaned_text = ddish_nm.replace('<br/>', '\n')
                        meals.append(cleaned_text)

                    meal_text = '\n'.join(meals)
                    await ctx.send(selected_day_str)
                    await ctx.send(f'{days[index]}의 급식:\n{meal_text}')

                else:
                    await ctx.send(selected_day_str)
                    await ctx.send(f'{days[index]}의 급식 정보가 없습니다.')
                
            except asyncio.TimeoutError:
                await ctx.send('시간이 초과되었습니다. 다시 시도해주세요.')

client.run(TOKEN)