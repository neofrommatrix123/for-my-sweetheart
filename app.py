import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="萌萌贪吃蛇", page_icon="🐍", layout="centered")

st.title("🐍 贪吃蛇：能量收集大作战")
st.write("操作方向键控制小蛇，收集尽可能多的“能量”，每吃一个都会变长变快哦！")

# 贪吃蛇 HTML/JS 逻辑
snake_html = """
<div style="display: flex; justify-content: center; flex-direction: column; align-items: center; position: relative;">
    <div id="game-ui" style="display: flex; justify-content: space-between; width: 400px; margin-bottom: 10px; font-family: 'Microsoft YaHei', sans-serif; font-size: 1.2em; font-weight: bold;">
        <span style="color: #ff4d6d;">当前能量值: <span id="currentScore">0</span></span>
        <span style="color: #4361ee;">最高纪录: <span id="highScore">0</span></span>
    </div>
    <div id="game-container" style="position: relative;">
        <canvas id="gameCanvas" width="400" height="400" style="border: 4px solid #ffafcc; border-radius: 10px; background: #fff5f8; box-shadow: 0 4px 10px rgba(0,0,0,0.1);"></canvas>
        <div id="overlay" style="position: absolute; top: 0; left: 0; width: 400px; height: 400px; background: rgba(255,255,255,0.9); display: none; flex-direction: column; justify-content: center; align-items: center; text-align: center; border-radius: 10px;">
            <h2 id="result-title" style="color: #ff4d6d;"></h2>
            <p id="result-msg" style="padding: 20px; color: #333; font-weight: bold;"></p>
            <button onclick="resetGame()" style="padding: 10px 20px; background: #ff4d6d; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1em;">再来一次</button>
        </div>
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const overlay = document.getElementById('overlay');
const resultTitle = document.getElementById('result-title');
const resultMsg = document.getElementById('result-msg');
const scoreSpan = document.getElementById('currentScore');
const highScoreSpan = document.getElementById('highScore');

const TILE = 20;
const ROWS = canvas.height / TILE;
const COLS = canvas.width / TILE;

let snake = [{x: 10, y: 10}];
let food = {x: 5, y: 5};
let dx = 0;
let dy = 0;
let nextDx = 1;
let nextDy = 0;
let score = 0;
let highScore = 0;
let gameState = 'countdown'; // countdown, playing, gameover
let countdownNum = 3;
let gameSpeed = 150; // 初始速度（毫秒）

// 监听键盘
window.addEventListener('keydown', e => {
    if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code)) e.preventDefault();
    
    if (e.code === 'ArrowUp' && dy === 0) { nextDx = 0; nextDy = -1; }
    if (e.code === 'ArrowDown' && dy === 0) { nextDx = 0; nextDy = 1; }
    if (e.code === 'ArrowLeft' && dx === 0) { nextDx = -1; nextDy = 0; }
    if (e.code === 'ArrowRight' && dx === 0) { nextDx = 1; nextDy = 0; }
});

function spawnFood() {
    food.x = Math.floor(Math.random() * COLS);
    food.y = Math.floor(Math.random() * ROWS);
    // 防止食物生成在蛇身上
    if (snake.some(seg => seg.x === food.x && seg.y === food.y)) spawnFood();
}

function resetGame() {
    snake = [{x: 10, y: 10}];
    dx = 0; dy = 0;
    nextDx = 1; nextDy = 0;
    score = 0;
    gameSpeed = 150;
    scoreSpan.innerText = score;
    overlay.style.display = 'none';
    startCountdown();
}

function startCountdown() {
    gameState = 'countdown';
    countdownNum = 3;
    let timer = setInterval(() => {
        countdownNum--;
        if (countdownNum < 0) {
            clearInterval(timer);
            gameState = 'playing';
            dx = nextDx; dy = nextDy;
            runLoop();
        }
    }, 800);
}

function runLoop() {
    if (gameState !== 'playing') return;

    // 更新方向
    dx = nextDx; dy = nextDy;

    // 计算新头部
    const head = {x: snake[0].x + dx, y: snake[0].y + dy};

    // 碰撞检测：墙壁或自己
    if (head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS || 
        snake.some(seg => seg.x === head.x && seg.y === head.y)) {
        endGame();
        return;
    }

    snake.unshift(head);

    // 吃到食物
    if (head.x === food.x && head.y === food.y) {
        score += 10;
        scoreSpan.innerText = score;
        if (score > highScore) {
            highScore = score;
            highScoreSpan.innerText = highScore;
        }
        spawnFood();
        // 加速
        if (gameSpeed > 60) gameSpeed -= 2;
    } else {
        snake.pop();
    }

    draw();
    setTimeout(runLoop, gameSpeed);
}

function endGame() {
    gameState = 'gameover';
    overlay.style.display = 'flex';
    resultTitle.innerText = "Game Over";
    resultMsg.innerText = `收集了 ${score} 点能量！继续加油。`;
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 画食物（小红心）
    ctx.fillStyle = "#ff4d6d";
    ctx.beginPath();
    let fx = food.x * TILE + TILE/2;
    let fy = food.y * TILE + TILE/2;
    ctx.arc(fx, fy, TILE/2 - 2, 0, Math.PI * 2);
    ctx.fill();

    // 画蛇
    snake.forEach((seg, index) => {
        ctx.fillStyle = index === 0 ? "#ff4d6d" : "#ffb5a7";
        ctx.beginPath();
        ctx.roundRect(seg.x * TILE + 1, seg.y * TILE + 1, TILE - 2, TILE - 2, 5);
        ctx.fill();
        
        // 给蛇头画眼睛
        if (index === 0) {
            ctx.fillStyle = "white";
            ctx.fillRect(seg.x * TILE + 4, seg.y * TILE + 4, 4, 4);
            ctx.fillRect(seg.x * TILE + 12, seg.y * TILE + 4, 4, 4);
        }
    });

    // 绘制倒计时
    if (gameState === 'countdown') {
        ctx.fillStyle = "rgba(255, 77, 109, 0.8)";
        ctx.font = "bold 60px Arial";
        ctx.textAlign = "center";
        ctx.fillText(countdownNum > 0 ? countdownNum : "GO!", canvas.width / 2, canvas.height / 2 + 20);
    }
}

// 初始启动
startCountdown();
setInterval(() => { if(gameState === 'countdown') draw(); }, 100);

</script>
"""

components.html(snake_html, height=500)

st.write("---")
st.info("🎮 **操作说明**：\n* 使用键盘 **方向键** 控制小蛇移动方向。\n* 吃到红点能量会得分并增加长度，速度也会越来越快。\n* ⚠️ 注意：不要撞到墙壁或自己的身体哦！")
