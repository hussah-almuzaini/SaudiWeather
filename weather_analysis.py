import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from EDA import load_data, preprocess_data
import geopandas as gpd
from datetime import date
import plotly.express as px
from streamlit_folium import folium_static
from EDA import generate_folium_map 

st.set_page_config(page_title="Saudi Weather Dashboard", layout="wide", page_icon=r"icon.png")

# file_path = r'C:\Users\PCD\Desktop\SaudiWeather\SaudiCitiesWeather.csv'
file_path = r'SaudiCitiesWeather.csv'

import base64

def load_image(image_file):
    with open(image_file, "rb") as img:
        return base64.b64encode(img.read()).decode()

# تأكد أن الصورة في نفس المجلد
image_path = 'download.jpg'
image_base64 = load_image(image_path)

# إضافة صورة كخلفية
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url('data:image/jpeg;base64,{image_base64}');
        background-size: cover;  
        background-repeat: no-repeat;  
        background-attachment: fixed;  
        background-position: center;  
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# استخدام st.image مباشرة
st.image("logo.png", width=150)
df = load_data(file_path)

df = preprocess_data(df)

import plotly.express as px 

def get_weather_extremes_latest_month(df):

    latest = df["date"].max()

    start = pd.Timestamp(year=latest.year, month=latest.month, day=1)

    if latest.month == 12:
        end = pd.Timestamp(year=latest.year + 1, month=1, day=1)
    else:
        end = pd.Timestamp(year=latest.year, month=latest.month + 1, day=1)

    df_month = df[(df["date"] >= start) & (df["date"] < end)]

    avg = df_month.groupby("city", as_index=False).agg({
        "avg_temp": "mean",
        "avg_humidity": "mean",
        "max_dew_point": "mean",
        "max_wind_speed": "mean"
    })

    if avg.empty:
        print("❌ No data available for the latest month.")
        return

    coldest = avg.loc[avg["avg_temp"].idxmin()]
    hottest = avg.loc[avg["avg_temp"].idxmax()]

    driest = avg.loc[avg["avg_humidity"].idxmin()]
    most_humid = avg.loc[avg["avg_humidity"].idxmax()]

    lowest_dew = avg.loc[avg["max_dew_point"].idxmin()]
    highest_dew = avg.loc[avg["max_dew_point"].idxmax()]

    calmest = avg.loc[avg["max_wind_speed"].idxmin()]
    windiest = avg.loc[avg["max_wind_speed"].idxmax()]

    st.markdown("""
        <hr style="border: 2px solid #1a237e; margin-top: 20px; margin-bottom: 20px;">
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <h3 style='color:#1a237e; font-weight:700;'>Map</h3>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <h3 style='color:#1a237e; font-weight:700;'>📅 Weather Summary for {start.strftime('%B %Y')}</h3>
    """, unsafe_allow_html=True)

    cards = [
        {
            "icon": "🌡️",
            "title": "Lowest Temperature",
            "value": f"{coldest['city']} — {coldest['avg_temp']:.1f}°C",
            "color": "#006064"
        },
        {
            "icon": "🔥",
            "title": "Highest Temperature",
            "value": f"{hottest['city']} — {hottest['avg_temp']:.1f}°C",
            "color": "#006064"
        },
        {
            "icon": "💧",
            "title": "Lowest Humidity",
            "value": f"{driest['city']} — {driest['avg_humidity']:.1f}%",
            "color": "#006064"
        },
        {
            "icon": "🌫️",
            "title": "Highest Humidity",
            "value": f"{most_humid['city']} — {most_humid['avg_humidity']:.1f}%",
            "color": "#006064"
        },
        {
            "icon": "🟢",
            "title": "Lowest Dew Point",
            "value": f"{lowest_dew['city']} — {lowest_dew['max_dew_point']:.1f}°C",
            "color": "#006064"
        },
        {
            "icon": "🔵",
            "title": "Highest Dew Point",
            "value": f"{highest_dew['city']} — {highest_dew['max_dew_point']:.1f}°C",
            "color": "#006064"
        },
        {
            "icon": "🍃",
            "title": "Lowest Wind Speed",
            "value": f"{calmest['city']} — {calmest['max_wind_speed']:.1f} km/h",
            "color": "#006064"
        },
        {
            "icon": "💨",
            "title": "Highest Wind Speed",
            "value": f"{windiest['city']} — {windiest['max_wind_speed']:.1f} km/h",
            "color": "#006064"
        }
    ]

    rows = [cards[i:i + 3] for i in range(0, len(cards), 3)]
    for row in rows:
        cols = st.columns(len(row))
        for col, card in zip(cols, row):
            with col:
                st.markdown(
                    f"""
                    <div style="background-color:{card['color']};padding:15px;border-radius:10px;
                                box-shadow:0 2px 5px rgba(0,0,0,0.1);text-align:center;margin:10px;">
                        <h4>{card['icon']} {card['title']}</h4>
                        <p style="font-size:16px;">{card['value']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
