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

    .stCard, .stContainer, .stPlot, .stMap {{
        background-color: #6c757d; /* خلفية رمادي غامق */
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
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

    st.subheader(f"📅 Weather Summary for {start.strftime('%B %Y')}")
    st.markdown("---")

    cards = [
        {
            "icon": "🌡️",
            "title": "Lowest Temperature",
            "value": f"{coldest['city']} — {coldest['avg_temp']:.1f}°C",
            "color": "#6c757d"  # خلفية رمادي غامق
        },
        {
            "icon": "🔥",
            "title": "Highest Temperature",
            "value": f"{hottest['city']} — {hottest['avg_temp']:.1f}°C",
            "color": "#6c757d"
        },
        {
            "icon": "💧",
            "title": "Lowest Humidity",
            "value": f"{driest['city']} — {driest['avg_humidity']:.1f}%",
            "color": "#6c757d"
        },
        {
            "icon": "🌫️",
            "title": "Highest Humidity",
            "value": f"{most_humid['city']} — {most_humid['avg_humidity']:.1f}%",
            "color": "#6c757d"
        },
        {
            "icon": "🟢",
            "title": "Lowest Dew Point",
            "value": f"{lowest_dew['city']} — {lowest_dew['max_dew_point']:.1f}°C",
            "color": "#6c757d"
        },
        {
            "icon": "🔵",
            "title": "Highest Dew Point",
            "value": f"{highest_dew['city']} — {highest_dew['max_dew_point']:.1f}°C",
            "color": "#6c757d"
        },
        {
            "icon": "🍃",
            "title": "Lowest Wind Speed",
            "value": f"{calmest['city']} — {calmest['max_wind_speed']:.1f} km/h",
            "color": "#6c757d"
        },
        {
            "icon": "🌪️",
            "title": "Highest Wind Speed",
            "value": f"{windiest['city']} — {windiest['max_wind_speed']:.1f} km/h",
            "color": "#6c757d"
        },
    ]

    # عرض البطاقات في صفوف من 3
    rows = [cards[i:i+3] for i in range(0, len(cards), 3)]

    for row in rows:
        cols = st.columns(3)
        for i, card in enumerate(row):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="background-color:{card['color']}; padding: 1rem; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                        <h3 style="text-align: center;">{card['icon']} {card['title']}</h3>
                        <h4 style="text-align: center;">{card['value']}</h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# إضافة رسم بياني باستخدام Plotly
fig = px.bar(df, x='city', y='avg_temp', title="Average Temperature per City")
st.plotly_chart(fig)

# إضافة خريطة باستخدام Folium
st.subheader("📍 Saudi Cities Weather Map")
generate_folium_map(df)
folium_static(generate_folium_map(df))

