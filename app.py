import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="末日求生：僵尸围城", page_icon="🧟", layout="centered")

st.title("🧟 僵尸围城：极限求生")
st.write("开局一把刀，装备全靠捡！一旦被抓咬即刻死亡，利用走位消灭所有感染者！")

zombie_html = """
<div style="display: flex; justify-content: center; flex-direction: column; align-items: center;">
    <div id="game-ui" style="display: flex; justify-content: space-between; width: 600px; margin-bottom: 10px; font-family: 'Microsoft YaHei', sans-serif; font-size: 1.2em; font-weight: bold; background: #1a1a1a; color: #fff; padding: 10px 20px; border-radius: 5px; border-bottom: 3px solid #e63946;">
        <span style="color: #e63946;">感染者剩余: <span id="zombieCount">30</span></span>
        <span style="color: #ffb703;" id="weaponStatus">武器: 🔪 战术匕首 (∞)</span>
        <span style="color: #52b788;">状态: 存活</span>
    </div>
    <div id="game-container" style="position: relative;">
        <canvas id="gameCanvas" width="600" height="500" style="border: 4px solid #343a40; border-radius: 5px; background: #2b2b2b; box-shadow: 0 10px 20px rgba(0,0,0,0.8); cursor: crosshair;"></canvas>
        <div id="overlay" style="position: absolute; top: 0; left: 0; width: 600px; height: 500px; background: rgba(0,0,0,0.85); display: none; flex-direction: column; justify-content: center; align-items: center; text-align: center; border-radius: 5px;">
            <h1 id="result-title" style="color: #e63946; font-size: 3.5em; margin-bottom: 10px; text-transform: uppercase;">YOU DIED</h1>
            <p id="result-msg" style="color: #aaa; font-size: 1.2em; margin-bottom: 30px;"></p>
            <button onclick="location.reload()" style="padding: 12px 30px; background: #e63946; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1.2em; font-weight: bold; letter-spacing: 2px;">RESTART</button>
        </div>
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const overlay = document.getElementById('overlay');
const resultTitle = document.getElementById('result-title');
const resultMsg = document.getElementById('result-msg');
const zombieCountSpan = document.getElementById('zombieCount');
const weaponStatusSpan = document.getElementById('weaponStatus');

// 游戏全局变量
let gameState = 'countdown';
let countdownNum = 3;
let totalZombies = 30;
let zombiesKilled = 0;
let bloodSplats = []; 
let crates = [ 
    {x: 100, y: 100, w: 60, h: 60}, {x: 440, y: 100, w: 60, h: 60},
    {x: 270, y: 220, w: 60, h: 60}, 
    {x: 100, y: 340, w: 60, h: 60}, {x: 440, y: 340, w: 60, h: 60}
];

const WEAPONS = {
    knife: { name: '🔪 战术匕首', type: 'melee', ammo: Infinity, cooldown: 25, range: 45, spread: 0 },
    shotgun: { name: '💥 霰弹枪', type: 'ranged', ammo: 12, cooldown: 40, speed: 10, life: 15, count: 3, spread: 0.3 },
    smg: { name: '🔫 冲锋枪', type: 'ranged', ammo: 50, cooldown: 6, speed: 12, life: 30, count: 1, spread: 0.05 }
};

let player = {
    x: 300, y: 250, radius: 14, speed: 4,
    dir: 'U', 
    weapon: 'knife', ammo: Infinity, attackTimer: 0,
    slashEffect: 0 
};

let bullets = [];
let zombies = [];
let items = [];

let keys = {};
window.addEventListener('keydown', e => {
    keys[e.code] = true;
    if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)) e.preventDefault();
});
window.addEventListener('keyup', e => keys[e.code] = false);

function spawnZombie() {
    if (zombies.length + zombiesKilled < totalZombies && zombies.length < 8) { 
        let edge = Math.floor(Math.random() * 4);
        let zx, zy;
        if(edge === 0) { zx = Math.random()*600; zy = -20; }
        else if(edge === 1) { zx = Math.random()*600; zy = 520; }
        else if(edge === 2) { zx = -20; zy = Math.random()*500; }
        else { zx = 620; zy = Math.random()*500; }
        
        zombies.push({
            x: zx, y: zy, radius: 14, speed: 1.5 + Math.random()*1.0, 
            hp: 2, 
            wobble: Math.random() * Math.PI * 2 
        });
    }
}

function circleRectCollide(cx, cy, cr, rx, ry, rw, rh) {
    let testX = cx; let testY = cy;
    if (cx < rx) testX = rx; else if (cx > rx + rw) testX = rx + rw;
    if (cy < ry) testY = ry; else if (cy > ry + rh) testY = ry + rh;
    let dist = Math.hypot(cx - testX, cy - testY);
    return dist <= cr;
}

function attack() {
    let wp = WEAPONS[player.weapon];
    if (player.attackTimer > 0) return;
    
    player.attackTimer = wp.cooldown;

    if (wp.type === 'melee') {
        player.slashEffect = 10; 
        let hitBox = {x: player.x, y: player.y, w: wp.range, h: wp.range};
        if(player.dir === 'U') { hitBox.x -= 20; hitBox.y -= wp.range; hitBox.w = 40; }
        if(player.dir === 'D') { hitBox.x -= 20; hitBox.w = 40; }
        if(player.dir === 'L') { hitBox.x -= wp.range; hitBox.y -= 20; hitBox.h = 40; }
        if(player.dir === 'R') { hitBox.y -= 20; hitBox.h = 40; }

        for (let i = zombies.length - 1; i >= 0; i--) {
            let z = zombies[i];
            if (circleRectCollide(z.x, z.y, z.radius, hitBox.x, hitBox.y, hitBox.w, hitBox.h)) {
                killZombie(i);
            }
        }
    } 
    else if (wp.type === 'ranged') {
        if (player.ammo <= 0) return;
        player.ammo--;
        if (player.ammo <= 0) {
            player.weapon = 'knife'; 
            player.ammo = Infinity;
        }
        
        let baseAngle = 0;
        if(player.dir === 'U') baseAngle = -Math.PI/2;
        if(player.dir === 'D') baseAngle = Math.PI/2;
        if(player.dir === 'L') baseAngle = Math.PI;
        if(player.dir === 'R') baseAngle = 0;

        for (let i = 0; i < wp.count; i++) {
            let angle = baseAngle + (Math.random() - 0.5) * wp.spread;
            if(wp.count === 3) angle = baseAngle + (i - 1) * wp.spread; 
            
            bullets.push({
                x: player.x, y: player.y,
                vx: Math.cos(angle) * wp.speed,
                vy: Math.sin(angle) * wp.speed,
                life: wp.life
            });
        }
    }
    
    let ammoStr = player.ammo === Infinity ? '∞' : player.ammo;
    weaponStatusSpan.innerText = `武器: ${WEAPONS[player.weapon].name} (${ammoStr})`;
}

function killZombie(index) {
    let z = zombies[index];
    for(let k=0; k<5; k++) {
        bloodSplats.push({
            x: z.x + (Math.random()-0.5)*20, 
            y: z.y + (Math.random()-0.5)*20, 
            r: 2 + Math.random()*4 
        });
    }
    zombies.splice(index, 1);
    zombiesKilled++;
    zombieCountSpan.innerText = totalZombies - zombiesKilled;
    
    if (Math.random() < 0.15) {
        items.push({
            x: z.x, y: z.y, 
            type: Math.random() > 0.5 ? 'shotgun' : 'smg',
            timer: 500
        });
    }

    if (zombiesKilled >= totalZombies) endGame(true);
}

function update() {
    if (gameState === 'gameover') return;

    // ==========================================
    // 修复点：将玩家的移动逻辑提前到状态判定之前
    // 这样在 countdown (倒计时) 期间也可以移动！
    // ==========================================
    if (player.attackTimer > 0) player.attackTimer--;
    if (player.slashEffect > 0) player.slashEffect--;

    let dx = 0, dy = 0;
    if (keys['ArrowUp']) { dy -= player.speed; player.dir = 'U'; }
    if (keys['ArrowDown']) { dy += player.speed; player.dir = 'D'; }
    if (keys['ArrowLeft']) { dx -= player.speed; player.dir = 'L'; }
    if (keys['ArrowRight']) { dx += player.speed; player.dir = 'R'; }

    // 尝试移动X
    player.x += dx;
    if (player.x < player.radius || player.x > canvas.width - player.radius || 
        crates.some(c => circleRectCollide(player.x, player.y, player.radius, c.x, c.y, c.w, c.h))) {
        player.x -= dx; 
    }
    // 尝试移动Y
    player.y += dy;
    if (player.y < player.radius || player.y > canvas.height - player.radius || 
        crates.some(c => circleRectCollide(player.x, player.y, player.radius, c.x, c.y, c.w, c.h))) {
        player.y -= dy; 
    }

    // 在倒计时期间，允许在屏幕边缘刷新僵尸（增加压迫感），但它们不会动
    spawnZombie();

    // 如果游戏还没正式开始（比如还在倒计时），就退出，不执行射击和僵尸移动逻辑
    if (gameState !== 'playing') return;

    // --- 射击、拾取、子弹与僵尸逻辑 (仅在 playing 状态执行) ---
    if (keys['Space']) attack();

    for (let i = items.length - 1; i >= 0; i--) {
        items[i].timer--;
        if (items[i].timer <= 0) { items.splice(i, 1); continue; }
        if (Math.hypot(player.x - items[i].x, player.y - items[i].y) < player.radius + 15) {
            player.weapon = items[i].type;
            player.ammo = WEAPONS[items[i].type].ammo;
            weaponStatusSpan.innerText = `武器: ${WEAPONS[player.weapon].name} (${player.ammo})`;
            items.splice(i, 1);
        }
    }

    for (let i = bullets.length - 1; i >= 0; i--) {
        let b = bullets[i];
        b.x += b.vx; b.y += b.vy; b.life--;
        
        let hitObstacle = crates.some(c => b.x>c.x && b.x<c.x+c.w && b.y>c.y && b.y<c.y+c.h);
        if (b.life <= 0 || b.x < 0 || b.x > canvas.width || b.y < 0 || b.y > canvas.height || hitObstacle) {
            bullets.splice(i, 1);
            continue;
        }

        let hit = false;
        for (let j = zombies.length - 1; j >= 0; j--) {
            if (Math.hypot(b.x - zombies[j].x, b.y - zombies[j].y) < zombies[j].radius + 3) {
                zombies[j].hp--;
                if(zombies[j].hp <= 0) killZombie(j);
                hit = true; break;
            }
        }
        if (hit) bullets.splice(i, 1);
    }

    for (let i = zombies.length - 1; i >= 0; i--) {
        let z = zombies[i];
        z.wobble += 0.1;
        
        let angle = Math.atan2(player.y - z.y, player.x - z.x);
        let zx = z.x + Math.cos(angle) * z.speed + Math.sin(z.wobble)*0.5;
        let zy = z.y + Math.sin(angle) * z.speed + Math.cos(z.wobble)*0.5;

        for (let j = 0; j < zombies.length; j++) {
            if (i === j) continue;
            let other = zombies[j];
            let dist = Math.hypot(zx - other.x, zy - other.y);
            if (dist < z.radius * 2) {
                zx -= (other.x - zx) * 0.05;
                zy -= (other.y - zy) * 0.05;
            }
        }

        if (!crates.some(c => circleRectCollide(zx, zy, z.radius, c.x, c.y, c.w, c.h))) {
            z.x = zx; z.y = zy;
        } else {
            if(!crates.some(c => circleRectCollide(zx, z.y, z.radius, c.x, c.y, c.w, c.h))) z.x = zx;
            else if(!crates.some(c => circleRectCollide(z.x, zy, z.radius, c.x, c.y, c.w, c.h))) z.y = zy;
        }

        if (Math.hypot(player.x - z.x, player.y - z.y) < player.radius + z.radius - 4) {
            endGame(false);
        }
    }
}

function drawCharacter(x, y, radius, dir, isZombie, wobble) {
    ctx.save();
    ctx.translate(x, y);
    if(dir) {
        if(dir === 'U') ctx.rotate(-Math.PI/2);
        if(dir === 'D') ctx.rotate(Math.PI/2);
        if(dir === 'L') ctx.rotate(Math.PI);
    } else if (isZombie) {
        ctx.rotate(Math.atan2(player.y - y, player.x - x));
    }

    ctx.fillStyle = isZombie ? "#2a9d8f" : "#457b9d";
    ctx.beginPath();
    ctx.ellipse(0, 0, radius, radius*1.5, 0, 0, Math.PI*2);
    ctx.fill();

    ctx.fillStyle = isZombie ? "#4c956c" : "#ffb5a7";
    if (isZombie) {
        let armExt = 10 + Math.sin(wobble)*3;
        ctx.beginPath(); ctx.arc(radius, -8, 4, 0, Math.PI*2); ctx.fill();
        ctx.beginPath(); ctx.arc(radius, 8, 4, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = "#1a1a1a";
        ctx.fillRect(-5, -5, 4, 4);
    } else {
        ctx.beginPath(); ctx.arc(radius, 8, 5, 0, Math.PI*2); ctx.fill();
        if(player.weapon === 'knife') {
            ctx.fillStyle = "#ced4da"; 
            ctx.fillRect(radius, 6, 12, 3);
        } else if(player.weapon === 'shotgun') {
            ctx.fillStyle = "#343a40"; 
            ctx.fillRect(radius-5, 5, 20, 6); 
        } else {
            ctx.fillStyle = "#212529"; 
            ctx.fillRect(radius-2, 6, 16, 4); 
        }
    }

    ctx.fillStyle = isZombie ? "#606c38" : "#ffcdb2";
    ctx.beginPath();
    ctx.arc(0, 0, radius*0.8, 0, Math.PI*2);
    ctx.fill();
    ctx.lineWidth = 1; ctx.strokeStyle = "rgba(0,0,0,0.5)"; ctx.stroke();

    ctx.restore();
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
    ctx.lineWidth = 2;
    for(let i=0; i<600; i+=40) { ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,500); ctx.stroke(); }
    for(let i=0; i<500; i+=40) { ctx.beginPath(); ctx.moveTo(0,i); ctx.lineTo(600,i); ctx.stroke(); }

    ctx.fillStyle = "rgba(138, 3, 3, 0.6)";
    bloodSplats.forEach(s => {
        ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, Math.PI*2); ctx.fill();
    });

    crates.forEach(c => {
        ctx.fillStyle = "#6f4e37";
        ctx.fillRect(c.x, c.y, c.w, c.h);
        ctx.strokeStyle = "#4a3b32"; ctx.lineWidth = 4;
        ctx.strokeRect(c.x+2, c.y+2, c.w-4, c.h-4);
        ctx.beginPath(); ctx.moveTo(c.x, c.y); ctx.lineTo(c.x+c.w, c.y+c.h); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(c.x+c.w, c.y); ctx.lineTo(c.x, c.y+c.h); ctx.stroke();
    });

    items.forEach(it => {
        ctx.fillStyle = it.type === 'shotgun' ? "#fca311" : "#8ecae6";
        ctx.beginPath(); ctx.fillRect(it.x-8, it.y-8, 16, 16);
        ctx.fillStyle = "white"; ctx.font = "10px Arial"; ctx.textAlign="center"; ctx.textBaseline="middle";
        ctx.fillText(it.type === 'shotgun' ? "S" : "M", it.x, it.y);
        if(it.timer % 20 < 10) {
            ctx.strokeStyle = ctx.fillStyle; ctx.lineWidth=2;
            ctx.beginPath(); ctx.arc(it.x, it.y, 14, 0, Math.PI*2); ctx.stroke();
        }
    });

    ctx.fillStyle = "#ffb703";
    bullets.forEach(b => {
        ctx.beginPath(); ctx.arc(b.x, b.y, 3, 0, Math.PI*2); ctx.fill();
    });

    if (player.weapon === 'knife' && player.slashEffect > 0) {
        ctx.strokeStyle = `rgba(255, 255, 255, ${player.slashEffect/10})`;
        ctx.lineWidth = 4;
        ctx.beginPath();
        let r = WEAPONS.knife.range;
        if(player.dir === 'U') { ctx.arc(player.x, player.y, r, Math.PI, 0); }
        if(player.dir === 'D') { ctx.arc(player.x, player.y, r, 0, Math.PI); }
        if(player.dir === 'L') { ctx.arc(player.x, player.y, r, Math.PI/2, Math.PI*1.5); }
        if(player.dir === 'R') { ctx.arc(player.x, player.y, r, -Math.PI/2, Math.PI/2); }
        ctx.stroke();
    }

    zombies.forEach(z => drawCharacter(z.x, z.y, z.radius, null, true, z.wobble));
    drawCharacter(player.x, player.y, player.radius, player.dir, false, 0);

    if (gameState === 'countdown') {
        ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
        ctx.fillRect(0,0,canvas.width, canvas.height);
        ctx.fillStyle = "#e63946";
        ctx.font = "bold 80px 'Impact', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(countdownNum > 0 ? countdownNum : "SURVIVE!", canvas.width/2, canvas.height/2 + 25);
    }
}

function endGame(isWin) {
    gameState = 'gameover';
    overlay.style.display = 'flex';
    if (isWin) {
        resultTitle.innerText = "AREA CLEARED";
        resultTitle.style.color = "#52b788";
        resultMsg.innerText = "你成功清剿了所有的感染者，活了下来！";
    } else {
        resultTitle.innerText = "YOU DIED";
        resultTitle.style.color = "#e63946";
        resultMsg.innerText = "你被感染者包围了。下一次注意拉开距离走位！";
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

// 提前生成几只僵尸在边缘，增加开局压迫感
for(let i=0; i<4; i++) spawnZombie();

startCountdown();
gameLoop();
</script>
"""

components.html(zombie_html, height=600)
