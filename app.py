import streamlit as st
# 引入你现有的所有逻辑函数，或者使用 from dgdg import ...

st.set_page_config(page_title="梅花易数排盘")
st.title("梅花易数排盘系统")

# 用户输入参数
s_in = st.number_input("上卦数", min_value=0, max_value=8, value=1)
x_in = st.number_input("下卦数", min_value=0, max_value=8, value=1)
d = st.number_input("动爻数", min_value=0, max_value=6, value=1)

if st.button("开始排盘"):
    # 调用你现有的排盘函数
    save_path = "result.png"
    generate_dgdg_result(s_in, x_in, d, save_path=save_path, show=False)
    # 在网页显示图片
    st.image(save_path)
    # 提供下载功能
    with open(save_path, "rb") as file:
        st.download_button("下载排盘结果", file, file_name="梅花排盘.png")