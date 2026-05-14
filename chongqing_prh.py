import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="重庆公租房数据新闻", layout="wide")

st.title("🏠 重庆市级公租房交互数据新闻")
st.markdown("**21个市级公租房小区全景分析**")

# 加载数据
try:
    df = pd.read_csv("prh_data.csv")
    st.success(f"成功加载 {len(df)} 条小区数据")
except Exception as e:
    st.error("CSV读取失败！请确保 prh_data.csv 存在且有内容")
    st.stop()

# 筛选
st.sidebar.header("🔍 筛选条件")
districts = st.sidebar.multiselect("区县", options=df['区县'].unique(), default=df['区县'].unique())
difficulties = st.sidebar.multiselect("中签难度", options=df['中签难度'].unique(), default=df['中签难度'].unique())

filtered_df = df[df['区县'].isin(districts) & df['中签难度'].isin(difficulties)]

tab1, tab2 = st.tabs(["🗺️ 交互地图", "📋 数据表格"])

with tab1:
    st.subheader("公租房小区分布地图")
    m = folium.Map(location=[29.55, 106.52], zoom_start=10.5, tiles="CartoDB positron")

    for _, row in filtered_df.iterrows():
        popup_text = f"""
        <b>{row['小区名称']}</b><br>
        区县：{row['区县']}<br>
        难度：{row['中签难度']}
        """
        folium.Marker(
            location=[row['纬度'], row['经度']],
            popup=popup_text,
            tooltip=row['小区名称']
        ).add_to(m)

    st_folium(m, width=800, height=600)

with tab2:
    st.subheader("小区数据表")
    st.dataframe(filtered_df, use_container_width=True)

st.caption("数据来源：重庆市公共租赁房管理局")