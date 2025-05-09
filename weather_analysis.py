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


import plotly.graph_objects as go




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

    
    st.markdown(f'<h1 style="color:#41755b;font-size:36px;">Weather Summary for {start.strftime("%B %Y")}</h1>', unsafe_allow_html=True)

    cards = [
        {
            "icon": "🌡️",
            "title": "Lowest Temperature",
            "value": f"{coldest['city']} — {coldest['avg_temp']:.1f}°C",
            "color": "#5d9c7d"
        },
        {
            "icon": "🔥",
            "title": "Highest Temperature",
            "value": f"{hottest['city']} — {hottest['avg_temp']:.1f}°C",
            "color": "#5d9c7d"
        },
        {
            "icon": "💧",
            "title": "Lowest Humidity",
            "value": f"{driest['city']} — {driest['avg_humidity']:.1f}%",
            "color": "#5d9c7d"
        },
        {
            "icon": "🌫️",
            "title": "Highest Humidity",
            "value": f"{most_humid['city']} — {most_humid['avg_humidity']:.1f}%",
            "color": "#5d9c7d"
        },
        {
            "icon": "🟢",
            "title": "Lowest Dew Point",
            "value": f"{lowest_dew['city']} — {lowest_dew['max_dew_point']:.1f}°C",
            "color": "#5d9c7d"
        },
        {
            "icon": "🔵",
            "title": "Highest Dew Point",
            "value": f"{highest_dew['city']} — {highest_dew['max_dew_point']:.1f}°C",
            "color": "#5d9c7d"
        },
        {
            "icon": "🍃",
            "title": "Lowest Wind Speed",
            "value": f"{calmest['city']} — {calmest['max_wind_speed']:.1f} km/h",
            "color": "#5d9c7d"
        },
        {
            "icon": "🌪️",
            "title": "Highest Wind Speed",
            "value": f"{windiest['city']} — {windiest['max_wind_speed']:.1f} km/h",
            "color": "#5d9c7d"
        },
    ]

    # عرض البطاقات في صفوف من 3
    rows = [cards[i:i+2] for i in range(0, len(cards), 2)]
    for row in rows:
        cols = st.columns(len(row))
        for col, card in zip(cols, row):
            with col:
                st.markdown(
                f"""
                <div style="background-color:{card['color']};padding:5px;border-radius:5px;
                            box-shadow:0 2px 5px rgba(0,0,0,0.1);text-align:center;margin:5px;">
                    <h4>{card['icon']} {card['title']}</h4>
                    <p style="font-size:16px;">{card['value']}</p>
                </div>
                """,
                    unsafe_allow_html=True
                )

