import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="坦克大战：专注力保卫战", page_icon="🚜", layout="centered")

st.title("🚜 坦克大战：击碎负能量")
st.write("操作坦克摧毁所有代表“负能量”的敌军，守护你的复习专注力！")

# 坦克大战 HTML/JS 逻辑
tank_html = """
<div style="display: flex; justify-content: center; flex-direction: column; align-items: center; position: relative;">
    <div id="game-ui" style="display: flex; justify-content: space-between; width: 500px; margin-bottom: 10px; font-family: 'Microsoft YaHei', sans-serif; font-size: 1.2em; font-weight: bold;">
        <span style="color: #4361ee;">敌军坦克: <span id="enemyCount">5</span></span>
        <span style="color: #ff4d6d;">你的生命: <span id="playerLife">3</span></span>
    </div>
    <div id="game-container" style="position: relative;">
        <canvas id="gameCanvas" width="500" height="500" style="border: 4px solid #ffafcc; border-radius: 10px; background: #2b2d42; box-shadow: 0 4px 10px rgba(0,0,0,0.5);"></canvas>
        <div id="overlay" style="position: absolute; top: 0; left: 0; width: 500px; height: 500px; background: rgba(255,255,255,0.95); display: none; flex-direction: column; justify-content: center; align-items: center; text-align: center; border-radius: 10px;">
            <h2 id="result-title" style="color: #ff4d6d;"></h2>
            <p id="result-msg" style="padding: 20px; color: #333; font-weight: bold;"></p>
            <button onclick="location.reload()" style="padding: 10px 20px; background: #ff4d6d; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1em;">重整旗鼓</button>
        </div>
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const overlay = document.getElementById('overlay');
const resultTitle = document.getElementById('result-title');
const resultMsg = document.getElementById('result-msg');
const enemyCountSpan = document.getElementById('enemyCount');
const playerLifeSpan = document.getElementById('playerLife');

const TILE = 40;
const ROWS = 12;
const COLS = 12;

// 地图 0:路, 1:砖块(可炸), 2:钢板(不可炸)
let map = [
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,0,1,1,1,1,0,1,1,0],
    [0,1,1,0,0,2,2,0,0,1,1,0],
    [0,0,0,1,0,0,0,0,1,0,0,0],
    [1,1,0,2,0,1,1,0,2,0,1,1],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,1,0,0,0,0,0],
    [1,1,0,2,0,1,1,0,2,0,1,1],
    [0,0,0,1,0,0,0,0,1,0,0,0],
    [0,1,1,0,0,2,2,0,0,1,1,0],
    [0,1,1,0,1,1,1,1,0,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0]
];

let player = { x: 240, y: 440, dir: 'U', size: 32, speed: 3, lives: 3, bullets: [] };
let enemies = [];
let totalEnemiesToSpawn = 5;
let enemiesDestroyed = 0;
let gameState = 'countdown';
let countdownNum = 3;

// 按键监听
let keys = {};
window.addEventListener('keydown', e => {
    keys[e.code] = true;
    if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)) e.preventDefault();
    if(e.code === 'Space' && gameState === 'playing') fireBullet(player);
});
window.addEventListener('keyup', e => keys[e.code] = false);

function fireBullet(tank) {
    if (tank.bullets.length >= 2) return;
    let bx = tank.x + tank.size/2;
    let by = tank.y + tank.size/2;
    tank.bullets.push({ x: bx, y: by, dir: tank.dir, speed: 6 });
}

function spawnEnemy() {
    if (enemies.length + enemiesDestroyed < totalEnemiesToSpawn && enemies.length < 3) {
        enemies.push({ 
            x: Math.random() < 0.5 ? 40 : 440, 
            y: 40, 
            dir: 'D', 
            size: 32, 
            speed: 2, 
            bullets: [],
            moveTimer: 0 
        });
    }
}

function checkCollision(x, y, size) {
    let margin = 2;
    let l = Math.floor((x+margin)/TILE), r = Math.floor((x+size-margin)/TILE);
    let t = Math.floor((y+margin)/TILE), b = Math.floor((y+size-margin)/TILE);
    if(l<0 || r>=COLS || t<0 || b>=ROWS) return true;
    for(let i=t; i<=b; i++) {
        for(let j=l; j<=r; j++) {
            if(map[i][j] !== 0) return true;
        }
    }
    return false;
}

function update() {
    if (gameState !== 'playing') return;

    // 玩家移动
    let oldX = player.x, oldY = player.y;
    if (keys['ArrowUp']) { player.y -= player.speed; player.dir = 'U'; }
    else if (keys['ArrowDown']) { player.y += player.speed; player.dir = 'D'; }
    else if (keys['ArrowLeft']) { player.x -= player.speed; player.dir = 'L'; }
    else if (keys['ArrowRight']) { player.x += player.speed; player.dir = 'R'; }
    
    if (checkCollision(player.x, player.y, player.size)) {
        player.x = oldX; player.y = oldY;
    }

    // 子弹更新
    [player, ...enemies].forEach(tank => {
        for (let i = tank.bullets.length - 1; i >= 0; i--) {
            let b = tank.bullets[i];
            if (b.dir === 'U') b.y -= b.speed;
            if (b.dir === 'D') b.y += b.speed;
            if (b.dir === 'L') b.x -= b.speed;
            if (b.dir === 'R') b.x += b.speed;

            // 碰墙
            let r = Math.floor(b.y/TILE), c = Math.floor(b.x/TILE);
            if(r<0 || r>=ROWS || c<0 || c>=COLS) { tank.bullets.splice(i, 1); continue; }
            
            if (map[r][c] === 1) { // 砖块
                map[r][c] = 0;
                tank.bullets.splice(i, 1);
                continue;
            } else if (map[r][c] === 2) { // 钢板
                tank.bullets.splice(i, 1);
                continue;
            }

            // 子弹击中坦克检测
            if (tank === player) { // 玩家子弹打敌人
                enemies.forEach((en, eIdx) => {
                    if (Math.abs(b.x - (en.x+16)) < 20 && Math.abs(b.y - (en.y+16)) < 20) {
                        enemies.splice(eIdx, 1);
                        tank.bullets.splice(i, 1);
                        enemiesDestroyed++;
                        enemyCountSpan.innerText = totalEnemiesToSpawn - enemiesDestroyed;
                        if(enemiesDestroyed >= totalEnemiesToSpawn) endGame(true);
                    }
                });
            } else { // 敌人子弹打玩家
                if (Math.abs(b.x - (player.x+16)) < 20 && Math.abs(b.y - (player.y+16)) < 20) {
                    player.lives--;
                    playerLifeSpan.innerText = player.lives;
                    tank.bullets.splice(i, 1);
                    player.x = 240; player.y = 440; // 重生
                    if(player.lives <= 0) endGame(false);
                }
            }
        }
    });

    // 敌人 AI
    enemies.forEach(en => {
        en.moveTimer--;
        if (en.moveTimer <= 0) {
            const dirs = ['U','D','L','R'];
            en.dir = dirs[Math.floor(Math.random()*4)];
            en.moveTimer = 30 + Math.random()*60;
        }
        let ex = en.x, ey = en.y;
        if (en.dir === 'U') en.y -= en.speed;
        if (en.dir === 'D') en.y += en.speed;
        if (en.dir === 'L') en.x -= en.speed;
        if (en.dir === 'R') en.x += en.speed;
        if (checkCollision(en.x, en.y, en.size)) { en.x = ex; en.y = ey; en.moveTimer = 0; }
        
        if (Math.random() < 0.02) fireBullet(en);
    });

    spawnEnemy();
}

function drawTank(tank, color) {
    ctx.fillStyle = color;
    ctx.fillRect(tank.x, tank.y, tank.size, tank.size);
    ctx.fillStyle = "rgba(0,0,0,0.3)";
    // 炮筒
    if(tank.dir === 'U') ctx.fillRect(tank.x + 12, tank.y - 8, 8, 12);
    if(tank.dir === 'D') ctx.fillRect(tank.x + 12, tank.y + 28, 8, 12);
    if(tank.dir === 'L') ctx.fillRect(tank.x - 8, tank.y + 12, 12, 8);
    if(tank.dir === 'R') ctx.fillRect(tank.x + 28, tank.y + 12, 12, 8);
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 绘图地图
    for(let r=0; r<ROWS; r++) {
        for(let c=0; c<COLS; c++) {
            if(map[r][c] === 1) { ctx.fillStyle = "#e5989b"; ctx.fillRect(c*TILE+2, r*TILE+2, TILE-4, TILE-4); }
            if(map[r][c] === 2) { ctx.fillStyle = "#8d99ae"; ctx.fillRect(c*TILE, r*TILE, TILE, TILE); }
        }
    }

    // 绘图坦克
    drawTank(player, "#ff4d6d");
    enemies.forEach(en => drawTank(en, "#4361ee"));

    // 绘图子弹
    [player, ...enemies].forEach(tank => {
        tank.bullets.forEach(b => {
            ctx.fillStyle = "#ffde59";
            ctx.beginPath(); ctx.arc(b.x, b.y, 4, 0, Math.PI*2); ctx.fill();
        });
    });

    if (gameState === 'countdown') {
        ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
        ctx.font = "bold 60px Arial";
        ctx.textAlign = "center";
        ctx.fillText(countdownNum > 0 ? countdownNum : "START!", canvas.width/2, canvas.height/2);
    }
}

function endGame(isWin) {
    gameState = 'gameover';
    overlay.style.display = 'flex';
    if (isWin) {
        resultTitle.innerText = "战役胜利！";
        resultMsg.innerText = "负能量坦克已被全数歼灭。专注力已恢复 100%，你是最棒的学霸！";
    } else {
        resultTitle.innerText = "基地失守！";
        resultMsg.innerText = "没关系，这局干扰太强。先休息 5 分钟，喝杯热可可再来战斗！";
    }
}

function startCountdown() {
    let timer = setInterval(() => {
        countdownNum--;
        if (countdownNum < 0) {
            clearInterval(timer);
            gameState = 'playing';
        }
    }, 1000);
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

startCountdown();
gameLoop();
</script>
"""

components.html(tank_html, height=580)

st.write("---")
st.info("🎮 **作战指令**：\n* **方向键 (↑↓←→)**：控制坦克移动方向。\n* **空格键 (Space)**：发射能量炮，击碎砖块或消灭敌军。\n* **战术目标**：消灭 5 辆蓝色敌军坦克，同时保护好自己不要被击中超过 3 次！")
