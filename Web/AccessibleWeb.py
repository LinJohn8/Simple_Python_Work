import streamlit as st

def stylish_webui():
    # 设置页面标题和图标
    st.set_page_config(page_title="我的 Web UI", page_icon=":sunglasses:")

    # 标题和副标题
    st.title("欢迎来到我的Web UI")
    st.subheader("使用Streamlit打造的Web应用")

    # 交互式按钮
    if st.button("点击我变nb"):
        st.balloons()
        st.success("你变得更nb了!")

    # 添加一个滑动条
    age = st.slider("选择你的年龄", 0, 100, 25)
    st.write(f"你选择的年龄是: {age}")

    # 添加一个选择框
    hobby = st.selectbox("选择你的爱好", ["编程", "游戏", "音乐", "阅读"])
    st.write(f"你的爱好是: {hobby}")

    # 添加一个文本输入框
    name = st.text_input("输入你的名字")
    if name:
        st.write(f"你好, {name}!")

    # 添加一个多选框
    interests = st.multiselect("选择你的兴趣", ["人工智能", "数据科学", "机器学习", "深度学习"])
    if interests:
        st.write("你的兴趣是:")
        for interest in interests:
            st.write(f"- {interest}")

    # 添加一个文本区域
    feedback = st.text_area("留下你的反馈")
    if st.button("提交反馈"):
        st.write("感谢你的反馈!")
        st.write(feedback)

# 运行这个函数
if __name__ == "__main__":
    stylish_webui()
