import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium

# 尝试导入 plotly，如果失败则使用备用方案
try:
    import plotly.express as px

    PLOTLY_AVAILABLE = True
except:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly 加载失败，部分图表将无法显示")

st.set_page_config(page_title="重庆公租房数据新闻", layout="wide")

st.title("🏠 重庆市级公租房交互数据新闻")
st.markdown("**21个市级公租房小区全景分析 | 数据新闻交互作品**")

# 加载数据
try:
    df = pd.read_csv("prh_data.csv")
    st.success(f"✅ 成功加载 {len(df)} 条小区数据")
except:
    st.error("CSV 读取失败")
    st.stop()

# 筛选
st.sidebar.header("🔍 筛选条件")
districts = st.sidebar.multiselect("区县", options=sorted(df['区县'].unique()), default=sorted(df['区县'].unique()))
difficulties = st.sidebar.multiselect("中签难度", options=df['中签难度'].unique(), default=df['中签难度'].unique())

filtered_df = df[(df['区县'].isin(districts)) & (df['中签难度'].isin(difficulties))]

tab1, tab2, tab3, tab4 = st.tabs(["🗺️ 交互地图", "📊 历年申请趋势", "📈 供需散点图", "📋 数据表格"])

with tab1:
    st.subheader("21个市级公租房小区分布地图")
    m = folium.Map(location=[29.55, 106.52], zoom_start=10.5, tiles="CartoDB positron")

    color_map = {"极高": "red", "高": "orange", "中": "blue", "低": "green"}

    for _, row in filtered_df.iterrows():
        popup_text = f"""
        <b>{row['小区名称']}</b><br>
        区县：{row['区县']}<br>
        难度：{row['中签难度']}
        """
        folium.Marker(
            location=[row['纬度'], row['经度']],
            popup=folium.Popup(popup_text, max_width=350),
            tooltip=row['小区名称'],
            icon=folium.Icon(color=color_map.get(row['中签难度'], 'blue'), icon="home", prefix="fa")
        ).add_to(m)

    st_folium(m, width=800, height=650)

with tab2:
    st.subheader("历年申请人数趋势")
    if PLOTLY_AVAILABLE and '年份' in df.columns:
        yearly = df.groupby('年份')['申请总人数'].sum().reset_index()
        fig = px.bar(yearly, x='年份', y='申请总人数', title="重庆公租房历年申请趋势")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 历年趋势图需要 Plotly 支持或检查 CSV 中的「年份」列")

with tab3:
    st.subheader("供需散点图")
    if PLOTLY_AVAILABLE:
        df['供需比'] = df.get('申请总计', df['单间配套_申请'] + df['一室_申请']) / \
                       df.get('房源总计', df['单间配套_房源'] + df['一室_房源']).replace(0, 1)
        fig = px.scatter(df, x='房源总计', y='申请总计', color='区县', size='供需比', hover_name='小区名称')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("散点图需要 Plotly 支持")

with tab4:
    st.dataframe(filtered_df, use_container_width=True)

st.caption("数据来源：重庆市公共租赁房管理局")