get_weather_extremes_latest_month(df)
left_col, right_col = st.columns([1, 3])




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
        hovertemplate="<b>%{customdata[0]}</b><br>🌡️ Temp: %{customdata[1]} °C<extra></extra>",

        hoverlabel=dict(font_size=14)  
    )

    # تعيين لون الحواف والإطار
    fig.update_layout(
        mapbox=dict(
        center=dict(lat=24, lon=45),  # حسب مكان بياناتك
        zoom=4
    ),
         coloraxis_colorbar=dict(
            len=0.9,  # النسبة المئوية لطول الليجند (من 0 إلى 1) — زيديها عشان يمط
            thickness=15,
            tickfont=dict(color="#4CAF8B"),  # لون الأرقام في شريط الألوان
            title="Temperature (°C)",
            title_font=dict(size=16, color="#4CAF8B")),
        margin=dict(l=50, r=50, t=50, b=50),
         height=600,
        width=1200,
        paper_bgcolor='rgba(0,0,0,0)',   # لون خلفية الورقة 
        plot_bgcolor='rgba(0,0,0,0)' ,   # لون خلفية الرسم
        
    )

    return fig 


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
        hovertemplate="<b>%{customdata[0]}</b><br>💧 Humidity: %{customdata[1]}% <extra></extra>",
        hoverlabel=dict(font_size=14)
    )

        # تعيين لون الحواف والإطار
    fig.update_layout(
        mapbox=dict(
        center=dict(lat=24, lon=45),  # حسب مكان بياناتك
        zoom=4
    ),
        coloraxis_colorbar=dict(
            len=0.9,  # النسبة المئوية لطول الليجند (من 0 إلى 1) — زيديها عشان يمط
            thickness=15,
            tickfont=dict(color="#4CAF8B"),  # لون الأرقام في شريط الألوان
            title="Humidity (%)",
            title_font=dict(size=16, color="#4CAF8B")),
        margin=dict(l=50, r=50, t=50, b=50),
         height=600,
        width=1200,
        paper_bgcolor='rgba(0,0,0,0)',  # لون خلفية الورقة 
        plot_bgcolor='rgba(0,0,0,0)'    # لون خلفية الرسم
    )
    return fig 


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
        hovertemplate="<b>%{customdata[0]}</b><br>🌬️ Wind: %{customdata[1]}  km/h<extra></extra>",
        hoverlabel=dict(font_size=14)
    )

        # تعيين لون الحواف والإطار
    fig.update_layout(
        mapbox=dict(
        center=dict(lat=24, lon=45),  # حسب مكان بياناتك
        zoom=4
    ),
        coloraxis_colorbar=dict(
            len=0.9,  # النسبة المئوية لطول الليجند (من 0 إلى 1) — زيديها عشان يمط
            thickness=15,
            tickfont=dict(color="#4CAF8B"),  # لون الأرقام في شريط الألوان
            title="Wind Speed (km/h)",
            title_font=dict(size=16, color="#4CAF8B")
),
        margin=dict(l=50, r=50, t=50, b=50),
        height=600,
        width=1200,
        paper_bgcolor='rgba(0,0,0,0)',   # لون خلفية الورقة 
        plot_bgcolor='rgba(0,0,0,0)'     # لون خلفية الرسم
    )
    
    return fig 

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
        hovertemplate="<b>%{customdata[0]}</b><br>🟢 Dew Point:%{customdata[1]} °C<extra></extra>",
        hoverlabel=dict(font_size=14)
    )

        # تعيين لون الحواف والإطار
    fig.update_layout(
        mapbox=dict(
        center=dict(lat=24, lon=45),  # حسب مكان بياناتك
        zoom=4
    ),
       coloraxis_colorbar=dict(
           len=0.9,  # النسبة المئوية لطول الليجند (من 0 إلى 1) — زيديها عشان يمط
            thickness=15,
    tickfont=dict(color="#4CAF8B"),
    title="Dew Point (°C)",
    title_font=dict(size=16, color="#4CAF8B")
),

        margin=dict(l=50, r=50, t=50, b=50),
        height=600,
        width=1200,
        paper_bgcolor='rgba(0,0,0,0)',   # لون خلفية الورقة 
        plot_bgcolor='rgba(0,0,0,0)'    # لون خلفية الرسم
    )
    return fig 


st.markdown("<hr style='border: 1px solid #d3d3d3; margin: 20px 0;'>", unsafe_allow_html=True)

st.markdown('##')
st.markdown(f'<h1 style="color:#41755b;font-size:30px;">Weather Map Overview : </h1>', unsafe_allow_html=True)


# --------- الفلاتر في صف واحد ---------
filter_cols = st.columns(3)




with filter_cols[0]:
    st.markdown("<h5 style='color:#5d9c7d; margin: 0; padding: 0;'>🗺️ Select Map Type</h5>", unsafe_allow_html=True)
    map_type = st.selectbox("", ["Temperature", "Humidity", "Dew Point", "Wind Speed"])
min_date = df["date"].min()
max_date = df["date"].max()

with filter_cols[1]:
    st.markdown("<h5 style='color:#5d9c7d; margin: 0; padding: 0;'>📅 Start Date</h5>", unsafe_allow_html=True)
    start_date = st.date_input("", value=min_date, min_value=min_date, max_value=max_date)

with filter_cols[2]:
    st.markdown("<h5 style='color:#5d9c7d; margin: 0; padding: 0;'>📅 End Date</h5>", unsafe_allow_html=True)
    end_date = st.date_input("", value=max_date, min_value=min_date, max_value=max_date)


# --------- معالجة البيانات وعرض الخريطة ---------
if start_date > end_date:
    st.error("📛 Start date must be before end date.")
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

        # إضافة الإطار حول التشارت بالكامل (الـ chart مع الـ legend)
    import streamlit.components.v1 as components

    # توليد الـ fig من الميثود المختارة
    if map_type == "Temperature":
        fig = temperature_plot(avg_df)
    elif map_type == "Humidity":
        fig = humidity_plot(avg_df)
    elif map_type == "Dew Point":
        fig = dew_point_plot(avg_df)
    elif map_type == "Wind Speed":
        fig = wind_plot(avg_df)
    
    # حوّلي الـ fig إلى HTML
    html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    # عرض التشارت داخل div له إطار
    components.html(f"""
    <div style="
        border: 3px solid #4CAF8B;
        border-radius: 12px;
        padding: 10px;
        margin: 10px 0;
        background-color: transparent;
        width: 100%;
        box-sizing: border-box;
        overflow: auto;
        ">
        {html}
    </div>
    """, height=700)






