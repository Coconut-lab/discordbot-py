import discord
import requests
from datetime import datetime, timedelta
from cmath import log
from distutils.sysconfig import PREFIX
from dotenv import load_dotenv
import os
import re
load_dotenv()


TOKEN = os.environ['TOKEN']
service_key = os.environ['service_key']



intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


sc_info = "https://open.neis.go.kr/hub/schoolInfo"


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    game = discord.Game("나이스 대국민서비스 일시 중단 및 지능형 나이스 전환에 따라 나이스 급식 시스템 연계가 잠시 중단됨을 알려드립니다.")
    await client.change_presence(status=discord.Status.online, activity=game)



@client.event
async def on_message(message):
    if message.content.startswith("$급식찾기"):
        school_name_to = message.content[len("$급식찾기 "):].strip()
        print(f'{message.author} 님이 검색한 학교 이름: {school_name_to}')

        params = {
            'KEY': service_key,
            'Type': 'json',
            'pIndex': '1',
            'pSize': '100',
            'SCHUL_NM': school_name_to
        }

        response = requests.get(sc_info, params=params)
        json_data = response.json()

        # ATPT_OFCDC_SC_CODE와 SD_SCHUL_CODE 추출 및 출력
        for item in json_data['schoolInfo'][1]['row']:
            # 시도교육청 코드
            atpt_ofcdc_sc_code = item['ATPT_OFCDC_SC_CODE']
            # 학교 코드
            sd_schul_code = item['SD_SCHUL_CODE']

        await message.channel.send("급식 찾는중...")
        today = datetime.today()
        today_date = today.strftime('%Y%m%d')

        meal = "https://open.neis.go.kr/hub/mealServiceDietInfo"

        params1 = {
            'KEY': service_key,
            'Type': 'json',
            'pIndex': '1',
            'pSize': '100',
            'ATPT_OFCDC_SC_CODE': atpt_ofcdc_sc_code,
            'SD_SCHUL_CODE': sd_schul_code,
            'MLSV_YMD': today_date
        }

        response1 = requests.get(meal, params=params1)
        json_data1 = response1.json()

        if 'mealServiceDietInfo' in json_data1 and len(json_data1['mealServiceDietInfo']) > 1 and 'row' in json_data1['mealServiceDietInfo'][1]:
            for item in json_data1['mealServiceDietInfo'][1]['row']:
                ddish_nm = item['DDISH_NM']

                input_text = ddish_nm

                cleaned_text = re.sub(r'<br/>', '', input_text)
                cleaned_text = re.sub(r'\s*\(([^)]+)\)\s*', r' (\1) ', cleaned_text)

                data = cleaned_text

                formatted_data = data.replace(") ", ")\n").replace(")  (", ")\n(")

                await message.channel.send(formatted_data)
            
        else:
            await message.channel.send(today_date)
            await message.channel.send("급식 정보가 없습니다.")


@client.event
async def on_message(message):
    if message.content.startswith("$내일급식찾기"):
        school_name = message.content[len("$내일급식찾기 "):].strip()
        print(f'{message.author} 님이 검색한 내일 급식 학교 이름: {school_name}')

        params_info = {
            'KEY': service_key,
            'Type': 'json',
            'pIndex': '1',
            'pSize': '100',
            'SCHUL_NM': school_name
        }

        response_to = requests.get(sc_info, params=params_info)
        json_data_to = response_to.json()

        # ATPT_OFCDC_SC_CODE와 SD_SCHUL_CODE 추출 및 출력
        for item in json_data_to['schoolInfo'][1]['row']:
            # 시도교육청 코드
            atpt_ofcdc_sc_code = item['ATPT_OFCDC_SC_CODE']
            # 학교 코드
            sd_schul_code = item['SD_SCHUL_CODE']

        await message.channel.send("급식 찾는중...")
        today = datetime.today()
        tomorrow = today + timedelta(days=1)
        tomorrow_date = tomorrow.strftime('%Y%m%d')

        meal = "https://open.neis.go.kr/hub/mealServiceDietInfo"

        params_meal = {
            'KEY': service_key,
            'Type': 'json',
            'pIndex': '1',
            'pSize': '100',
            'ATPT_OFCDC_SC_CODE': atpt_ofcdc_sc_code,
            'SD_SCHUL_CODE': sd_schul_code,
            'MLSV_YMD': tomorrow_date
        }

        response_meal = requests.get(meal, params=params_meal)
        json_data_meal = response_meal.json()

        if 'mealServiceDietInfo' in json_data_meal:
            for item in json_data_meal['mealServiceDietInfo'][1]['row']:
                ddish_nm = item['DDISH_NM']

                input_text = ddish_nm

                cleaned_text = re.sub(r'<br/>', '', input_text)
                cleaned_text = re.sub(r'\s*\(([^)]+)\)\s*', r' (\1) ', cleaned_text)

                data = cleaned_text

                formatted_data = data.replace(") ", ")\n").replace(")  (", ")\n(")


                await message.channel.send(tomorrow_date)
                await message.channel.send(formatted_data)
            
        else:
            await message.channel.send("급식 정보가 없습니다.")


client.run(TOKEN)
