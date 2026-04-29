import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="硬核坦克保卫战", page_icon="🚜", layout="centered")

st.title("🚜 坦克大战：全面进化版")
st.write("敌军全面升级，AI更狡猾，数量更庞大。收集空投道具，用重火力摧毁它们！")

tank_html = """
<div style="display: flex; justify-content: center; flex-direction: column; align-items: center;">
    <div id="game-ui" style="display: flex; justify-content: space-between; width: 520px; margin-bottom: 10px; font-family: 'Microsoft YaHei', sans-serif; font-size: 1.2em; font-weight: bold; background: #f8f9fa; padding: 10px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <span style="color: #e63946;">敌军剩余: <span id="enemyCount">15</span></span>
        <span style="color: #4361ee;" id="weaponStatus">武器: 标配</span>
        <span style="color: #ff4d6d;">装甲生命: <span id="playerLife">3</span></span>
    </div>
    <div id="game-container" style="position: relative;">
        <canvas id="gameCanvas" width="520" height="520" style="border: 5px solid #6c757d; border-radius: 8px; background: #212529; box-shadow: 0 8px 16px rgba(0,0,0,0.6);"></canvas>
        <div id="overlay" style="position: absolute; top: 0; left: 0; width: 520px; height: 520px; background: rgba(0,0,0,0.85); display: none; flex-direction: column; justify-content: center; align-items: center; text-align: center; border-radius: 8px;">
            <h1 id="result-title" style="color: #ffb703; font-size: 3em; text-shadow: 2px 2px 0px #000;"></h1>
            <p id="result-msg" style="padding: 20px; color: #f8f9fa; font-size: 1.2em; font-weight: bold;"></p>
            <button onclick="location.reload()" style="padding: 12px 30px; background: #e63946; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1.2em; text-transform: uppercase; letter-spacing: 2px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">Reload & Retry</button>
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
const weaponStatusSpan = document.getElementById('weaponStatus');

const TILE = 40;
const ROWS = 13;
const COLS = 13;

// 0:空地, 1:红砖(可炸), 2:钢板(只有火焰弹可熔化)
let map = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,0,1,2,1,2,1,0,1,1,0],
    [0,1,1,0,1,1,1,1,1,0,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,0,2,2,0,1,0,2,2,0,1,1],
    [1,1,0,2,1,0,1,0,1,2,0,1,1],
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,0,2,1,0,1,0,1,2,0,1,1],
    [1,1,0,2,2,0,1,0,2,2,0,1,1],
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,0,1,1,2,1,1,0,1,1,0],
    [0,1,1,0,1,1,1,1,1,0,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0]
];

let player = { x: 240, y: 480, dir: 'U', size: 32, speed: 4, lives: 3, bullets: [], weapon: 'normal', shieldTimer: 0 };
let enemies = [];
let items = [];
let totalEnemiesToSpawn = 15;
let enemiesDestroyed = 0;
let gameState = 'countdown';
let countdownNum = 3;

let keys = {};
window.addEventListener('keydown', e => {
    keys[e.code] = true;
    if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)) e.preventDefault();
    if(e.code === 'Space' && gameState === 'playing') fireBullet(player);
});
window.addEventListener('keyup', e => keys[e.code] = false);

// 绘制精致版坦克
function drawTank(tank, baseColor, turretColor) {
    ctx.save();
    ctx.translate(tank.x + tank.size/2, tank.y + tank.size/2);
    
    // 旋转炮管朝向
    if(tank.dir === 'U') ctx.rotate(0);
    else if(tank.dir === 'R') ctx.rotate(Math.PI/2);
    else if(tank.dir === 'D') ctx.rotate(Math.PI);
    else if(tank.dir === 'L') ctx.rotate(-Math.PI/2);

    // 1. 履带 (带纹理)
    ctx.fillStyle = "#343a40";
    ctx.fillRect(-16, -16, 8, 32);
    ctx.fillRect(8, -16, 8, 32);
    ctx.fillStyle = "#212529";
    for(let i = -14; i <= 14; i += 6) {
        ctx.fillRect(-16, i, 8, 2);
        ctx.fillRect(8, i, 8, 2);
    }

    // 2. 车身底座
    ctx.fillStyle = baseColor;
    ctx.beginPath();
    ctx.roundRect(-10, -14, 20, 28, 4);
    ctx.fill();
    ctx.strokeStyle = "rgba(0,0,0,0.3)";
    ctx.lineWidth = 2;
    ctx.stroke();

    // 3. 炮筒
    ctx.fillStyle = "#adb5bd";
    ctx.fillRect(-2, -22, 4, 16);
    ctx.fillStyle = "#495057";
    ctx.fillRect(-3, -24, 6, 4); // 炮口

    // 4. 中央炮塔
    ctx.fillStyle = turretColor;
    ctx.beginPath();
    ctx.arc(0, 0, 8, 0, Math.PI*2);
    ctx.fill();
    ctx.stroke();

    ctx.restore();

    // 护盾特效
    if(tank.shieldTimer > 0) {
        ctx.strokeStyle = `rgba(0, 255, 255, ${0.5 + Math.abs(Math.sin(Date.now()/100))*0.5})`;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(tank.x + tank.size/2, tank.y + tank.size/2, 22, 0, Math.PI*2);
        ctx.stroke();
    }
}

// 武器开火逻辑
function fireBullet(tank) {
    let maxB = tank.weapon === 'spread' ? 6 : 3; // 玩家允许同屏多子弹
    if (tank.bullets.length >= maxB) return;
    
    let bx = tank.x + tank.size/2;
    let by = tank.y + tank.size/2;
    let speed = tank.weapon === 'fire' ? 8 : 6;
    let type = tank.weapon || 'normal';

    if (tank.weapon === 'spread') {
        const dirs = ['U','R','D','L'];
        let fIdx = dirs.indexOf(tank.dir);
        // 发射前方、左方、右方
        tank.bullets.push({x: bx, y: by, dir: dirs[fIdx], speed: speed, type: 'normal'});
        tank.bullets.push({x: bx, y: by, dir: dirs[(fIdx+1)%4], speed: speed, type: 'normal'});
        tank.bullets.push({x: bx, y: by, dir: dirs[(fIdx+3)%4], speed: speed, type: 'normal'});
    } else {
        tank.bullets.push({x: bx, y: by, dir: tank.dir, speed: speed, type: type});
    }
}

function spawnEnemy() {
    if (enemies.length + enemiesDestroyed < totalEnemiesToSpawn && enemies.length < 6) { // 同屏最多6辆
        let spawnPos = [40, 240, 440];
        let sx = spawnPos[Math.floor(Math.random() * spawnPos.length)];
        enemies.push({ 
            x: sx, y: 0, dir: 'D', size: 32, speed: 2, bullets: [], moveTimer: 0 
        });
    }
}

function checkCollision(x, y, size) {
    let margin = 4; // 碰撞容错
    let l = Math.floor((x+margin)/TILE), r = Math.floor((x+size-margin)/TILE);
    let t = Math.floor((y+margin)/TILE), b = Math.floor((y+size-margin)/TILE);
    if(l<0 || r>=COLS || t<0 || b>=ROWS) return true; // 越界
    for(let i=t; i<=b; i++) {
        for(let j=l; j<=r; j++) {
            if(map[i][j] !== 0) return true;
        }
    }
    return false;
}

function update() {
    if (gameState !== 'playing') return;

    // --- 道具系统：随机生成 ---
    if(Math.random() < 0.005 && items.length < 2) {
        let r = Math.floor(Math.random()*ROWS), c = Math.floor(Math.random()*COLS);
        if(map[r][c] === 0) {
           let types = ['fire', 'spread', 'shield'];
           items.push({r: r, c: c, type: types[Math.floor(Math.random()*3)], timer: 600});
        }
    }

    // --- 玩家逻辑 ---
    if (player.shieldTimer > 0) player.shieldTimer--;
    
    let oldX = player.x, oldY = player.y;
    if (keys['ArrowUp']) { player.y -= player.speed; player.dir = 'U'; }
    else if (keys['ArrowDown']) { player.y += player.speed; player.dir = 'D'; }
    else if (keys['ArrowLeft']) { player.x -= player.speed; player.dir = 'L'; }
    else if (keys['ArrowRight']) { player.x += player.speed; player.dir = 'R'; }
    
    if (checkCollision(player.x, player.y, player.size)) {
        player.x = oldX; player.y = oldY;
    }

    // 道具拾取
    for(let i = items.length-1; i>=0; i--) {
        items[i].timer--;
        if(items[i].timer <= 0) { items.splice(i,1); continue; }
        
        let cx = items[i].c * TILE + TILE/2, cy = items[i].r * TILE + TILE/2;
        if (Math.abs((player.x+16) - cx) < 24 && Math.abs((player.y+16) - cy) < 24) {
            let t = items[i].type;
            if(t === 'shield') player.shieldTimer = 400; // 约6秒无敌
            else {
                player.weapon = t;
                weaponStatusSpan.innerText = t === 'fire' ? "武器: 🔥 火焰弹" : "武器: 🌟 散射弹";
            }
            items.splice(i,1);
        }
    }

    // --- 智能 AI 逻辑 ---
    enemies.forEach(en => {
        let dx = player.x - en.x;
        let dy = player.y - en.y;

        // 视线与射击判定：如果与玩家处在同一直线，开火并调整方向
        let aligned = false;
        if (Math.abs(dx) < 20) {
            en.dir = dy > 0 ? 'D' : 'U';
            aligned = true;
        } else if (Math.abs(dy) < 20) {
            en.dir = dx > 0 ? 'R' : 'L';
            aligned = true;
        }
        
        if (aligned && Math.random() < 0.05) fireBullet(en);
        else if (Math.random() < 0.01) fireBullet(en);

        en.moveTimer--;
        // 遇到障碍或定时器到，重新寻路
        if (en.moveTimer <= 0 || checkCollision(en.x, en.y, en.size)) {
            let possibleDirs = [];
            // 优先向玩家方向移动
            if(Math.abs(dx) > Math.abs(dy)) {
                possibleDirs.push(dx > 0 ? 'R' : 'L');
                possibleDirs.push(dy > 0 ? 'D' : 'U');
            } else {
                possibleDirs.push(dy > 0 ? 'D' : 'U');
                possibleDirs.push(dx > 0 ? 'R' : 'L');
            }
            ['U','D','L','R'].forEach(d => { if(!possibleDirs.includes(d)) possibleDirs.push(d); });
            
            for(let d of possibleDirs) {
                let testX = en.x, testY = en.y;
                if(d==='U') testY -= 4; if(d==='D') testY += 4;
                if(d==='L') testX -= 4; if(d==='R') testX += 4;
                if(!checkCollision(testX, testY, en.size)) {
                    en.dir = d;
                    break;
                }
            }
            en.moveTimer = 30 + Math.random()*50;
        }

        let ex = en.x, ey = en.y;
        if (en.dir === 'U') en.y -= en.speed;
        if (en.dir === 'D') en.y += en.speed;
        if (en.dir === 'L') en.x -= en.speed;
        if (en.dir === 'R') en.x += en.speed;
        if (checkCollision(en.x, en.y, en.size)) { en.x = ex; en.y = ey; en.moveTimer = 0; }
    });

    // --- 子弹与碰撞物理 ---
    [player, ...enemies].forEach(tank => {
        for (let i = tank.bullets.length - 1; i >= 0; i--) {
            let b = tank.bullets[i];
            if (b.dir === 'U') b.y -= b.speed; if (b.dir === 'D') b.y += b.speed;
            if (b.dir === 'L') b.x -= b.speed; if (b.dir === 'R') b.x += b.speed;

            // 碰墙判断
            let r = Math.floor(b.y/TILE), c = Math.floor(b.x/TILE);
            if(r<0 || r>=ROWS || c<0 || c>=COLS) { tank.bullets.splice(i, 1); continue; }
            
            if (map[r][c] === 1) { // 砖块
                map[r][c] = 0;
                if(b.type !== 'fire') { tank.bullets.splice(i, 1); continue; } // 火焰弹可以穿透砖块！
            } else if (map[r][c] === 2) { // 钢板
                if(b.type === 'fire') map[r][c] = 0; // 火焰弹能熔化钢板！
                tank.bullets.splice(i, 1);
                continue;
            }

            // 击中坦克判定
            let hitTarget = false;
            if (tank === player) { // 玩家打敌人
                enemies.forEach((en, eIdx) => {
                    if (Math.abs(b.x - (en.x+16)) < 20 && Math.abs(b.y - (en.y+16)) < 20) {
                        enemies.splice(eIdx, 1);
                        hitTarget = true;
                        enemiesDestroyed++;
                        enemyCountSpan.innerText = totalEnemiesToSpawn - enemiesDestroyed;
                        if(enemiesDestroyed >= totalEnemiesToSpawn) endGame(true);
                    }
                });
            } else { // 敌人打玩家
                if (Math.abs(b.x - (player.x+16)) < 20 && Math.abs(b.y - (player.y+16)) < 20) {
                    if (player.shieldTimer <= 0) { // 有护盾免疫伤害
                        player.lives--;
                        playerLifeSpan.innerText = player.lives;
                        player.weapon = 'normal'; // 死亡掉落武器
                        weaponStatusSpan.innerText = "武器: 标配";
                        player.x = 240; player.y = 480; // 重生回起点
                        player.shieldTimer = 180; // 重生给3秒无敌
                        if(player.lives <= 0) endGame(false);
                    }
                    hitTarget = true;
                }
            }
            if (hitTarget) tank.bullets.splice(i, 1);
        }
    });

    spawnEnemy();
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 绘制地图环境
    for(let r=0; r<ROWS; r++) {
        for(let c=0; c<COLS; c++) {
            let x = c*TILE, y = r*TILE;
            if(map[r][c] === 1) { 
                ctx.fillStyle = "#e07a5f"; // 红砖
                ctx.fillRect(x+1, y+1, TILE-2, TILE-2);
                ctx.fillStyle = "#f4a261"; // 砖块纹理
                ctx.fillRect(x+1, y+18, TILE-2, 4);
                ctx.fillRect(x+18, y+1, 4, TILE-2);
            }
            if(map[r][c] === 2) { 
                ctx.fillStyle = "#ced4da"; // 银白钢板
                ctx.fillRect(x, y, TILE, TILE);
                ctx.fillStyle = "#6c757d"; // 钢板边框和铆钉
                ctx.strokeRect(x+2, y+2, TILE-4, TILE-4);
                ctx.fillRect(x+6, y+6, 4, 4); ctx.fillRect(x+30, y+6, 4, 4);
                ctx.fillRect(x+6, y+30, 4, 4); ctx.fillRect(x+30, y+30, 4, 4);
            }
        }
    }

    // 绘制道具
    items.forEach(it => {
        let x = it.c * TILE + 20, y = it.r * TILE + 25;
        ctx.font = "24px Arial";
        ctx.textAlign = "center";
        if(it.timer % 30 > 10) { // 闪烁效果
            if(it.type === 'fire') ctx.fillText("🔥", x, y);
            if(it.type === 'spread') ctx.fillText("🌟", x, y);
            if(it.type === 'shield') ctx.fillText("🛡️", x, y);
        }
    });

    // 绘制坦克
    if(player.lives > 0) drawTank(player, "#ff4d6d", "#c1121f");
    enemies.forEach(en => drawTank(en, "#3a86ff", "#03045e"));

    // 绘制子弹
    [player, ...enemies].forEach(tank => {
        tank.bullets.forEach(b => {
            ctx.beginPath();
            ctx.arc(b.x, b.y, b.type === 'fire' ? 6 : 4, 0, Math.PI*2);
            if(b.type === 'fire') {
                ctx.fillStyle = "#fb8500"; // 火焰弹颜色
                ctx.shadowColor = "#ff0000";
                ctx.shadowBlur = 10;
            } else {
                ctx.fillStyle = tank === player ? "#ffde59" : "#00f5d4";
                ctx.shadowBlur = 0;
            }
            ctx.fill();
            ctx.shadowBlur = 0; // 重置阴影
        });
    });

    // 开局倒计时
    if (gameState === 'countdown') {
        ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
        ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#ffb703";
        ctx.font = "bold 80px 'Impact', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(countdownNum > 0 ? countdownNum : "BATTLE!", canvas.width/2, canvas.height/2 + 25);
    }
}

function endGame(isWin) {
    gameState = 'gameover';
    overlay.style.display = 'flex';
    if (isWin) {
        resultTitle.innerText = "MISSION CLEAR!";
        resultMsg.innerText = "硬核任务达成！你用强大的火力和战术摧毁了所有的阻碍。";
        resultTitle.style.color = "#52b788";
    } else {
        resultTitle.innerText = "ARMOR DESTROYED";
        resultMsg.innerText = "被火力压制了！敌方数量太多，休息一下，制定新的战术吧。";
        resultTitle.style.color = "#e63946";
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

components.html(tank_html, height=650)

st.write("---")
st.info("""
### 📡 战地手册：
* **移动与开火**：方向键控制，空格键射击。
* **🔥 火焰弹 (Fire)**：子弹变红变大。**能熔化银色钢板，并且可以直接穿透红砖！**
* **🌟 散射弹 (Spread)**：按一次空格，同时向你的**前方与左右侧**发射三枚子弹，形成火力网。
* **🛡️ 能量盾 (Shield)**：获得持续数秒的无敌光环。
* **⚠️ 注意**：敌军现在极其聪明，不要在毫无掩体的地方和他们处于同一直线上，他们会立刻瞄准你！
""")
