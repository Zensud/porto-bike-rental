import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load dataset
csv_dir = os.path.dirname(os.path.abspath(__file__))
hour_path = os.path.join(csv_dir, "hour.csv")
hour_df = pd.read_csv(hour_path)

# Konversi tanggal
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

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
    
    # Filter Date, weather
    st.sidebar.header("Filter Data")
    start_date = st.sidebar.date_input("Pilih Tanggal Mulai", hour_df['dteday'].min())
    end_date = st.sidebar.date_input("Pilih Tanggal Akhir", hour_df['dteday'].max())
    selected_weather = st.sidebar.multiselect(
        "Pilih Kondisi Cuaca",
        options=hour_df['weather_desc'].unique(),
        default=hour_df['weather_desc'].unique()
    )
    
    filtered_df = hour_df[
        (hour_df['dteday'] >= pd.Timestamp(start_date)) &
        (hour_df['dteday'] <= pd.Timestamp(end_date)) &
        (hour_df['weather_desc'].isin(selected_weather))
    ]
    
    st.markdown(f"Data ditampilkan dari **{start_date}** hingga **{end_date}** dengan kondisi cuaca: **{', '.join(selected_weather)}**")
    
    # Analisis berdasarkan filter
    weather_rentals = filtered_df.groupby(['weathersit', 'weather_desc', 'workingday', 'holiday'])['cnt'].mean().reset_index()
    workingday_data = weather_rentals[(weather_rentals['workingday'] == 1) & (weather_rentals['holiday'] == 0)]
    holiday_data = weather_rentals[(weather_rentals['holiday'] == 1) & (weather_rentals['workingday'] == 0)]
    holiday_data = holiday_data.set_index('weathersit').reindex(workingday_data['weathersit']).reset_index()


    #Grouped Bar Chart
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    bar_width = 0.35
    index = np.arange(len(workingday_data))
    ax1.bar(index, workingday_data['cnt'], bar_width, label='Hari Kerja', color='steelblue')
    ax1.bar(index + bar_width, holiday_data['cnt'], bar_width, label='Hari Libur', color='darkorange')
    ax1.set_xlabel('Kondisi Cuaca')
    ax1.set_ylabel('Rata-rata Jumlah Penyewaan Sepeda')
    ax1.set_title('Pengaruh Kondisi Cuaca terhadap Penyewaan Sepeda (Hari Kerja vs Hari Libur)')
    ax1.set_xticks(index + bar_width / 2)
    ax1.set_xticklabels(workingday_data['weather_desc'])
    ax1.legend()
    st.pyplot(fig1)

    #Line plot
    st.header("Line Plot")
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.plot(workingday_data['weathersit'], workingday_data['cnt'], marker='o', linestyle='-', label='Hari Kerja', color='steelblue')
    ax2.plot(holiday_data['weathersit'], holiday_data['cnt'], marker='o', linestyle='-', label='Hari Libur', color='darkorange')

    ax2.set_xlabel('Kondisi Cuaca (weathersit)')
    ax2.set_ylabel('Rata-rata Jumlah Penyewaan Sepeda (cnt)')
    ax2.set_title('Pengaruh Kondisi Cuaca terhadap Penyewaan Sepeda\n(Hari Kerja vs Hari Libur) - Line Plot')
    ax2.set_xticks(workingday_data['weathersit'])
    ax2.set_xticklabels(workingday_data['weather_desc'])
    ax2.legend()
    fig2.tight_layout()
    st.pyplot(fig2)

    st.title("Conclusion")

    st.markdown("""
    - Penyewaan sepeda lebih tinggi pada kondisi cuaca cerah dibandingkan hujan atau badai.
    - Jumlah penyewaan lebih tinggi pada hari kerja dibandingkan hari libur.
    - Saat cuaca memburuk (hujan lebat, badai), jumlah penyewaan menurun drastis.
    """)

# Pertanyaan 2
else:
    st.subheader("Pola Musiman dan Dampak Suhu/Kelembapan")

    # Filter Date moment!!!
    st.sidebar.header("Filter Data")
    start_date = st.sidebar.date_input("Pilih Tanggal Mulai", hour_df['dteday'].min())
    end_date = st.sidebar.date_input("Pilih Tanggal Akhir", hour_df['dteday'].max())
    
    filtered_df = hour_df[
        (hour_df['dteday'] >= pd.Timestamp(start_date)) &
        (hour_df['dteday'] <= pd.Timestamp(end_date))
    ]
    
    st.markdown(f"Data ditampilkan dari **{start_date}** hingga **{end_date}**")
    
    # Ganti analysis sama dengan filter
    monthly_rentals = filtered_df.groupby(['yr', 'month'], observed=False)['cnt'].sum().reset_index()
    monthly_weather = filtered_df.groupby(['yr', 'month'], observed=False)[['temp', 'hum']].mean().reset_index()
    monthly_data = pd.merge(monthly_rentals, monthly_weather, on=['yr', 'month'])

    fig, ax = plt.subplots(figsize=(12, 6))
    for year in monthly_data['yr'].unique():
        year_data = monthly_data[monthly_data['yr'] == year]
        plt.plot(year_data['month'], year_data['cnt'], label=f'Tahun {year}')
    
    # Pola musiman dalam Jumlah Penyewaan Sepeda (2011-2012)
    plt.xlabel('Bulan')
    plt.ylabel('Jumlah Penyewaan Sepeda (cnt)')
    plt.title('Pola musiman dalam Jumlah Penyewaan Sepeda (2011-2012)')
    plt.legend()
    st.pyplot(fig)
    
    # Hubungan antara Suhu dan Jumlah Penyewaan Sepeda
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=monthly_data, x='temp', y='cnt', hue='month', palette='viridis', ax=ax)
    plt.xlabel('Suhu (temp)')
    plt.ylabel('Jumlah Penyewaan Sepeda (cnt)')
    plt.title('Hubungan antara Suhu dan Jumlah Penyewaan Sepeda')
    st.pyplot(fig)

    # Hubungan antara Kelembaban dan Jumlah Penyewaan Sepeda
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=monthly_data, x='hum', y='cnt', hue='month', palette='viridis', ax=ax)
    plt.xlabel('Kelembaban (hum)')
    plt.ylabel('Jumlah Penyewaan Sepeda (cnt)')
    plt.title('Hubungan antara Kelembaban dan Jumlah Penyewaan Sepeda')
    st.pyplot(fig)

    # Heatmap Jumlah Penyewaan Sepeda per Bulan (2011-2012)
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
