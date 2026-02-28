class Game2048 {
    constructor() {
        this.grid = [];
        this.score = 0;
        this.highScore = parseInt(localStorage.getItem('highScore')) || 0;
        this.gameOver = false;
        
        this.init();
        this.setupEventListeners();
    }

    init() {
        // 初始化 4x4 网格
        this.grid = Array(4).fill(null).map(() => Array(4).fill(0));
        this.score = 0;
        this.gameOver = false;
        
        // 添加两个初始方块
        this.addRandomTile();
        this.addRandomTile();
        
        this.render();
        this.updateScore();
    }

    setupEventListeners() {
        // 键盘事件
        document.addEventListener('keydown', (e) => {
            if (this.gameOver) return;
            
            switch(e.key) {
                case 'ArrowUp':
                    e.preventDefault();
                    this.move('up');
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    this.move('down');
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    this.move('left');
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.move('right');
                    break;
            }
        });

        // 新游戏按钮
        document.getElementById('new-game-btn').addEventListener('click', () => {
            this.init();
            document.getElementById('game-over').classList.add('hidden');
        });

        // 重新开始按钮
        document.getElementById('restart-btn').addEventListener('click', () => {
            this.init();
            document.getElementById('game-over').classList.add('hidden');
        });

        // 触摸支持
        let touchStartX = 0;
        let touchStartY = 0;
        
        document.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            if (this.gameOver) return;
            
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            
            const dx = touchEndX - touchStartX;
            const dy = touchEndY - touchStartY;
            
            const absDx = Math.abs(dx);
            const absDy = Math.abs(dy);
            
            if (Math.max(absDx, absDy) > 30) {
                if (absDx > absDy) {
                    this.move(dx > 0 ? 'right' : 'left');
                } else {
                    this.move(dy > 0 ? 'down' : 'up');
                }
            }
        });
    }

    addRandomTile() {
        const emptyCells = [];
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                if (this.grid[i][j] === 0) {
                    emptyCells.push({row: i, col: j});
                }
            }
        }
        
        if (emptyCells.length > 0) {
            const {row, col} = emptyCells[Math.floor(Math.random() * emptyCells.length)];
            this.grid[row][col] = Math.random() < 0.9 ? 2 : 4;
        }
    }

    move(direction) {
        const oldGrid = JSON.stringify(this.grid);
        
        switch(direction) {
            case 'up':
                this.moveUp();
                break;
            case 'down':
                this.moveDown();
                break;
            case 'left':
                this.moveLeft();
                break;
            case 'right':
                this.moveRight();
                break;
        }
        
        // 如果网格发生了变化
        if (oldGrid !== JSON.stringify(this.grid)) {
            this.addRandomTile();
            this.render();
            this.updateScore();
            
            // 检查游戏是否结束
            if (this.isGameOver()) {
                this.gameOver = true;
                this.showGameOver();
            }
        }
    }

    moveLeft() {
        for (let i = 0; i < 4; i++) {
            let row = this.grid[i].filter(val => val !== 0);
            
            // 合并相同的方块
            for (let j = 0; j < row.length - 1; j++) {
                if (row[j] === row[j + 1]) {
                    row[j] *= 2;
                    this.score += row[j];
                    row.splice(j + 1, 1);
                }
            }
            
            // 填充空位
            while (row.length < 4) {
                row.push(0);
            }
            
            this.grid[i] = row;
        }
    }

    moveRight() {
        for (let i = 0; i < 4; i++) {
            let row = this.grid[i].filter(val => val !== 0);
            
            // 合并相同的方块（从右向左）
            for (let j = row.length - 1; j > 0; j--) {
                if (row[j] === row[j - 1]) {
                    row[j] *= 2;
                    this.score += row[j];
                    row.splice(j - 1, 1);
                }
            }
            
            // 填充空位
            while (row.length < 4) {
                row.unshift(0);
            }
            
            this.grid[i] = row;
        }
    }

    moveUp() {
        // 转置 -> 向左移动 -> 转置回来
        this.transpose();
        this.moveLeft();
        this.transpose();
    }

    moveDown() {
        // 转置 -> 向右移动 -> 转置回来
        this.transpose();
        this.moveRight();
        this.transpose();
    }

    transpose() {
        const newGrid = [];
        for (let i = 0; i < 4; i++) {
            newGrid[i] = [];
            for (let j = 0; j < 4; j++) {
                newGrid[i][j] = this.grid[j][i];
            }
        }
        this.grid = newGrid;
    }

    isGameOver() {
        // 检查是否有空格
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                if (this.grid[i][j] === 0) return false;
            }
        }
        
        // 检查是否可以合并
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 3; j++) {
                if (this.grid[i][j] === this.grid[i][j + 1]) return false;
            }
        }
        
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 4; j++) {
                if (this.grid[i][j] === this.grid[i + 1][j]) return false;
            }
        }
        
        return true;
    }

    showGameOver() {
        document.getElementById('final-score').textContent = this.score;
        document.getElementById('game-over').classList.remove('hidden');
    }

    updateScore() {
        document.getElementById('current-score').textContent = this.score;
        
        if (this.score > this.highScore) {
            this.highScore = this.score;
            localStorage.setItem('highScore', this.highScore);
        }
        
        document.getElementById('high-score').textContent = this.highScore;
    }

    render() {
        const gridElement = document.getElementById('grid');
        gridElement.innerHTML = '';
        
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                const tile = document.createElement('div');
                tile.className = 'tile';
                
                const value = this.grid[i][j];
                if (value !== 0) {
                    tile.textContent = value;
                    tile.setAttribute('data-value', value);
                }
                
                gridElement.appendChild(tile);
            }
        }
    }
}

// 启动游戏
const game = new Game2048();
