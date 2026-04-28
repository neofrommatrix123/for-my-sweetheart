import streamlit as st
import streamlit.components.v1 as components

# 设置页面
st.set_page_config(page_title="小仙女守护计划 2.0", page_icon="💖", layout="centered")

# 自定义 CSS 美化 Streamlit 原生组件
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #fff5f8 0%, #ffe3ec 100%);
    }
    h1 {
        color: #ff4d6d;
        font-family: 'Microsoft YaHei', sans-serif;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .stMarkdown {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💖 守护小仙女：击退姨妈大作战")
st.write("避开那些烦人的‘紫乌龟’，跳上云端，去找门后等你的那个拥抱吧！")

# 核心游戏组件
game_html = """
<div style="display: flex; flex-direction: column; align-items: center; gap: 10px;">
    <canvas id="gameCanvas" width="600" height="400" style="border:5px solid #ff8fa3; border-radius:20px; background: #87CEEB; box-shadow: 0 10px 30px rgba(0,0,0,0.1);"></canvas>
    <div id="status" style="color: #ff4d6d; font-weight: bold; font-size: 1.2em; height: 30px;"></div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const statusDiv = document.getElementById('status');

// 游戏状态
let gameState = 'playing'; // playing, win
let alpha = 0; // 用于最后的渐变动画

// 玩家设置
let player = {
    x: 50, y: 300, width: 35, height: 35,
    dx: 0, dy: 0, 
    speed: 5, jumpPower: -12, 
    gravity: 0.6, grounded: false
};

// 平台设置 (x, y, width, height)
let platforms = [
    { x: 0, y: 370, w: 600, h: 30 },   // 地面
    { x: 150, y: 280, w: 120, h: 20 }, // 平台1
    { x: 350, y: 200, w: 120, h: 20 }, // 平台2
    { x: 100, y: 150, w: 100, h: 20 }, // 平台3
    { x: 480, y: 120, w: 120, h: 20 }  // 终点平台
];

// 敌人设置 (紫色小乌龟)
let enemies = [
    { x: 160, y: 250, w: 30, h: 30, range: 100, startX: 160, dir: 1, speed: 2 },
    { x: 360, y: 170, w: 30, h: 30, range: 80, startX: 360, dir: 1, speed: 3 }
];

// 终点门
let door = { x: 540, y: 70, w: 40, h: 50 };

let keys = {};
window.addEventListener('keydown', e => {
    keys[e.code] = true;
    if(['Space', 'ArrowUp', 'ArrowDown'].includes(e.code)) e.preventDefault();
});
window.addEventListener('keyup', e => keys[e.code] = false);

function update() {
    if (gameState === 'playing') {
        // 左右移动
        if (keys['ArrowLeft']) player.x -= player.speed;
        if (keys['ArrowRight']) player.x += player.speed;
        
        // 跳跃
        if ((keys['Space'] || keys['ArrowUp']) && player.grounded) {
            player.dy = player.jumpPower;
            player.grounded = false;
        }

        // 重力
        player.dy += player.gravity;
        player.y += player.dy;
        player.grounded = false;

        // 碰撞检测：平台
        platforms.forEach(p => {
            if (player.x < p.x + p.w && player.x + player.width > p.x &&
                player.y < p.y + p.h && player.y + player.height > p.y) {
                if (player.dy > 0 && player.y + player.height - player.dy <= p.y) {
                    player.y = p.y - player.height;
                    player.dy = 0;
                    player.grounded = true;
                }
            }
        });

        // 敌人移动与检测
        enemies.forEach(en => {
            en.x += en.dir * en.speed;
            if (Math.abs(en.x - en.startX) > en.range) en.dir *= -1;

            if (Math.abs(player.x - en.x) < 25 && Math.abs(player.y - en.y) < 25) {
                player.x = 50; player.y = 300; // 回到起点
                statusDiv.innerText = "哎呀，被姨妈痛抓住了！加油！";
                setTimeout(() => { statusDiv.innerText = ""; }, 2000);
            }
        });

        // 边界限制
        if (player.x < 0) player.x = 0;
        if (player.x > 565) player.x = 565;

        // 检测开门
        if (player.x + player.width > door.x && player.y < door.y + door.h && player.y + player.height > door.y) {
            gameState = 'transition';
        }
    }
    draw();
    requestAnimationFrame(update);
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 画云朵背景
    ctx.fillStyle = "white";
    ctx.beginPath(); ctx.arc(100, 80, 30, 0, Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.arc(130, 80, 40, 0, Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.arc(400, 50, 25, 0, Math.PI*2); ctx.fill();

    // 画平台
    ctx.fillStyle = "#ffafcc";
    platforms.forEach(p => {
        ctx.fillRect(p.x, p.y, p.w, p.h);
        ctx.strokeStyle = "#ff8fa3";
        ctx.strokeRect(p.x, p.y, p.w, p.h);
    });

    // 画紫色乌龟 (简易版)
    enemies.forEach(en => {
        ctx.fillStyle = "#9d4edd"; // 紫色
        ctx.beginPath();
        ctx.arc(en.x + 15, en.y + 15, 15, Math.PI, 0); // 龟壳
        ctx.fill();
        ctx.fillStyle = "#7b2cbf";
        ctx.fillRect(en.x + 5, en.y + 15, 20, 10); // 身体
    });

    // 画门
    ctx.fillStyle = "#8d4925"; // 门框
    ctx.fillRect(door.x, door.y, door.w, door.h);
    ctx.fillStyle = "#b5651d"; // 门面
    ctx.fillRect(door.x+5, door.y+5, door.w-10, door.h-5);
    ctx.fillStyle = "yellow"; // 门把手
    ctx.beginPath(); ctx.arc(door.x + 10, door.y + 30, 3, 0, Math.PI*2); ctx.fill();

    // 画玩家 (带蝴蝶结的小红人)
    ctx.fillStyle = "#ff4d6d";
    ctx.fillRect(player.x, player.y, player.width, player.height);
    ctx.fillStyle = "white";
    ctx.fillRect(player.x + 5, player.y + 8, 8, 8); // 眼1
    ctx.fillRect(player.x + 22, player.y + 8, 8, 8); // 眼2
    ctx.fillStyle = "black";
    ctx.fillRect(player.x + 8, player.y + 11, 3, 3); 
    ctx.fillRect(player.x + 25, player.y + 11, 3, 3);
    // 蝴蝶结
    ctx.fillStyle = "#ff0000";
    ctx.beginPath();
    ctx.moveTo(player.x, player.y); ctx.lineTo(player.x-10, player.y-10); ctx.lineTo(player.x, player.y-10); ctx.fill();
    ctx.beginPath();
    ctx.moveTo(player.x+player.width, player.y); ctx.lineTo(player.x+player.width+10, player.y-10); ctx.lineTo(player.x+player.width, player.y-10); ctx.fill();

    // 结局转场动画
    if (gameState === 'transition') {
        alpha += 0.02;
        ctx.fillStyle = `rgba(255, 245, 248, ${alpha})`;
        ctx.fillRect(0, 0, 600, 400);
        if (alpha >= 1) gameState = 'win';
    }

    if (gameState === 'win') {
        ctx.fillStyle = "#fff5f8";
        ctx.fillRect(0, 0, 600, 400);
        
        // 画出拥抱的场景 (简易插画)
        ctx.textAlign = "center";
        ctx.fillStyle = "#ff4d6d";
        ctx.font = "bold 30px Arial";
        ctx.fillText("你推开了那扇门...", 300, 100);
        
        // 男朋友形象 (简笔画)
        ctx.lineWidth = 5;
        ctx.strokeStyle = "#4361ee"; // 蓝色代表男朋友
        ctx.beginPath();
        ctx.arc(300, 180, 25, 0, Math.PI*2); // 头
        ctx.moveTo(300, 205); ctx.lineTo(300, 280); // 身体
        // 张开的双臂
        ctx.moveTo(300, 220); ctx.lineTo(250, 190); 
        ctx.moveTo(300, 220); ctx.lineTo(350, 190);
        ctx.stroke();

        ctx.font = "24px Arial";
        ctx.fillText("❤️ 男朋友在这里给你一个大大的拥抱 ❤️", 300, 340);
        ctx.font = "18px Arial";
        ctx.fillStyle = "#666";
        ctx.fillText("“辛苦啦，小仙女，我会一直陪着你的。”", 300, 370);
    }
}

update();
</script>
"""

components.html(game_html, height=480)

st.write("---")
st.caption("操作说明：键盘左右键移动，空格或上方向键跳跃。")
