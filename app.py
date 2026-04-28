import streamlit as st
import streamlit.components.v1 as components

# 设置页面
st.set_page_config(page_title="小仙女守护计划", page_icon="🌹", layout="centered")

# 标题
st.title("🌹 小仙女姨妈期大作战")

# 关卡 1：文字互动
with st.expander("第一关：暖心选择题", expanded=True):
    st.write("做出你的选择，提升身体舒适度...")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌡️ 抱个暖宝宝"):
            st.toast("肚子暖暖的，舒服多了！", icon='❤️')
    with col2:
        if st.button("🍵 喝杯燕麦奶"):
            st.toast("温热的液体治愈了心情~", icon='🥛')

st.write("---")

# 关卡 2：马里奥小游戏
st.subheader("第二关：超级玛丽——击退负能量！")
st.caption("🎮 电脑操作：左右键移动，空格跳跃。吃到右侧的 ☕ 即可通关！")

# 游戏代码
mario_game_js = """
<div style="display: flex; justify-content: center;">
    <canvas id="gameCanvas" width="500" height="250" style="border:3px solid #ffafcc; border-radius:15px; background: #fffafb; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"></canvas>
</div>
<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');

    let player = { x: 30, y: 190, width: 25, height: 25, dy: 0, jumpPower: -10, gravity: 0.5, grounded: false };
    let enemies = [
        { x: 200, y: 215, text: "腰酸", speed: 1.5 },
        { x: 400, y: 215, text: "小烦躁", speed: 2 }
    ];
    let goal = { x: 460, y: 205, text: "☕" };
    let keys = {};

    window.addEventListener('keydown', e => { keys[e.code] = true; if(e.code === 'Space') e.preventDefault(); });
    window.addEventListener('keyup', e => keys[e.code] = false);

    function update() {
        if (keys['ArrowLeft'] && player.x > 0) player.x -= 4;
        if (keys['ArrowRight'] && player.x < 475) player.x += 4;
        if (keys['Space'] && player.grounded) {
            player.dy = player.jumpPower;
            player.grounded = false;
        }

        player.dy += player.gravity;
        player.y += player.dy;

        if (player.y > 190) {
            player.y = 190;
            player.dy = 0;
            player.grounded = true;
        }

        enemies.forEach(en => {
            en.x -= en.speed;
            if (en.x < -50) en.x = 550;
            if (Math.abs(player.x - en.x) < 20 && Math.abs(player.y - en.y) < 20) {
                player.x = 30; // 撞到敌人回起点
            }
        });

        if (player.x > 450) {
            alert("✨ 挑战成功！负能量全被你踩扁啦！快去找男朋友领奖品！✨");
            player.x = 30;
        }

        draw();
        requestAnimationFrame(update);
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // 装饰背景
        ctx.fillStyle = "#ffc107";
        ctx.fillRect(0, 215, 500, 35); // 地板

        // 玩家 (画成一个小粉方块)
        ctx.fillStyle = "#ff85a1";
        ctx.fillRect(player.x, player.y, player.width, player.height);
        ctx.fillStyle = "white";
        ctx.font = "10px Arial";
        ctx.fillText("你", player.x + 8, player.y + 17);

        // 敌人
        ctx.fillStyle = "#555";
        ctx.font = "14px Arial";
        enemies.forEach(en => {
            ctx.fillText("👾 " + en.text, en.x, en.y);
        });

        // 终点
        ctx.font = "24px Arial";
        ctx.fillText(goal.text, goal.x, goal.y);
    }
    update();
</script>
"""

components.html(mario_game_js, height=300)

st.write("---")
st.info("💡 提示：这是一个属于你的避风港，不舒服的时候就来踩扁那些负能量吧！")
