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

st.set_page_config(page_title="Saudi Weather Dashboard", layout="wide", page_icon="icon.png")

file_path = 'SaudiCitiesWeather.csv'

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
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.image("logo.png", width=150)

st.divider()

df = load_data(file_path)
df = preprocess_data(df)

st.divider()

latest = df["date"].max()
start = pd.Timestamp(year=latest.year, month=latest.month, day=1)
end = pd.Timestamp(year=latest.year + 1, month=1, day=1) if latest.month == 12 else pd.Timestamp(year=latest.year, month=latest.month + 1, day=1)
df_month = df[(df["date"] >= start) & (df["date"] < end)]
avg = df_month.groupby("city", as_index=False).agg({"avg_temp": "mean", "avg_humidity": "mean", "max_dew_point": "mean", "max_wind_speed": "mean"})

# Extract weather extremes
coldest = avg.loc[avg["avg_temp"].idxmin()]
hottest = avg.loc[avg["avg_temp"].idxmax()]
driest = avg.loc[avg["avg_humidity"].idxmin()]
most_humid = avg.loc[avg["avg_humidity"].idxmax()]
lowest_dew = avg.loc[avg["max_dew_point"].idxmin()]
highest_dew = avg.loc[avg["max_dew_point"].idxmax()]
calmest = avg.loc[avg["max_wind_speed"].idxmin()]
windiest = avg.loc[avg["max_wind_speed"].idxmax()]

# Display Weather Extremes
st.subheader("📅 Latest Monthly Weather Extremes")
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Hottest City", value=hottest["city"], delta=f'{hottest["avg_temp"]:.1f}°C')
with col2:
    st.metric(label="Coldest City", value=coldest["city"], delta=f'{coldest["avg_temp"]:.1f}°C')
with col3:
    st.metric(label="Most Humid City", value=most_humid["city"], delta=f'{most_humid["avg_humidity"]:.1f}%')

st.divider()

# Adding Preferences Section (Example)
st.subheader("🌞 Preferences & Insights")
st.markdown("Here you can add detailed preferences or insights based on weather analysis.")

st.divider()

# Add Map section (Example)
st.subheader("📍 Location-based Weather Map")
# Add your folium map here, for example, using `folium_static(generate_folium_map())`
# folium_static(generate_folium_map())

st.divider()

# Add Heatmap (Example)
st.subheader("🔥 Heatmap of Weather Extremes")
# Add your heatmap plotting here if required

st.divider()
