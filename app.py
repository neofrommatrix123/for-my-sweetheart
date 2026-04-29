import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Q版泡泡堂：大作战", page_icon="💣", layout="centered")

st.title("💣 Q版泡泡堂：冰雪融化大作战")
st.write("放置“暖水袋”，融化冰块，把代表“大姨妈”的小红怪全部赶走！")

# 泡泡堂 HTML/JS 逻辑
bomberman_html = """
<div style="display: flex; justify-content: center; flex-direction: column; align-items: center; position: relative;">
    <div id="game-ui" style="display: flex; justify-content: space-between; width: 520px; margin-bottom: 10px; font-family: 'Microsoft YaHei', sans-serif; font-size: 1.2em; font-weight: bold;">
        <span style="color: #4361ee;">剩余冰块随时可炸</span>
        <span style="color: #ff4d6d;">怪物剩余: <span id="enemyCount">3</span></span>
    </div>
    <div id="game-container" style="position: relative;">
        <canvas id="gameCanvas" width="520" height="520" style="border: 4px solid #ffafcc; border-radius: 10px; background: #e0fbfc; box-shadow: 0 4px 10px rgba(0,0,0,0.2);"></canvas>
        <div id="overlay" style="position: absolute; top: 0; left: 0; width: 520px; height: 520px; background: rgba(255,255,255,0.9); display: none; flex-direction: column; justify-content: center; align-items: center; text-align: center; border-radius: 10px;">
            <h2 id="result-title" style="color: #ff4d6d;"></h2>
            <p id="result-msg" style="padding: 20px; color: #333; font-weight: bold;"></p>
            <button onclick="location.reload()" style="padding: 10px 20px; background: #ff4d6d; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1em;">重新开始</button>
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

const TILE = 40;
const ROWS = 13;
const COLS = 13;

// 0: 空地, 1: 坚固的墙(灰色), 2: 冰块(淡蓝色,可炸毁)
let map = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,2,2,2,2,2,2,2,0,0,1],
    [1,0,1,2,1,2,1,2,1,2,1,0,1],
    [1,2,2,2,2,0,2,0,2,2,2,2,1],
    [1,2,1,2,1,2,1,2,1,2,1,2,1],
    [1,2,0,2,2,2,2,2,2,2,0,2,1],
    [1,2,1,2,1,2,1,2,1,2,1,2,1],
    [1,2,0,2,2,2,2,2,2,2,0,2,1],
    [1,2,1,2,1,2,1,2,1,2,1,2,1],
    [1,2,2,2,2,0,2,0,2,2,2,2,1],
    [1,0,1,2,1,2,1,2,1,2,1,0,1],
    [1,0,0,2,2,2,2,2,2,2,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1]
];

// 游戏实体
let player = { r: 1, c: 1, x: 40, y: 40, speed: 3, size: 24, maxBombs: 2, power: 2, alive: true };
let bombs = [];
let explosions = [];
let enemies = [
    { x: 11*TILE, y: 11*TILE, r: 11, c: 11, speed: 1.5, dir: {x: -1, y: 0}, alive: true },
    { x: 11*TILE, y: 1*TILE, r: 1, c: 11, speed: 1.5, dir: {x: 0, y: 1}, alive: true },
    { x: 1*TILE, y: 11*TILE, r: 11, c: 1, speed: 1.5, dir: {x: 1, y: 0}, alive: true }
];

let gameState = 'playing';

// 按键控制
let keys = {};
window.addEventListener('keydown', e => { 
    keys[e.code] = true; 
    if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)) e.preventDefault(); 
});
window.addEventListener('keyup', e => {
    keys[e.code] = false;
    // 抬起空格键时放置炸弹
    if (e.code === 'Space' && gameState === 'playing' && player.alive) {
        placeBomb();
    }
});

function placeBomb() {
    if (bombs.length >= player.maxBombs) return;
    let gridC = Math.floor((player.x + TILE/2) / TILE);
    let gridR = Math.floor((player.y + TILE/2) / TILE);
    
    // 检查该位置是否已有炸弹
    if (bombs.some(b => b.r === gridR && b.c === gridC)) return;

    bombs.push({ r: gridR, c: gridC, timer: 150 }); // 约2.5秒
}

function triggerExplosion(bomb) {
    let cells = [{r: bomb.r, c: bomb.c}];
    const dirs = [[0,1], [0,-1], [1,0], [-1,0]];
    
    for (let d of dirs) {
        for (let i = 1; i <= player.power; i++) {
            let nr = bomb.r + d[0] * i;
            let nc = bomb.c + d[1] * i;
            
            if (map[nr][nc] === 1) break; // 撞到硬墙停止
            
            cells.push({r: nr, c: nc});
            
            if (map[nr][nc] === 2) {
                // 炸毁冰块
                map[nr][nc] = 0;
                break; // 炸毁冰块后，火焰不穿透
            }
        }
    }
    explosions.push({ cells: cells, timer: 30 }); // 火焰持续约0.5秒
}

// 碰撞检测辅助函数
function canMove(newX, newY, size) {
    // 将玩家的四角转换为网格坐标
    let margin = (TILE - size) / 2;
    let left = Math.floor((newX + margin) / TILE);
    let right = Math.floor((newX + TILE - margin - 0.1) / TILE);
    let top = Math.floor((newY + margin) / TILE);
    let bottom = Math.floor((newY + TILE - margin - 0.1) / TILE);

    if (map[top][left] !== 0 || map[top][right] !== 0 || 
        map[bottom][left] !== 0 || map[bottom][right] !== 0) {
        return false;
    }
    
    // 简易炸弹碰撞：如果没站在炸弹上，就不能走进炸弹
    // 这里为了简化手感，允许穿过炸弹，但需要小心走位
    return true; 
}

function update() {
    if (gameState !== 'playing') return;

    // --- 玩家移动 ---
    let dx = 0, dy = 0;
    if (keys['ArrowUp']) dy -= player.speed;
    if (keys['ArrowDown']) dy += player.speed;
    if (keys['ArrowLeft']) dx -= player.speed;
    if (keys['ArrowRight']) dx += player.speed;

    if (dx !== 0 && canMove(player.x + dx, player.y, player.size)) player.x += dx;
    if (dy !== 0 && canMove(player.x, player.y + dy, player.size)) player.y += dy;

    // 更新玩家网格中心点
    player.r = Math.floor((player.y + TILE/2) / TILE);
    player.c = Math.floor((player.x + TILE/2) / TILE);

    // --- 炸弹倒计时 ---
    for (let i = bombs.length - 1; i >= 0; i--) {
        bombs[i].timer--;
        if (bombs[i].timer <= 0) {
            triggerExplosion(bombs[i]);
            bombs.splice(i, 1);
        }
    }

    // --- 火焰逻辑与伤害检测 ---
    for (let i = explosions.length - 1; i >= 0; i--) {
        let exp = explosions[i];
        exp.timer--;
        
        // 检测伤害
        exp.cells.forEach(cell => {
            // 烧玩家
            if (player.alive && player.r === cell.r && player.c === cell.c) {
                player.alive = false;
                endGame(false);
            }
            // 烧怪物
            enemies.forEach(en => {
                let enR = Math.floor((en.y + TILE/2) / TILE);
                let enC = Math.floor((en.x + TILE/2) / TILE);
                if (en.alive && enR === cell.r && enC === cell.c) {
                    en.alive = false;
                }
            });
        });

        if (exp.timer <= 0) explosions.splice(i, 1);
    }

    // 清理死亡怪物并检测胜利
    let aliveEnemiesCount = enemies.filter(e => e.alive).length;
    enemyCountSpan.innerText = aliveEnemiesCount;
    if (aliveEnemiesCount === 0 && player.alive) {
        endGame(true);
    }

    // --- 怪物移动 (简单的网格对齐与随机转向) ---
    enemies.forEach(en => {
        if (!en.alive) return;
        
        en.x += en.dir.x * en.speed;
        en.y += en.dir.y * en.speed;

        // 如果正好对齐在一个网格上
        if (Math.abs(en.x % TILE) < en.speed && Math.abs(en.y % TILE) < en.speed) {
            en.x = Math.round(en.x / TILE) * TILE;
            en.y = Math.round(en.y / TILE) * TILE;
            
            let enR = en.y / TILE;
            let enC = en.x / TILE;
            
            // 找出所有可行走的方向
            let possibleDirs = [];
            const dList = [{x:1,y:0}, {x:-1,y:0}, {x:0,y:1}, {x:0,y:-1}];
            dList.forEach(d => {
                if (map[enR + d.y][enC + d.x] === 0) {
                    possibleDirs.push(d);
                }
            });

            if (possibleDirs.length > 0) {
                // 如果当前方向走不通，或者有一定概率随机转向
                let canGoStraight = map[enR + en.dir.y][enC + en.dir.x] === 0;
                if (!canGoStraight || Math.random() < 0.2) {
                    let randDir = possibleDirs[Math.floor(Math.random() * possibleDirs.length)];
                    en.dir = randDir;
                }
            } else {
                en.dir = {x:0, y:0}; // 被困住了
            }
        }
        
        // 怪物碰到玩家
        if (player.alive && Math.abs(player.x - en.x) < 20 && Math.abs(player.y - en.y) < 20) {
            player.alive = false;
            endGame(false);
        }
    });
}

function endGame(isWin) {
    gameState = 'gameover';
    overlay.style.display = 'flex';
    if (isWin) {
        resultTitle.innerText = "🎉 完美清场！";
        resultMsg.innerText = "太棒了！所有的障碍和烦心事都被你炸飞啦！现在闭上眼睛休息一下吧~";
    } else {
        resultTitle.innerText = "💥 哎呀，失误了！";
        resultMsg.innerText = "没关系，调整呼吸，再来一次！";
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 绘制地图
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            let cx = c * TILE;
            let cy = r * TILE;
            
            if (map[r][c] === 1) { // 坚固墙壁
                ctx.fillStyle = "#8d99ae";
                ctx.fillRect(cx, cy, TILE, TILE);
                ctx.strokeStyle = "#4a4e69";
                ctx.strokeRect(cx, cy, TILE, TILE);
            } else if (map[r][c] === 2) { // 冰块
                ctx.fillStyle = "#ade8f4";
                ctx.fillRect(cx+2, cy+2, TILE-4, TILE-4);
                ctx.fillStyle = "#caf0f8";
                ctx.fillRect(cx+5, cy+5, TILE-10, TILE-10);
            }
        }
    }

    // 绘制炸弹 (暖水袋)
    bombs.forEach(b => {
        let bx = b.c * TILE + TILE/2;
        let by = b.r * TILE + TILE/2;
        
        // 袋子本体
        ctx.fillStyle = "#ef233c";
        ctx.beginPath();
        ctx.roundRect(bx - 12, by - 12, 24, 24, 8);
        ctx.fill();
        
        // 袋子口
        ctx.fillStyle = "#d90429";
        ctx.fillRect(bx - 6, by - 16, 12, 6);
        
        // 倒计时动画提示（闪烁）
        if (b.timer % 20 < 10) {
            ctx.fillStyle = "white";
            ctx.font = "12px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText("暖", bx, by);
        }
    });

    // 绘制爆炸火焰
    explosions.forEach(exp => {
        ctx.fillStyle = "#ffb703"; // 外焰
        exp.cells.forEach(cell => {
            ctx.fillRect(cell.c * TILE + 2, cell.r * TILE + 2, TILE - 4, TILE - 4);
        });
        ctx.fillStyle = "#fb8500"; // 内焰
        exp.cells.forEach(cell => {
            ctx.fillRect(cell.c * TILE + 8, cell.r * TILE + 8, TILE - 16, TILE - 16);
        });
    });

    // 绘制怪物 (大姨妈怪)
    enemies.forEach(en => {
        if (!en.alive) return;
        let ex = en.x + TILE/2;
        let ey = en.y + TILE/2;
        
        ctx.fillStyle = "#e63946"; // 红色
        ctx.beginPath();
        ctx.arc(ex, ey, 14, 0, Math.PI * 2);
        ctx.fill();
        
        // 生气的眼睛
        ctx.fillStyle = "white";
        ctx.fillRect(ex - 8, ey - 6, 6, 6);
        ctx.fillRect(ex + 2, ey - 6, 6, 6);
        ctx.fillStyle = "black";
        ctx.fillRect(ex - 6, ey - 4, 3, 3);
        ctx.fillRect(ex + 4, ey - 4, 3, 3);
        // 愤怒的眉毛
        ctx.beginPath(); ctx.moveTo(ex-9, ey-8); ctx.lineTo(ex-2, ey-6); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(ex+9, ey-8); ctx.lineTo(ex+2, ey-6); ctx.stroke();
    });

    // 绘制玩家 (Q版小粉人)
    if (player.alive) {
        let px = player.x + TILE/2;
        let py = player.y + TILE/2;
        
        ctx.fillStyle = "#ffb5a7"; // 粉色身体
        ctx.beginPath();
        ctx.arc(px, py, player.size/2, 0, Math.PI * 2);
        ctx.fill();
        
        // 蝴蝶结
        ctx.fillStyle = "#d00000";
        ctx.beginPath();
        ctx.moveTo(px, py - 10); ctx.lineTo(px - 8, py - 16); ctx.lineTo(px - 8, py - 6); ctx.fill();
        ctx.beginPath();
        ctx.moveTo(px, py - 10); ctx.lineTo(px + 8, py - 16); ctx.lineTo(px + 8, py - 6); ctx.fill();
        
        // 眼睛
        ctx.fillStyle = "#333";
        ctx.beginPath(); ctx.arc(px - 4, py - 2, 2, 0, Math.PI*2); ctx.fill();
        ctx.beginPath(); ctx.arc(px + 4, py - 2, 2, 0, Math.PI*2); ctx.fill();
    }
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

// 启动游戏
gameLoop();
</script>
"""

components.html(bomberman_html, height=600)

st.write("---")
st.info("🎮 **操作说明**：\n* 使用 **键盘方向键 (← ↑ ↓ →)** 移动。\n* 按下 **空格键 (Space)** 放置“暖水袋”炸弹。\n* 炸弹会在几秒后呈十字形爆炸，可以炸碎冰块和赶走小红怪。\n* ⚠️ 注意：不要被自己的炸弹烧到，也不要碰到小红怪哦！")
