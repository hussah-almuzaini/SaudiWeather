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

    st.subheader(f"📅 Weather Summary for {start.strftime('%B %Y')}")
    st.markdown("---")

    cards = [
        {
            "icon": "🌡️",
            "title": "Lowest Temperature",
            "value": f"{coldest['city']} — {coldest['avg_temp']:.1f}°C",
            "color": "#e0f7fa"
        },
        {
            "icon": "🔥",
            "title": "Highest Temperature",
            "value": f"{hottest['city']} — {hottest['avg_temp']:.1f}°C",
            "color": "#e0f7fa"
        },
        {
            "icon": "💧",
            "title": "Lowest Humidity",
            "value": f"{driest['city']} — {driest['avg_humidity']:.1f}%",
            "color": "#e0f7fa"
        },
        {
            "icon": "🌫️",
            "title": "Highest Humidity",
            "value": f"{most_humid['city']} — {most_humid['avg_humidity']:.1f}%",
            "color": "#e0f7fa"
        },
        {
            "icon": "🟢",
            "title": "Lowest Dew Point",
            "value": f"{lowest_dew['city']} — {lowest_dew['max_dew_point']:.1f}°C",
            "color": "#e0f7fa"
        },
        {
            "icon": "🔵",
            "title": "Highest Dew Point",
            "value": f"{highest_dew['city']} — {highest_dew['max_dew_point']:.1f}°C",
            "color": "#e0f7fa"
        },
        {
            "icon": "🍃",
            "title": "Lowest Wind Speed",
            "value": f"{calmest['city']} — {calmest['max_wind_speed']:.1f} km/h",
            "color": "#e0f7fa"
        },
        {
            "icon": "🌪️",
            "title": "Highest Wind Speed",
            "value": f"{windiest['city']} — {windiest['max_wind_speed']:.1f} km/h",
            "color": "#e0f7fa"
        },
    ]

    # عرض البطاقات في صفوف من 3
    rows = [cards[i:i+3] for i in range(0, len(cards), 3)]
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

get_weather_extremes_latest_month(df)
left_col, right_col = st.columns([1, 3])

with left_col:
    st.markdown("### 🔍 Filters")
    map_type = st.selectbox("Select Map Type 🗺️:", ["Temperature", "Humidity", "Dew Point", "Wind Speed"])
    
    min_date = df["date"].min()
    max_date = df["date"].max()

    start_date = st.date_input("📅 Start date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("📅 End date", value=max_date, min_value=min_date, max_value=max_date)

st.markdown("<hr>", unsafe_allow_html=True)


def temperature_plot(avg_df):
    avg_df["avg_temp"] = avg_df["avg_temp"].round(1)

    fig = px.scatter_mapbox(
        avg_df,
        lat="latitude",             
        lon="longitude",         
        color="avg_temp",         
        size="avg_temp",          
        color_continuous_scale="Hot_r", 
        size_max=20,               
        zoom=4,                    
        mapbox_style="carto-darkmatter",  
        hover_name=None,           
        custom_data=["city", "avg_temp"]  
    )

    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>🌡️ Temp: %{customdata[1]}°C<extra></extra>",
        hoverlabel=dict(font_size=14)  
    )

    # تعيين لون الحواف والإطار
    fig.update_layout(
        height=600,
        width=800,
        margin=dict(l=0, r=0, t=0, b=0),  # إزالة الهوامش
        paper_bgcolor='black',   # لون خلفية الورقة 
        plot_bgcolor='black'     # لون خلفية الرسم
    )

    st.plotly_chart(fig, use_container_width=True)

