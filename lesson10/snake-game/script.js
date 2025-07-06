// --- 游戏配置常量 ---
const CANVAS_WIDTH = 400;
const CANVAS_HEIGHT = 400;
const CELL_SIZE = 20; // 每个单元格20x20像素

const BOARD_COLS = CANVAS_WIDTH / CELL_SIZE;
const BOARD_ROWS = CANVAS_HEIGHT / CELL_SIZE;

const INITIAL_SNAKE_LENGTH = 3; // 初始蛇长
const INITIAL_GAME_SPEED = 150; // 初始游戏速度 (毫秒/帧)
const SPEED_INCREASE_THRESHOLD = 50; // 每增加50分加速
const SPEED_INCREASE_PERCENTAGE = 0.9; // 每次加速到当前速度的90% (即加快10%)
const MAX_GAME_SPEED = 50; // 最快速度 (毫秒/帧)

// --- 游戏状态枚举 ---
const GAME_STATE = {
    INITIAL: 'INITIAL',
    RUNNING: 'RUNNING',
    PAUSED: 'PAUSED',
    GAME_OVER: 'GAME_OVER'
};

// --- 颜色定义 ---
const COLORS = {
    BOARD_BACKGROUND: '#1a1e24',
    BOARD_BORDER: '#61dafb',
    SNAKE_HEAD: '#4CAF50', // 绿色
    SNAKE_BODY: '#8BC34A', // 浅绿色
    FOOD: '#FFC107', // 橙色
    TEXT_NORMAL: '#f0f0f0',
    TEXT_WARNING: '#FF5722'
};

// --- 游戏变量 ---
let canvas;
let ctx;
let snake;
let food;
let direction; // 当前蛇的移动方向
let nextDirection; // 下一个方向，用于防止180度反转和快速按键
let score;
let gameIntervalId; // setInterval的ID，用于清除
let currentSpeed;
let gameState;

// --- 获取DOM元素 ---
const scoreDisplay = document.getElementById('score');
const gameStatusMessage = document.getElementById('gameStatusMessage');

// --- 初始化游戏 ---
function init() {
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');

    // 绑定键盘事件
    document.addEventListener('keydown', handleKeyPress);

    resetGame(); // 首次加载时重置游戏到初始状态
}

// --- 绘制单元格 ---
function drawRect(x, y, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
    ctx.strokeStyle = COLORS.BOARD_BACKGROUND; // 绘制网格线
    ctx.strokeRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
}

// --- 绘制游戏板 ---
function drawBoard() {
    ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT); // 清空画布
    // 背景色在CSS中设置，这里主要用于绘制网格线
    for (let x = 0; x < BOARD_COLS; x++) {
        for (let y = 0; y < BOARD_ROWS; y++) {
            // 可以选择性绘制网格背景
            // drawRect(x, y, COLORS.BOARD_BACKGROUND);
        }
    }
}

// --- 绘制蛇 ---
function drawSnake() {
    for (let i = 0; i < snake.length; i++) {
        const segment = snake[i];
        const color = (i === 0) ? COLORS.SNAKE_HEAD : COLORS.SNAKE_BODY; // 区分蛇头和蛇身
        drawRect(segment.x, segment.y, color);
    }
}

// --- 绘制食物 ---
function drawFood() {
    drawRect(food.x, food.y, COLORS.FOOD);
}

// --- 更新分数显示 ---
function updateScoreDisplay() {
    scoreDisplay.textContent = score;
}

// --- 更新游戏状态消息 ---
function updateGameStatusMessage(message, color = COLORS.TEXT_NORMAL) {
    gameStatusMessage.textContent = message;
    gameStatusMessage.style.color = color;
}

// --- 生成食物 ---
function generateFood() {
    let newFoodX, newFoodY;
    let collisionWithSnake;
    do {
        newFoodX = Math.floor(Math.random() * BOARD_COLS);
        newFoodY = Math.floor(Math.random() * BOARD_ROWS);
        collisionWithSnake = snake.some(segment => segment.x === newFoodX && segment.y === newFoodY);
    } while (collisionWithSnake); // 确保食物不生成在蛇身上

    food = { x: newFoodX, y: newFoodY };
}

