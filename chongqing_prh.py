import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster
import json

st.set_page_config(page_title="重庆公租房数据洞察", layout="wide")
st.title("🎯 重庆市级公租房：供给、需求与城市故事")
st.markdown("**数据新闻交互作品** | 21个市级公租房小区全景分析")

# ==================== 样本数据（可替换为真实CSV） ====================
data = {
    '小区名称': ['半岛逸景乐园', '学府悦园', '民安华福', '城西家园', '缙云新居', 
                '民心佳园', '康庄美地', '江南水岸', '空港佳园', '幸福华庭',
                '美丽阳光家园', '康居西城', '两江名居', '云篆山水', '樵坪人家'],
    '区县': ['大渡口区', '沙坪坝区', '九龙坡区', '九龙坡区', '北碚区',
            '两江新区', '两江新区', '南岸区', '渝北区', '大渡口区',
            '沙坪坝区', '沙坪坝区', '两江新区', '巴南区', '巴南区'],
    '纬度': [29.434, 29.58, 29.48, 29.45, 29.72, 29.63, 29.65, 29.52, 29.72, 29.43,
            29.55, 29.57, 29.68, 29.45, 29.40],  # 近似值，可优化
    '经度': [106.47, 106.45, 106.35, 106.32, 106.42, 106.56, 106.55, 106.57, 106.62, 106.48,
            106.46, 106.40, 106.58, 106.55, 106.60],
    '单间配套_申请': [1250, 2845, 800, 22, 242, 20604, 23781, 4500, 3200, 600, 1200, 1500, 2830, 900, 300],
    '单间配套_房源': [499, 1315, 400, 75, 1594, 356, 539, 800, 100, 300, 500, 600, 1200, 700, 400],
    '一室_申请': [600, 1200, 500, 5, 114, 8000, 9000, 2000, 4500, 300, 600, 700, 1188, 400, 200],
    '一室_房源': [350, 600, 250, 243, 345, 200, 300, 400, 29, 200, 300, 350, 500, 300, 150],
    '中签难度': ['高', '高', '中', '低', '低', '极高', '极高', '高', '极高', '中', '中', '中', '高', '中', '低'],
    '配套小学': ['公民小学校', '学府悦园一/二小', '华福小学校', '西彭一小', '相关小学', 
                '附近小学', '附近小学', '江南水岸小学校', '相关小学', '景翔小学校', 
                '阳光家园小学校', '相关小学', '相关小学', '相关小学', '相关小学']
}

df = pd.DataFrame(data)
df['申请总计'] = df['单间配套_申请'] + df['一室_申请']
df['房源总计'] = df['单间配套_房源'] + df['一室_房源']
df['供需比'] = df['申请总计'] / df['房源总计'].replace(0, 1)

# ==================== 侧边栏过滤器 ====================
st.sidebar.header("🔍 筛选条件")
selected_districts = st.sidebar.multiselect("选择区县", options=df['区县'].unique(), default=df['区县'].unique())
difficulty = st.sidebar.multiselect("中签难度", options=df['中签难度'].unique(), default=df['中签难度'].unique())

filtered_df = df[(df['区县'].isin(selected_districts)) & (df['中签难度'].isin(difficulty))]

# ==================== Tab 布局 ====================
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ 交互地图", "📊 供需分析", "📈 趋势与画像", "🧭 个人模拟器"])

with tab1:
    st.subheader("21个市级公租房小区分布")
    m = folium.Map(location=[29.55, 106.55], zoom_start=10, tiles="CartoDB positron")
    
    for idx, row in filtered_df.iterrows():
        popup_html = f"""
        <b>{row['小区名称']}</b><br>
        区县：{row['区县']}<br>
        单间申请/房源：{row['单间配套_申请']}/{row['单间配套_房源']}<br>
        一室申请/房源：{row['一室_申请']}/{row['一室_房源']}<br>
        难度：{row['中签难度']}<br>
        配套：{row['配套小学']}
        """
        folium.Marker(
            location=[row['纬度'], row['经度']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['小区名称'],
            icon=folium.Icon(color='blue' if row['中签难度']=='低' else 'red' if row['中签难度']=='极高' else 'orange')
        ).add_to(m)
    
    st_folium(m, width=700, height=500)

with tab2:
    st.subheader("供需匹配概览")
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(filtered_df[['小区名称', '区县', '单间配套_申请', '单间配套_房源', 
                                '一室_申请', '一室_房源', '中签难度']], use_container_width=True)
    with col2:
        fig = px.bar(filtered_df.sort_values('供需比', ascending=False), 
                    x='小区名称', y='供需比', color='中签难度',
                    title="各小区供需比（越高越难）")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("整体趋势")
    fig2 = px.scatter(df, x='房源总计', y='申请总计', color='区县', size='供需比',
                     hover_name='小区名称', title="申请量 vs 房源量")
    st.plotly_chart(fig2, use_container_width=True)
    
    st.info("**职住分离提示**：多数公租房位于主城外围，就业集中内环，平均通勤距离约14-17km。")

with tab4:
    st.subheader("🧭 我的公租房通勤模拟器")
    work_lat = st.number_input("工作地点纬度（例如解放碑 ≈29.56）", value=29.56)
    work_lon = st.number_input("工作地点经度（例如解放碑 ≈106.57）", value=106.57)
    
    filtered_df['估算距离_km'] = ((filtered_df['纬度'] - work_lat)**2 + (filtered_df['经度'] - work_lon)**2)**0.5 * 111
    recommendation = filtered_df.nsmallest(5, '估算距离_km')
    
    st.write("**推荐小区（距离较近 + 供需参考）**")
    st.dataframe(recommendation[['小区名称', '区县', '估算距离_km', '中签难度', '供需比']])

# ==================== 结尾 ====================
st.markdown("---")
st.caption("数据来源：重庆市公共租赁房管理局官网、配租公告、本地宝汇总及学术研究（2024-2026）。坐标为近似值，实际制作时建议用高德/百度API精确获取。")
st.caption("适合扩展：接入真实CSV、添加时间序列摇号数据、部署到Streamlit Cloud。")