def humidity_plot(avg_df):
    avg_df["avg_humidity"] = avg_df["avg_humidity"].round(1)

    fig = px.scatter_mapbox(
        avg_df,
        lat="latitude",
        lon="longitude",
        color="avg_humidity",       
        size="avg_humidity",        
        color_continuous_scale="Blues",  
        size_max=20,
        zoom=4,
        mapbox_style="carto-darkmatter",
        hover_name=None,
        custom_data=["city", "avg_humidity"]
    )

    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>💧 Humidity: %{customdata[1]}%<extra></extra>",
        hoverlabel=dict(font_size=14)
    )

        # تعيين لون الحواف والإطار
    fig.update_layout(
        height=600,
        width=800,
        margin=dict(l=0, r=0, t=0, b=0),  # إزالة الهوامش
        paper_bgcolor='black',   # لون خلفية الورقة 
        plot_bgcolor='black'     # لون خلفية الرسم
    )
    st.plotly_chart(fig, use_container_width=True)


def wind_plot(avg_df):
    avg_df["max_wind_speed"] = avg_df["max_wind_speed"].round(1)

    fig = px.scatter_mapbox(
        avg_df,
        lat="latitude",
        lon="longitude",
        color="max_wind_speed",     
        size="max_wind_speed",     
        color_continuous_scale="Viridis",  
        size_max=20,
        zoom=4,
        mapbox_style="carto-darkmatter",
        hover_name=None,
        custom_data=["city", "max_wind_speed"]
    )

    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>🌬️ Wind: %{customdata[1]} km/h<extra></extra>",
        hoverlabel=dict(font_size=14)
    )

        # تعيين لون الحواف والإطار
    fig.update_layout(
        height=600,
        width=800,
        margin=dict(l=0, r=0, t=0, b=0),  # إزالة الهوامش
        paper_bgcolor='black',   # لون خلفية الورقة 
        plot_bgcolor='black'     # لون خلفية الرسم
    )
    st.plotly_chart(fig, use_container_width=True)

def dew_point_plot(avg_df):
    avg_df["max_dew_point"] = avg_df["max_dew_point"].round(1)

    fig = px.scatter_mapbox(
        avg_df,
        lat="latitude",
        lon="longitude",
        color="max_dew_point",         
        size="max_dew_point",          
        color_continuous_scale="Tealrose",  
        size_max=20,
        zoom=4,
        mapbox_style="carto-darkmatter",
        hover_name=None,
        custom_data=["city", "max_dew_point"]
    )

    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>🟢 Dew Point: %{customdata[1]}°C<extra></extra>",
        hoverlabel=dict(font_size=14)
    )

        # تعيين لون الحواف والإطار
    fig.update_layout(
        height=600,
        width=800,
        margin=dict(l=0, r=0, t=0, b=0),  # إزالة الهوامش
        paper_bgcolor='black',   # لون خلفية الورقة 
        plot_bgcolor='black'     # لون خلفية الرسم
    )
    st.plotly_chart(fig, use_container_width=True)


filtered_df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]


avg_df = filtered_df.groupby("city", as_index=False).agg({
    "avg_temp": "mean",              
    "avg_humidity": "mean",          
    "max_wind_speed": "mean",        
    "max_dew_point": "mean",         
    "latitude": "first",             
    "longitude": "first"
})

avg_df['avg_temp'] = avg_df['avg_temp'].round(2)
avg_df['avg_humidity'] = avg_df['avg_humidity'].round(2)
avg_df['max_wind_speed'] = avg_df['max_wind_speed'].round(2)
avg_df['max_dew_point'] = avg_df['max_dew_point'].round(2)

with right_col:
        if start_date > end_date:
            st.error("Start date must be before end date ❌.")
        else:
                filtered_df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]

                avg_df = filtered_df.groupby("city", as_index=False).agg({
                    "avg_temp": "mean",
                    "avg_humidity": "mean",
                    "max_wind_speed": "mean",
                    "max_dew_point": "mean",
                    "latitude": "first",
                    "longitude": "first"
                })

                avg_df['avg_temp'] = avg_df['avg_temp'].round(2)
                avg_df['avg_humidity'] = avg_df['avg_humidity'].round(2)
                avg_df['max_wind_speed'] = avg_df['max_wind_speed'].round(2)
                avg_df['max_dew_point'] = avg_df['max_dew_point'].round(2)


                if map_type == "Temperature":
                    temperature_plot(avg_df)
                elif map_type == "Humidity":
                        humidity_plot(avg_df)
                elif map_type == "Dew Point":
                        dew_point_plot(avg_df)
                elif map_type == "Wind Speed":
                        wind_plot(avg_df)

