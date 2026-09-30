/**
 * ==============================================================================
 *                       UNDERWATER TREASURE HUNT
 *        Vision-Controlled Hand Gesture Interactive Web Engine
 * ==============================================================================
 */

// --- Audio Synthesizer (Web Audio API) ---
class SoundSynth {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggle() {
    this.enabled = !this.enabled;
    return this.enabled;
  }

  playBubble() {
    if (!this.enabled || !this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(350, now);
    osc.frequency.exponentialRampToValueAtTime(900, now + 0.12);
    gain.gain.setValueAtTime(0.3, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.12);
  }

  playChime() {
    if (!this.enabled || !this.ctx) return;
    const notes = [987.77, 1318.51, 1975.53];
    notes.forEach((freq, idx) => {
      const now = this.ctx.currentTime + idx * 0.06;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, now);
      gain.gain.setValueAtTime(0.25, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.4);
    });
  }

  playRareChime() {
    if (!this.enabled || !this.ctx) return;
    const chord = [587.33, 880.0, 1174.66, 1760.0];
    chord.forEach((freq) => {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, now);
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.7);
    });
  }

  playSonar() {
    if (!this.enabled || !this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, now);
    osc.frequency.exponentialRampToValueAtTime(440, now + 0.8);
    gain.gain.setValueAtTime(0.35, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.8);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.8);
  }

  playCurrent() {
    if (!this.enabled || !this.ctx) return;
    const now = this.ctx.currentTime;
    const bufferSize = this.ctx.sampleRate * 0.8;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    let last = 0;
    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      data[i] = (last + 0.02 * white) / 1.02;
      last = data[i];
      data[i] *= 1.8;
    }
    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;
    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.4, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.8);
    noise.connect(gain);
    gain.connect(this.ctx.destination);
    noise.start(now);
  }

  playAlarm() {
    if (!this.enabled || !this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(140, now);
    osc.frequency.setValueAtTime(200, now + 0.1);
    gain.gain.setValueAtTime(0.3, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.3);
  }

  playExplosion() {
    if (!this.enabled || !this.ctx) return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(120, now);
    osc.frequency.exponentialRampToValueAtTime(30, now + 0.6);
    gain.gain.setValueAtTime(0.6, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.6);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.6);
  }

  playWin() {
    if (!this.enabled || !this.ctx) return;
    const fanfare = [523.25, 659.25, 783.99, 1046.5];
    fanfare.forEach((freq, idx) => {
      const now = this.ctx.currentTime + idx * 0.12;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, now);
      gain.gain.setValueAtTime(0.3, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + (idx === 3 ? 0.6 : 0.2));
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + (idx === 3 ? 0.6 : 0.2));
    });
  }

  playGameOver() {
    if (!this.enabled || !this.ctx) return;
    const notes = [440, 370, 311.13];
    notes.forEach((freq, idx) => {
      const now = this.ctx.currentTime + idx * 0.25;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(freq, now);
      gain.gain.setValueAtTime(0.25, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.4);
    });
  }
}

// --- Levels Specification ---
const LEVELS = [
  {
    id: 1,
    name: "Shallow Sea",
    depth: "10m Depth",
    targetRelics: 3,
    colorTop: "#12427a",
    colorBottom: "#091e38",
    hasFakes: false,
    hasMines: false,
    hasShark: false,
    desc: "Sunlit waters. Learn basic swimmer steering & grab relics!"
  },
  {
    id: 2,
    name: "Coral Reef",
    depth: "35m Depth",
    targetRelics: 5,
    colorTop: "#0f3361",
    colorBottom: "#06182f",
    hasFakes: true,
    hasMines: false,
    hasShark: false,
    desc: "Vibrant marine corals. Counterfeit relics appear (use Sonar ✌️)!"
  },
  {
    id: 3,
    name: "Deep Ocean",
    depth: "85m Depth",
    targetRelics: 5,
    colorTop: "#072042",
    colorBottom: "#030e1d",
    hasFakes: true,
    hasMines: true,
    hasShark: false,
    desc: "Abyssal darkness. Volumetric torch & beware of spiked naval mines!"
  },
  {
    id: 4,
    name: "Lost Ship",
    depth: "140m Depth",
    targetRelics: 7,
    colorTop: "#051833",
    colorBottom: "#020a14",
    hasFakes: true,
    hasMines: true,
    hasShark: true,
    desc: "Sunken galleon ruins. Apex Predator Sharks patrol (curl Fist ✊ for Shield)!"
  },
  {
    id: 5,
    name: "Ancient Ruins",
    depth: "220m Depth",
    targetRelics: 8,
    colorTop: "#031024",
    colorBottom: "#01050a",
    hasFakes: true,
    hasMines: true,
    hasShark: true,
    desc: "Sunken Poseidon temple. Find the legendary Sunken Crown of Atlantis!"
  }
];

