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
    year_gz = lunar.getYearInGanZhi()
    month_gz = lunar.getMonthInGanZhi()
    day_gz = lunar.getDayInGanZhi()
    time_gz = lunar.getTimeInGanZhi()
    return {"numbers": (dz_map.get(year_gz[1], 0), lunar.getMonth(), lunar.getDay(), dz_map.get(time_gz[1], 0))}

def calculate_hexagram(y, m, d, t):
    shang = (y + m + d) % 8 or 8
    xia = (y + m + d + t) % 8 or 8
    yao = (y + m + d + t) % 6 or 6
    return shang, xia, yao

def get_gua_info():
    return {
        1: ("乾", "金", [1, 1, 1]), 2: ("兑", "金", [0, 1, 1]),
        3: ("离", "火", [1, 0, 1]), 4: ("震", "木", [0, 0, 1]),
        5: ("巽", "木", [1, 1, 0]), 6: ("坎", "水", [0, 1, 0]),
        7: ("艮", "土", [1, 0, 0]), 8: ("坤", "土", [0, 0, 0])
    }

def get_result(ti_wx, yong_wx):
    if ti_wx == yong_wx: return "比和"
    win = [("木", "火"), ("火", "土"), ("土", "金"), ("金", "水"), ("水", "木")]
    lose = [("木", "土"), ("土", "水"), ("水", "火"), ("火", "金"), ("金", "木")]
    if (yong_wx, ti_wx) in win: return "吉"
    if (ti_wx, yong_wx) in win: return "凶"
    if (yong_wx, ti_wx) in lose: return "凶"
    if (ti_wx, yong_wx) in lose: return "吉"
    return "平"

def get_gua_wx(yao_list, info):
    for v in info.values():
        if v[2] == yao_list: return v[1]
    return "土"

def get_font(size=20):
    return ImageFont.load_default()

def draw_integrated_image(gua_list, is_lower_yong, results):
    font = get_font(20)
    img = Image.new('RGB', (650, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    titles = ["本卦", "互卦", "变卦"]
    for idx, gua in enumerate(gua_list):
        x_start = 110 + (idx * 200)
        draw.text((x_start + 10, 30), titles[idx], fill='black')
        draw.text((x_start + 15, 340), results[idx], fill='black')
        
        # 卦象绘制：从下往上 (gua[0] 为初爻)
        for i in range(6):
            y_pos = 300 - (i * 40)
            if gua[i] == 1: # 阳爻
                draw.line([(x_start, y_pos), (x_start + 60, y_pos)], fill='black', width=8)
            else: # 阴爻
                draw.line([(x_start, y_pos), (x_start + 25, y_pos)], fill='black', width=8)
                draw.line([(x_start + 35, y_pos), (x_start + 60, y_pos)], fill='black', width=8)
            
            # 体用标注 (仅本卦)
            if idx == 0:
                label = "体" if (i < 3 and not is_lower_yong) or (i >= 3 and is_lower_yong) else "用"
                if i == 1 or i == 4:
                    draw.text((x_start - 30, y_pos - 10), label, fill='gray')
    return img

# --- Streamlit 界面 ---
st.title("梅花易数排盘系统")
s = st.number_input("上卦数", 0, 8, 1)
x = st.number_input("下卦数", 0, 8, 1)
d = st.number_input("动爻数", 0, 6, 1)

if st.button("开始排盘"):
    info = get_gua_info()
    # 根据用户修正：动爻1,2,3时下卦为用卦；4,5,0时下卦为体卦
    is_lower_yong = d in [1, 2, 3]
    
    ben_raw = info[x][2] + info[s][2]
    hu_raw = [ben_raw[1], ben_raw[2], ben_raw[3]] + [ben_raw[2], ben_raw[3], ben_raw[4]]
    bian_raw = list(ben_raw)
    if 1 <= d <= 6: bian_raw[d - 1] = 1 - bian_raw[d - 1]
    
    ti_wx = info[s if not is_lower_yong else x][1]
    results = []
    for g in [ben_raw, hu_raw, bian_raw]:
        y_wx = get_gua_wx(g[3:6] if is_lower_yong else g[0:3], info)
        results.append(get_result(ti_wx, y_wx))
        
    img = draw_integrated_image([ben_raw, hu_raw, bian_raw], is_lower_yong, results)
    img.save("result.png")
    st.image("result.png")