# get_weather_extremes_latest_month(df)


def heatmap_temperature(df, city):
    city_df = df[df["city"] == city]

    grouped = city_df.groupby(["month", "day"], as_index=False)["avg_temp"].mean()

    fig = px.density_heatmap(
        grouped,
        x="day",  
        y="month",  
        z="avg_temp",  
        color_continuous_scale="YlOrRd",  
        title=f"🌡️ Daily Avg Temperature (°C) — {city}", 
        labels={"avg_temp": "Temp (°C)", "day": "Day", "month": "Month"},
        nbinsx=31
    )
         # تعيين لون الحواف والإطار
    fig.update_layout(
        height=500,
        width=800,
        paper_bgcolor='black',   # لون خلفية الورقة 
        plot_bgcolor='black'     # لون خلفية الرسم
    )
    st.plotly_chart(fig, use_container_width=True)

def heatmap_humidity(df, city):
    city_df = df[df["city"] == city]


    grouped = city_df.groupby(["month", "day"], as_index=False)["avg_humidity"].mean()

    fig = px.density_heatmap(
        grouped,
        x="day",
        y="month",
        z="avg_humidity",  
        color_continuous_scale="Blues",  
        title=f"💧 Daily Avg Humidity (%) — {city}",
        labels={"avg_humidity": "Humidity (%)", "day": "Day", "month": "Month"},
        nbinsx=31
    )

    fig.update_layout(
        height=500,
        width=800,
        paper_bgcolor='black',   # لون خلفية الورقة 
        plot_bgcolor='black'     # لون خلفية الرسم
    )
    st.plotly_chart(fig, use_container_width=True)


def heatmap_dew_point(df, city):
    city_df = df[df["city"] == city]

    
    grouped = city_df.groupby(["month", "day"], as_index=False)["max_dew_point"].mean()

    fig = px.density_heatmap(
        grouped,
        x="day",
        y="month",
        z="max_dew_point", 
        color_continuous_scale="Greens",  
        title=f"🟢 Daily Avg Dew Point (°C) — {city}",
        labels={"max_dew_point": "Dew Point (°C)", "day": "Day", "month": "Month"},
        nbinsx=31
    )
    fig.update_layout(
        height=500,
        width=800,
        paper_bgcolor='black',   # لون خلفية الورقة 
        plot_bgcolor='black'     # لون خلفية الرسم
    )
    st.plotly_chart(fig, use_container_width=True)

def heatmap_wind(df, city):
    city_df = df[df["city"] == city]

    
    grouped = city_df.groupby(["month", "day"], as_index=False)["max_wind_speed"].mean()

    fig = px.density_heatmap(
        grouped,
        x="day",
        y="month",
        z="max_wind_speed",  
        color_continuous_scale="Purples",  
        title=f"🍃 Daily Avg Wind Speed (km/h) — {city}",
        labels={"max_wind_speed": "Wind Speed (km/h)", "day": "Day", "month": "Month"},
        nbinsx=31
    )

    fig.update_layout(
        height=500,
        width=800,
        paper_bgcolor='black',   # لون خلفية الورقة 
        plot_bgcolor='black'     # لون خلفية الرسم
    )
    st.plotly_chart(fig, use_container_width=True)


def show_all_weather_heatmaps(df, city):

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])  
    df["month"] = df["date"].dt.strftime("%b")  
    df["day"] = df["date"].dt.day  

    
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    df["month"] = pd.Categorical(df["month"], categories=month_order, ordered=True)

    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🌡️ Temperature")
        heatmap_temperature(df, city)

        st.markdown("#### 💧 Humidity")
        heatmap_humidity(df, city)

    with col2:

        st.markdown("#### 🟢 Dew Point")
        heatmap_dew_point(df, city)

        st.markdown("#### 🍃 Wind Speed")
        heatmap_wind(df, city)


