import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style="dark")

# Menyiapkan DataFrame
day_df = pd.read_csv('day.csv')
# mengubah tipe data pada column dteday
day_df["dteday"] = pd.to_datetime(day_df["dteday"])


def create_grouped_df(df):
    cnt_per_month_df = day_df.resample(rule="M", on="dteday").agg(
        {
            "cnt": "sum"
        }
    )
    cnt_per_month_df.index = cnt_per_month_df.index.strftime("%B")
    cnt_per_month_df = cnt_per_month_df.reset_index()

    cnt_per_month_df.rename(
        columns={
            "dteday": "month",
            "cnt": "total_rent"
        }, inplace=True
    )
    # total rental bike per month
    cnt_per_month_df = day_df.resample(rule="M", on="dteday").agg(
        {
            "cnt": "sum"
        }
    )

    # Menambahkan kolom tahun
    cnt_per_month_df['tahun'] = cnt_per_month_df.index.year

    # Mengelompokkan berdasarkan tahun dan bulan
    grouped_df = cnt_per_month_df.groupby(['tahun', cnt_per_month_df.index.strftime("%B")]).agg(
        {
            "cnt": "sum"
        }
    )

    grouped_df.reset_index(inplace=True)

    grouped_df.rename(
        columns={
            "dteday": "month",
            "cnt": "total_rent"
        }, inplace=True
    )

    # Sorting DataFrame by month
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    grouped_df['month'] = pd.Categorical(
        grouped_df['month'], categories=month_order, ordered=True)
    grouped_df = grouped_df.sort_values(['tahun', 'month'])
    return grouped_df


def create_season_df(df):
    season_df = day_df.groupby(by="season").cnt.sum(
    ).sort_values(ascending=False).reset_index()

    season_df.rename(
        columns={
            "cnt": "total_rent"
        }, inplace=True
    )

    # Mapping nilai season ke string yang diinginkan
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}

    # Mengganti nilai season dengan string yang sesuai
    season_df['season'] = season_df['season'].replace(season_mapping)
    return season_df


def create_casual_vs_registered_df(df):
    # casual vs registered transaction
    total_casual = day_df["casual"].sum()
    total_registered = day_df["registered"].sum()

    casual_vs_registered_df = pd.DataFrame({
        "casual": [total_casual],
        "registered": [total_registered]
    })

    return casual_vs_registered_df


def create_holiday_vs_workingday(df):
    # holiday vs workingday
    holiday_vs_workingday = day_df.groupby(["holiday", "workingday"]).agg(
        {
            "cnt": "sum"
        }
    ).reset_index()

    holiday_vs_workingday.rename(
        columns={
            "cnt": "total_rent"
        }, inplace=True
    )
    return holiday_vs_workingday


def create_cnt_corr(df):
    cnt_corr = day_df.loc[:, ["cnt", "temp", "atemp", "hum", "windspeed"]]
    cnt_corr = cnt_corr.corr(method="pearson")

    return cnt_corr


grouped_df = create_grouped_df(day_df)
season_df = create_season_df(day_df)
casual_vs_registered_df = create_casual_vs_registered_df(day_df)
holiday_vs_workingday = create_holiday_vs_workingday(day_df)
cnt_corr = create_cnt_corr(day_df)

# Melengkapi Dashboard dengan berbagai visualisasi data
st.title("Bike Sharing Dashboard:bike:")


st.subheader("Total Rent Bike per Month")
fig, ax = plt.subplots(figsize=(16, 8))
for year in grouped_df['tahun'].unique():
    year_data = grouped_df[grouped_df['tahun'] == year]
    ax.plot(year_data['month'], year_data['total_rent'],
            label=str(year), marker="o")
plt.legend()
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
plt.xticks(rotation=45)
st.pyplot(fig)
with st.expander("See explanation"):
    st.write(
        """ Pada diagram di atas menunjukkan tren penyewaan sepeda per bulan pada tahun 2011 dan 2012. Pada tahun 2011 paling banyak terjadi transaksi pada bulan Juni, sedangkan pada tahun 2012 paling banyak terjadi transaksi pada September. Pada kedua tahun tersebut bulan Januari menjadi yang paling sedikit menyewakan sepeda.
        """
    )