// --- 检查碰撞 ---
function checkCollision() {
    const head = snake[0];

    // FR.004.1 撞墙
    if (head.x < 0 || head.x >= BOARD_COLS || head.y < 0 || head.y >= BOARD_ROWS) {
        return 'wall';
    }

    // FR.004.2 撞自身 (从蛇的第二节开始检查，即蛇头不能撞到除了紧随其后的第一节之外的任何身体部分)
    // 蛇头移动到新位置后，snake[1]是旧的蛇头位置。
    // 如果蛇头撞到自身，它必须撞到snake[2]或更后面的节。
    for (let i = 1; i < snake.length; i++) {
        if (head.x === snake[i].x && head.y === snake[i].y) {
            // 排除紧随其后的一个身体节（即当前snake[1]，它在逻辑上是蛇头刚刚离开的位置）
            // 实际上，由于nextDirection的180度反转限制，蛇头不会立即撞到snake[1]，
            // 因此这个循环从i=1开始检查是安全的，它会正确捕获蛇头撞到任何其他身体部分的情况。
            // 简单来说，如果蛇头的新位置与蛇的任何一个身体节（包括旧头位置）重合，就视为碰撞。
            // 但如果蛇长为1或2，它不可能撞到自己。
            if (snake.length > 2 && i > 0) { // 蛇长大于2且不是蛇头本身
                return 'self';
            }
        }
    }

    // FR.004.3 吃到食物
    if (head.x === food.x && head.y === food.y) {
        return 'food';
    }

    return 'none';
}

// --- 调整游戏速度 ---
function adjustSpeed() {
    // 每当分数达到特定阈值，游戏刷新频率加快
    // 检查是否达到加速点 (例如：50, 100, 150分...)
    if (score > 0 && score % SPEED_INCREASE_THRESHOLD === 0) {
        const newSpeed = currentSpeed * SPEED_INCREASE_PERCENTAGE;
        currentSpeed = Math.max(newSpeed, MAX_GAME_SPEED); // 确保不低于最小速度

        // 清除旧的定时器并设置新的
        clearInterval(gameIntervalId);
        gameIntervalId = setInterval(gameLoop, currentSpeed);
    }
}

// --- 游戏循环 ---
function gameLoop() {
    if (gameState !== GAME_STATE.RUNNING) {
        return;
    }

    // 更新方向，防止180度反转
    if (nextDirection) {
        const currentX = direction === 'left' ? 1 : (direction === 'right' ? -1 : 0);
        const currentY = direction === 'up' ? 1 : (direction === 'down' ? -1 : 0);
        const nextX = nextDirection === 'left' ? -1 : (nextDirection === 'right' ? 1 : 0);
        const nextY = nextDirection === 'up' ? -1 : (nextDirection === 'down' ? 1 : 0);

        // 如果新方向与当前方向相反，则不改变
        if (currentX + nextX !== 0 || currentY + nextY !== 0) {
            direction = nextDirection;
        }
        nextDirection = null; // 清除待处理方向
    }

    // 计算新的蛇头位置
    const head = { x: snake[0].x, y: snake[0].y };
    switch (direction) {
        case 'up':
            head.y--;
            break;
        case 'down':
            head.y++;
            break;
        case 'left':
            head.x--;
            break;
        case 'right':
            head.x++;
            break;
    }

    snake.unshift(head); // 将新蛇头添加到蛇数组的开头

    const collisionType = checkCollision();

    if (collisionType === 'food') {
        score += 10; // FR.014 计分
        updateScoreDisplay();
        generateFood(); // 生成新食物
        adjustSpeed(); // FR.015 难度递增
    } else if (collisionType === 'wall' || collisionType === 'self') {
        endGame(); // 游戏结束
        return;
    } else {
        snake.pop(); // 移除蛇尾，使蛇移动但长度不变
    }

    // 重新绘制所有元素
    drawBoard();
    drawFood();
    drawSnake();
}

