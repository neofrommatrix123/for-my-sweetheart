import streamlit as st
import streamlit.components.v1 as components

# 设置页面
st.set_page_config(page_title="大姨妈大作战 - 硬核版", page_icon="🔥", layout="centered")

st.title("🔥 击退大姨妈：硬核保卫战")
st.write("现在的“大姨妈”实力与你旗鼓相当！挥舞你的木板，用愤怒的火球把她打飞吧！先赢三局者胜。")

# 乒乓游戏 HTML/JS 逻辑
pong_html = """
<div style="display: flex; justify-content: center; flex-direction: column; align-items: center;">
    <div id="game-ui" style="display: flex; justify-content: space-between; width: 400px; margin-bottom: 10px; font-family: 'Microsoft YaHei', sans-serif; font-size: 1.2em; font-weight: bold;">
        <span style="color: #4361ee;">大姨妈: <span id="aiScore">0</span></span>
        <span style="color: #ff4d6d;">仙女学霸: <span id="playerScore">0</span></span>
    </div>
    <div id="game-container" style="position: relative;">
        <canvas id="pongCanvas" width="400" height="500" style="border: 4px solid #ffafcc; border-radius: 10px; background: #2b2d42; box-shadow: 0 4px 10px rgba(0,0,0,0.5);"></canvas>
        <div id="overlay" style="position: absolute; top: 0; left: 0; width: 400px; height: 500px; background: rgba(255,255,255,0.95); display: none; flex-direction: column; justify-content: center; align-items: center; text-align: center; border-radius: 10px;">
            <h2 id="result-title" style="color: #ff4d6d;"></h2>
            <p id="result-msg" style="padding: 20px; color: #333; font-weight: bold;"></p>
            <button onclick="location.reload()" style="padding: 10px 20px; background: #ff4d6d; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1em;">再战一局</button>
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

// 【修改1 & 3】：木板长度一样（都是80），移动速度一样（都是6）
const player = { x: 160, y: 470, w: 80, h: 12, color: '#ff4d6d', score: 0, speed: 6 };
const ai = { x: 160, y: 18, w: 80, h: 12, color: '#4361ee', score: 0, speed: 6 };

// 球的初始属性
let initialBallSpeed = 5;
const ball = { x: 200, y: 250, r: 8, speed: initialBallSpeed, dx: 3, dy: 3 };

// 【修改2】：用于存储火球尾迹的数组
let trail = [];

let keys = {};
window.addEventListener('keydown', e => { 
    keys[e.code] = true; 
    if(['ArrowLeft', 'ArrowRight', 'Space'].includes(e.code)) e.preventDefault(); 
});
window.addEventListener('keyup', e => keys[e.code] = false);

function resetBall(scorer) {
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    ball.speed = initialBallSpeed; 
    ball.dy = scorer === 'player' ? -initialBallSpeed : initialBallSpeed;
    ball.dx = (Math.random() > 0.5 ? 1 : -1) * initialBallSpeed;
    trail = []; // 重置球时清空尾迹
}

function endGame(winner) {
    isGameOver = true;
    overlay.style.display = 'flex';
    if (winner === 'player') {
        resultTitle.innerText = "🏆 浴火重生，大获全胜！";
        resultMsg.innerHTML = "你用熊熊燃烧的火球彻底击退了“大姨妈”！<br><br>战斗结束，快把手机扔给男朋友，去兑换你的专属按摩服务吧 ❤️";
    } else {
        resultTitle.innerText = "💥 哎呀，大意了！";
        resultMsg.innerText = "这次“大姨妈”有点猛，深呼吸，喝口热水，呼叫男朋友来助阵！";
    }
}

function update() {
    if (isGameOver) return;

    // 记录球的位置用于生成火球尾迹
    trail.push({x: ball.x, y: ball.y});
    if (trail.length > 12) {
        trail.shift(); // 保持尾迹长度
    }

    // 玩家移动
    if (keys['ArrowLeft'] && player.x > 0) player.x -= player.speed;
    if (keys['ArrowRight'] && player.x + player.w < canvas.width) player.x += player.speed;

    // AI 移动 (难度增加：速度和玩家一样快)
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
        ball.x = ball.x - ball.r < 0 ? ball.r : canvas.width - ball.r; // 防止卡墙
    }

    // 碰撞检测：玩家木板
    if (ball.y + ball.r > player.y && ball.x > player.x && ball.x < player.x + player.w && ball.dy > 0) {
        let hitPoint = ball.x - (player.x + player.w / 2);
        let normalizedHit = hitPoint / (player.w / 2); 
        let angle = normalizedHit * (Math.PI / 3); 

        ball.speed += 0.6; // 火球越打越快
        ball.dx = ball.speed * Math.sin(angle);
        ball.dy = -ball.speed * Math.cos(angle);
    }

    // 碰撞检测：AI 木板
    if (ball.y - ball.r < ai.y + ai.h && ball.x > ai.x && ball.x < ai.x + ai.w && ball.dy < 0) {
        let hitPoint = ball.x - (ai.x + ai.w / 2);
        let normalizedHit = hitPoint / (ai.w / 2);
        let angle = normalizedHit * (Math.PI / 3);

        ball.speed += 0.6; 
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

    // 中间虚线 (为了配合火球，把网线改暗一点)
    ctx.setLineDash([10, 10]);
    ctx.beginPath();
    ctx.moveTo(0, canvas.height / 2);
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
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

    // 【修改2】：绘制火球尾迹
    for (let i = 0; i < trail.length; i++) {
        let alpha = i / trail.length; // 越老的尾迹越透明
        let radius = ball.r * alpha;  // 越老的尾迹越小
        ctx.beginPath();
        ctx.arc(trail[i].x, trail[i].y, radius, 0, Math.PI * 2);
        // 尾迹颜色：红色到橙色的过渡
        ctx.fillStyle = `rgba(255, ${100 + alpha * 50}, 0, ${alpha * 0.6})`;
        ctx.fill();
    }

    // 【修改2】：绘制火球本体 (径向渐变，中心黄，边缘红)
    let gradient = ctx.createRadialGradient(ball.x, ball.y, 1, ball.x, ball.y, ball.r);
    gradient.addColorStop(0, "#fffbd5"); // 核心白黄
    gradient.addColorStop(0.3, "#ffb703"); // 内圈金黄
    gradient.addColorStop(0.7, "#fb8500"); // 中圈橙色
    gradient.addColorStop(1, "#d00000");   // 外圈深红
    
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
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
st.info("💡 **致学霸女友**：\n\n开启硬核模式！把你的烦恼和痛楚全都灌注到这个火球里，狠狠地砸向对面吧！打赢了重重有赏！")