st.subheader("Total Rent per Season")
fig, ax = plt.subplots(figsize=(16, 8))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x="season",
    y="total_rent",
    data=season_df,
    palette=colors
)
plt.ylabel("Total Rent (Million)", fontsize=20)
plt.xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)
st.pyplot(fig)
with st.expander("See explanation"):
    st.write(
        """ Dari diagram ini, kita bisa melihat bahwa musim gugur adalah musim yang paling diminati oleh orang-orang untuk menyewa sepeda, mungkin karena cuaca yang sejuk dan pemandangan yang indah. Sedangkan musim semi adalah musim yang paling kurang diminati, mungkin karena cuaca yang dingin dan basah. Musim panas dan musim dingin memiliki jumlah penyewaan yang hampir sama, mungkin karena orang-orang memiliki preferensi yang berbeda-beda terhadap cuaca yang panas atau dingin.
        """
    )

st.subheader("Casual VS Registered Transaction")
total_casual = day_df["casual"].sum()
total_registered = day_df["registered"].sum()
fig, ax = plt.subplots(figsize=(16, 8))
data = {
    "Casual": total_casual,
    "Registered": total_registered
}
explode = (0.1, 0)
colors = ["#D3D3D3", "#72BCD4"]
# membuat pie chart
fig, ax = plt.subplots()
ax.pie(data.values(), labels=data.keys(),
       autopct='%1.1f%%', explode=explode, colors=colors)
ax.axis('equal')
st.pyplot(fig)
with st.expander("See explanation"):
    st.write(
        """ Pada pie chart di atas, kita bisa melihat bahwa sebagian besar orang yang menyewa sepeda adalah orang yang sudah terdaftar sebagai pelanggan, yang mungkin menunjukkan bahwa mereka adalah pengguna sepeda yang rutin atau loyal. Sedangkan orang yang menyewa sepeda secara kasual adalah orang yang mungkin hanya mencoba sepeda sekali-sekali atau untuk tujuan tertentu.
        """
    )


st.subheader("Workingday vs Holiday vs Weekend")
fig, ax = plt.subplots(figsize=(16, 8))
labels = ['Workingday', 'Holiday', "Weekend"]
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3"]
# Menghitung total sewa sepeda untuk setiap kategori
workingday_rent = holiday_vs_workingday[(holiday_vs_workingday['holiday'] == 0) & (
    holiday_vs_workingday['workingday'] == 1)]['total_rent'].sum()
holiday_rent = holiday_vs_workingday[(holiday_vs_workingday['holiday'] == 1) & (
    holiday_vs_workingday['workingday'] == 0)]['total_rent'].sum()
weekend_rent = holiday_vs_workingday[(holiday_vs_workingday['holiday'] == 0) & (
    holiday_vs_workingday['workingday'] == 0)]['total_rent'].sum()
# data diubah menjadi diagram batang
plt.ylabel("Total Rent (Million)")
plt.bar(labels, [workingday_rent, holiday_rent, weekend_rent], color=colors)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)
st.pyplot(fig)
with st.expander("See explanation"):
    st.write(
        """ Dari diagram ini, kita bisa melihat bahwa jumlah penyewaan sepeda yang dilakukan pada hari kerja jauh lebih banyak daripada pada hari libur atau akhir pekan. Ini mungkin menunjukkan bahwa sebagian besar orang menggunakan sepeda untuk berangkat dan pulang kerja, atau untuk keperluan lain yang berkaitan dengan pekerjaan. Sedangkan pada hari libur atau akhir pekan, orang lebih jarang menggunakan sepeda, mungkin karena mereka lebih memilih untuk beristirahat di rumah atau menggunakan moda transportasi lain.
        """
    )


st.subheader("Correlation Between Total Rent & Temp, Atemp, Hum, and Windspeed")
fig, ax = plt.subplots(figsize=(16, 8))
# Membuat tabel korelasi dari dataframe cnt_corr
corr = cnt_corr.corr(method="pearson")
# Membuat plot heatmap
sns.heatmap(corr, annot=True, cmap="coolwarm")
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)
with st.expander("See explanation"):
    st.write(
        """ Kolom cnt memiliki korelasi positif kuat dengan kolom temp dan atemp, yang yang berarti semakin tinggi nilai suhu, semakin banyak sepeda yang disewa. Kolom cnt memiliki korelasi negatif lemah dengan kolom hum dan windspeed, yang berarti tidak terlalu mempengaruhi penyewaan sepeda.
        """
    )

st.caption('Copyright © Naufal Hadi Darmawan')