available_cities = sorted(df["city"].dropna().unique())

# تعريف المتغير selected_city
selected_city = None

# إضافة عنوان
st.markdown("### 🌆 Select the city to view the weather: ")

# عدد الأزرار في الصف الواحد
buttons_per_row = 12

# إنشاء عمود واحد
cols = st.columns(buttons_per_row)

# توزيع الأزرار في صف واحد
for i, city in enumerate(available_cities):
    with cols[i % buttons_per_row]:  # توزيع الأزرار في العمود المناسب
        if st.button(city, key=city):  # استخدام key لضمان عدم حدوث تعارض
            selected_city = city

# التأكد من اختيار مدينة
if selected_city:
    show_all_weather_heatmaps(df, selected_city)


st.header("Select Weather Preferences 🎯")


desired_temp = st.slider("Ideal Temperature (°C)", 0, 50, 25)
desired_humidity = st.slider("Ideal Humidity (%)", 0, 100, 50)
desired_dew = st.slider("Ideal Dew Point (°C)", -10, 40, 10)
desired_wind = st.slider("Ideal Wind Speed (km/h)", 0, 100, 10)

if st.button("Show Top 3 Options 🔎"):

    def recommend_top3_by_preferences(df, desired_temp, desired_humidity, desired_dew, desired_wind):
        df = df.copy()
        df["month"] = df["date"].dt.strftime("%b")

        monthly_avg = df.groupby(["city", "month"], as_index=False).agg({
            "avg_temp": "mean",
            "avg_humidity": "mean",
            "max_dew_point": "mean",
            "max_wind_speed": "mean"
        })

        temp_weight = 4
        humidity_weight = 3
        wind_weight = 2
        dew_weight = 1
        total_weight = temp_weight + humidity_weight + wind_weight + dew_weight

        def get_score(row):
            temp_diff = abs(row["avg_temp"] - desired_temp)
            humidity_diff = abs(row["avg_humidity"] - desired_humidity)
            dew_diff = abs(row["max_dew_point"] - desired_dew)
            wind_diff = abs(row["max_wind_speed"] - desired_wind)

            temp_score = max(0, 100 - temp_diff * 5)
            humidity_score = max(0, 100 - humidity_diff * 2)
            dew_score = max(0, 100 - dew_diff * 5)
            wind_score = max(0, 100 - wind_diff * 5)

            weighted = (
                temp_score * temp_weight +
                humidity_score * humidity_weight +
                wind_score * wind_weight +
                dew_score * dew_weight
            )

            return round(weighted / total_weight, 1)

        monthly_avg["match_percent"] = monthly_avg.apply(get_score, axis=1)
        results = monthly_avg.sort_values(by="match_percent", ascending=False).head(3)

        
        st.subheader("✅ Top 3 matching city/month combinations:\n")
        cols = st.columns(3)
        for i, (_, row) in enumerate(results.iterrows()):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="background-color:#e0f7fa;padding:15px;border-radius:10px;box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                        <h4 style="text-align:center;">📍 {row['city']} — {row['month']}</h4>
                        <p>🔥 <b>Temp:</b> {row['avg_temp']:.1f}°C</p>
                        <p>💧 <b>Humidity:</b> {row['avg_humidity']:.0f}%</p>
                        <p>🟢 <b>Dew Point:</b> {row['max_dew_point']:.1f}°C</p>
                        <p>🍃 <b>Wind Speed:</b> {row['max_wind_speed']:.1f} km/h</p>
                        <hr style="margin:10px 0;">
                        <p style="text-align:center;font-weight:bold;">✅ Match: {row['match_percent']}%</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    
    recommend_top3_by_preferences(df, desired_temp, desired_humidity, desired_dew, desired_wind)
