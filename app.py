import streamlit as st
import streamlit.components.v1 as components

# 设置页面
st.set_page_config(page_title="解压乒乓大作战", page_icon="🏓", layout="centered")

st.title("🏓 反弹吧！压力退散")
st.write("控制下方的小粉板，把“医考压力”狠狠打回去！")

# 乒乓游戏 HTML/JS 逻辑
pong_html = """
<div style="display: flex; justify-content: center; flex-direction: column; align-items: center;">
    <div style="display: flex; justify-content: space-between; width: 400px; margin-bottom: 10px; font-family: 'Microsoft YaHei', sans-serif; font-size: 1.2em; font-weight: bold;">
        <span style="color: #4361ee;">医考压力怪: <span id="aiScore">0</span></span>
        <span style="color: #ff4d6d;">仙女学霸: <span id="playerScore">0</span></span>
    </div>
    <canvas id="pongCanvas" width="400" height="500" style="border: 4px solid #ffafcc; border-radius: 10px; background: #fff5f8; box-shadow: 0 4px 10px rgba(0,0,0,0.1);"></canvas>
</div>

<script>
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');

// 玩家和AI的木板属性
const player = { x: 150, y: 470, w: 100, h: 12, color: '#ff4d6d', score: 0, speed: 6 };
const ai = { x: 150, y: 18, w: 100, h: 12, color: '#4361ee', score: 0, speed: 3.5 };
const ball = { x: 200, y: 250, r: 8, speed: 5, dx: 3, dy: 4, color: '#e5989b' };

let keys = {};
window.addEventListener('keydown', e => { 
    keys[e.code] = true; 
    if(['ArrowLeft', 'ArrowRight'].includes(e.code)) e.preventDefault(); 
});
window.addEventListener('keyup', e => keys[e.code] = false);

function resetBall(scorer) {
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    ball.speed = 5; // 重置速度
    // 如果玩家得分，球发给AI；如果AI得分，球发给玩家
    ball.dy = scorer === 'player' ? -4 : 4;
    ball.dx = 3 * (Math.random() > 0.5 ? 1 : -1);
}

function update() {
    // 玩家移动 (左右方向键)
    if (keys['ArrowLeft'] && player.x > 0) player.x -= player.speed;
    if (keys['ArrowRight'] && player.x + player.w < canvas.width) player.x += player.speed;

    // AI 移动 (跟随球的 X 坐标，但有速度限制)
    let aiCenter = ai.x + ai.w / 2;
    if (aiCenter < ball.x - 10) {
        ai.x += ai.speed;
    } else if (aiCenter > ball.x + 10) {
        ai.x -= ai.speed;
    }
    
    // 限制 AI 不出界
    if (ai.x < 0) ai.x = 0;
    if (ai.x + ai.w > canvas.width) ai.x = canvas.width - ai.w;

    // 球的移动
    ball.x += ball.dx;
    ball.y += ball.dy;

    // 左右墙壁反弹
    if (ball.x - ball.r < 0 || ball.x + ball.r > canvas.width) {
        ball.dx *= -1;
    }

    // --- 核心逻辑：基于击球位置的反弹角度 ---
    
    // 碰撞检测：玩家木板
    if (ball.y + ball.r > player.y && ball.x > player.x && ball.x < player.x + player.w && ball.dy > 0) {
        // 计算击中点距离木板中心的偏差值 (-1 到 1 之间)
        let hitPoint = ball.x - (player.x + player.w / 2);
        let normalizedHit = hitPoint / (player.w / 2); 
        // 最大反弹角度为 60 度 (Math.PI / 3)
        let angle = normalizedHit * (Math.PI / 3); 

        ball.speed += 0.2; // 每次击球稍微加速，增加刺激感
        ball.dx = ball.speed * Math.sin(angle);
        ball.dy = -ball.speed * Math.cos(angle);
    }

    // 碰撞检测：AI 木板
    if (ball.y - ball.r < ai.y + ai.h && ball.x > ai.x && ball.x < ai.x + ai.w && ball.dy < 0) {
        let hitPoint = ball.x - (ai.x + ai.w / 2);
        let normalizedHit = hitPoint / (ai.w / 2);
        let angle = normalizedHit * (Math.PI / 3);

        ball.speed += 0.2;
        ball.dx = ball.speed * Math.sin(angle);
        ball.dy = ball.speed * Math.cos(angle);
    }

    // 计分系统
    if (ball.y < 0) {
        player.score++;
        document.getElementById('playerScore').innerText = player.score;
        resetBall('player');
    } else if (ball.y > canvas.height) {
        ai.score++;
        document.getElementById('aiScore').innerText = ai.score;
        resetBall('ai');
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 画中间的虚线网
    ctx.setLineDash([10, 10]);
    ctx.beginPath();
    ctx.moveTo(0, canvas.height / 2);
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.strokeStyle = "#ffb5a7";
    ctx.stroke();
    ctx.setLineDash([]);

    // 画玩家木板 (圆角)
    ctx.fillStyle = player.color;
    ctx.beginPath();
    ctx.roundRect(player.x, player.y, player.w, player.h, 5);
    ctx.fill();

    // 画 AI 木板 (圆角)
    ctx.fillStyle = ai.color;
    ctx.beginPath();
    ctx.roundRect(ai.x, ai.y, ai.w, ai.h, 5);
    ctx.fill();

    // 画球
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
    ctx.fillStyle = ball.color;
    ctx.fill();
    ctx.closePath();
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

gameLoop();
</script>
"""

components.html(pong_html, height=550)

st.write("---")
st.caption("🎮 **操作说明**：键盘 **左右方向键** 移动下方的粉色木板。**击球位置越靠近木板边缘，反弹角度越大！** 让它在屏幕里飞舞起来吧！")
