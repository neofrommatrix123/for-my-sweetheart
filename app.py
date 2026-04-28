import streamlit as st

st.set_page_config(page_title="小仙女守护计划", page_icon="🌹")

st.markdown("""
<style>
.main { background-color: #fffafb; }
.stRadio > label { font-weight: bold; color: #e91e63; }
h1 { color: #e91e63; text-align: center; }
div[data-testid="stMetricValue"] { color: #e91e63; }
</style>
""", unsafe_allow_html=True)

st.title("🌹 小仙女姨妈期守护计划")
st.write("""
<div style='text-align: center; color: #666; font-size: 1.1em;'>
    系统检测到：当前身体处于“大姨妈”状态。<br>
    你的任务是：做出选择，让身体舒适度回升！
</div>
""", unsafe_allow_html=True)
st.write("---")

st.subheader("📍 场景 1：现在肚子有点闷闷的，你打算？")
c1 = st.radio("请做出选择：", ["请选择...", "A. 喝一杯冰美式提提神", "B. 抱个暖宝宝，喝杯暖暖的饮品"], key="q1")

st.subheader("📍 场景 2：心情突然有点莫名的小烦躁，怎么办？")
c2 = st.radio("请做出选择：", ["请选择...", "A. 找男朋友撒个娇", "B. 憋在心里，自己刷手机"], key="q2")

st.subheader("📍 场景 3：晚餐时间到了，你想吃什么？")
c3 = st.radio("请做出选择：", ["请选择...", "A. 麻辣火锅，一定要爆辣！", "B. 清淡温和的热汤面"], key="q3")

st.write("---")

if st.button("✨ 生成舒适度报告 ✨"):
    if "请选择..." in [c1, c2, c3]:
        st.error("请先完成所有选择哦！")
    else:
        score = 50
        if "B" in c1: score += 20
        elif "A" in c1: score -= 20
        if "A" in c2: score += 30
        elif "B" in c2: score -= 10
        if "B" in c3: score += 20
        elif "A" in c3: score -= 15
        
        st.metric(label="最终身体舒适度", value=f"{score}%")
        
        if score >= 80:
            st.balloons()
            st.success("🏆 恭喜获得【头等宠爱】奖牌！")
            st.write("**男朋友留言：** 辛苦啦！我知道最近备考压力大，今晚剩下的家务和按摩都交给我，你只管负责休息就好 ❤️")
        else:
            st.warning("⚠️ 警告：检测到身体舒适度较低！")
            st.write("**男朋友留言：** 乖，快放下手机，让我给你揉揉肚子，或者抱抱你。")
