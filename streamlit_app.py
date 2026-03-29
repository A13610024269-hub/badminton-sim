import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. 网页设置
st.set_page_config(page_title="Shuttlecock Physics Sim", layout="wide")
st.title("羽毛球非对称弹道实时模拟 (f = -kv)")

# 2. 侧边栏参数控制
st.sidebar.header("物理参数设置")
v0 = st.sidebar.slider("初速度 v0 (m/s)", min_value=10.0, max_value=120.0, value=65.0, step=1.0)
angle_deg = st.sidebar.slider("仰角 Theta (度)", min_value=10.0, max_value=85.0, value=45.0, step=1.0)
k = st.sidebar.slider("阻力系数 k (对速度敏感度)", min_value=0.0, max_value=0.1, value=0.02, step=0.001)

# 固定参数
m = 0.005  # 质量 (kg)
g = 9.8    # 重力加速度
dt = 0.01  # 时间步长

angle_rad = np.radians(angle_deg)
v0x = v0 * np.cos(angle_rad)
v0y = v0 * np.sin(angle_rad)

# 3. 物理模型计算函数
def calculate_trajectory(vk, vm):
    if vk == 0:  # 真空模型 (高中抛物线)
        t_flight = 2 * v0y / g
        t = np.linspace(0, t_flight, 500)
        x = v0x * t
        y = v0y * t - 0.5 * g * t**2
        return x, y
    else:  # 线性阻力模型 (大学物理)
        # 使用积分得到的解析解
        exp_term = lambda t: np.exp(-(vk / vm) * t)
        
        t_max_x = 5.0 # 预估水平最远时间
        t = np.linspace(0, t_max_x, 1000)
        
        x = (vm * v0x / vk) * (1 - exp_term(t))
        y = (vm / vk) * (v0y + (vm * g / vk)) * (1 - exp_term(t)) - (vm * g / vk) * t
        
        # 只保留 y >= 0 的部分
        valid_indices = y >= 0
        return x[valid_indices], y[valid_indices]

# 4. 计算轨迹
x_real, y_real = calculate_trajectory(k, m)
x_vacuum, y_vacuum = calculate_trajectory(0, m)

# 5. 使用 Plotly 绘图
fig = go.Figure()

# 添加真空轨迹 (虚线)
fig.add_trace(go.Scatter(
    x=x_vacuum, y=y_vacuum,
    mode='lines',
    name='真空 (高中模型, k=0)',
    line=dict(color='gray', dash='dash', width=2)
))

# 添加真实轨迹 (实线)
fig.add_trace(go.Scatter(
    x=x_real, y=y_real,
    mode='lines',
    name=f'真实弹道 (大学模型, k={k:.3f})',
    line=dict(color='firebrick', width=4)
))

# 图表布局优化
fig.update_layout(
    xaxis_title="水平射程 x (m)",
    yaxis_title="竖直高度 y (m)",
    xaxis=dict(range=[0, 70], gridcolor='lightgray'),
    yaxis=dict(range=[0, 35], gridcolor='lightgray'),
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    plot_bgcolor='white',
    height=600,
    margin=dict(l=20, r=20, t=20, b=20)
)

# 6. 在网页展示图表和关键数据
st.plotly_chart(fig, use_container_width=True)

col1, col2, col3 = st.columns(3)
col1.metric("最大射程 (x_max)", f"{x_real[-1]:.2f} m")
col2.metric("最高点高度 (y_max)", f"{np.max(y_real):.2f} m")
col3.metric("收尾速度 (mg/k)", f"{ (m*g/k) if k>0 else '无穷大' :.2f} m/s")
