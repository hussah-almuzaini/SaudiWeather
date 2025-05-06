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
import base64

st.set_page_config(page_title="Saudi Weather Dashboard", layout="wide", page_icon=r"icon.png")

file_path = r'SaudiCitiesWeather.csv'

def load_image(image_file):
    with open(image_file, "rb") as img:
        return base64.b64encode(img.read()).decode()

image_path = 'download.jpg'
image_base64 = load_image(image_path)

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
    .block-container {{
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 12px;
    }}
    .stCard {{
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }}
    .stMetric {{
        background-color: #B4E1D7;
        padding: 10px;
        border-radius: 10px;
    }}
    .stSubheader {{
        color: #017C74;
        font-weight: bold;
    }}
    .stTitle {{
        color: #3B9E7A;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.image("logo.png", width=150)

df = load_data(file_path)
df = preprocess_data(df)

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
            "color": "#B4E1D7"
        },
        {
            "icon": "🔥",
            "title": "Highest Temperature",
            "value": f"{hottest['city']} — {hottest['avg_temp']:.1f}°C",
            "color": "#F8D7DA"
        },
        {
            "icon": "💧",
            "title": "Lowest Humidity",
            "value": f"{driest['city']} — {driest['avg_humidity']:.1f}%",
            "color": "#C3E6CB"
        },
        {
            "icon": "🌫️",
            "title": "Highest Humidity",
            "value": f"{most_humid['city']} — {most_humid['avg_humidity']:.1f}%",
            "color": "#F8D7DA"
        },
        {
            "icon": "🟢",
            "title": "Lowest Dew Point",
            "value": f"{lowest_dew['city']} — {lowest_dew['max_dew_point']:.1f}°C",
            "color": "#C3E6CB"
        },
        {
            "icon": "🔵",
            "title": "Highest Dew Point",
            "value": f"{highest_dew['city']} — {highest_dew['max_dew_point']:.1f}°C",
            "color": "#B4E1D7"
        },
        {
            "icon": "🍃",
            "title": "Lowest Wind Speed",
            "value": f"{calmest['city']} — {calmest['max_wind_speed']:.1f} km/h",
            "color": "#D1ECF1"
        },
        {
            "icon": "🌪️",
            "title": "Highest Wind Speed",
            "value": f"{windiest['city']} — {windiest['max_wind_speed']:.1f} km/h",
            "color": "#F8D7DA"
        },
    ]

    rows = [cards[i:i+3] for i in range(0, len(cards), 3)]
    for row in rows:
        cols = st.columns(3)
        for idx, card in enumerate(row):
            with cols[idx]:
                st.card(
                    label=card["title"],
                    value=card["value"],
                    icon=card["icon"],
                    style=f"background-color: {card['color']}; padding: 10px; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"
                )

    st.divider()

    folium_static(generate_folium_map(df))

    st.divider()

    fig = plt.figure(figsize=(10, 6))
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", center=0)
    st.pyplot(fig)