// --- Main Game Engine ---
class UnderwaterGame {
  constructor() {
    this.canvas = document.getElementById('game-canvas');
    this.ctx = this.canvas.getContext('2d');
    this.pipCanvas = document.getElementById('pip-canvas');
    this.pipCtx = this.pipCanvas.getContext('2d');
    this.video = document.getElementById('webcam-raw');

    this.sound = new SoundSynth();

    // Game state
    this.state = 'MENU'; // MENU, PLAYING, PAUSED, LEVEL_SELECT, INSTRUCTIONS, WIN, GAMEOVER
    this.currentLevelIndex = 0;
    this.score = 0;
    this.oxygen = 100.0;
    this.storedCount = 0;
    this.sonarCharges = 3;
    this.activeGesture = 'SWIM FREE';
    this.activeEmoji = '🖐️';

    // Camera / Control tracking
    this.isCameraMode = true;
    this.cameraReady = false;
    this.hands = null;
    this.cameraUtils = null;

    // Swimmer diver entity
    this.swimmer = {
      x: 300,
      y: 300,
      targetX: 300,
      targetY: 300,
      vx: 0,
      vy: 0,
      angle: 0,
      finPhase: 0,
      shieldActive: false,
      flashlightAngle: 0,
      bubbles: []
    };

    // World entities
    this.relics = [];
    this.vault = { x: 120, y: 550, width: 90, height: 70 };
    this.fishSchools = [];
    this.sharks = [];
    this.particles = [];
    this.sonarWaves = [];
    this.waterCurrentActive = false;
    this.currentTimer = 0;

    // Screen Shake
    this.shakeAmount = 0;

    // Timing
    this.lastTime = performance.now();

    // Mouse coordinates fallback
    this.mouseX = 300;
    this.mouseY = 300;
    this.isMouseDown = false;

    this.initDOM();
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
    this.setupInputs();

    // Start render loop
    requestAnimationFrame((t) => this.loop(t));
  }

