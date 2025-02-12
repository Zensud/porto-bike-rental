import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
hour_df = pd.read_csv("../data/hour.csv")

# Mapping untuk deskripsi kondisi cuaca
weather_mapping = {
    1: "Cerah hingga Berawan Sebagian",
    2: "Berkabut dan Berawan",
    3: "Salju/Hujan Ringan dengan Petir",
    4: "Hujan Lebat, Es, dan Badai Petir"
}

hour_df['weather_desc'] = hour_df['weathersit'].map(weather_mapping)

# Mapping untuk setiap nama bulan
month_mapping = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

month_order = list(month_mapping.values())

hour_df['month'] = pd.Categorical(hour_df['mnth'].map(month_mapping), categories=month_order, ordered=True)

# Mapping untuk tahun
hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})

# Dashboard and filter thing
st.title("Bike Sharing Dashboard")

st.markdown("### Pertanyaan")
st.markdown("1. Bagaimana pengaruh kondisi cuaca (**weathersit**) terhadap jumlah penyewaan sepeda (**cnt**) pada hari kerja (**workingday**) dibandingkan dengan hari libur (**holiday**) selama tahun 2011 dan 2012?")
st.markdown("2. Apakah terdapat pola musiman (**seasonal pattern**) dalam jumlah penyewaan sepeda (**cnt**) yang dapat diidentifikasi dari data bulanan (**mnth**) selama tahun 2011 dan 2012, dan bagaimana pola tersebut berhubungan dengan suhu (**temp**) dan kelembaban (**hum**)?")

st.sidebar.header("Filters Pertanyaan")
selected_question = st.sidebar.radio("Select Analysis", ["Pertanyaan 1", "Pertanyaan 2"])

# Pertanyaan 1
if selected_question == "Pertanyaan 1":
    st.subheader("Dampak Cuaca pada Penyewaan Sepeda")
    weather_rentals = hour_df.groupby(['weathersit', 'weather_desc', 'workingday', 'holiday'])['cnt'].mean().reset_index()
    workingday_data = weather_rentals[(weather_rentals['workingday'] == 1) & (weather_rentals['holiday'] == 0)]
    holiday_data = weather_rentals[(weather_rentals['holiday'] == 1) & (weather_rentals['workingday'] == 0)]
    holiday_data = holiday_data.set_index('weathersit').reindex(workingday_data['weathersit']).reset_index()
    fig, ax = plt.subplots(figsize=(12, 6))
    bar_width = 0.35
    index = np.arange(len(workingday_data))
    plt.bar(index, workingday_data['cnt'], bar_width, label='Hari Kerja')
    plt.bar(index + bar_width, holiday_data['cnt'], bar_width, label='Hari Libur')
    plt.xlabel('Kondisi Cuaca')
    plt.ylabel('Rata-rata Jumlah Penyewaan Sepeda (cnt)')
    plt.title('Pengaruh Kondisi Cuaca terhadap Penyewaan Sepeda pada Hari Kerja vs Hari Libur')
    plt.xticks(index + bar_width / 2, workingday_data['weather_desc'])
    plt.legend()
    st.pyplot(fig)

    st.title("Conclusion")

    st.markdown("""
    - Penyewaan sepeda lebih tinggi pada kondisi cuaca cerah dibandingkan hujan atau badai.
    - Jumlah penyewaan lebih tinggi pada hari kerja dibandingkan hari libur.
    - Saat cuaca memburuk (hujan lebat, badai), jumlah penyewaan menurun drastis.
    """)

# Pertanyaan 2
else:
    st.subheader("Pola Musiman dan Dampak Suhu/Kelembapan")
    monthly_rentals = hour_df.groupby(['yr', 'month'], observed=False)['cnt'].sum().reset_index()
    monthly_weather = hour_df.groupby(['yr', 'month'], observed=False)[['temp', 'hum']].mean().reset_index()
    monthly_data = pd.merge(monthly_rentals, monthly_weather, on=['yr', 'month'])
    fig, ax = plt.subplots(figsize=(12, 6))
    for year in monthly_data['yr'].unique():
        year_data = monthly_data[monthly_data['yr'] == year]
        plt.plot(year_data['month'], year_data['cnt'], label=f'Tahun {year}')
    
    plt.xlabel('Bulan')
    plt.ylabel('Jumlah Penyewaan Sepeda (cnt)')
    plt.title('Pola musiman dalam Jumlah Penyewaan Sepeda (2011-2012)')
    plt.legend()
    st.pyplot(fig)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=monthly_data, x='temp', y='cnt', hue='month', palette='viridis', ax=ax)
    plt.xlabel('Suhu (temp)')
    plt.ylabel('Jumlah Penyewaan Sepeda (cnt)')
    plt.title('Hubungan antara Suhu dan Jumlah Penyewaan Sepeda')
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=monthly_data, x='hum', y='cnt', hue='month', palette='viridis', ax=ax)
    plt.xlabel('Kelembaban (hum)')
    plt.ylabel('Jumlah Penyewaan Sepeda (cnt)')
    plt.title('Hubungan antara Kelembaban dan Jumlah Penyewaan Sepeda')
    st.pyplot(fig)

    heatmap_data = monthly_data.pivot(index='month', columns='yr', values='cnt')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap='YlGnBu', ax=ax)
    plt.xlabel('Tahun')
    plt.ylabel('Bulan')
    plt.title('Heatmap Jumlah Penyewaan Sepeda per Bulan (2011-2012)')
    st.pyplot(fig)

    st.title("Conclusion")

    st.markdown("""
    - Peningkatan jumlah penyewaan sepeda terlihat pada bulan-bulan musim panas (Juni, Juli, Agustus), sementara jumlah penyewaan menurun pada musim dingin (Desember, Januari, Februari).
    - Dari pola musiman, disimpulkan penyewaan sepeda meningkat ketika suhu lebih hangat (musim panas) dan menurun ketika suhu lebih dingin (musim dingin).
    - Pada kelembaban yang sangat tinggi atau rendah, jumlah penyewaan cenderung lebih sedikit, yang disebabkan oleh kenyamanan berkendara berkurang.
    - Pola musiman menunjukkan jumlah penyewaan tertinggi pada bulan Mei hingga September.
    """)

