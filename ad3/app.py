import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import datetime
import urllib.request
import requests

# функція для завантаження CSV-файлів NOAA та об'єднання в один

def download_files():
    df_all = pd.DataFrame()
    for ids in range(1, 28):
        url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={ids}&year1=1981&year2=2024&type=Mean"
        response = requests.get(url)

        if response.status_code == 200:
            if not os.path.exists('vhi'):
                os.mkdir('vhi')
                print("Папка 'vhi' створена")

            date_now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f'vhi/vhi_id_{ids}_{date_now}.csv'
            with open(file_name, 'wb') as out:
                out.write(response.content)

            print(f"Дані з області ID {ids} завантажено")

            headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
            df = pd.read_csv(file_name, header=1, names=headers, skiprows=1)[:-1]
            df = df[df['VHI'] != -1]
            df['area'] = ids
            df = df.drop(columns=['empty'])
            df_all = pd.concat([df_all, df], ignore_index=True)
        else:
            print(f" Помилка завантаження для області ID {ids}")
            continue

    df_all.to_csv('vhi/df_all.csv', index=False)
    print("\n Файл df_all.csv успішно створено!")

# кешування і читання даних
@st.cache_data
def load_data():
    if not os.path.exists('vhi/df_all.csv'):
        download_files()
    df = pd.read_csv('vhi/df_all.csv')
    df = df[df['VHI'] != -1]
    return df

df = load_data()

# бічна панель з фільтрами
st.sidebar.title("Фільтри даних")

vhi_type = st.sidebar.selectbox("Оберіть індекс", ['VCI', 'TCI', 'VHI'])

region_names = {
    1: 'Cherkasy', 2: 'Chernihiv', 3: 'Chernivtsi', 4: 'Crimea', 5: 'Dnipro',
    6: 'Donets’k', 7: 'Ivano-Frankivsk', 8: 'Kharkiv', 9: 'Kherson', 10: 'Khmel’nyts’kyy',
    11: 'Kiev', 12: 'Kiev City', 13: 'Kirovohrad', 14: 'Luhans’k', 15: 'L’viv',
    16: 'Mykolayiv', 17: 'Odessa', 18: 'Poltava', 19: 'Rivne', 20: 'Sevastopol’',
    21: 'Sumy', 22: 'Ternopil’', 23: 'Transcarpathia', 24: 'Vinnytsya',
    25: 'Volyn', 26: 'Zaporizhzhya', 27: 'Zhytomyr'
}
region_id = st.sidebar.selectbox("Оберіть область", options=list(region_names.keys()), format_func=lambda x: region_names[x])

min_week, max_week = int(df['Week'].min()), int(df['Week'].max())
week_range = st.sidebar.slider("Інтервал тижнів", min_value=min_week, max_value=max_week, value=(1, 52))

min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
year_range = st.sidebar.slider("Інтервал років", min_value=min_year, max_value=max_year, value=(2000, 2024))

sort_asc = st.sidebar.checkbox("Сортувати за зростанням")
sort_desc = st.sidebar.checkbox("Сортувати за спаданням")

if st.sidebar.button("Скинути фільтри"):
    st.experimental_rerun()

# різні вкладки: таблиця, графік, порівняння

filtered_df = df[
    (df['area'] == region_id) &
    (df['Week'].between(*week_range)) &
    (df['Year'].between(*year_range))
]

if sort_asc and sort_desc:
    st.sidebar.warning("Не можна одночасно сортувати за зростанням і спаданням")
elif sort_asc:
    filtered_df = filtered_df.sort_values(by=vhi_type, ascending=True)
elif sort_desc:
    filtered_df = filtered_df.sort_values(by=vhi_type, ascending=False)

tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік", "Порівняння з іншими"])

with tab1:
    st.subheader(f"Відфільтровані дані для області {region_names[region_id]}")
    st.dataframe(filtered_df)

with tab2:
    st.subheader("Графік по фільтрованих даних")
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=filtered_df, x='Week', y=vhi_type, hue='Year', palette='tab10')
    st.pyplot(plt.gcf())

with tab3:
    st.subheader(f"Порівняння {vhi_type} з іншими областями")
    df_compare = df[
        (df['Week'].between(*week_range)) &
        (df['Year'].between(*year_range))
    ]
    plt.figure(figsize=(14, 6))
    sns.lineplot(data=df_compare, x='Week', y=vhi_type, hue=df_compare['area'].map(region_names), legend=False)
    st.pyplot(plt.gcf())