  resizeCanvas() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
    this.vault.y = this.canvas.height - 90;
    this.vault.x = 100;
  }

  initDOM() {
    // Buttons
    document.getElementById('btn-play-expedition').onclick = () => {
      this.sound.init();
      this.startLevel(this.currentLevelIndex);
      this.initCamera();
    };

    document.getElementById('btn-level-select').onclick = () => {
      this.sound.init();
      this.showScreen('level-screen');
      this.renderLevelGrid();
    };

    document.getElementById('btn-how-to-play').onclick = () => {
      this.sound.init();
      this.showScreen('instructions-screen');
    };

    document.getElementById('btn-back-from-levels').onclick = () => {
      this.showScreen('menu-screen');
    };

    document.getElementById('btn-close-guide').onclick = () => {
      this.showScreen('menu-screen');
    };

    document.getElementById('btn-toggle-sound').onclick = () => {
      const on = this.sound.toggle();
      document.getElementById('sound-icon').textContent = on ? '🔊' : '🔇';
    };

    document.getElementById('btn-toggle-fullscreen').onclick = () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    };

    document.getElementById('btn-switch-control').onclick = () => {
      this.isCameraMode = !this.isCameraMode;
      const dot = document.getElementById('camera-status-dot');
      const text = document.getElementById('control-mode-text');
      if (this.isCameraMode) {
        dot.className = 'status-dot online';
        text.textContent = 'WEBCAM ACTIVE';
        if (!this.cameraReady) this.initCamera();
      } else {
        dot.className = 'status-dot mouse';
        text.textContent = 'MOUSE MODE';
      }
    };

    document.getElementById('btn-pause-game').onclick = () => {
      if (this.state === 'PLAYING') {
        this.state = 'PAUSED';
        this.showScreen('pause-screen');
      }
    };

    document.getElementById('btn-resume-game').onclick = () => {
      this.state = 'PLAYING';
      this.hideAllScreens();
    };

    document.getElementById('btn-restart-level').onclick = () => {
      this.startLevel(this.currentLevelIndex);
    };

    document.getElementById('btn-exit-to-menu').onclick = () => {
      this.state = 'MENU';
      this.showScreen('menu-screen');
      document.getElementById('game-hud').style.display = 'none';
      document.getElementById('btn-pause-game').style.display = 'none';
    };

    document.getElementById('btn-next-level').onclick = () => {
      this.currentLevelIndex = Math.min(LEVELS.length - 1, this.currentLevelIndex + 1);
      this.startLevel(this.currentLevelIndex);
    };

    document.getElementById('btn-win-to-menu').onclick = () => {
      this.showScreen('level-screen');
      this.renderLevelGrid();
    };

    document.getElementById('btn-retry-level').onclick = () => {
      this.startLevel(this.currentLevelIndex);
    };

    document.getElementById('btn-over-to-menu').onclick = () => {
      this.state = 'MENU';
      this.showScreen('menu-screen');
      document.getElementById('game-hud').style.display = 'none';
      document.getElementById('btn-pause-game').style.display = 'none';
    };
  }

  showScreen(id) {
    document.querySelectorAll('.app-screen').forEach((el) => {
      el.style.display = 'none';
    });
    const target = document.getElementById(id);
    if (target) target.style.display = 'flex';
  }

  hideAllScreens() {
    document.querySelectorAll('.app-screen').forEach((el) => {
      el.style.display = 'none';
    });
  }

  renderLevelGrid() {
    const grid = document.getElementById('levels-grid');
    grid.innerHTML = '';
    LEVELS.forEach((lvl, idx) => {
      const card = document.createElement('div');
      card.className = `level-card ${idx === this.currentLevelIndex ? 'active' : ''}`;
      card.innerHTML = `
        <div class="level-num">LEVEL 0${lvl.id} • ${lvl.depth}</div>
        <div class="level-title">${lvl.name}</div>
        <div class="level-req">Objective: Store ${lvl.targetRelics} Relics</div>
      `;
      card.onclick = () => {
        this.currentLevelIndex = idx;
        this.startLevel(idx);
        this.initCamera();
      };
      grid.appendChild(card);
    });
  }

  setupInputs() {
    window.addEventListener('mousemove', (e) => {
      this.mouseX = e.clientX;
      this.mouseY = e.clientY;
      if (!this.isCameraMode && this.state === 'PLAYING') {
        this.swimmer.targetX = e.clientX;
        this.swimmer.targetY = e.clientY;
      }
    });

    window.addEventListener('mousedown', (e) => {
      this.isMouseDown = true;
      if (this.state === 'PLAYING') {
        this.sound.init();
        if (e.button === 0) {
          // Left click: grab / collect check
          this.triggerCollectCheck();
        } else if (e.button === 2) {
          // Right click: Sonar
          this.triggerSonar();
        }
      }
    });

    window.addEventListener('contextmenu', (e) => e.preventDefault());

    window.addEventListener('mouseup', () => {
      this.isMouseDown = false;
    });

    window.addEventListener('keydown', (e) => {
      if (e.code === 'KeyM') {
        const on = this.sound.toggle();
        document.getElementById('sound-icon').textContent = on ? '🔊' : '🔇';
      }
      if (e.code === 'Escape' && this.state === 'PLAYING') {
        this.state = 'PAUSED';
        this.showScreen('pause-screen');
      }
      if (e.code === 'Space' && this.state === 'PLAYING') {
        this.triggerCurrent();
      }
      if (e.code === 'KeyS' && this.state === 'PLAYING') {
        this.swimmer.shieldActive = true;
      }
    });

    window.addEventListener('keyup', (e) => {
      if (e.code === 'KeyS') {
        this.swimmer.shieldActive = false;
      }
    });
  }

  // --- Computer Vision & MediaPipe Hands Pipeline ---
  async initCamera() {
    if (this.cameraReady) return;
    try {
      if (!window.Hands) {
        console.warn("[Vision] MediaPipe Hands script loading or unavailable. Using mouse mode.");
        return;
      }

      this.hands = new window.Hands({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
      });

      this.hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 1,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
      });

      this.hands.onResults((results) => this.onHandResults(results));

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' }
      });
      this.video.srcObject = stream;
      await this.video.play();

      this.cameraReady = true;

      // Processing Loop
      const processFrame = async () => {
        if (this.cameraReady && this.video.readyState >= 2) {
          await this.hands.send({ image: this.video });
        }
        requestAnimationFrame(processFrame);
      };
      requestAnimationFrame(processFrame);
    } catch (err) {
      console.warn("[Vision] Camera access rejected or unavailable:", err);
      this.isCameraMode = false;
      const dot = document.getElementById('camera-status-dot');
      const text = document.getElementById('control-mode-text');
      dot.className = 'status-dot mouse';
      text.textContent = 'MOUSE MODE';
    }
  }

  onHandResults(results) {
    // Draw Picture-In-Picture View
    this.pipCtx.clearRect(0, 0, 160, 120);
    this.pipCtx.drawImage(this.video, 0, 0, 160, 120);

    if (!results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
      return;
    }

    const landmarks = results.multiHandLandmarks[0];

    // Landmark 8 is Index Fingertip, Landmark 4 is Thumb tip
    const indexTip = landmarks[8];
    const thumbTip = landmarks[4];
    const middleTip = landmarks[12];
    const ringTip = landmarks[16];
    const pinkyTip = landmarks[20];
    const wrist = landmarks[0];

    // Mirror horizontal: 1 - x
    const screenX = (1.0 - indexTip.x) * this.canvas.width;
    const screenY = indexTip.y * this.canvas.height;

    // EMA Smooth position tracking
    if (this.isCameraMode && this.state === 'PLAYING') {
      const alpha = 0.35;
      this.swimmer.targetX = this.swimmer.targetX + alpha * (screenX - this.swimmer.targetX);
      this.swimmer.targetY = this.swimmer.targetY + alpha * (screenY - this.swimmer.targetY);
    }

    // Draw hand skeleton in PiP
    this.pipCtx.fillStyle = '#00d4ff';
    landmarks.forEach((pt) => {
      this.pipCtx.beginPath();
      this.pipCtx.arc(pt.x * 160, pt.y * 120, 2, 0, Math.PI * 2);
      this.pipCtx.fill();
    });

    // Gesture Classification
    const pinchDist = Math.hypot(indexTip.x - thumbTip.x, indexTip.y - thumbTip.y);
    const middleExtended = middleTip.y < landmarks[10].y;
    const ringCurled = ringTip.y > landmarks[14].y;
    const pinkyCurled = pinkyTip.y > landmarks[18].y;

    // 1. Pinch Gesture (🤏)
    if (pinchDist < 0.08) {
      this.setGesture('PINCH / COLLECT', '🤏');
      this.triggerCollectCheck();
      return;
    }

    // 2. Two Fingers / Peace (✌️) -> Sonar
    if (middleExtended && ringCurled && pinkyCurled) {
      this.setGesture('SONAR PULSE', '✌️');
      this.triggerSonar();
      return;
    }

    // 3. Fist (✊) -> Energy Shield
    const avgDistToWrist = (
      Math.hypot(indexTip.x - wrist.x, indexTip.y - wrist.y) +
      Math.hypot(middleTip.x - wrist.x, middleTip.y - wrist.y) +
      Math.hypot(ringTip.x - wrist.y, ringTip.y - wrist.y)
    ) / 3;

    if (avgDistToWrist < 0.22) {
      this.setGesture('ENERGY SHIELD', '✊');
      this.swimmer.shieldActive = true;
      return;
    } else {
      this.swimmer.shieldActive = false;
    }

    // 4. Open Palm (✋) -> Current
    const allExtended = indexTip.y < landmarks[6].y &&
                        middleTip.y < landmarks[10].y &&
                        ringTip.y < landmarks[14].y &&
                        pinkyTip.y < landmarks[18].y;

    if (allExtended) {
      this.setGesture('WATER CURRENT', '✋');
      this.triggerCurrent();
      return;
    }

    this.setGesture('SWIM FREE', '🖐️');
  }

  setGesture(name, emoji) {
    this.activeGesture = name;
    this.activeEmoji = emoji;
    const badgeName = document.getElementById('hud-gesture-name');
    const badgeEmoji = document.getElementById('hud-gesture-emoji');
    if (badgeName) badgeName.textContent = name;
    if (badgeEmoji) badgeEmoji.textContent = emoji;
  }

  // --- Game Loop and Entities ---
  startLevel(index) {
    const lvl = LEVELS[index];
    this.currentLevelIndex = index;
    this.oxygen = 100.0;
    this.storedCount = 0;
    this.sonarCharges = 3;
    this.state = 'PLAYING';
    this.shakeAmount = 0;

    // Reset Swimmer
    this.swimmer.x = this.canvas.width / 2;
    this.swimmer.y = this.canvas.height / 2;
    this.swimmer.targetX = this.swimmer.x;
    this.swimmer.targetY = this.swimmer.y;
    this.swimmer.vx = 0;
    this.swimmer.vy = 0;
    this.swimmer.bubbles = [];

    // Spawn relics
    this.relics = [];
    const types = ['common', 'gold', 'rare', 'ancient'];
    for (let i = 0; i < lvl.targetRelics + 3; i++) {
      const isFake = lvl.hasFakes && Math.random() < 0.28;
      const isMine = lvl.hasMines && Math.random() < 0.22;
      let type = types[Math.floor(Math.random() * (lvl.id >= 4 ? 4 : 3))];
      if (lvl.id === 5 && i === 0) type = 'ancient'; // Atlantis crown

      this.relics.push({
        x: 200 + Math.random() * (this.canvas.width - 320),
        y: 120 + Math.random() * (this.canvas.height - 240),
        type: type,
        isFake: isFake,
        isMine: isMine,
        collected: false,
        sonarRevealed: false,
        radius: isMine ? 24 : 20,
        bobPhase: Math.random() * Math.PI * 2
      });
    }

    // Spawn Fish Schools
    this.fishSchools = [];
    for (let i = 0; i < 18; i++) {
      this.fishSchools.push({
        x: Math.random() * this.canvas.width,
        y: 100 + Math.random() * (this.canvas.height - 200),
        vx: (Math.random() > 0.5 ? 1 : -1) * (1.2 + Math.random() * 1.5),
        color: ['#00d4ff', '#ffd700', '#ff6b6b', '#00e676'][Math.floor(Math.random() * 4)],
        size: 8 + Math.random() * 8
      });
    }

    // Spawn Apex Sharks
    this.sharks = [];
    if (lvl.hasShark) {
      for (let s = 0; s < 2; s++) {
        this.sharks.push({
          x: Math.random() * this.canvas.width,
          y: 200 + Math.random() * (this.canvas.height - 350),
          vx: (s % 2 === 0 ? 1 : -1) * 2.2,
          radius: 36
        });
      }
    }

    this.particles = [];
    this.sonarWaves = [];

    // Update HUD
    document.getElementById('hud-level-name').textContent = `${lvl.name} (${lvl.depth})`;
    document.getElementById('hud-objective-text').textContent = `0 / ${lvl.targetRelics} STORED`;
    document.getElementById('hud-sonar-val').textContent = `${this.sonarCharges} / 3`;
    document.getElementById('hud-score-val').textContent = this.score;

    this.hideAllScreens();
    document.getElementById('game-hud').style.display = 'flex';
    document.getElementById('btn-pause-game').style.display = 'flex';
  }

  triggerSonar() {
    if (this.sonarCharges <= 0) return;
    this.sonarCharges--;
    document.getElementById('hud-sonar-val').textContent = `${this.sonarCharges} / 3`;
    this.sound.playSonar();

    this.sonarWaves.push({
      x: this.swimmer.x,
      y: this.swimmer.y,
      radius: 10,
      maxRadius: 750,
      speed: 420
    });
  }

  triggerCurrent() {
    if (this.waterCurrentActive) return;
    this.waterCurrentActive = true;
    this.currentTimer = 2.0;
    this.sound.playCurrent();

    // Push fish & relics
    this.relics.forEach((r) => {
      if (!r.collected) r.x += 120;
    });
    this.fishSchools.forEach((f) => {
      f.vx = Math.abs(f.vx) * 3;
    });
  }

  triggerCollectCheck() {
    // Check if swimmer is near any relic
    for (let r of this.relics) {
      if (r.collected) continue;
      const d = Math.hypot(this.swimmer.x - r.x, this.swimmer.y - r.y);
      if (d < 50) {
        this.collectRelic(r);
        break;
      }
    }
  }

  collectRelic(relic) {
    relic.collected = true;

    if (relic.isMine) {
      // Detonate Sea Mine
      this.sound.playExplosion();
      this.oxygen = Math.max(0, this.oxygen - 25.0);
      this.shakeAmount = 20;
      this.spawnExplosionParticles(relic.x, relic.y);
      return;
    }

    if (relic.isFake) {
      // Deceptive Fake
      this.sound.playAlarm();
      this.score = Math.max(0, this.score - 50);
      this.oxygen = Math.max(0, this.oxygen - 12.0);
      this.spawnPopup(relic.x, relic.y, "-50 (FAKE!)", "#ff5252");
      return;
    }

    // Genuine Relic -> Automatic Vault Deposit!
    let pts = 50;
    if (relic.type === 'gold') pts = 100;
    if (relic.type === 'rare') pts = 250;
    if (relic.type === 'ancient') pts = 500;

    if (relic.type === 'rare' || relic.type === 'ancient') {
      this.sound.playRareChime();
    } else {
      this.sound.playChime();
    }

    this.score += pts;
    this.storedCount++;

    const lvl = LEVELS[this.currentLevelIndex];
    document.getElementById('hud-score-val').textContent = this.score;
    document.getElementById('hud-objective-text').textContent = `${this.storedCount} / ${lvl.targetRelics} STORED`;
    this.spawnPopup(relic.x, relic.y, `+${pts}`, '#ffd700');
    this.spawnDepositCelebration(relic.x, relic.y);

    // Check Win
    if (this.storedCount >= lvl.targetRelics) {
      setTimeout(() => this.triggerWin(), 600);
    }
  }

  triggerWin() {
    this.state = 'WIN';
    this.sound.playWin();
    document.getElementById('win-score-val').textContent = this.score;
    document.getElementById('win-oxygen-val').textContent = `${Math.ceil(this.oxygen)}%`;
    this.showScreen('win-screen');
  }

  triggerGameOver(cause) {
    this.state = 'GAMEOVER';
    this.sound.playGameOver();
    document.getElementById('gameover-cause').textContent = cause || "Your oxygen supply ran out.";
    this.showScreen('gameover-screen');
  }

  spawnPopup(x, y, text, color) {
    this.particles.push({
      type: 'text',
      x, y, text, color,
      vy: -1.5,
      alpha: 1.0,
      life: 1.0
    });
  }

  spawnExplosionParticles(x, y) {
    for (let i = 0; i < 28; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 2 + Math.random() * 5;
      this.particles.push({
        type: 'spark',
        x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        color: ['#ff1744', '#ff9100', '#ffd600'][Math.floor(Math.random() * 3)],
        radius: 3 + Math.random() * 4,
        alpha: 1.0,
        life: 0.6 + Math.random() * 0.4
      });
    }
  }

  spawnDepositCelebration(startX, startY) {
    // Arc towards the vault at bottom left
    for (let i = 0; i < 12; i++) {
      this.particles.push({
        type: 'deposit_trail',
        x: startX,
        y: startY,
        tx: this.vault.x + this.vault.width / 2 + (Math.random() * 20 - 10),
        ty: this.vault.y + 20,
        color: '#ffd700',
        progress: 0,
        speed: 0.02 + Math.random() * 0.02
      });
    }
  }

  // --- Main Engine Update & Render Loop ---
  loop(timestamp) {
    const dt = Math.min(0.1, (timestamp - this.lastTime) / 1000);
    this.lastTime = timestamp;

    if (this.state === 'PLAYING') {
      this.update(dt);
    }

    this.render();
    requestAnimationFrame((t) => this.loop(t));
  }

  update(dt) {
    // 1. Oxygen Depletion
    this.oxygen = Math.max(0, this.oxygen - 0.85 * dt);
    const oxyBar = document.getElementById('hud-oxygen-bar');
    const oxyText = document.getElementById('hud-oxygen-text');
    if (oxyBar) oxyBar.style.width = `${this.oxygen}%`;
    if (oxyText) oxyText.textContent = `${Math.ceil(this.oxygen)}%`;

    if (this.oxygen <= 25) {
      oxyBar.classList.add('critical');
    } else {
      oxyBar.classList.remove('critical');
    }

    if (this.oxygen <= 0) {
      this.triggerGameOver("Oxygen supply depleted before vault objective was secured!");
      return;
    }

    // 2. Swimmer Kinematics
    const dx = this.swimmer.targetX - this.swimmer.x;
    const dy = this.swimmer.targetY - this.swimmer.y;
    this.swimmer.vx = this.swimmer.vx * 0.82 + dx * 0.08;
    this.swimmer.vy = this.swimmer.vy * 0.82 + dy * 0.08;
    this.swimmer.x += this.swimmer.vx;
    this.swimmer.y += this.swimmer.vy;

    const speed = Math.hypot(this.swimmer.vx, this.swimmer.vy);
    if (speed > 0.5) {
      this.swimmer.angle = Math.atan2(this.swimmer.vy, this.swimmer.vx);
      this.swimmer.finPhase += speed * 0.12;
    }

    // Emit exhaust regulator bubbles
    if (Math.random() < 0.25) {
      this.swimmer.bubbles.push({
        x: this.swimmer.x - Math.cos(this.swimmer.angle) * 20,
        y: this.swimmer.y - Math.sin(this.swimmer.angle) * 20,
        radius: 2 + Math.random() * 3,
        vy: -0.8 - Math.random() * 1.2,
        alpha: 0.8
      });
      if (Math.random() < 0.05) this.sound.playBubble();
    }

    // Update Swimmer Bubbles
    for (let i = this.swimmer.bubbles.length - 1; i >= 0; i--) {
      const b = this.swimmer.bubbles[i];
      b.y += b.vy;
      b.alpha -= 0.015;
      if (b.alpha <= 0 || b.y < 0) this.swimmer.bubbles.splice(i, 1);
    }

    // 3. Proximity Hover Auto-Collect
    for (let r of this.relics) {
      if (r.collected) continue;
      const d = Math.hypot(this.swimmer.x - r.x, this.swimmer.y - r.y);
      if (d < 38) {
        this.collectRelic(r);
        break;
      }
    }

    // 4. Update Sonar Waves
    for (let i = this.sonarWaves.length - 1; i >= 0; i--) {
      const w = this.sonarWaves[i];
      w.radius += w.speed * dt;
      this.relics.forEach((r) => {
        const d = Math.hypot(r.x - w.x, r.y - w.y);
        if (Math.abs(d - w.radius) < 25) {
          r.sonarRevealed = true;
        }
      });
      if (w.radius > w.maxRadius) this.sonarWaves.splice(i, 1);
    }

    // 5. Update Water Current Burst
    if (this.waterCurrentActive) {
      this.currentTimer -= dt;
      if (this.currentTimer <= 0) this.waterCurrentActive = false;
    }

    // 6. Update Fish Schools
    this.fishSchools.forEach((f) => {
      f.x += f.vx;
      if (f.vx > 0 && f.x > this.canvas.width + 20) f.x = -20;
      if (f.vx < 0 && f.x < -20) f.x = this.canvas.width + 20;
    });

    // 7. Update Apex Sharks
    this.sharks.forEach((s) => {
      s.x += s.vx;
      if (s.x > this.canvas.width + 60) s.x = -60;
      if (s.x < -60) s.x = this.canvas.width + 60;

      // Check collision with player
      const dist = Math.hypot(this.swimmer.x - s.x, this.swimmer.y - s.y);
      if (dist < s.radius + 20) {
        if (this.swimmer.shieldActive) {
          // Deflected by Energy Shield!
          s.vx = -s.vx * 1.5;
          this.sound.playAlarm();
          this.spawnPopup(this.swimmer.x, this.swimmer.y - 30, "DEFLECTED! 🛡️", "#00e676");
        } else {
          // Unshielded Shark Bite!
          this.oxygen = Math.max(0, this.oxygen - 35.0);
          this.sound.playExplosion();
          this.shakeAmount = 25;
          this.spawnPopup(this.swimmer.x, this.swimmer.y - 30, "SHARK BITE! -35%", "#ff1744");
          s.x += s.vx * 30; // Move shark away
        }
      }
    });

    // 8. Update Particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      if (p.type === 'text') {
        p.y += p.vy;
        p.alpha -= dt;
        if (p.alpha <= 0) this.particles.splice(i, 1);
      } else if (p.type === 'spark') {
        p.x += p.vx;
        p.y += p.vy;
        p.alpha -= dt * 1.5;
        if (p.alpha <= 0) this.particles.splice(i, 1);
      } else if (p.type === 'deposit_trail') {
        p.progress += p.speed;
        p.x += (p.tx - p.x) * 0.1;
        p.y += (p.ty - p.y) * 0.1;
        if (p.progress >= 1.0) {
          this.particles.splice(i, 1);
        }
      }
    }

    // Screen Shake decay
    if (this.shakeAmount > 0) {
      this.shakeAmount = Math.max(0, this.shakeAmount - dt * 40);
    }
  }

  // --- Rendering Pipeline ---
  render() {
    this.ctx.save();

    // Screen Shake
    if (this.shakeAmount > 0) {
      const ox = (Math.random() - 0.5) * this.shakeAmount;
      const oy = (Math.random() - 0.5) * this.shakeAmount;
      this.ctx.translate(ox, oy);
    }

    // 1. Oceanic Background Gradient
    const lvl = LEVELS[this.currentLevelIndex] || LEVELS[0];
    const grad = this.ctx.createLinearGradient(0, 0, 0, this.canvas.height);
    grad.addColorStop(0, lvl.colorTop);
    grad.addColorStop(1, lvl.colorBottom);
    this.ctx.fillStyle = grad;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // 2. Volumetric Caustic God Rays
    this.drawGodRays();

    // 3. Seafloor Terrain Silhouettes & Vault Depot
    this.drawSeafloor();

    // 4. Sonar Expansion Rings
    this.drawSonarWaves();

    // 5. Relics & Hazards
    this.drawRelics();

    // 6. Fish Schools & Sharks
    this.drawFishAndSharks();

    // 7. Swimmer Character ("The Man")
    this.drawSwimmer();

    // 8. Particles, Trails, & Floating Text
    this.drawParticles();

    this.ctx.restore();
  }

  drawGodRays() {
    this.ctx.save();
    this.ctx.globalAlpha = 0.08;
    this.ctx.fillStyle = '#cce6ff';
    for (let i = 0; i < 5; i++) {
      const x = (i * 320 + Math.sin(performance.now() * 0.001 + i) * 60) % this.canvas.width;
      this.ctx.beginPath();
      this.ctx.moveTo(x - 40, 0);
      this.ctx.lineTo(x + 180, this.canvas.height);
      this.ctx.lineTo(x + 240, this.canvas.height);
      this.ctx.lineTo(x + 20, 0);
      this.ctx.closePath();
      this.ctx.fill();
    }
    this.ctx.restore();
  }

  drawSeafloor() {
    // Seabed Mound
    this.ctx.fillStyle = '#020710';
    this.ctx.beginPath();
    this.ctx.moveTo(0, this.canvas.height - 40);
    this.ctx.quadraticCurveTo(this.canvas.width * 0.3, this.canvas.height - 80, this.canvas.width * 0.6, this.canvas.height - 45);
    this.ctx.quadraticCurveTo(this.canvas.width * 0.85, this.canvas.height - 90, this.canvas.width, this.canvas.height - 50);
    this.ctx.lineTo(this.canvas.width, this.canvas.height);
    this.ctx.lineTo(0, this.canvas.height);
    this.ctx.closePath();
    this.ctx.fill();

    // Seafloor Vault Chest (Collection Depot)
    const v = this.vault;
    this.ctx.save();
    this.ctx.fillStyle = '#795548';
    this.ctx.fillRect(v.x, v.y, v.width, v.height);
    // Gold Trim
    this.ctx.strokeStyle = '#ffd700';
    this.ctx.lineWidth = 4;
    this.ctx.strokeRect(v.x, v.y, v.width, v.height);

    // Vault Glow & Label
    this.ctx.fillStyle = '#ffd700';
    this.ctx.font = "bold 11px Rajdhani, sans-serif";
    this.ctx.fillText("VAULT DEPOT", v.x + 8, v.y + 40);
    this.ctx.restore();
  }

  drawSonarWaves() {
    this.sonarWaves.forEach((w) => {
      this.ctx.save();
      this.ctx.strokeStyle = `rgba(0, 212, 255, ${Math.max(0, 1 - w.radius / w.maxRadius)})`;
      this.ctx.lineWidth = 3;
      this.ctx.beginPath();
      this.ctx.arc(w.x, w.y, w.radius, 0, Math.PI * 2);
      this.ctx.stroke();
      this.ctx.restore();
    });
  }

  drawRelics() {
    this.relics.forEach((r) => {
      if (r.collected) return;
      const bob = Math.sin(performance.now() * 0.003 + r.bobPhase) * 6;
      const y = r.y + bob;

      this.ctx.save();

      // Sonar Reveal Ring
      if (r.sonarRevealed) {
        this.ctx.lineWidth = 3;
        if (r.isMine) {
          this.ctx.strokeStyle = '#ff1744'; // Red for Sea Mine
        } else if (r.isFake) {
          this.ctx.strokeStyle = '#ffd600'; // Yellow for Fake
        } else {
          this.ctx.strokeStyle = '#00e676'; // Green for genuine
        }
        this.ctx.beginPath();
        this.ctx.arc(r.x, y, r.radius + 12, 0, Math.PI * 2);
        this.ctx.stroke();
      }

      if (r.isMine) {
        // Sea Mine: Spiked Dark Sphere
        this.ctx.fillStyle = '#212121';
        this.ctx.beginPath();
        this.ctx.arc(r.x, y, r.radius, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.strokeStyle = '#ff1744';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();

        // Spikes
        for (let a = 0; a < Math.PI * 2; a += Math.PI / 4) {
          this.ctx.beginPath();
          this.ctx.moveTo(r.x + Math.cos(a) * r.radius, y + Math.sin(a) * r.radius);
          this.ctx.lineTo(r.x + Math.cos(a) * (r.radius + 8), y + Math.sin(a) * (r.radius + 8));
          this.ctx.stroke();
        }
      } else {
        // Relic Icons
        let emoji = '🦪';
        if (r.type === 'gold') emoji = '🪙';
        if (r.type === 'rare') emoji = '💎';
        if (r.type === 'ancient') emoji = '👑';
        if (r.isFake) emoji = '📦';

        this.ctx.font = `${r.radius * 1.6}px sans-serif`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(emoji, r.x, y);

        // Glow Aura
        this.ctx.beginPath();
        this.ctx.arc(r.x, y, r.radius, 0, Math.PI * 2);
        this.ctx.fillStyle = r.type === 'ancient' ? 'rgba(255,215,0,0.2)' : 'rgba(0,212,255,0.15)';
        this.ctx.fill();
      }

      this.ctx.restore();
    });
  }

  drawFishAndSharks() {
    // Fish
    this.fishSchools.forEach((f) => {
      this.ctx.save();
      this.ctx.fillStyle = f.color;
      this.ctx.beginPath();
      this.ctx.ellipse(f.x, f.y, f.size, f.size / 2, 0, 0, Math.PI * 2);
      this.ctx.fill();

      // Tail
      const tailDir = f.vx > 0 ? -1 : 1;
      this.ctx.beginPath();
      this.ctx.moveTo(f.x + tailDir * f.size, f.y);
      this.ctx.lineTo(f.x + tailDir * (f.size + 6), f.y - 4);
      this.ctx.lineTo(f.x + tailDir * (f.size + 6), f.y + 4);
      this.ctx.closePath();
      this.ctx.fill();
      this.ctx.restore();
    });

    // Apex Sharks
    this.sharks.forEach((s) => {
      this.ctx.save();
      this.ctx.translate(s.x, s.y);
      if (s.vx < 0) this.ctx.scale(-1, 1);

      // Shark Body
      this.ctx.fillStyle = '#455a64';
      this.ctx.beginPath();
      this.ctx.ellipse(0, 0, 48, 18, 0, 0, Math.PI * 2);
      this.ctx.fill();

      // Dorsal Fin
      this.ctx.beginPath();
      this.ctx.moveTo(-5, -16);
      this.ctx.lineTo(10, -32);
      this.ctx.lineTo(18, -14);
      this.ctx.closePath();
      this.ctx.fill();

      // Red Eye
      this.ctx.fillStyle = '#ff1744';
      this.ctx.beginPath();
      this.ctx.arc(32, -4, 3, 0, Math.PI * 2);
      this.ctx.fill();

      this.ctx.restore();
    });
  }

  drawSwimmer() {
    const s = this.swimmer;

    // Draw Bubbles
    s.bubbles.forEach((b) => {
      this.ctx.save();
      this.ctx.fillStyle = `rgba(255, 255, 255, ${b.alpha})`;
      this.ctx.beginPath();
      this.ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.restore();
    });

    this.ctx.save();
    this.ctx.translate(s.x, s.y);
    this.ctx.rotate(s.angle);

    // Volumetric Flashlight Beam
    const beam = this.ctx.createRadialGradient(25, 0, 5, 180, 0, 160);
    beam.addColorStop(0, 'rgba(255, 255, 220, 0.45)');
    beam.addColorStop(1, 'rgba(255, 255, 220, 0)');
    this.ctx.fillStyle = beam;
    this.ctx.beginPath();
    this.ctx.moveTo(25, -6);
    this.ctx.lineTo(240, -75);
    this.ctx.lineTo(240, 75);
    this.ctx.lineTo(25, 6);
    this.ctx.closePath();
    this.ctx.fill();

    // Twin Swimming Fins (fluttering animation)
    const finFlutter = Math.sin(s.finPhase) * 10;
    this.ctx.fillStyle = '#00d4ff';
    // Top fin
    this.ctx.beginPath();
    this.ctx.moveTo(-25, -6);
    this.ctx.lineTo(-44, -14 + finFlutter);
    this.ctx.lineTo(-38, -6);
    this.ctx.closePath();
    this.ctx.fill();
    // Bottom fin
    this.ctx.beginPath();
    this.ctx.moveTo(-25, 6);
    this.ctx.lineTo(-44, 14 - finFlutter);
    this.ctx.lineTo(-38, 6);
    this.ctx.closePath();
    this.ctx.fill();

    // Diver Wetsuit Body
    this.ctx.fillStyle = '#1e3c72';
    this.ctx.beginPath();
    this.ctx.ellipse(0, 0, 26, 12, 0, 0, Math.PI * 2);
    this.ctx.fill();

    // Yellow Oxygen Tank on Back
    this.ctx.fillStyle = '#ffd700';
    this.ctx.fillRect(-14, -15, 22, 6);

    // Scuba Mask / Head
    this.ctx.fillStyle = '#ffcc80';
    this.ctx.beginPath();
    this.ctx.arc(18, 0, 10, 0, Math.PI * 2);
    this.ctx.fill();

    // Glass Visor
    this.ctx.fillStyle = '#00e5ff';
    this.ctx.beginPath();
    this.ctx.arc(22, 0, 6, 0, Math.PI * 2);
    this.ctx.fill();

    // Energy Shield Dome (Fist ✊ active)
    if (s.shieldActive) {
      this.ctx.strokeStyle = 'rgba(0, 230, 118, 0.75)';
      this.ctx.lineWidth = 4;
      this.ctx.fillStyle = 'rgba(0, 230, 118, 0.18)';
      this.ctx.beginPath();
      this.ctx.arc(0, 0, 48, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.stroke();
    }

    this.ctx.restore();
  }

  drawParticles() {
    this.particles.forEach((p) => {
      this.ctx.save();
      if (p.type === 'text') {
        this.ctx.fillStyle = p.color;
        this.ctx.font = "bold 18px Rajdhani, Orbitron, sans-serif";
        this.ctx.globalAlpha = p.alpha;
        this.ctx.textAlign = 'center';
        this.ctx.fillText(p.text, p.x, p.y);
      } else if (p.type === 'spark') {
        this.ctx.fillStyle = p.color;
        this.ctx.globalAlpha = p.alpha;
        this.ctx.beginPath();
        this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        this.ctx.fill();
      } else if (p.type === 'deposit_trail') {
        this.ctx.fillStyle = p.color;
        this.ctx.beginPath();
        this.ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
        this.ctx.fill();
      }
      this.ctx.restore();
    });
  }
}

// Instantiate engine when DOM is ready
window.addEventListener('DOMContentLoaded', () => {
  window.app = new UnderwaterGame();
});