def heatmap_temperature(df, city):
    city_df = df[df["city"] == city]

    grouped = city_df.groupby(["month", "day"], as_index=False)["avg_temp"].mean()

    fig = px.density_heatmap(
        grouped,
        x="day",  
        y="month",  
        z="avg_temp", 
        title=f"🌡️ Daily Avg Temperature (°C) — {city}",
        color_continuous_scale="YlOrRd",  
        
        labels={"avg_temp": "Temp (°C)", "day": "Day", "month": "Month"},
        nbinsx=31
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',  
        title_font=dict(color='#006400', size=20),  
        font=dict(color='#006400'),  
        xaxis=dict(title_font=dict(color='#006400'),   tickfont=dict(color='#006400') ),
        yaxis=dict(title_font=dict(color='#006400'),  tickfont=dict(color='#006400')  ),
        legend=dict(
            title_font=dict(color='#006400'), font=dict(color='#006400') ),
        coloraxis_colorbar=dict(
            len=0.9, 
            thickness=15,
            tickfont=dict(color="#4CAF8B"),  
            title="temperature (C)",
            title_font=dict(size=16, color="#4CAF8B"))
    
    )
 
    return fig 

        
        


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
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',  
        title_font=dict(color='#006400', size=20),  
        font=dict(color='#006400'),  
        xaxis=dict(title_font=dict(color='#006400'),   tickfont=dict(color='#006400') ),
        yaxis=dict(title_font=dict(color='#006400'),  tickfont=dict(color='#006400')  ),
        legend=dict(
            title_font=dict(color='#006400'), font=dict(color='#006400') ),
        coloraxis_colorbar=dict(
            len=0.9, 
            thickness=15,
            tickfont=dict(color="#4CAF8B"),  
            title="Humidity (%)",
            title_font=dict(size=16, color="#4CAF8B"))
    
    )
     

    return fig 
    


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
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',  
        title_font=dict(color='#006400', size=20),  
        font=dict(color='#006400'),  
        xaxis=dict(title_font=dict(color='#006400'),   tickfont=dict(color='#006400') ),
        yaxis=dict(title_font=dict(color='#006400'),  tickfont=dict(color='#006400')  ),
        legend=dict(
            title_font=dict(color='#006400'), font=dict(color='#006400') ),
        coloraxis_colorbar=dict(
            len=0.9, 
            thickness=15,
            tickfont=dict(color="#4CAF8B"),  
            title="dew  (%)",
            title_font=dict(size=16, color="#4CAF8B"))
    
    )
    
    return fig 



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
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',  
        title_font=dict(color='#006400', size=20),  
        font=dict(color='#006400'),  
        xaxis=dict(title_font=dict(color='#006400'),   tickfont=dict(color='#006400') ),
        yaxis=dict(title_font=dict(color='#006400'),  tickfont=dict(color='#006400')  ),
        legend=dict(
            title_font=dict(color='#006400'), font=dict(color='#006400') ),
        coloraxis_colorbar=dict(
            len=0.9, 
            thickness=15,
            tickfont=dict(color="#4CAF8B"),  
            title="wind (k/h)",
            title_font=dict(size=16, color="#4CAF8B"))
    
    )
    return fig 
    


available_cities = sorted(df["city"].dropna().unique())
if "selected_city" not in st.session_state:
    st.session_state.selected_city = None


city = None
# إضافة عنوان
st.markdown("<hr style='border: 1px solid #d3d3d3; margin: 20px 0;'>", unsafe_allow_html=True)

st.markdown(f'<h1 style="color:#41755b;font-size:30px;">🌆 Select the city to view the weather: </h1>', unsafe_allow_html=True)


buttons_per_row = 6
cols = st.columns(buttons_per_row)
st.markdown("""
    <style>
        .stButton>button {
            background-color: #d3f9d8;  /* Light green background */
            border: 2px solid #333;  /* Dark border */
            color: #333;  /* Dark text */
            border-radius: 5px;
            font-size: 16px;
            padding: 10px;
            width: 100%;  /* Make buttons fill the column space */
            text-align: center;  /* Center-align the text inside the button */
        }
        .stButton>button:hover {
            background-color: #b8f7c5;  /* Slightly darker green on hover */
        }
        .stButton>button:active {
            background-color: #ffcccc;  /* Light red background when clicked */
            color: #721c24;;  /* Dark red text */
        }
    </style>
""", unsafe_allow_html=True)

