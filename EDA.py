import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file_path):
    return pd.read_csv(file_path)


# file_path = r'C:\Users\PCD\Desktop\SaudiWeather\SaudiCitiesWeather.csv'
file_path = r'SaudiCitiesWeather.csv'
df = load_data(file_path)

print("First 5 rows:")
print(df.head())

print("\nShape of the dataset:")
print(df.shape)

print("\nInfo:")
print(df.info())

df.isnull().sum()

def preprocess_data(df):
    df = df.rename(columns={
        'time': 'date',
        'temperature_2m_max': 'max_temp',
        'temperature_2m_min': 'min_temp',
        'relative_humidity_2m_max': 'max_humidity',
        'relative_humidity_2m_min': 'min_humidity',
        'wind_speed_10m_max': 'max_wind_speed',
        'dew_point_2m_max': 'max_dew_point',
        'dew_point_2m_min': 'min_dew_point',
    })
        
    df['date'] = pd.to_datetime(df['date'])

    
    df['avg_temp'] = (df['max_temp'] + df['min_temp']) / 2
    df[['date', 'city', 'max_temp', 'min_temp', 'avg_temp']].head()

    df['avg_humidity'] = (df['max_humidity'] + df['min_humidity']) / 2
    df[['date', 'city', 'max_humidity', 'min_humidity', 'avg_humidity']].head()

    
    df['year'] = df['date'].dt.year
    
    df['month'] = df['date'].dt.month
   
    return df
df = preprocess_data(df)

df.info()

df.describe()

city_stats = df.groupby('city')[['avg_temp', 'avg_humidity', 'max_wind_speed']].describe()
print(city_stats)

print(df['city'].value_counts())

city_ranks = df.groupby('city')[['avg_temp', 'avg_humidity', 'max_wind_speed']].mean().sort_values(by='avg_temp', ascending=False)
print(city_ranks)



temp_pivot = df.pivot_table(index='city', columns='month', values='avg_temp', aggfunc='mean')
plt.figure(figsize=(12, 6))
sns.heatmap(temp_pivot, cmap='coolwarm', annot=True, fmt=".1f")
plt.title("Average Temperature by City & Month")
plt.ylabel("City")
plt.xlabel("Month")
plt.show()


def plot_avg_temp_by_month(df):
    
    years = df['year'].unique()
    for year in sorted(years):
        plt.figure(figsize=(12, 6))
        yearly = df[df['year'] == year]
        avg_month = yearly.groupby(['city', 'month'])['avg_temp'].mean().reset_index()
        sns.lineplot(x='month', y='avg_temp', hue='city', data=avg_month, marker='o')
        plt.title(f"Average Temperature by Month - {year}")
        plt.xlabel("Month")
        plt.ylabel("Avg Temp (°C)")
        plt.grid(True)
        plt.show()
            
def plot_avg_humidity_by_month(df):

    years = df['year'].unique()
    for year in sorted(years):
        plt.figure(figsize=(12, 6))
        yearly = df[df['year'] == year]
        avg_month = yearly.groupby(['city', 'month'])['avg_humidity'].mean().reset_index()
        sns.lineplot(x='month', y='avg_humidity', hue='city', data=avg_month, marker='o')
        plt.title(f"Average Humidity by Month - {year}")
        plt.xlabel("Month")
        plt.ylabel("Avg Humidity (%)")
        plt.grid(True)
        plt.show()

def plot_wind_speed_by_month(df):

    years = df['year'].unique()
    for year in sorted(years):
        plt.figure(figsize=(12, 6))
        yearly = df[df['year'] == year]
        avg_month = yearly.groupby(['city', 'month'])['max_wind_speed'].mean().reset_index()
        sns.lineplot(x='month', y='max_wind_speed', hue='city', data=avg_month, marker='o')
        plt.title(f"Max Wind Speed by Month - {year}")
        plt.xlabel("Month")
        plt.ylabel("Max Wind Speed (km/h)")
        plt.grid(True)
        plt.show()

def plot_boxplots_by_month(df):
   
    for month in range(1, 13):
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='city', y='avg_temp', data=df[df['month'] == month])
        plt.title(f"Avg Temp by City - Month {month}")
        plt.xticks(rotation=45)
        plt.show()

        plt.figure(figsize=(12, 6))
        sns.boxplot(x='city', y='avg_humidity', data=df[df['month'] == month])
        plt.title(f"Avg Humidity by City - Month {month}")
        plt.xticks(rotation=45)
        plt.show()

        plt.figure(figsize=(12, 6))
        sns.boxplot(x='city', y='max_wind_speed', data=df[df['month'] == month])
        plt.title(f"Max Wind Speed by City - Month {month}")
        plt.xticks(rotation=45)
        plt.show()


import folium
from streamlit_folium import folium_static
def generate_folium_map(df):
  
    m = folium.Map(location=[24.7136, 46.6753], zoom_start=5)
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=row['city'],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

        
    m.save("saudi_cities_map.html")
    print("Map has been saved as saudi_cities_map.html")
    return m


#plot_avg_temp_by_month(df)
#plot_avg_humidity_by_month(df)
#plot_wind_speed_by_month(df)
#m = generate_folium_map(df)

#plot_boxplots_by_month(df)

