import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="重庆公租房数据新闻", layout="wide")

st.title("🏠 重庆市级公租房交互数据新闻")
st.markdown("**21个市级公租房小区全景分析 | 数据新闻交互作品**")

# ==================== 加载数据 ====================
try:
    df = pd.read_csv("prh_data.csv")
    st.success(f"✅ 成功加载 {len(df)} 条小区数据")
except Exception as e:
    st.error("❌ CSV读取失败！请确认 prh_data.csv 格式正确")
    st.stop()

# ==================== 侧边栏筛选 ====================
st.sidebar.header("🔍 筛选条件")
districts = st.sidebar.multiselect("区县", options=sorted(df['区县'].unique()), default=sorted(df['区县'].unique()))
difficulties = st.sidebar.multiselect("中签难度", options=df['中签难度'].unique(), default=df['中签难度'].unique())

filtered_df = df[(df['区县'].isin(districts)) & (df['中签难度'].isin(difficulties))]

# ==================== Tabs ====================
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ 交互地图", "📊 历年申请趋势", "📈 供需散点图", "📋 数据表格"])

with tab1:
    st.subheader("21个市级公租房小区分布地图")
    m = folium.Map(location=[29.55, 106.52], zoom_start=10.5, tiles="CartoDB positron")

    color_map = {"极高": "red", "高": "orange", "中": "blue", "低": "green"}

    for _, row in filtered_df.iterrows():
        popup_text = f"""
        <b>{row['小区名称']}</b><br>
        区县：{row['区县']}<br>
        中签难度：{row['中签难度']}<br>
        单间申请/房源：{row.get('单间配套_申请', 'N/A')}/{row.get('单间配套_房源', 'N/A')}<br>
        一室申请/房源：{row.get('一室_申请', 'N/A')}/{row.get('一室_房源', 'N/A')}
        """
        icon_color = color_map.get(row['中签难度'], 'blue')

        folium.Marker(
            location=[row['纬度'], row['经度']],
            popup=folium.Popup(popup_text, max_width=350),
            tooltip=row['小区名称'],
            icon=folium.Icon(color=icon_color, icon="home", prefix="fa")
        ).add_to(m)

    st_folium(m, width=800, height=650)

with tab2:
    st.subheader("历年申请人数趋势（交互柱状图）")

    if '年份' in df.columns and '申请总人数' in df.columns:
        yearly = df.groupby('年份', as_index=False)['申请总人数'].sum()
        fig_bar = px.bar(yearly, x='年份', y='申请总人数',
                         title="重庆公租房历年申请人数趋势",
                         labels={"申请总人数": "申请总人数"},
                         color_discrete_sequence=['#1f77b4'])
        fig_bar.update_layout(xaxis_title="年份", yaxis_title="申请人数")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("💡 提示：要在柱状图中显示历年趋势，请在 CSV 中添加「年份」和「申请总人数」列")

with tab3:
    st.subheader("申请量 vs 房源量 散点图")
    df['供需比'] = df['申请总计'] / df['房源总计'].replace(0, 1)

    fig_scatter = px.scatter(df,
                             x='房源总计',
                             y='申请总计',
                             color='区县',
                             size='供需比',
                             hover_name='小区名称',
                             title="各小区申请量与房源量分布（气泡大小=供需比）",
                             labels={"房源总计": "房源数量", "申请总计": "申请数量"})
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab4:
    st.subheader("详细数据表格")
    st.dataframe(filtered_df, use_container_width=True)

# ==================== 底部信息 ====================
st.markdown("---")
st.caption("数据来源：重庆市公共租赁房管理局官网及公开配租公告 | 坐标为近似值")