// --- 键盘事件处理 ---
function handleKeyPress(event) {
    // 限制方向键的响应频率，防止在一个游戏周期内多次改变方向
    // 并且只在游戏运行时或初始状态接受方向键输入
    if (gameState === GAME_STATE.RUNNING || gameState === GAME_STATE.INITIAL) {
        const oldDirection = direction; // 记录旧方向，防止方向键连按导致的问题

        switch (event.key) {
            case 'ArrowUp':
            case 'w':
            case 'W':
                if (oldDirection !== 'down') nextDirection = 'up';
                break;
            case 'ArrowDown':
            case 's':
            case 'S':
                if (oldDirection !== 'up') nextDirection = 'down';
                break;
            case 'ArrowLeft':
            case 'a':
            case 'A':
                if (oldDirection !== 'right') nextDirection = 'left';
                break;
            case 'ArrowRight':
            case 'd':
            case 'D':
                if (oldDirection !== 'left') nextDirection = 'right';
                break;
        }
    }

    // FR.012 游戏开始/暂停/恢复
    if (event.key === ' ' || event.key === 'Spacebar') {
        event.preventDefault(); // 阻止空格键滚动页面
        if (gameState === GAME_STATE.INITIAL) {
            startGame();
        } else if (gameState === GAME_STATE.RUNNING) {
            pauseGame();
        } else if (gameState === GAME_STATE.PAUSED) {
            resumeGame();
        }
    }

    // FR.013 重新开始游戏
    if ((event.key === 'r' || event.key === 'R') && gameState === GAME_STATE.GAME_OVER) {
        resetGame();
    }
}

// --- 游戏状态管理函数 ---
function startGame() {
    if (gameState === GAME_STATE.INITIAL || gameState === GAME_STATE.PAUSED) {
        gameState = GAME_STATE.RUNNING;
        updateGameStatusMessage('游戏进行中...');
        if (!gameIntervalId) { // 避免重复设置interval
            gameIntervalId = setInterval(gameLoop, currentSpeed);
        }
    }
}

function pauseGame() {
    if (gameState === GAME_STATE.RUNNING) {
        gameState = GAME_STATE.PAUSED;
        clearInterval(gameIntervalId);
        gameIntervalId = null;
        updateGameStatusMessage('游戏暂停 (按空格键继续)', COLORS.TEXT_WARNING);
    }
}

function resumeGame() {
    if (gameState === GAME_STATE.PAUSED) {
        startGame(); // 重新开始计时器
    }
}

function endGame() {
    gameState = GAME_STATE.GAME_OVER;
    clearInterval(gameIntervalId);
    gameIntervalId = null;
    updateGameStatusMessage(`游戏结束！您的分数是: ${score} (按R键重新开始)`, COLORS.TEXT_WARNING);
}

function resetGame() {
    snake = [];
    // 初始蛇的位置在中央附近，方向向右
    for (let i = 0; i < INITIAL_SNAKE_LENGTH; i++) {
        snake.push({
            x: Math.floor(BOARD_COLS / 2) - i, // 从中心向左延伸
            y: Math.floor(BOARD_ROWS / 2)
        });
    }
    direction = 'right';
    nextDirection = null; // 重置待处理方向
    score = 0;
    currentSpeed = INITIAL_GAME_SPEED;

    clearInterval(gameIntervalId); // 清除任何可能存在的旧定时器
    gameIntervalId = null; // 确保定时器ID被重置

    generateFood();
    updateScoreDisplay();
    updateGameStatusMessage('按空格键开始游戏');
    drawBoard();
    drawFood();
    drawSnake();

    gameState = GAME_STATE.INITIAL;
}

// --- 页面加载完成后初始化游戏 ---
window.onload = init;