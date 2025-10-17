<div align="center">

<!-- Game of Life Animation -->
<canvas id="gol-canvas" width="800" height="480" style="border: 2px solid #30363d; border-radius: 6px; background-color: #0d1117; display: block; margin: 20px auto;"></canvas>

<div id="gol-intro" style="position: absolute; text-align: center; color: #e6e6e6; margin-top: -240px; font-family: 'Monaco', 'Courier New', monospace; font-size: 32px; line-height: 1.6; letter-spacing: 3px; text-shadow: 0 0 20px rgba(0, 0, 0, 1), 0 0 40px rgba(0, 0, 0, 0.9), 2px 2px 4px rgba(0, 0, 0, 1); width: 100%; font-weight: bold; pointer-events: none;">
  <div style="color: #3fb950; font-size: 40px; margin-bottom: 8px; text-shadow: 0 0 30px rgba(63, 185, 80, 0.4), 0 0 20px rgba(0, 0, 0, 1), 2px 2px 6px rgba(0, 0, 0, 1);">hi there ! i'm andrew</div>
  <div style="color: #3fb950; font-size: 22px; text-shadow: 0 0 20px rgba(63, 185, 80, 0.3), 0 0 15px rgba(0, 0, 0, 1), 1px 1px 3px rgba(0, 0, 0, 1);">(0.1x dev)</div>
</div>

<script>

