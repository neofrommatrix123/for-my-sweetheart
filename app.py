import streamlit as st
import streamlit.components.v1 as components

# 设置页面
st.set_page_config(page_title="大姨妈大作战 2.0", page_icon="🏓", layout="centered")

st.title("🏓 击退大姨妈：仙女学霸保卫战")
st.write("用你超长的“无敌木板”，把那个讨厌的“大姨妈”打飞！先赢三局就胜利哦！")

# 乒乓游戏 HTML/JS 逻辑
pong_html = """
<div style="display: flex; justify-content: center; flex-direction: column; align-items: center;">
    <div id="game-ui" style="display: flex; justify-content: space-between; width: 400px; margin-bottom: 10px; font-family: 'Microsoft YaHei', sans-serif; font-size: 1.2em; font-weight: bold;">
        <span style="color: #4361ee;">大姨妈: <span id="aiScore">0</span></span>
        <span style="color: #ff4d6d;">仙女学霸: <span id="playerScore">0</span></span>
    </div>
    <div id="game-container" style="position: relative;">
        <canvas id="pongCanvas" width="400" height="500" style="border: 4px solid #ffafcc; border-radius: 10px; background: #fff5f8; box-shadow: 0 4px 10px rgba(0,0,0,0.1);"></canvas>
        <div id="overlay" style="position: absolute; top: 0; left: 0; width: 400px; height: 500px; background: rgba(255,255,255,0.9); display: none; flex-direction: column; justify-content: center; align-items: center; text-align: center; border-radius: 10px;">
            <h2 id="result-title" style="color: #ff4d6d;"></h2>
            <p id="result-msg" style="padding: 20px; color: #666;"></p>
            <button onclick="location.reload()" style="padding: 10px 20px; background: #ff4d6d; color: white; border: none; border-radius: 5px; cursor: pointer;">再玩一局</button>
        </div>
    </div>
</div>

<script>
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');
const overlay = document.getElementById('overlay');
const resultTitle = document.getElementById('result-title');
const resultMsg = document.getElementById('result-msg');

// 游戏配置
const winScore = 3;
let isGameOver = false;

// 木板属性：玩家 100px, 对方 50px (两倍长度)
const player = { x: 150, y: 470, w: 100, h: 12, color: '#ff4d6d', score: 0, speed: 8 };
const ai = { x: 175, y: 18, w: 50, h: 12, color: '#4361ee', score: 0, speed: 4 };

// 球的初始属性
let initialBallSpeed = 4;
const ball = { x: 200, y: 250, r: 8, speed: initialBallSpeed, dx: 3, dy: 3, color: '#e5989b' };

let keys = {};
window.addEventListener('keydown', e => { 
    keys[e.code] = true; 
    if(['ArrowLeft', 'ArrowRight', 'Space'].includes(e.code)) e.preventDefault(); 
});
window.addEventListener('keyup', e => keys[e.code] = false);

function resetBall(scorer) {
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    ball.speed = initialBallSpeed; // 重置球速
    ball.dy = scorer === 'player' ? -initialBallSpeed : initialBallSpeed;
    ball.dx = (Math.random() > 0.5 ? 1 : -1) * initialBallSpeed;
}

function endGame(winner) {
    isGameOver = true;
    overlay.style.display = 'flex';
    if (winner === 'player') {
        resultTitle.innerText = "🏆 你赢了！";
        resultMsg.innerHTML = "哪怕是大姨妈也挡不住仙女学霸的威力！<br>辛苦啦，现在放下手机，让男朋友来照顾你吧 ❤️";
    } else {
        resultTitle.innerText = "哎呀，差一点点！";
        resultMsg.innerText = "大姨妈这次有点凶，快呼叫男朋友来帮你揉揉肚子！";
    }
}

function update() {
    if (isGameOver) return;

    // 玩家移动
    if (keys['ArrowLeft'] && player.x > 0) player.x -= player.speed;
    if (keys['ArrowRight'] && player.x + player.w < canvas.width) player.x += player.speed;

    // AI 移动
    let aiCenter = ai.x + ai.w / 2;
    if (aiCenter < ball.x - 5) ai.x += ai.speed;
    else if (aiCenter > ball.x + 5) ai.x -= ai.speed;
    
    if (ai.x < 0) ai.x = 0;
    if (ai.x + ai.w > canvas.width) ai.x = canvas.width - ai.w;

    // 球的移动
    ball.x += ball.dx;
    ball.y += ball.dy;

    // 左右墙壁反弹
    if (ball.x - ball.r < 0 || ball.x + ball.r > canvas.width) {
        ball.dx *= -1;
    }

    // 碰撞检测：玩家木板
    if (ball.y + ball.r > player.y && ball.x > player.x && ball.x < player.x + player.w && ball.dy > 0) {
        let hitPoint = ball.x - (player.x + player.w / 2);
        let normalizedHit = hitPoint / (player.w / 2); 
        let angle = normalizedHit * (Math.PI / 3); 

        ball.speed += 0.5; // 每撞一次速度明显增加
        ball.dx = ball.speed * Math.sin(angle);
        ball.dy = -ball.speed * Math.cos(angle);
    }

    // 碰撞检测：AI 木板
    if (ball.y - ball.r < ai.y + ai.h && ball.x > ai.x && ball.x < ai.x + ai.w && ball.dy < 0) {
        let hitPoint = ball.x - (ai.x + ai.w / 2);
        let normalizedHit = hitPoint / (ai.w / 2);
        let angle = normalizedHit * (Math.PI / 3);

        ball.speed += 0.5; // 每撞一次速度增加
        ball.dx = ball.speed * Math.sin(angle);
        ball.dy = ball.speed * Math.cos(angle);
    }

    // 计分系统
    if (ball.y < 0) {
        player.score++;
        document.getElementById('playerScore').innerText = player.score;
        if (player.score >= winScore) endGame('player');
        else resetBall('player');
    } else if (ball.y > canvas.height) {
        ai.score++;
        document.getElementById('aiScore').innerText = ai.score;
        if (ai.score >= winScore) endGame('ai');
        else resetBall('ai');
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 中间虚线
    ctx.setLineDash([10, 10]);
    ctx.beginPath();
    ctx.moveTo(0, canvas.height / 2);
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.strokeStyle = "#ffb5a7";
    ctx.stroke();
    ctx.setLineDash([]);

    // 玩家木板
    ctx.fillStyle = player.color;
    ctx.beginPath();
    ctx.roundRect(player.x, player.y, player.w, player.h, 5);
    ctx.fill();

    // AI 木板
    ctx.fillStyle = ai.color;
    ctx.beginPath();
    ctx.roundRect(ai.x, ai.y, ai.w, ai.h, 5);
    ctx.fill();

    // 球
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
st.info("💡 **致学霸女友**：\n\n我知道医学院的考试压力很大，再加上生理期身体不舒服，真的辛苦了。这个“无敌大木板”只属于你，希望你能把所有的不愉快和痛痛都反弹掉！赢了三局之后，记得来找我拿【揉肚肚+按摩券】哦！")
