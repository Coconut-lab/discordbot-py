import discord
import requests
from datetime import datetime, timedelta
from cmath import log
from distutils.sysconfig import PREFIX
from dotenv import load_dotenv
from discord.ext import commands
import json
import os
import asyncio
load_dotenv()


TOKEN = os.environ['TOKEN']
KEY = os.environ['KEY']

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='$', intents=intents)

sc_info_url = "https://open.neis.go.kr/hub/schoolInfo"
meal_info_url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
sc_time = "https://open.neis.go.kr/hub/hisTimetable"

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    game = discord.Game("정상작동")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    if message.author.bot:
        return

    await client.process_commands(message)

@client.command(name='급식찾기')
async def find_school_info(ctx, *, school_name):
    if school_name.endswith(("고", "초")):
        corrected_school_name = school_name + "등학교"
    elif school_name.endswith("중"):
        corrected_school_name = school_name + "학교"
    else:
        corrected_school_name = school_name

    params = {
        'KEY': KEY,
        'Type': 'json',
        'pIndex': '1',
        'pSize': '100',
        'SCHUL_NM': corrected_school_name
    }

    response = requests.get(sc_info_url, params=params)
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

                response = requests.get(meal_info_url, params=params1)
                json_data = response.json()

                if 'mealServiceDietInfo' in json_data and len(json_data['mealServiceDietInfo']) > 1 and 'row' in json_data['mealServiceDietInfo'][1]:
                    meals = []
                    for item in json_data['mealServiceDietInfo'][1]['row']:
                        ddish_nm = item['DDISH_NM']
                        cleaned_text = ddish_nm.replace('<br/>', '\n')
                        meals.append(cleaned_text)

                    meal_text = '\n'.join(meals)
                    await ctx.send(f'{selected_day_str}, {corrected_school_name}')
                    await ctx.send(f'## {days[index]} 급식:\n{meal_text}')

                else:
                    await ctx.send(selected_day_str)
                    await ctx.send(f'{days[index]}의 급식 정보가 없습니다.')
                
            except asyncio.TimeoutError:
                await ctx.send('시간이 초과되었습니다. 다시 시도해주세요.')

@client.command(name='시간표')
async def find_school_info(ctx, *, args):
    arguments = args.split()

    if len(arguments) != 2:
        await ctx.send('올바른 명령어 형식: $시간표 (학교이름) (학년반)')
        return
    
    school_name = arguments[0]
    grade_class = arguments[1]

    if len(grade_class) == 3 and grade_class.isdigit():
        grade = int(grade_class[0])
        class_number = int(grade_class[1:])
    else:
        await ctx.send("올바른 학년반 형식이 아닙니다. 예시: 205")
        return
    
    if school_name.endswith(("고", "초")):
        corrected_school_name = school_name + "등학교"
    elif school_name.endswith("중"):
        corrected_school_name = school_name + "학교"
    else:
        corrected_school_name = school_name

    await ctx.send(f'{corrected_school_name}, 학년: {grade}, 반: {class_number}')

    params_info = {
        'KEY': KEY,
        'Type': 'json',
        'pIndex': '1',
        'pSize': '100',
        'SCHUL_NM': corrected_school_name
    }

    response_info = requests.get(sc_info_url, params=params_info)
    contents = json.loads(response_info.text)


    school_info_list = contents['schoolInfo'][1]['row'] if 'schoolInfo' in contents else []

    if 'schoolInfo' in contents and len(contents['schoolInfo']) > 1 and 'row' in contents['schoolInfo'][1]:
        for item in contents['schoolInfo'][1]['row']:
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

                def define_values(month):
                    if 3 <= month <= 7:
                        return 1
                    else:
                        return 2
                
                # 현재 월을 얻어옴
                current_month = datetime.now().month

                # 현재 월의 값을 확인
                current_month_value = define_values(current_month)

                time_params = {
                    'KEY' : KEY,
                    'Type' : 'json',
                    'pIndex' : 1,
                    'pSize' : 100,
                    'ATPT_OFCDC_SC_CODE' : atpt_ofcdc_sc_code,
                    'SD_SCHUL_CODE' : sd_schul_code,
                    'AY' : datetime.now().year,
                    'SEM' : current_month_value,
                    'ALL_TI_YMD' : selected_day_str,
                    'GRADE' : grade,
                    'CLASS_NM' : class_number
                }

                response_time = requests.get(sc_time, params=time_params)

                if response_time.status_code == 200:
                    data = json.loads(response_time.text)

                    if 'hisTimetable' in data:
                        for entry in data['hisTimetable']:
                            rows = entry.get('row', [])

                            for row_data in rows:
                                perio = row_data.get('PERIO')
                                itrt_cntnt = row_data.get('ITRT_CNTNT')

                                await ctx.send(f"**{perio}교시** {itrt_cntnt}")
                    else:
                        await ctx.send("응답에 'hisTimetable' 키가 없습니다.")
                else:
                    await ctx.send("에러:", response_time.status_code)
            
            except asyncio.TimeoutError:
                await ctx.send('시간이 초과되었습니다. 다시 시도해주세요.')

client.run(TOKEN)
