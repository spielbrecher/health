import streamlit as st
from PIL import Image
import requests
import json
import ssl
ssl.create_default_https_context = ssl._create_unverified_context

import pandas as pd
import numpy as np
import osmnx as ox

# команда для запуска сервиса в терминале:
# streamlit run app_sochi.py


# оформление вкладки браузера:

st.set_page_config(page_title="Сочи, Команда", page_icon=':snake:')


# логотипы:

img_hack = Image.open("logo_hack.jpg")
st.sidebar.image(img_hack, width=300)
img_logo = Image.open("logo_case.jpg")
st.sidebar.image(img_logo, width=300)


# левый блок:

st.sidebar.title("""
Сервис предлагает пользователю ввести название города и получить:
- визуализацию и анализ данных
- коэффициенты и параметры
- рекомендации по улучшению качества среды
""")
st.sidebar.write("""
ЮФО, Сочи\n
'Команда'
""")
st.sidebar.caption("""
Андрей Ягелло\n
Маргарита Баталова\n
Николай Кривоногов
""")


# центральный заголовок:

st.markdown(
    "<h2 style='text-align: center;'>Web-приложение для оценки городской инфраструктуры, влияющей на здоровье населения</h1>",
    unsafe_allow_html=True
)

# запрос города:

input_city = st.text_input(
    "Введите название города и страну для анализа и нажмите 'Сгенерировать карту': (пример: Екатеринбург, Россия)"
)


# карта:

if st.button('Сгенерировать карту'):

    inputs = {'input_city': input_city}

    response = requests.post(url='http://127.0.0.1:8000/set_city', data=json.dumps(inputs))
    st.write(response.text)

    #response_education = requests.post(url='http://127.0.0.1:8000/get_education', data=json.dumps(inputs))

    #data_education, data_positive, data_negative = response

    #data_education = pd.read_json(response_education.content)

    #response = requests.get("http://localhost:8000/dataframe")

    response = requests.get("http://localhost:8000/get_education")

    data_education = pd.DataFrame(json.loads(response.json()))
    #json_data = response.json()
    #prepared = json.loads(json_data)
    #data_education = pd.DataFrame.from_dict(prepared['properties'])
    #data_education = pd.read_json(json_data, orient='index')

    #data_education = data_education[['lat', 'lon']]


    st.write(data_education)

    st.subheader("Карта")
    # не знаю, как отрисовать три набора точек на одной карте...
    st.map(data_education,
           latitude='lat',
           longitude='lon',
           # size='col3',
           color='#0000FF')
    st.map(data_positive,
           latitude='lat',
           longitude='lon',
           # # size='col3',
           color='#00FF00')
    st.map(data_negative,
           latitude='lat',
           longitude='lon',
           # # size='col3',
           color='#FF0000')


else:
    pass
    #st.subheader('Что-то пошло не так...')
