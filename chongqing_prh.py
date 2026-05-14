!pip install plotly -q
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="重庆公租房数据新闻", layout="wide", initial_sidebar_state="expanded")
st.title("🏠 重庆市级公租房：供给·需求·生活")
st.markdown("**数据新闻交互作品** | 21个市级公租房小区全景分析与个人决策工具")


# 读取CSV数据（推荐方式）
@st.cache_data
def load_data():
    return pd.read_csv("prh_data.csv")


df = load_data()

# 侧边栏筛选
st.sidebar.header("🔍 筛选条件")
districts = st.sidebar.multiselect("区县", options=sorted(df['区县'].unique()), default=sorted(df['区县'].unique()))
difficulties = st.sidebar.multiselect("中签难度", options=df['中签难度'].unique(), default=df['中签难度'].unique())

filtered_df = df[(df['区县'].isin(districts)) & (df['中签难度'].isin(difficulties))]

tab1, tab2, tab3, tab4 = st.tabs(["🗺️ 交互地图", "📊 供需分析", "📈 趋势洞察", "🧭 我的通勤模拟器"])

with tab1:
    st.subheader("21个市级公租房小区分布")
    m = folium.Map(location=[29.55, 106.52], zoom_start=10.5, tiles="CartoDB positron")

    color_map = {"低": "green", "中": "blue", "高": "orange", "极高": "red"}

    for _, row in filtered_df.iterrows():
        popup = f"""
        <b>{row['小区名称']}</b><br>
        区县：{row['区县']}<br>
        单间申请/房源：{row['单间配套_申请']}/{row['单间配套_房源']}<br>
        一室申请/房源：{row['一室_申请']}/{row['一室_房源']}<br>
        难度：{row['中签难度']}<br>
        配套小学：{row['配套小学']}
        """
        folium.Marker(
            [row['纬度'], row['经度']],
            popup=folium.Popup(popup, max_width=350),
            tooltip=row['小区名称'],
            icon=folium.Icon(color=color_map.get(row['中签难度'], 'blue'), icon='home')
        ).add_to(m)

    st_folium(m, width=800, height=550)

with tab2:
    st.subheader("供需匹配情况")
    st.dataframe(filtered_df, use_container_width=True)

    fig = px.bar(filtered_df.sort_values('供需比', ascending=False),
                 x='小区名称', y='供需比', color='中签难度',
                 title="各小区供需比（越高越难中签）")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("申请量 vs 房源量")
    fig2 = px.scatter(df, x='房源总计', y='申请总计', color='区县',
                      size='供需比', hover_name='小区名称', title="供需分布散点图")
    st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.subheader("🧭 我的公租房通勤模拟器")
    col1, col2 = st.columns(2)
    with col1:
        work_lat = st.number_input("工作地点纬度（解放碑≈29.56）", value=29.56)
        work_lon = st.number_input("工作地点经度（解放碑≈106.57）", value=106.57)
    with col2:
        filtered_df['距离_km'] = ((filtered_df['纬度'] - work_lat) ** 2 + (
                    filtered_df['经度'] - work_lon) ** 2) ** 0.5 * 111
        rec = filtered_df.nsmallest(5, '距离_km')
        st.dataframe(rec[['小区名称', '区县', '距离_km', '中签难度', '供需比']].round(2))

st.markdown("---")
st.caption("数据来源：重庆市公共租赁房管理局官网及公开配租公告（2024-2026） | 坐标为公开可得近似值")