for i, city in enumerate(available_cities):  
    with cols[i % buttons_per_row]: 
        if st.button(city, key=city):  
            st.session_state.selected_city = city
            st.write(f"You selected: {city}")




if  st.session_state.selected_city:
    city = st.session_state.selected_city
else :
     city =  'Riyadh'
    
df = df.copy()
df["date"] = pd.to_datetime(df["date"])  
df["month"] = df["date"].dt.strftime("%b")  
df["day"] = df["date"].dt.day  

month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun","Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
df["month"] = pd.Categorical(df["month"], categories=month_order, ordered=True)
    
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
        }
        iframe {
            display: block;
            margin: 0px !important;
            padding: 0px !important;
        }
        .element-container {
            padding: 0px !important;
            margin: 0px !important;
        }
        .stColumns {
            gap: 0rem !important;
        }
    </style>
""", unsafe_allow_html=True)


    
def display_chart_with_frame(fig, height=550):
    html = fig.to_html(include_plotlyjs="cdn")
    components.html(f"""
        <div style="
            border: 2px solid #4CAF8B;
            border-radius: 10px;
            padding: 5px;
            margin: 0px;
            background-color: transparent;
            width: 100%;
            box-sizing: border-box;
            overflow: hidden;">
            {html}
        </div>
    """, height=height)




# الصف الأول: الحرارة والرطوبة
col1, col2 = st.columns(2 , gap="small")

with col1:
    fig_temp = heatmap_temperature(df, city)
    display_chart_with_frame(fig_temp)

with col2:
    fig_humidity = heatmap_humidity(df, city)
    display_chart_with_frame(fig_humidity)

# الصف الثاني: نقطة الندى والرياح
col3, col4 = st.columns(2 , gap="small")

with col3:
    fig_dew = heatmap_dew_point(df, city)
    display_chart_with_frame(fig_dew)

with col4:
    fig_wind = heatmap_wind(df, city)
    display_chart_with_frame(fig_wind)



st.markdown("<hr style='border: 1px solid #d3d3d3; margin: 20px 0;'>", unsafe_allow_html=True)

st.markdown('##')
st.markdown(f'<h1 style="color:#41755b;font-size:30px;">Select Weather Preferences 🎯</h1>', unsafe_allow_html=True)



import streamlit as st

# ✅ CSS متكامل لتعديل لون الخط والأرقام
st.markdown("""
    <style>
    div[data-baseweb="slider"] > div:first-child {
        color: black !important;
    }

    div[data-baseweb="slider"] > div > div:nth-child(3) {
        background: #003366 !important;
    }

    div[data-baseweb="slider"] > div > div:nth-child(2) {
        background: #ccc !important;
    }

    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #003366 !important;
        border: 2px solid #003366 !important;
    }
    </style>
""", unsafe_allow_html=True)


col1, col2, _, _ = st.columns([1, 1, 0.4, 0.4])

with col1:
    st.markdown('<p style="font-size:16px; color:#2a4d69;"><b>🌡️ Ideal Temperature (°C)</b></p>', unsafe_allow_html=True)
    desired_temp = st.slider("temp", 0, 50, 25, label_visibility="collapsed")

with col2:
    st.markdown('<p style="font-size:16px; color:#2a4d69;"><b>💧 Ideal Humidity (%)</b></p>', unsafe_allow_html=True)
    desired_humidity = st.slider("humidity", 0, 100, 50, label_visibility="collapsed")

col3, col4, _, _ = st.columns([1, 1, 0.4, 0.4])

with col3:
    st.markdown('<p style="font-size:16px; color:#2a4d69;"><b>🟢 Ideal Dew Point (°C)</b></p>', unsafe_allow_html=True)
    desired_dew = st.slider("dew", -10, 40, 10, label_visibility="collapsed")

with col4:
    st.markdown('<p style="font-size:16px; color:#2a4d69;"><b>🍃 Ideal Wind Speed (km/h)</b></p>', unsafe_allow_html=True)
    desired_wind = st.slider("wind", 0, 100, 10, label_visibility="collapsed")




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

        st.markdown(f'<h1 style="color:#41755b;font-size:30px;">✅ Top 3 matching city/month combinations</h1>', unsafe_allow_html=True)

        cols = st.columns(3)
        for i, (_, row) in enumerate(results.iterrows()):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="background-color:#5d9c7d;padding:15px;border-radius:10px;box-shadow:0 2px 5px rgba(0,0,0,0.1);">
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
