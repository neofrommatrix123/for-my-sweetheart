import streamlit as st
import streamlit.components.v1 as components

# 设置页面
st.set_page_config(page_title="硬核反击战", page_icon="🔥", layout="centered")

st.title("🔥 硬核反击战：打飞大姨妈")
st.write("现在的“大姨妈”实力与你旗鼓相当。用火球把她狠狠打飞，先赢三局者胜！")

# 乒乓游戏 HTML/JS 逻辑
pong_html = """
<div style="display: flex; justify-content: center; flex-direction: column; align-items: center;">
    <div id="game-ui" style="display: flex; justify-content: space-between; width: 400px; margin-bottom: 10px; font-family: 'Microsoft YaHei', sans-serif; font-size: 1.2em; font-weight: bold;">
        <span style="color: #4361ee;">大姨妈: <span id="aiScore">0</span></span>
        <span style="color: #ff4d6d;">你: <span id="playerScore">0</span></span>
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
let gameState = 'countdown'; // 状态：countdown, playing, gameover
let countdownNum = 3;
let countInterval;
let lastScorer = 'ai'; // 记录上次得分者，决定发球方向

// 木板属性
const player = { x: 160, y: 470, w: 80, h: 12, color: '#ff4d6d', score: 0, speed: 6 };
const ai = { x: 160, y: 18, w: 80, h: 12, color: '#4361ee', score: 0, speed: 6 };

// 球的初始属性
let initialBallSpeed = 5;
const ball = { x: 200, y: 250, r: 8, speed: initialBallSpeed, dx: 0, dy: 0 };
let trail = [];

let keys = {};
window.addEventListener('keydown', e => { 
    keys[e.code] = true; 
    if(['ArrowLeft', 'ArrowRight', 'Space'].includes(e.code)) e.preventDefault(); 
});
window.addEventListener('keyup', e => keys[e.code] = false);

// 发球与倒计时逻辑
function resetBall(scorer) {
    if (scorer) lastScorer = scorer;
    
    // 把球放回中心
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    ball.dx = 0;
    ball.dy = 0;
    trail = []; // 清空尾迹
    
    gameState = 'countdown';
    countdownNum = 3;

    if (countInterval) clearInterval(countInterval);
    
    countInterval = setInterval(() => {
        countdownNum--;
        if (countdownNum < 0) {
            clearInterval(countInterval);
            gameState = 'playing';
            ball.speed = initialBallSpeed; 
            // 谁得分，球就发给对方（向对方移动）
            ball.dy = lastScorer === 'player' ? -initialBallSpeed : initialBallSpeed;
            ball.dx = (Math.random() > 0.5 ? 1 : -1) * initialBallSpeed;
        }
    }, 800); // 800ms 一跳，节奏更紧凑
}

function endGame(winner) {
    gameState = 'gameover';
    overlay.style.display = 'flex';
    if (winner === 'player') {
        resultTitle.innerText = "🏆 完胜！";
        resultMsg.innerHTML = "成功击退大姨妈！<br><br>放下手机，你的专属跑腿已就位，想吃什么直接点单。";
    } else {
        resultTitle.innerText = "💥 惜败！";
        resultMsg.innerText = "这局大姨妈有点猛。喝口热水休息一下，我来替你报仇！";
    }
}

function update() {
    if (gameState === 'gameover') return;

    // 无论是否在倒计时，玩家和AI都可以移动木板找位置
    if (keys['ArrowLeft'] && player.x > 0) player.x -= player.speed;
    if (keys['ArrowRight'] && player.x + player.w < canvas.width) player.x += player.speed;

    let aiCenter = ai.x + ai.w / 2;
    if (aiCenter < ball.x - 5) ai.x += ai.speed;
    else if (aiCenter > ball.x + 5) ai.x -= ai.speed;
    
    if (ai.x < 0) ai.x = 0;
    if (ai.x + ai.w > canvas.width) ai.x = canvas.width - ai.w;

    // 只有在 playing 状态下，球才移动和判定
    if (gameState === 'playing') {
        trail.push({x: ball.x, y: ball.y});
        if (trail.length > 12) trail.shift();

        ball.x += ball.dx;
        ball.y += ball.dy;

        // 左右墙壁反弹
        if (ball.x - ball.r < 0 || ball.x + ball.r > canvas.width) {
            ball.dx *= -1;
            ball.x = ball.x - ball.r < 0 ? ball.r : canvas.width - ball.r; 
        }

        // 碰撞检测：玩家
        if (ball.y + ball.r > player.y && ball.x > player.x && ball.x < player.x + player.w && ball.dy > 0) {
            let hitPoint = ball.x - (player.x + player.w / 2);
            let normalizedHit = hitPoint / (player.w / 2); 
            let angle = normalizedHit * (Math.PI / 3); 

            ball.speed += 0.6; // 加速
            ball.dx = ball.speed * Math.sin(angle);
            ball.dy = -ball.speed * Math.cos(angle);
        }

        // 碰撞检测：AI
        if (ball.y - ball.r < ai.y + ai.h && ball.x > ai.x && ball.x < ai.x + ai.w && ball.dy < 0) {
            let hitPoint = ball.x - (ai.x + ai.w / 2);
            let normalizedHit = hitPoint / (ai.w / 2);
            let angle = normalizedHit * (Math.PI / 3);

            ball.speed += 0.6; 
            ball.dx = ball.speed * Math.sin(angle);
            ball.dy = ball.speed * Math.cos(angle);
        }

        // 计分
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
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 中间网格线
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

    // 绘制火球尾迹
    for (let i = 0; i < trail.length; i++) {
        let alpha = i / trail.length; 
        let radius = ball.r * alpha;  
        ctx.beginPath();
        ctx.arc(trail[i].x, trail[i].y, radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, ${100 + alpha * 50}, 0, ${alpha * 0.6})`;
        ctx.fill();
    }

    // 绘制火球本体
    let gradient = ctx.createRadialGradient(ball.x, ball.y, 1, ball.x, ball.y, ball.r);
    gradient.addColorStop(0, "#fffbd5"); 
    gradient.addColorStop(0.3, "#ffb703"); 
    gradient.addColorStop(0.7, "#fb8500"); 
    gradient.addColorStop(1, "#d00000");   
    
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();
    ctx.closePath();

    // --- 绘制倒计时 ---
    if (gameState === 'countdown') {
        ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
        ctx.font = "bold 80px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        let text = countdownNum > 0 ? countdownNum : "GO!";
        
        // 发光特效
        ctx.shadowColor = "#ff4d6d";
        ctx.shadowBlur = 15;
        ctx.fillText(text, canvas.width / 2, canvas.height / 2);
        ctx.shadowBlur = 0; // 恢复正常状态
    }
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

// 初始化游戏：开局让AI发球（球向玩家飞）
resetBall('ai'); 
gameLoop();
</script>
"""

components.html(pong_html, height=550)

st.write("---")
st.info("💡 操作提示：键盘左右键控制。备考辛苦啦，把复习的压力和身体的烦躁都砸进火球里打飞吧！通关后可解锁特殊奖励（比如某人包揽今晚家务）。")
