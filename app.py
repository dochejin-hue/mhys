import streamlit as st
import datetime
from lunar_python import Lunar
from PIL import Image, ImageDraw, ImageFont
import os

# --- 核心逻辑函数 ---
def get_meihua_data():
    now = datetime.datetime.now()
    lunar = Lunar.fromDate(now)
    dz_map = {"子": 1, "丑": 2, "寅": 3, "卯": 4, "辰": 5, "巳": 6, "午": 7, "未": 8, "申": 9, "酉": 10, "戌": 11, "亥": 12}
    
    y_num = dz_map.get(lunar.getYearInGanZhi()[1], 0)
    m_num = lunar.getMonth()
    d_num = lunar.getDay()
    t_num = dz_map.get(lunar.getTimeInGanZhi()[1], 0)
    return y_num, m_num, d_num, t_num

def calculate_hexagram(y, m, d, t):
    shang = (y + m + d) % 8 or 8
    xia = (y + m + d + t) % 8 or 8
    yao = (y + m + d + t) % 6 or 6
    return shang, xia, yao

def get_gua_info():
    return {
        1: ("乾", "金", [1, 1, 1]), 2: ("兑", "金", [1, 1, 0]),
        3: ("离", "火", [1, 0, 1]), 4: ("震", "木", [1, 0, 0]),
        5: ("巽", "木", [0, 1, 1]), 6: ("坎", "水", [0, 1, 0]),
        7: ("艮", "土", [0, 0, 1]), 8: ("坤", "土", [0, 0, 0])
    }

def get_result(ti_wx, yong_wx):
    win = [("木", "火"), ("火", "土"), ("土", "金"), ("金", "水"), ("水", "木")]
    lose = [("木", "土"), ("土", "水"), ("水", "火"), ("火", "金"), ("金", "木")]
    if ti_wx == yong_wx: return "吉"
    if (yong_wx, ti_wx) in win: return "大吉"
    if (ti_wx, yong_wx) in win: return "中凶"
    if (yong_wx, ti_wx) in lose: return "大凶"
    if (ti_wx, yong_wx) in lose: return "中吉"
    return "未知"

def get_gua_wx(yao_list, info):
    for v in info.values():
        if v[2] == yao_list: return v[1]
    return "土"

# --- 兼容性字体加载 ---
def get_font(size=20):
    try:
        return ImageFont.truetype("simhei.ttf", size)
    except:
        return ImageFont.load_default()

def draw_integrated_image(gua_list, results):
    font = get_font(20)
    img = Image.new('RGB', (650, 400), color='white')
    draw = ImageDraw.Draw(img)
    titles = ["本卦", "互卦", "变卦"]
    
    for idx, gua in enumerate(gua_list):
        x_start = 110 + (idx * 200)
        draw.text((x_start + 10, 30), titles[idx], fill='black', font=font)
        for i, yao in enumerate(gua):
            y_pos = 300 - (i * 30)
            if yao:
                draw.line([(x_start, y_pos), (x_start + 60, y_pos)], fill='black', width=8)
            else:
                draw.line([(x_start, y_pos), (x_start + 25, y_pos)], fill='black', width=8)
                draw.line([(x_start + 35, y_pos), (x_start + 60, y_pos)], fill='black', width=8)
        draw.text((x_start, 340), results[idx], fill='black', font=font)
    return img

# --- Streamlit UI ---
st.title("梅花易数排盘系统")

# 选项卡：自动起卦或手动输入
tab1, tab2 = st.tabs(["自动起卦", "手动输入"])

with tab1:
    if st.button("使用当前时间起卦"):
        y, m, d, t = get_meihua_data()
        s, x, yao = calculate_hexagram(y, m, d, t)
        st.write(f"当前时间计算结果: 上卦{s}, 下卦{x}, 动爻{yao}")
    else:
        s, x, yao = None, None, None

with tab2:
    s_in = st.number_input("上卦数", 1, 8, 1)
    x_in = st.number_input("下卦数", 1, 8, 1)
    d_in = st.number_input("动爻数", 1, 6, 1)
    if st.button("手动开始排盘"):
        s, x, yao = s_in, x_in, d_in

if s and x and yao:
    info = get_gua_info()
    is_lower_yong = yao in [1, 2, 3]
    ti_wx = info[s if is_lower_yong else x][1]
    
    ben = info[x][2] + info[s][2]
    hu = [ben[1], ben[2], ben[3]] + [ben[2], ben[3], ben[4]]
    bian = list(ben)
    if 1 <= yao <= 6: bian[yao - 1] = 1 - bian[yao - 1]
    
    results = []
    for g in [ben, hu, bian]:
        y_wx = get_gua_wx(g[0:3] if is_lower_yong else g[3:6], info)
        results.append(get_result(ti_wx, y_wx))
        
    img = draw_integrated_image([ben, hu, bian], results)
    st.image(img)