(function() {
  class GameOfLife {
    constructor(width, height) {
      this.width = width;
      this.height = height;
      this.cells = new Uint8Array(width * height);
      this.nextCells = new Uint8Array(width * height);
      this.initializeRandom();
    }

    initializeRandom() {
      for (let i = 0; i < this.cells.length; i++) {
        this.cells[i] = Math.random() > 0.7 ? 1 : 0;
      }
    }

    getCell(x, y) {
      x = ((x % this.width) + this.width) % this.width;
      y = ((y % this.height) + this.height) % this.height;
      return this.cells[y * this.width + x];
    }

    setCell(x, y, state) {
      x = ((x % this.width) + this.width) % this.width;
      y = ((y % this.height) + this.height) % this.height;
      this.cells[y * this.width + x] = state ? 1 : 0;
    }

    countNeighbors(x, y) {
      let count = 0;
      for (let dx = -1; dx <= 1; dx++) {
        for (let dy = -1; dy <= 1; dy++) {
          if (dx === 0 && dy === 0) continue;
          count += this.getCell(x + dx, y + dy);
        }
      }
      return count;
    }

    step() {
      for (let y = 0; y < this.height; y++) {
        for (let x = 0; x < this.width; x++) {
          const neighbors = this.countNeighbors(x, y);
          const cell = this.getCell(x, y);
          let newState = 0;

          if (cell === 1 && (neighbors === 2 || neighbors === 3)) {
            newState = 1;
          } else if (cell === 0 && neighbors === 3) {
            newState = 1;
          }

          this.nextCells[y * this.width + x] = newState;
        }
      }

      // Record changes before swapping
      this.recordChanges();
      [this.cells, this.nextCells] = [this.nextCells, this.cells];
    }

    getChangedCells() {
      const changed = [];
      for (let i = 0; i < this.cells.length; i++) {
        if (this.cells[i] !== this.nextCells[i]) {
          changed.push(i);
        }
      }
      return changed;
    }

    recordChanges() {
      this.changedIndices = [];
      for (let i = 0; i < this.cells.length; i++) {
        if (this.cells[i] !== this.nextCells[i]) {
          this.changedIndices.push(i);
        }
      }
    }

    getRecordedChanges() {
      return this.changedIndices || [];
    }
  }

  const canvas = document.getElementById('gol-canvas');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const CELL_SIZE = 8;
  const GRID_WIDTH = Math.floor(canvas.width / CELL_SIZE);
  const GRID_HEIGHT = Math.floor(canvas.height / CELL_SIZE);

  const gameOfLife = new GameOfLife(GRID_WIDTH, GRID_HEIGHT);

  // Cache canvas rect for mousemove events
  let cachedRect = canvas.getBoundingClientRect();
  let lastMouseX = -1;
  let lastMouseY = -1;

  // Store dead zone bounds for reference
  const deadZoneStartY = Math.floor(GRID_HEIGHT * 2 / 5);
  const deadZoneEndY = Math.floor(GRID_HEIGHT * 7 / 8);

  // Handle canvas mouse movement to draw cells with throttling
  // Hover works everywhere, including the dead zone
  canvas.addEventListener('mousemove', (event) => {
    const x = Math.floor((event.clientX - cachedRect.left) / CELL_SIZE);
    const y = Math.floor((event.clientY - cachedRect.top) / CELL_SIZE);
    
    // Only update if mouse moved to a new cell
    if ((x !== lastMouseX || y !== lastMouseY) && x >= 0 && x < GRID_WIDTH && y >= 0 && y < GRID_HEIGHT) {
      gameOfLife.setCell(x, y, 1);
      lastMouseX = x;
      lastMouseY = y;
    }
  });

  // Update cached rect on window resize
  window.addEventListener('resize', () => {
    cachedRect = canvas.getBoundingClientRect();
  });

  // Create a "dead zone" from 2/5 down to 7/8 down (initialization only)
  for (let y = deadZoneStartY; y < deadZoneEndY; y++) {
    for (let x = 0; x < GRID_WIDTH; x++) {
      if (x >= 0 && x < GRID_WIDTH && y >= 0 && y < GRID_HEIGHT) {
        gameOfLife.setCell(x, y, 0);
      }
    }
  }

  const ALIVE_COLOR = '#043873ff';
  const DEAD_COLOR = '#0d1117';
  let changedCells = [];
  let needsFullRedraw = true;

  function render() {
    // Full redraw on first render or when too many cells changed
    if (needsFullRedraw || changedCells.length > GRID_WIDTH * GRID_HEIGHT * 0.1) {
      ctx.fillStyle = DEAD_COLOR;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = ALIVE_COLOR;
      for (let y = 0; y < GRID_HEIGHT; y++) {
        for (let x = 0; x < GRID_WIDTH; x++) {
          if (gameOfLife.cells[y * GRID_WIDTH + x] === 1) {
            ctx.fillRect(
              x * CELL_SIZE,
              y * CELL_SIZE,
              CELL_SIZE - 1,
              CELL_SIZE - 1
            );
          }
        }
      }
      needsFullRedraw = false;
    } else {
      // Dirty rect rendering - only redraw changed cells
      for (let idx of changedCells) {
        const y = Math.floor(idx / GRID_WIDTH);
        const x = idx % GRID_WIDTH;
        
        ctx.fillStyle = gameOfLife.cells[idx] === 1 ? ALIVE_COLOR : DEAD_COLOR;
        ctx.fillRect(
          x * CELL_SIZE,
          y * CELL_SIZE,
          CELL_SIZE - 1,
          CELL_SIZE - 1
        );
      }
    }
    changedCells = [];
  }

  function renderDirty(changedIndices) {
    // Redraw only changed cells
    for (let idx of changedIndices) {
      const y = Math.floor(idx / GRID_WIDTH);
      const x = idx % GRID_WIDTH;
      
      ctx.fillStyle = gameOfLife.cells[idx] === 1 ? ALIVE_COLOR : DEAD_COLOR;
      ctx.fillRect(
        x * CELL_SIZE,
        y * CELL_SIZE,
        CELL_SIZE - 1,
        CELL_SIZE - 1
      );
    }
  }

  let lastUpdateTime = 0;
  let UPDATE_INTERVAL = 1000 / 8; // Start at 8 updates per second
  const MIN_UPDATE_INTERVAL = 1000 / 5; // Minimum 5 updates per second
  const MAX_UPDATE_INTERVAL = 1000 / 15; // Maximum 8 updates per second
  
  let frameCount = 0;
  let frameTimeSum = 0;
  let lastAdaptiveCheck = 0;
  const ADAPTIVE_CHECK_INTERVAL = 1000; // Check every 1 second

  function gameLoop(currentTime) {
    const frameStartTime = performance.now();
    
    if (currentTime - lastUpdateTime >= UPDATE_INTERVAL) {
      gameOfLife.step();
      // Collect changed cells for dirty rect rendering
      changedCells = gameOfLife.getRecordedChanges();
      // Also track user-drawn cells by marking dead zone area as changed
      lastUpdateTime = currentTime;
    }
    render();
    
    // Adaptive frame rate adjustment
    const frameTime = performance.now() - frameStartTime;
    frameTimeSum += frameTime;
    frameCount++;
    
    if (currentTime - lastAdaptiveCheck >= ADAPTIVE_CHECK_INTERVAL) {
      const avgFrameTime = frameTimeSum / frameCount;
      const targetFrameTime = 16.67; // 60fps target
      
      // If we're taking too long per frame, lower the update interval
      if (avgFrameTime > targetFrameTime * 1.5) {
        UPDATE_INTERVAL = Math.min(UPDATE_INTERVAL * 1.2, MIN_UPDATE_INTERVAL);
      }
      // If we have plenty of headroom, we could increase (but keep conservative)
      else if (avgFrameTime < targetFrameTime * 0.7 && UPDATE_INTERVAL > MAX_UPDATE_INTERVAL * 0.8) {
        UPDATE_INTERVAL = Math.max(UPDATE_INTERVAL * 0.95, MAX_UPDATE_INTERVAL);
      }
      
      frameCount = 0;
      frameTimeSum = 0;
      lastAdaptiveCheck = currentTime;
    }
    
    requestAnimationFrame(gameLoop);
  }

  render();
  requestAnimationFrame(gameLoop);
})();
</script>

</div>

<div align="center">

*Hover over the canvas to draw cells in Conway's Game of Life*

</div>

## 
I'm Andrew, and I write spaghetti code sometimes. I usually work on projects or problems that I find interesting or challenging.

I like learning about niche low-level details and wonky optimizations.

I'm also an avid chess programmer—my chess engine [Tuna](https://github.com/andrew-y-xia/Tuna) plays at ~2950 elo. I play at like 900 elo.

I try thinking about concurrency a lot, both on distributed-scale and processor-scale. On the processor side, it'll be a while until I can reliably write lock-free data structures. On the distributed side, I'm currently working on a project similar to Google's distributed SQL database, [Spanner](https://static.googleusercontent.com/media/research.google.com/en//archive/spanner-osdi2012.pdf).

---

> tl;dr — I poke at low-level weirdness, concurrency shenanigans, and computer chess

<details>
	<summary><b>Random things corner</b> (click to expand)</summary>

	- I like thinking about memory models, cache coherence, and when a "minor" branch mispredict is actually your whole problem.
	- On the distributed side: time, sharding, and whatever it means to be web scale
	- On the CPU side: pipelining, atomics, and misinterpreting what memory_order_acquire really entails
    - I love cursed software and cursed things about programming languages

</details>

---

If anything sounds fun to talk about, reach out at andrew.xia@princeton.edu!
