/**
 * ==============================================================================
 * Underwater Treasure Hunt — High-Performance Browser Engine
 * Computer Vision Hand Tracking via MediaPipe Hands, Canvas 60FPS Game Loop,
 * Web Audio Procedural Synthesis, and Hydrodynamic Kinematics.
 * ==============================================================================
 */

// Global Configuration
const CONFIG = {
  OXYGEN_DEPLETION_RATE: 0.85, // % per second
  INITIAL_OXYGEN: 100,
  SONAR_DURATION: 3.5, // seconds
  CURRENT_DURATION: 2.0, // seconds
  PINCH_THRESHOLD: 0.08,
  PINCH_RELEASE: 0.11,
  SMOOTHING_ALPHA: 0.35,
};

// ==============================================================================
// 1. Procedural Web Audio Engine (Zero External Audio Files Required)
// ==============================================================================
class SoundEngine {
  constructor() {
    this.ctx = null;
    this.muted = false;
    this.ambientGain = null;
    this.ambientOsc = null;
    this.ambientNoise = null;
    this.isAmbientPlaying = false;
  }

  init() {
    if (this.ctx) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
      this._startAmbient();
    } catch (e) {
      console.warn('[SoundEngine] Web Audio not supported or blocked:', e);
    }
  }

  toggleMute() {
    this.muted = !this.muted;
    if (this.ctx && this.ambientGain) {
      this.ambientGain.gain.setValueAtTime(this.muted ? 0 : 0.05, this.ctx.currentTime);
    }
    return !this.muted;
  }

  _startAmbient() {
    if (!this.ctx || this.isAmbientPlaying || this.muted) return;
    try {
      // Gentle underwater ocean drone
      this.ambientOsc = this.ctx.createOscillator();
      this.ambientGain = this.ctx.createGain();
      const filter = this.ctx.createBiquadFilter();

      this.ambientOsc.type = 'sine';
      this.ambientOsc.frequency.setValueAtTime(55, this.ctx.currentTime); // Low 55Hz ocean hum

      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(220, this.ctx.currentTime);

      this.ambientGain.gain.setValueAtTime(0.04, this.ctx.currentTime);

      this.ambientOsc.connect(filter);
      filter.connect(this.ambientGain);
      this.ambientGain.connect(this.ctx.destination);
      this.ambientOsc.start();
      this.isAmbientPlaying = true;
    } catch (e) {}
  }

  playBubble() {
    if (!this.ctx || this.muted) return;
    try {
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      const startFreq = 280 + Math.random() * 200;
      const endFreq = startFreq + 350;

      osc.frequency.setValueAtTime(startFreq, t);
      osc.frequency.exponentialRampToValueAtTime(endFreq, t + 0.12);

      gain.gain.setValueAtTime(0.08, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.12);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.13);
    } catch (e) {}
  }

  playGrab() {
    if (!this.ctx || this.muted) return;
    try {
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(600, t);
      osc.frequency.exponentialRampToValueAtTime(950, t + 0.08);

      gain.gain.setValueAtTime(0.2, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.08);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.09);
    } catch (e) {}
  }

  playDeposit() {
    if (!this.ctx || this.muted) return;
    try {
      const t = this.ctx.currentTime;
      const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6 arpeggio
      notes.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        const start = t + idx * 0.07;

        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, start);

        gain.gain.setValueAtTime(0.18, start);
        gain.gain.exponentialRampToValueAtTime(0.001, start + 0.28);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(start);
        osc.stop(start + 0.3);
      });
    } catch (e) {}
  }

  playSonar() {
    if (!this.ctx || this.muted) return;
    try {
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(1150, t);
      osc.frequency.exponentialRampToValueAtTime(700, t + 0.45);

      gain.gain.setValueAtTime(0.25, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.45);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.46);
    } catch (e) {}
  }

  playCurrent() {
    if (!this.ctx || this.muted) return;
    try {
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      const filter = this.ctx.createBiquadFilter();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(80, t);

      filter.type = 'bandpass';
      filter.frequency.setValueAtTime(300, t);
      filter.frequency.exponentialRampToValueAtTime(1200, t + 0.4);
      filter.frequency.exponentialRampToValueAtTime(250, t + 0.8);

      gain.gain.setValueAtTime(0.15, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.8);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.85);
    } catch (e) {}
  }

  playShield() {
    if (!this.ctx || this.muted) return;
    try {
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(220, t);
      osc.frequency.linearRampToValueAtTime(380, t + 0.25);

      gain.gain.setValueAtTime(0.15, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.35);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.36);
    } catch (e) {}
  }

  playDamage() {
    if (!this.ctx || this.muted) return;
    try {
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(180, t);
      osc.frequency.exponentialRampToValueAtTime(45, t + 0.3);

      gain.gain.setValueAtTime(0.3, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.3);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + 0.32);
    } catch (e) {}
  }

  playWin() {
    if (!this.ctx || this.muted) return;
    try {
      const t = this.ctx.currentTime;
      const chord = [440, 554.37, 659.25, 880]; // A Major chord
      chord.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        const start = t + idx * 0.08;

        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, start);

        gain.gain.setValueAtTime(0.2, start);
        gain.gain.exponentialRampToValueAtTime(0.001, start + 0.7);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(start);
        osc.stop(start + 0.75);
      });
    } catch (e) {}
  }
}

// ==============================================================================
// 2. Vision & Hand Gesture Tracker (MediaPipe + Mouse Fallback)
// ==============================================================================
class VisionTracker {
  constructor(onGestureChange) {
    this.onGestureChange = onGestureChange;
    this.videoElement = document.getElementById('webcam-video');
    this.pipCanvas = document.getElementById('pip-canvas');
    this.pipCtx = this.pipCanvas.getContext('2d');
    this.calibCanvas = document.getElementById('calib-canvas');
    this.calibCtx = this.calibCanvas ? this.calibCanvas.getContext('2d') : null;

    this.hands = null;
    this.camera = null;
    this.isCameraActive = false;
    this.forceMouseMode = false;

    // Smoothed Normalized Coordinates (0 to 1)
    this.normX = 0.5;
    this.normY = 0.5;
    this.targetNormX = 0.5;
    this.targetNormY = 0.5;

    // Gesture State
    this.isDetected = false;
    this.isPinching = false;
    this.isOpenPalm = false;
    this.isTwoFingers = false;
    this.isFist = false;

    // Single-trigger flags
    this.pinchTriggered = false;
    this.palmTriggered = false;
    this.sonarTriggered = false;
    this.shieldActive = false;

    this.landmarks = [];

    // Cooldowns
    this.lastPinchTime = 0;
    this.lastPalmTime = 0;
    this.lastSonarTime = 0;

    this._initMediaPipe();
    this._setupMouseListeners();
  }

  _initMediaPipe() {
    if (typeof Hands === 'undefined') {
      console.warn('[Vision] MediaPipe Hands CDN not loaded. Running in Mouse Mode.');
      this.forceMouseMode = true;
      return;
    }

    try {
      this.hands = new Hands({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
      });

      this.hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 1,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });

      this.hands.onResults((results) => this._onHandResults(results));
    } catch (e) {
      console.warn('[Vision] Error initializing MediaPipe:', e);
      this.forceMouseMode = true;
    }
  }

  async startCamera() {
    if (this.forceMouseMode || !this.hands) return false;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
      });
      this.videoElement.srcObject = stream;
      await this.videoElement.play();

      if (typeof Camera !== 'undefined') {
        this.camera = new Camera(this.videoElement, {
          onFrame: async () => {
            if (this.isCameraActive && this.hands) {
              await this.hands.send({ image: this.videoElement });
            }
          },
          width: 640,
          height: 480,
        });
        await this.camera.start();
        this.isCameraActive = true;
        return true;
      }
    } catch (err) {
      console.warn('[Vision] Camera access rejected or unavailable:', err);
      this.forceMouseMode = true;
      this.isCameraActive = false;
      return false;
    }
    return false;
  }

  stopCamera() {
    if (this.camera) {
      try { this.camera.stop(); } catch (e) {}
    }
    if (this.videoElement && this.videoElement.srcObject) {
      this.videoElement.srcObject.getTracks().forEach(track => track.stop());
      this.videoElement.srcObject = null;
    }
    this.isCameraActive = false;
  }

  _setupMouseListeners() {
    window.addEventListener('mousemove', (e) => {
      if (!this.isCameraActive || this.forceMouseMode || !this.isDetected) {
        this.normX = e.clientX / window.innerWidth;
        this.normY = e.clientY / window.innerHeight;
      }
    });

    window.addEventListener('mousedown', (e) => {
      if (e.button === 0) { // LMB
        this.isPinching = true;
        this.pinchTriggered = true;
      } else if (e.button === 2) { // RMB
        e.preventDefault();
        this.sonarTriggered = true;
      }
    });

    window.addEventListener('mouseup', (e) => {
      if (e.button === 0) {
        this.isPinching = false;
      }
    });

    window.addEventListener('contextmenu', (e) => e.preventDefault());

    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space') {
        this.palmTriggered = true;
      } else if (e.key === 's' || e.key === 'S') {
        this.shieldActive = true;
      }
    });

    window.addEventListener('keyup', (e) => {
      if (e.key === 's' || e.key === 'S') {
        this.shieldActive = false;
      }
    });
  }

  _onHandResults(results) {
    if (this.forceMouseMode) return;

    if (!results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
      this.isDetected = false;
      this.isPinching = false;
      this.isOpenPalm = false;
      this.isTwoFingers = false;
      this.isFist = false;
      this._drawPip(null);
      return;
    }

    this.isDetected = true;
    const lms = results.multiHandLandmarks[0];
    this.landmarks = lms;

    // Index tip landmark 8, Thumb tip landmark 4, Wrist landmark 0
    const indexTip = lms[8];
    const thumbTip = lms[4];
    const wrist = lms[0];

    // Smooth cursor movement (Mirror X for natural interaction)
    const targetX = 1.0 - indexTip.x;
    const targetY = indexTip.y;
    this.normX = this.normX * (1 - CONFIG.SMOOTHING_ALPHA) + targetX * CONFIG.SMOOTHING_ALPHA;
    this.normY = this.normY * (1 - CONFIG.SMOOTHING_ALPHA) + targetY * CONFIG.SMOOTHING_ALPHA;

    // Gesture: Pinch (Distance between index tip and thumb tip)
    const pinchDist = Math.hypot(thumbTip.x - indexTip.x, thumbTip.y - indexTip.y);
    const now = performance.now() / 1000;

    if (pinchDist < CONFIG.PINCH_THRESHOLD) {
      if (!this.isPinching && now - this.lastPinchTime > 0.25) {
        this.pinchTriggered = true;
        this.lastPinchTime = now;
      }
      this.isPinching = true;
    } else if (pinchDist > CONFIG.PINCH_RELEASE) {
      this.isPinching = false;
    }

    // Extended finger count
    // Tip is further from wrist than PIP joint
    const fingersExtended = [
      Math.hypot(lms[8].x - wrist.x, lms[8].y - wrist.y) > Math.hypot(lms[6].x - wrist.x, lms[6].y - wrist.y),   // Index
      Math.hypot(lms[12].x - wrist.x, lms[12].y - wrist.y) > Math.hypot(lms[10].x - wrist.x, lms[10].y - wrist.y), // Middle
      Math.hypot(lms[16].x - wrist.x, lms[16].y - wrist.y) > Math.hypot(lms[14].x - wrist.x, lms[14].y - wrist.y), // Ring
      Math.hypot(lms[20].x - wrist.x, lms[20].y - wrist.y) > Math.hypot(lms[18].x - wrist.x, lms[18].y - wrist.y), // Pinky
    ];
    const countExtended = fingersExtended.filter(Boolean).length;

    // Gesture: Open Palm (All 4 non-thumb fingers extended)
    if (countExtended >= 4 && !this.isPinching) {
      this.isOpenPalm = true;
      if (now - this.lastPalmTime > 2.0) {
        this.palmTriggered = true;
        this.lastPalmTime = now;
      }
    } else {
      this.isOpenPalm = false;
    }

    // Gesture: Two Fingers (Index & Middle extended, Ring & Pinky curled)
    if (fingersExtended[0] && fingersExtended[1] && !fingersExtended[2] && !fingersExtended[3]) {
      this.isTwoFingers = true;
      if (now - this.lastSonarTime > 1.8) {
        this.sonarTriggered = true;
        this.lastSonarTime = now;
      }
    } else {
      this.isTwoFingers = false;
    }

    // Gesture: Fist (All 4 fingers curled)
    if (countExtended === 0 && pinchDist > 0.05) {
      this.isFist = true;
      this.shieldActive = true;
    } else {
      this.isFist = false;
      this.shieldActive = false;
    }

    this._drawPip(results);
    if (this.onGestureChange) this.onGestureChange();
  }

  _drawPip(results) {
    const ctx = this.pipCtx;
    const w = this.pipCanvas.width = 220;
    const h = this.pipCanvas.height = 140;

    ctx.clearRect(0, 0, w, h);

    if (!results || !results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
      ctx.fillStyle = 'rgba(2, 10, 24, 0.8)';
      ctx.fillRect(0, 0, w, h);
      ctx.fillStyle = '#64748b';
      ctx.font = '11px Outfit, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Searching Hand...', w / 2, h / 2);
      return;
    }

    // Draw camera image
    try {
      ctx.drawImage(results.image, 0, 0, w, h);
    } catch (e) {}

    // Dark semi-transparent tint for landmark glow
    ctx.fillStyle = 'rgba(2, 8, 20, 0.4)';
    ctx.fillRect(0, 0, w, h);

    // Draw hand skeleton landmarks
    const lms = results.multiHandLandmarks[0];
    const connections = [
      [0, 1], [1, 2], [2, 3], [3, 4],
      [0, 5], [5, 6], [6, 7], [7, 8],
      [5, 9], [9, 10], [10, 11], [11, 12],
      [9, 13], [13, 14], [14, 15], [15, 16],
      [13, 17], [17, 18], [18, 19], [19, 20],
      [0, 17],
    ];

    ctx.strokeStyle = '#00f5d4';
    ctx.lineWidth = 2;
    connections.forEach(([i, j]) => {
      ctx.beginPath();
      ctx.moveTo(lms[i].x * w, lms[i].y * h);
      ctx.lineTo(lms[j].x * w, lms[j].y * h);
      ctx.stroke();
    });

    // Draw landmark joints
    lms.forEach((pt, idx) => {
      ctx.beginPath();
      ctx.arc(pt.x * w, pt.y * h, idx === 8 || idx === 4 ? 4 : 2.5, 0, Math.PI * 2);
      ctx.fillStyle = idx === 8 ? '#ffd166' : (idx === 4 ? '#ff3366' : '#00b4d8');
      ctx.fill();
    });

    // Mirror landmark to calibration canvas if active
    if (this.calibCtx) {
      const cw = this.calibCanvas.width = 380;
      const ch = this.calibCanvas.height = 280;
      this.calibCtx.drawImage(this.pipCanvas, 0, 0, cw, ch);
    }
  }

  consumePinch() {
    const val = this.pinchTriggered;
    this.pinchTriggered = false;
    return val;
  }

  consumePalm() {
    const val = this.palmTriggered;
    this.palmTriggered = false;
    return val;
  }

  consumeSonar() {
    const val = this.sonarTriggered;
    this.sonarTriggered = false;
    return val;
  }
}

// ==============================================================================
// 3. Particle System (Bubbles, Caustics, Sonar Waves, Sparks)
// ==============================================================================
class ParticleSystem {
  constructor() {
    this.bubbles = [];
    this.sparkles = [];
    this.sonarRings = [];
    this.currentStreams = [];
    this.causticRays = [];

    // Pre-populate ambient sea bubbles
    for (let i = 0; i < 45; i++) {
      this.bubbles.push(this._createAmbientBubble(true));
    }

    // Sunlight caustics
    for (let i = 0; i < 7; i++) {
      this.causticRays.push({
        x: Math.random() * window.innerWidth,
        width: 80 + Math.random() * 120,
        speed: 0.15 + Math.random() * 0.25,
        alpha: 0.04 + Math.random() * 0.06,
        phase: Math.random() * Math.PI * 2,
      });
    }
  }

  _createAmbientBubble(randomY = false) {
    return {
      x: Math.random() * window.innerWidth,
      y: randomY ? Math.random() * window.innerHeight : window.innerHeight + 10,
      radius: 1.5 + Math.random() * 4.5,
      speedY: 0.8 + Math.random() * 2.2,
      driftX: (Math.random() - 0.5) * 0.6,
      wobbleSpeed: 1.5 + Math.random() * 2.5,
      wobbleAmount: 0.8 + Math.random() * 1.5,
      phase: Math.random() * Math.PI * 2,
      alpha: 0.25 + Math.random() * 0.45,
    };
  }

  addRegulatorBubbles(x, y, count = 3) {
    for (let i = 0; i < count; i++) {
      this.bubbles.push({
        x: x + (Math.random() - 0.5) * 8,
        y: y + (Math.random() - 0.5) * 8,
        radius: 2.0 + Math.random() * 4.0,
        speedY: 2.5 + Math.random() * 2.0,
        driftX: (Math.random() - 0.5) * 1.2,
        wobbleSpeed: 2.0 + Math.random() * 2.0,
        wobbleAmount: 1.2,
        phase: Math.random() * Math.PI * 2,
        alpha: 0.6,
      });
    }
  }

  addSparkles(x, y, color = '#ffd166', count = 15) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 1.5 + Math.random() * 4.5;
      this.sparkles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        radius: 2 + Math.random() * 3,
        color,
        life: 1.0,
        decay: 0.02 + Math.random() * 0.03,
      });
    }
  }

  addSonarWave(x, y) {
    this.sonarRings.push({
      x,
      y,
      radius: 10,
      maxRadius: Math.max(window.innerWidth, window.innerHeight) * 0.85,
      speed: 480,
      alpha: 0.9,
    });
  }

  addCurrentWave(direction = 1) {
    for (let i = 0; i < 40; i++) {
      this.currentStreams.push({
        x: direction > 0 ? -20 : window.innerWidth + 20,
        y: Math.random() * window.innerHeight,
        vx: direction * (400 + Math.random() * 300),
        vy: (Math.random() - 0.5) * 40,
        length: 30 + Math.random() * 60,
        alpha: 0.6,
        life: 1.2,
      });
    }
  }

  update(dt) {
    // 1. Ambient Bubbles
    for (let i = this.bubbles.length - 1; i >= 0; i--) {
      const b = this.bubbles[i];
      b.y -= b.speedY;
      b.phase += dt * b.wobbleSpeed;
      b.x += Math.sin(b.phase) * b.wobbleAmount + b.driftX;
      if (b.y < -20) {
        this.bubbles[i] = this._createAmbientBubble(false);
      }
    }

    // 2. Sparkles
    for (let i = this.sparkles.length - 1; i >= 0; i--) {
      const s = this.sparkles[i];
      s.x += s.vx;
      s.y += s.vy;
      s.vx *= 0.94;
      s.vy *= 0.94;
      s.life -= s.decay;
      if (s.life <= 0) this.sparkles.splice(i, 1);
    }

    // 3. Sonar Rings
    for (let i = this.sonarRings.length - 1; i >= 0; i--) {
      const ring = this.sonarRings[i];
      ring.radius += ring.speed * dt;
      ring.alpha = Math.max(0, 1.0 - ring.radius / ring.maxRadius);
      if (ring.radius >= ring.maxRadius || ring.alpha <= 0) {
        this.sonarRings.splice(i, 1);
      }
    }

    // 4. Current Streams
    for (let i = this.currentStreams.length - 1; i >= 0; i--) {
      const c = this.currentStreams[i];
      c.x += c.vx * dt;
      c.y += c.vy * dt;
      c.life -= dt;
      if (c.life <= 0 || c.x < -100 || c.x > window.innerWidth + 100) {
        this.currentStreams.splice(i, 1);
      }
    }

    // 5. Caustic Sunbeams
    this.causticRays.forEach((ray) => {
      ray.phase += dt * ray.speed;
      ray.currentAlpha = ray.alpha + Math.sin(ray.phase) * 0.02;
    });
  }

  render(ctx) {
    // Caustic Sunbeams from ocean surface
    this.causticRays.forEach((ray) => {
      const grad = ctx.createLinearGradient(ray.x, 0, ray.x + 80, window.innerHeight);
      grad.addColorStop(0, `rgba(0, 245, 212, ${ray.currentAlpha * 2.2})`);
      grad.addColorStop(0.5, `rgba(0, 180, 216, ${ray.currentAlpha})`);
      grad.addColorStop(1, 'rgba(0, 180, 216, 0)');

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.moveTo(ray.x, 0);
      ctx.lineTo(ray.x + ray.width, 0);
      ctx.lineTo(ray.x + ray.width + 120, window.innerHeight);
      ctx.lineTo(ray.x - 40, window.innerHeight);
      ctx.closePath();
      ctx.fill();
    });

    // Bubbles
    ctx.lineWidth = 1.2;
    this.bubbles.forEach((b) => {
      ctx.beginPath();
      ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(180, 240, 255, ${b.alpha * 0.4})`;
      ctx.fill();
      ctx.strokeStyle = `rgba(255, 255, 255, ${b.alpha})`;
      ctx.stroke();

      // Bubble highlight glint
      ctx.beginPath();
      ctx.arc(b.x - b.radius * 0.35, b.y - b.radius * 0.35, b.radius * 0.3, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 255, 255, ${b.alpha * 0.9})`;
      ctx.fill();
    });

    // Water Current Streams
    this.currentStreams.forEach((c) => {
      ctx.beginPath();
      ctx.moveTo(c.x, c.y);
      ctx.lineTo(c.x - (c.vx > 0 ? c.length : -c.length), c.y);
      ctx.strokeStyle = `rgba(0, 245, 212, ${c.alpha * 0.45})`;
      ctx.lineWidth = 2.5;
      ctx.stroke();
    });

    // Sonar Shockwaves
    this.sonarRings.forEach((ring) => {
      ctx.beginPath();
      ctx.arc(ring.x, ring.y, ring.radius, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(0, 245, 212, ${ring.alpha})`;
      ctx.lineWidth = 4.0;
      ctx.shadowColor = '#00f5d4';
      ctx.shadowBlur = 15;
      ctx.stroke();
      ctx.shadowBlur = 0;
    });

    // Sparkles
    this.sparkles.forEach((s) => {
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.radius * s.life, 0, Math.PI * 2);
      ctx.fillStyle = s.color;
      ctx.shadowColor = s.color;
      ctx.shadowBlur = 8;
      ctx.fill();
      ctx.shadowBlur = 0;
    });
  }
}

// ==============================================================================
// 4. Scuba Explorer Player Entity
// ==============================================================================
class Player {
  constructor() {
    this.x = window.innerWidth / 2;
    this.y = window.innerHeight / 2;
    this.vx = 0;
    this.vy = 0;
    this.angle = 0;
    this.facingRight = true;
    this.finCycle = 0;
    this.carriedTreasure = null;
    this.bubbleTimer = 0;
    this.shieldTimer = 0;
  }

  update(dt, targetX, targetY, isShieldActive, particles) {
    // Hydrodynamic Spring Physics toward Hand Cursor
    const dx = targetX - this.x;
    const dy = targetY - this.y;
    const dist = Math.hypot(dx, dy);

    const speed = 7.5;
    this.vx = this.vx * 0.82 + dx * speed * dt;
    this.vy = this.vy * 0.82 + dy * speed * dt;

    this.x += this.vx;
    this.y += this.vy;

    // Boundary constraints
    this.x = Math.max(50, Math.min(window.innerWidth - 50, this.x));
    this.y = Math.max(50, Math.min(window.innerHeight - 80, this.y));

    // Facing direction & Fin kicking
    if (Math.abs(this.vx) > 0.5) {
      this.facingRight = this.vx > 0;
    }
    const movementSpeed = Math.hypot(this.vx, this.vy);
    this.finCycle += movementSpeed * 0.25 + dt * 4;

    // Pitch tilt angle based on velocity
    const targetAngle = Math.atan2(this.vy, Math.abs(this.vx) + 0.1) * (this.facingRight ? 0.45 : -0.45);
    this.angle += (targetAngle - this.angle) * 0.12;

    // Regulator air bubbles
    this.bubbleTimer += dt;
    if (this.bubbleTimer > 1.2 && particles) {
      const mouthX = this.x + (this.facingRight ? 24 : -24);
      const mouthY = this.y - 4;
      particles.addRegulatorBubbles(mouthX, mouthY, 2);
      this.bubbleTimer = 0;
    }

    if (isShieldActive) {
      this.shieldTimer += dt * 5;
    }
  }

  render(ctx, isShieldActive) {
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate(this.angle);
    if (!this.facingRight) ctx.scale(-1, 1);

    // 1. Directional Flashlight Beam
    const beamGrad = ctx.createRadialGradient(28, -2, 5, 140, -2, 110);
    beamGrad.addColorStop(0, 'rgba(255, 255, 230, 0.45)');
    beamGrad.addColorStop(0.5, 'rgba(0, 245, 212, 0.15)');
    beamGrad.addColorStop(1, 'rgba(0, 180, 216, 0)');
    ctx.fillStyle = beamGrad;
    ctx.beginPath();
    ctx.moveTo(25, -4);
    ctx.lineTo(220, -55);
    ctx.lineTo(220, 45);
    ctx.closePath();
    ctx.fill();

    // 2. Flutter Twin Fins
    const finAngle = Math.sin(this.finCycle) * 0.35;
    ctx.save();
    ctx.translate(-26, 4);
    ctx.rotate(finAngle);
    ctx.fillStyle = '#00f5d4';
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(-24, -8);
    ctx.lineTo(-28, 6);
    ctx.closePath();
    ctx.fill();
    ctx.restore();

    // 3. Scuba Diver Wetsuit Body
    ctx.fillStyle = '#08254f';
    ctx.beginPath();
    ctx.ellipse(0, 2, 26, 13, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#00b4d8';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // 4. Oxygen Tank on Back
    ctx.fillStyle = '#ffd166';
    ctx.beginPath();
    ctx.roundRect(-14, -13, 24, 7, 3);
    ctx.fill();
    ctx.strokeStyle = '#e6af2e';
    ctx.stroke();

    // 5. Diving Helmet & Visor
    ctx.fillStyle = '#1e3a5f';
    ctx.beginPath();
    ctx.arc(18, -2, 11, 0, Math.PI * 2);
    ctx.fill();

    // Glowing Neon Cyan Visor
    ctx.fillStyle = '#00f5d4';
    ctx.shadowColor = '#00f5d4';
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.ellipse(22, -2, 6, 8, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    // Diver Hands (Extended forward)
    ctx.fillStyle = '#ff758c';
    ctx.beginPath();
    ctx.arc(22, 10, 4, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();

    // 6. Energy Shield Dome Forcefield
    if (isShieldActive) {
      ctx.save();
      ctx.translate(this.x, this.y);
      const shieldPulse = Math.sin(this.shieldTimer) * 4;
      const radius = 46 + shieldPulse;

      ctx.beginPath();
      ctx.arc(0, 0, radius, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0, 245, 212, 0.18)';
      ctx.fill();

      ctx.strokeStyle = '#00f5d4';
      ctx.lineWidth = 3;
      ctx.shadowColor = '#00f5d4';
      ctx.shadowBlur = 18;
      ctx.stroke();

      // Outer hexagonal energy ring
      ctx.beginPath();
      ctx.arc(0, 0, radius + 6, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(255, 209, 102, 0.6)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([8, 6]);
      ctx.stroke();

      ctx.restore();
    }
  }
}

// ==============================================================================
// 5. Game Level, Treasures, Hazards & Vault Definitions
// ==============================================================================
const TREASURE_TYPES = {
  COMMON: { name: 'Pearl Shell', points: 50, color: '#e2e8f0', icon: '🐚', radius: 18 },
  GOLD: { name: 'Gold Doubloons', points: 100, color: '#ffd166', icon: '🪙', radius: 20 },
  RARE: { name: 'Ancient Chalice', points: 250, color: '#00f5d4', icon: '🏆', radius: 22 },
  ANCIENT: { name: 'Neptune Crown', points: 500, color: '#ff758c', icon: '👑', radius: 25 },
  MIMIC: { name: 'Cursed Mimic', points: -50, color: '#ff3366', icon: '💀', radius: 20, isHazard: true },
};

class Treasure {
  constructor(type, x, y) {
    this.type = type;
    this.x = x;
    this.y = y;
    this.vx = 0;
    this.vy = 0;
    this.radius = type.radius;
    this.isCarried = false;
    this.isDeposited = false;
    this.bobPhase = Math.random() * Math.PI * 2;
    this.revealed = false; // Revealed by Sonar
  }

  update(dt) {
    if (this.isCarried || this.isDeposited) return;
    this.bobPhase += dt * 1.8;
    this.y += Math.sin(this.bobPhase) * 0.4;

    // Apply loose drag from currents
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    this.vx *= 0.95;
    this.vy *= 0.95;
  }

  render(ctx) {
    if (this.isDeposited) return;

    ctx.save();
    ctx.translate(this.x, this.y);

    // Glowing aura
    ctx.beginPath();
    ctx.arc(0, 0, this.radius + 6, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${this.type.isHazard ? '255, 51, 102' : '255, 209, 102'}, 0.25)`;
    ctx.fill();

    // Treasure body icon
    ctx.font = `${this.radius * 1.4}px Outfit, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(this.type.icon, 0, 0);

    // Sonar reveal highlight ring
    if (this.revealed) {
      ctx.beginPath();
      ctx.arc(0, 0, this.radius + 10, 0, Math.PI * 2);
      ctx.strokeStyle = '#00f5d4';
      ctx.lineWidth = 2.5;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
    }

    ctx.restore();
  }
}

class MarineHazard {
  constructor(type, x, y, speedX = 120) {
    this.type = type; // 'SHARK', 'MINE', 'JELLYFISH', 'OXYGEN'
    this.x = x;
    this.y = y;
    this.speedX = speedX;
    this.radius = type === 'SHARK' ? 34 : (type === 'MINE' ? 22 : 18);
    this.cycle = Math.random() * Math.PI * 2;
  }

  update(dt, playerX, playerY) {
    this.cycle += dt * 2.5;

    if (this.type === 'SHARK') {
      this.x += this.speedX * dt;
      // Reverse at screen borders
      if (this.x < 50) { this.x = 50; this.speedX = Math.abs(this.speedX); }
      if (this.x > window.innerWidth - 50) { this.x = window.innerWidth - 50; this.speedX = -Math.abs(this.speedX); }
      this.y += Math.sin(this.cycle) * 0.8;
    } else if (this.type === 'JELLYFISH') {
      this.y += Math.sin(this.cycle) * 1.4;
      this.x += Math.cos(this.cycle * 0.5) * 0.5;
    } else if (this.type === 'MINE') {
      this.y += Math.sin(this.cycle) * 0.5;
    } else if (this.type === 'OXYGEN') {
      this.y += Math.sin(this.cycle) * 0.6;
    }
  }

  render(ctx) {
    ctx.save();
    ctx.translate(this.x, this.y);

    if (this.type === 'SHARK') {
      const facingRight = this.speedX > 0;
      if (!facingRight) ctx.scale(-1, 1);

      // Sleek predatory shark silhouette
      ctx.fillStyle = '#334155';
      ctx.beginPath();
      ctx.ellipse(0, 0, 36, 16, 0, 0, Math.PI * 2);
      ctx.fill();

      // Dorsal Fin
      ctx.beginPath();
      ctx.moveTo(-6, -15);
      ctx.lineTo(6, -30);
      ctx.lineTo(16, -14);
      ctx.closePath();
      ctx.fill();

      // Tail
      const tailAngle = Math.sin(this.cycle * 3) * 0.3;
      ctx.save();
      ctx.translate(-34, 0);
      ctx.rotate(tailAngle);
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(-20, -18);
      ctx.lineTo(-20, 18);
      ctx.closePath();
      ctx.fill();
      ctx.restore();

      // Menacing Eye
      ctx.fillStyle = '#ff3366';
      ctx.beginPath();
      ctx.arc(22, -4, 3, 0, Math.PI * 2);
      ctx.fill();
    } else if (this.type === 'MINE') {
      // Spiked Naval Mine
      ctx.fillStyle = '#1e293b';
      ctx.beginPath();
      ctx.arc(0, 0, 16, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#ff3366';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Spikes
      for (let i = 0; i < 8; i++) {
        const ang = (i * Math.PI) / 4;
        ctx.beginPath();
        ctx.moveTo(Math.cos(ang) * 16, Math.sin(ang) * 16);
        ctx.lineTo(Math.cos(ang) * 24, Math.sin(ang) * 24);
        ctx.stroke();
      }

      // Blinking red diode
      const blink = Math.sin(this.cycle * 5) > 0;
      ctx.fillStyle = blink ? '#ff3366' : '#880808';
      ctx.beginPath();
      ctx.arc(0, 0, 4, 0, Math.PI * 2);
      ctx.fill();
    } else if (this.type === 'JELLYFISH') {
      // Bioluminescent Jellyfish
      ctx.fillStyle = 'rgba(255, 117, 140, 0.7)';
      ctx.beginPath();
      ctx.arc(0, -4, 16, Math.PI, 0);
      ctx.closePath();
      ctx.fill();

      // Flowing tentacles
      ctx.strokeStyle = 'rgba(255, 180, 200, 0.8)';
      ctx.lineWidth = 1.8;
      for (let i = -10; i <= 10; i += 5) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.quadraticCurveTo(i + Math.sin(this.cycle + i) * 6, 12, i, 24);
        ctx.stroke();
      }
    } else if (this.type === 'OXYGEN') {
      // Oxygen Pod
      ctx.beginPath();
      ctx.arc(0, 0, 16, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0, 245, 212, 0.35)';
      ctx.fill();
      ctx.strokeStyle = '#00f5d4';
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.font = '16px Outfit, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('🫧', 0, 0);
    }

    ctx.restore();
  }
}

// Seafloor Vault Chest Entity
class SeafloorVault {
  constructor() {
    this.x = window.innerWidth / 2;
    this.y = window.innerHeight - 60;
    this.width = 130;
    this.height = 70;
    this.radius = 80;
    this.pulse = 0;
  }

  resize() {
    this.x = window.innerWidth / 2;
    this.y = window.innerHeight - 60;
  }

  update(dt) {
    this.pulse += dt * 3;
  }

  render(ctx) {
    ctx.save();
    ctx.translate(this.x, this.y);

    // Glowing Deposit Aura Zone
    const auraRadius = this.radius + Math.sin(this.pulse) * 6;
    ctx.beginPath();
    ctx.arc(0, 0, auraRadius, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 245, 212, 0.12)';
    ctx.fill();
    ctx.strokeStyle = '#00f5d4';
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 6]);
    ctx.stroke();

    // Vault Base
    ctx.fillStyle = '#654321';
    ctx.beginPath();
    ctx.roundRect(-45, -20, 90, 40, 8);
    ctx.fill();
    ctx.strokeStyle = '#ffd166';
    ctx.lineWidth = 3;
    ctx.stroke();

    // Gilded Trim & Lock
    ctx.fillStyle = '#ffd166';
    ctx.beginPath();
    ctx.rect(-10, -10, 20, 20);
    ctx.fill();

    // Label
    ctx.font = '10px Outfit, sans-serif';
    ctx.fillStyle = '#ffd166';
    ctx.textAlign = 'center';
    ctx.fillText('VAULT DEPOSIT', 0, 32);

    ctx.restore();
  }
}

// ==============================================================================
// 6. Master Game Engine & UI State Controller
// ==============================================================================
class GameEngine {
  constructor() {
    this.canvas = document.getElementById('game-canvas');
    this.ctx = this.canvas.getContext('2d');

    this.sound = new SoundEngine();
    this.vision = new VisionTracker(() => this.updateGestureUI());
    this.particles = new ParticleSystem();
    this.player = new Player();
    this.vault = new SeafloorVault();

    // State Variables
    this.state = 'MAIN_MENU'; // 'MAIN_MENU', 'PLAYING', 'PAUSED', 'LEVEL_COMPLETE', 'GAME_OVER', 'VICTORY'
    this.levelId = 1;
    this.score = 0;
    this.oxygen = CONFIG.INITIAL_OXYGEN;
    this.combo = 1.0;
    this.comboCount = 0;
    this.sonarCharges = 3;
    this.relicsStored = 0;
    this.levelTimeRemaining = 60;
    this.carriedTreasure = null;

    // Entities
    this.treasures = [];
    this.hazards = [];

    // Screen Dimensions
    this._resizeCanvas();
    window.addEventListener('resize', () => this._resizeCanvas());

    this.lastTime = performance.now();
    this._initUI();
    this._buildCards();

    // Start 60 FPS Render Loop
    requestAnimationFrame((t) => this._loop(t));
  }

  _resizeCanvas() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
    this.vault.resize();
  }

  _initUI() {
    // Menu Button bindings
    document.getElementById('btn-start-game').addEventListener('click', () => {
      this.sound.init();
      this.startLevel(1);
    });

    document.getElementById('btn-open-levels').addEventListener('click', () => this._showModal('screen-level-select'));
    document.getElementById('btn-back-from-levels').addEventListener('click', () => this._showModal('screen-main-menu'));

    document.getElementById('btn-open-challenges').addEventListener('click', () => this._showModal('screen-challenges'));
    document.getElementById('btn-back-from-challenges').addEventListener('click', () => this._showModal('screen-main-menu'));

    document.getElementById('btn-open-instructions').addEventListener('click', () => this._showModal('screen-how-to-play'));
    document.getElementById('btn-back-from-guide').addEventListener('click', () => this._showModal('screen-main-menu'));

    document.getElementById('btn-open-camera-check').addEventListener('click', () => {
      this._showModal('screen-camera-check');
      this.vision.startCamera();
    });
    document.getElementById('btn-back-from-calib').addEventListener('click', () => this._showModal('screen-main-menu'));
    document.getElementById('btn-calib-start').addEventListener('click', () => {
      this.sound.init();
      this.startLevel(1);
    });

    // In-Game Buttons
    document.getElementById('btn-pause-toggle').addEventListener('click', () => this.pauseGame());
    document.getElementById('btn-resume-game').addEventListener('click', () => this.resumeGame());
    document.getElementById('btn-restart-level').addEventListener('click', () => this.startLevel(this.levelId));
    document.getElementById('btn-pause-to-menu').addEventListener('click', () => this.returnToMenu());

    document.getElementById('btn-next-level').addEventListener('click', () => this.startLevel(this.levelId + 1));
    document.getElementById('btn-win-to-menu').addEventListener('click', () => this.returnToMenu());

    document.getElementById('btn-retry-level').addEventListener('click', () => this.startLevel(this.levelId));
    document.getElementById('btn-over-to-menu').addEventListener('click', () => this.returnToMenu());

    document.getElementById('btn-play-again').addEventListener('click', () => this.startLevel(1));
    document.getElementById('btn-vic-to-menu').addEventListener('click', () => this.returnToMenu());

    // Utility Toggles
    const soundBtn = document.getElementById('btn-sound-toggle');
    soundBtn.addEventListener('click', () => {
      const active = this.sound.toggleMute();
      soundBtn.textContent = active ? '🔊' : '🔇';
    });

    const fullBtn = document.getElementById('btn-fullscreen-toggle');
    fullBtn.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    });

    // PIP Camera Buttons
    document.getElementById('pip-minimize-btn').addEventListener('click', () => {
      document.getElementById('camera-pip-container').classList.toggle('minimized');
    });

    const camBtn = document.getElementById('camera-toggle-btn');
    camBtn.addEventListener('click', async () => {
      if (this.vision.isCameraActive) {
        this.vision.stopCamera();
        camBtn.textContent = '📷 Start Cam';
      } else {
        const ok = await this.vision.startCamera();
        camBtn.textContent = ok ? '📷 Stop Cam' : '📷 Unavailable';
      }
    });

    const mouseBtn = document.getElementById('mouse-mode-btn');
    mouseBtn.addEventListener('click', () => {
      this.vision.forceMouseMode = !this.vision.forceMouseMode;
      mouseBtn.textContent = this.vision.forceMouseMode ? '🖐️ Hand Mode' : '🖱️ Mouse Mode';
    });
  }

  _buildCards() {
    const levels = [
      { id: 1, title: 'Coral Shallows', desc: 'Sunny reefs with sparkling pearl shells.', req: 3, time: 60, hazards: 'Gentle Currents' },
      { id: 2, title: 'Sunken Galleon', desc: 'Wreckage laden with gold doubloons and sea mines.', req: 4, time: 60, hazards: 'Sea Mines' },
      { id: 3, title: 'Abyssal Trench', desc: 'Pitch-black waters guarded by patrol sharks.', req: 5, time: 55, hazards: 'Patrol Sharks' },
      { id: 4, title: 'Sunken Atlantis', desc: 'Ancient temples with electric jellyfish swarms.', req: 6, time: 50, hazards: 'Jellyfish Swarms' },
      { id: 5, title: 'The Kraken’s Abyss', desc: 'The deepest ocean floor holding legendary crowns.', req: 7, time: 45, hazards: 'Extreme Hazards' },
    ];

    const levelContainer = document.getElementById('level-cards-container');
    levelContainer.innerHTML = levels.map((lvl) => `
      <div class="level-card" onclick="game.startLevel(${lvl.id})">
        <div class="card-num">EXPEDITION 0${lvl.id}</div>
        <div class="card-title">${lvl.title}</div>
        <div class="card-desc">${lvl.desc}</div>
        <div class="card-meta-row">
          <span>🎯 Stored: ${lvl.req}</span>
          <span>⏱️ ${lvl.time}s</span>
          <span>⚠️ ${lvl.hazards}</span>
        </div>
      </div>
    `).join('');

    const challenges = [
      { id: 1, title: '⚡ Speed Diver Trial', desc: 'Collect 4 rare treasures under intense 35-second pressure.', time: 35, req: 4 },
      { id: 2, title: '🦈 Shark Frenzy', desc: 'Multiple apex sharks patrol the seabed. Keep your shield primed!', time: 50, req: 5 },
      { id: 3, title: '💣 Abyssal Minefield', desc: 'Dense minefield zone. Sonar pulses are essential for survival.', time: 55, req: 5 },
    ];

    const chalContainer = document.getElementById('challenge-cards-container');
    chalContainer.innerHTML = challenges.map((ch) => `
      <div class="challenge-card" onclick="game.startChallenge(${ch.id})">
        <div class="card-num">CHALLENGE 0${ch.id}</div>
        <div class="card-title">${ch.title}</div>
        <div class="card-desc">${ch.desc}</div>
        <div class="card-meta-row">
          <span>🎯 Relics: ${ch.req}</span>
          <span>⏱️ ${ch.time}s</span>
        </div>
      </div>
    `).join('');
  }

  _showModal(id) {
    const modals = [
      'screen-main-menu', 'screen-level-select', 'screen-challenges',
      'screen-how-to-play', 'screen-camera-check', 'screen-pause',
      'screen-level-complete', 'screen-game-over', 'screen-victory'
    ];
    modals.forEach((m) => {
      const el = document.getElementById(m);
      if (el) el.style.display = (m === id) ? 'block' : 'none';
    });
    document.getElementById('ui-overlay').style.display = id ? 'flex' : 'none';
  }

  startLevel(lvlId) {
    this.sound.init();
    if (lvlId > 5) {
      this.triggerVictory();
      return;
    }

    this.levelId = lvlId;
    this.state = 'PLAYING';
    this.oxygen = CONFIG.INITIAL_OXYGEN;
    this.combo = 1.0;
    this.comboCount = 0;
    this.sonarCharges = 3;
    this.relicsStored = 0;
    this.carriedTreasure = null;

    const reqDeposits = 2 + lvlId;
    this.targetRelics = reqDeposits;
    this.levelTimeRemaining = Math.max(40, 65 - lvlId * 4);

    this._spawnLevelEntities(lvlId);

    // Hide UI modal and display HUD
    this._showModal(null);
    document.getElementById('game-hud').style.display = 'flex';
    document.getElementById('hud-level-title').textContent = `LEVEL ${lvlId}: DIVE EXPEDITION`;

    this.updateHUD();
  }

  startChallenge(chId) {
    this.sound.init();
    this.levelId = 10 + chId;
    this.state = 'PLAYING';
    this.oxygen = CONFIG.INITIAL_OXYGEN;
    this.combo = 1.0;
    this.comboCount = 0;
    this.sonarCharges = 4;
    this.relicsStored = 0;
    this.carriedTreasure = null;
    this.targetRelics = 4;
    this.levelTimeRemaining = 40;

    this.treasures = [];
    this.hazards = [];

    // Spawn challenge tailored items
    for (let i = 0; i < 7; i++) {
      this.treasures.push(new Treasure(TREASURE_TYPES.GOLD, 100 + Math.random() * (window.innerWidth - 200), 120 + Math.random() * (window.innerHeight - 250)));
    }
    if (chId === 2) { // Shark frenzy
      this.hazards.push(new MarineHazard('SHARK', 100, 200, 160));
      this.hazards.push(new MarineHazard('SHARK', 300, 380, -180));
    } else if (chId === 3) { // Minefield
      for (let i = 0; i < 6; i++) {
        this.hazards.push(new MarineHazard('MINE', 150 + Math.random() * (window.innerWidth - 300), 150 + Math.random() * (window.innerHeight - 300)));
      }
    }

    this._showModal(null);
    document.getElementById('game-hud').style.display = 'flex';
    document.getElementById('hud-level-title').textContent = `ABYSSAL CHALLENGE 0${chId}`;
    this.updateHUD();
  }

  _spawnLevelEntities(lvlId) {
    this.treasures = [];
    this.hazards = [];

    const w = window.innerWidth;
    const h = window.innerHeight;

    // Spawn Relics
    const count = 4 + lvlId * 2;
    for (let i = 0; i < count; i++) {
      let type = TREASURE_TYPES.COMMON;
      const rand = Math.random();
      if (rand > 0.85) type = TREASURE_TYPES.ANCIENT;
      else if (rand > 0.6) type = TREASURE_TYPES.RARE;
      else if (rand > 0.35) type = TREASURE_TYPES.GOLD;
      else if (rand < 0.1 && lvlId >= 2) type = TREASURE_TYPES.MIMIC;

      const tx = 80 + Math.random() * (w - 160);
      const ty = 120 + Math.random() * (h - 260);
      this.treasures.push(new Treasure(type, tx, ty));
    }

    // Spawn Hazards based on level
    if (lvlId >= 2) {
      for (let i = 0; i < lvlId; i++) {
        this.hazards.push(new MarineHazard('MINE', 120 + Math.random() * (w - 240), 150 + Math.random() * (h - 300)));
      }
    }
    if (lvlId >= 3) {
      this.hazards.push(new MarineHazard('SHARK', 100, 220, 140));
    }
    if (lvlId >= 4) {
      this.hazards.push(new MarineHazard('JELLYFISH', w / 3, 260));
      this.hazards.push(new MarineHazard('JELLYFISH', (w * 2) / 3, 340));
    }

    // Spawn 2 Oxygen Pods
    for (let i = 0; i < 2; i++) {
      this.hazards.push(new MarineHazard('OXYGEN', 150 + Math.random() * (w - 300), 150 + Math.random() * (h - 300)));
    }
  }

  pauseGame() {
    if (this.state !== 'PLAYING') return;
    this.state = 'PAUSED';
    this._showModal('screen-pause');
  }

  resumeGame() {
    if (this.state !== 'PAUSED') return;
    this.state = 'PLAYING';
    this._showModal(null);
  }

  returnToMenu() {
    this.state = 'MAIN_MENU';
    document.getElementById('game-hud').style.display = 'none';
    this._showModal('screen-main-menu');
  }

  triggerLevelComplete() {
    this.state = 'LEVEL_COMPLETE';
    this.sound.playWin();
    document.getElementById('win-level-title').textContent = `Expedition Level ${this.levelId} Cleared!`;
    document.getElementById('win-score-val').textContent = this.score.toLocaleString();
    document.getElementById('win-time-val').textContent = `${Math.round(60 - this.levelTimeRemaining)}s`;
    document.getElementById('win-combo-val').textContent = `x${this.combo.toFixed(1)}`;
    this._showModal('screen-level-complete');
  }

  triggerGameOver(reason) {
    this.state = 'GAME_OVER';
    this.sound.playDamage();
    document.getElementById('game-over-cause').textContent = reason;
    document.getElementById('over-score-val').textContent = this.score.toLocaleString();
    document.getElementById('over-relics-val').textContent = `${this.relicsStored} / ${this.targetRelics}`;
    this._showModal('screen-game-over');
  }

  triggerVictory() {
    this.state = 'VICTORY';
    this.sound.playWin();
    document.getElementById('vic-score-val').textContent = this.score.toLocaleString();
    this._showModal('screen-victory');
  }

  // ==============================================================================
  // 7. Update & Collision Dynamics
  // ==============================================================================
  _update(dt) {
    // 1. Cursor Target coordinates
    const cursorX = this.vision.normX * window.innerWidth;
    const cursorY = this.vision.normY * window.innerHeight;

    // 2. Gesture Actions
    // A. Sonar Trigger
    if (this.vision.consumeSonar() && this.sonarCharges > 0) {
      this.sonarCharges--;
      this.sound.playSonar();
      this.particles.addSonarWave(this.player.x, this.player.y);
      this.treasures.forEach((t) => t.revealed = true);
      setTimeout(() => this.treasures.forEach((t) => t.revealed = false), CONFIG.SONAR_DURATION * 1000);
      this.updateHUD();
    }

    // B. Water Current Trigger
    if (this.vision.consumePalm()) {
      this.sound.playCurrent();
      this.particles.addCurrentWave(this.player.facingRight ? 1 : -1);
      const pushX = (this.player.facingRight ? 1 : -1) * 350;
      this.treasures.forEach((t) => {
        if (!t.isCarried) t.vx += pushX;
      });
      this.hazards.forEach((h) => {
        if (h.type === 'JELLYFISH' || h.type === 'SHARK') h.x += pushX * 0.4;
      });
    }

    // 3. Update Player & Particles
    const isShield = this.vision.shieldActive;
    if (isShield) this.sound.playShield();
    this.player.update(dt, cursorX, cursorY, isShield, this.particles);
    this.particles.update(dt);
    this.vault.update(dt);

    if (this.state !== 'PLAYING') return;

    // 4. Deplete Oxygen & Timer
    this.oxygen -= CONFIG.OXYGEN_DEPLETION_RATE * dt;
    this.levelTimeRemaining -= dt;

    if (this.oxygen <= 0) {
      this.triggerGameOver('Oxygen depleted in deep waters!');
      return;
    }
    if (this.levelTimeRemaining <= 0) {
      this.triggerGameOver('Expedition time expired!');
      return;
    }

    // 5. Update Treasures & Grab / Carry / Deposit Logic
    const isPinch = this.vision.isPinching;

    // Carrying relic attached to player hands
    if (this.carriedTreasure) {
      this.carriedTreasure.x = this.player.x + (this.player.facingRight ? 24 : -24);
      this.carriedTreasure.y = this.player.y + 12;

      // Deposit at Seafloor Vault
      const distToVault = Math.hypot(this.player.x - this.vault.x, this.player.y - this.vault.y);
      if (!isPinch) { // Pinch Released!
        if (distToVault < this.vault.radius) {
          // Deposit Success!
          this.relicsStored++;
          this.carriedTreasure.isDeposited = true;
          const pts = Math.round(this.carriedTreasure.type.points * this.combo);
          this.score += pts;
          this.comboCount++;
          this.combo = Math.min(3.5, 1.0 + this.comboCount * 0.25);

          this.sound.playDeposit();
          this.particles.addSparkles(this.vault.x, this.vault.y, '#ffd166', 25);
          this.carriedTreasure = null;

          if (this.relicsStored >= this.targetRelics) {
            this.triggerLevelComplete();
            return;
          }
        } else {
          // Released outside vault: Drop relic back down to seafloor
          this.carriedTreasure.isCarried = false;
          this.carriedTreasure.vy = 60;
          this.carriedTreasure = null;
        }
      }
    } else if (isPinch) {
      // Attempt to grab closest treasure near cursor or hands
      for (const t of this.treasures) {
        if (!t.isDeposited) {
          const dist = Math.hypot(cursorX - t.x, cursorY - t.y);
          if (dist < t.radius + 28) {
            if (t.type.isHazard) {
              // Mimic Fake Trap Hit!
              this.oxygen -= 18;
              this.score = Math.max(0, this.score - 50);
              this.sound.playDamage();
              this.particles.addSparkles(t.x, t.y, '#ff3366', 20);
              t.isDeposited = true;
            } else {
              // Successfully grabbed
              this.carriedTreasure = t;
              t.isCarried = true;
              this.sound.playGrab();
            }
            break;
          }
        }
      }
    }

    this.treasures.forEach((t) => t.update(dt));

    // 6. Hazard Collisions
    for (let i = this.hazards.length - 1; i >= 0; i--) {
      const h = this.hazards[i];
      h.update(dt, this.player.x, this.player.y);

      const dist = Math.hypot(this.player.x - h.x, this.player.y - h.y);
      if (dist < h.radius + 26) {
        if (h.type === 'OXYGEN') {
          // Collect Oxygen Pod
          this.oxygen = Math.min(100, this.oxygen + 30);
          this.sound.playDeposit();
          this.particles.addSparkles(h.x, h.y, '#00f5d4', 20);
          this.hazards.splice(i, 1);
        } else if (!isShield) {
          // Take Damage!
          const dmg = h.type === 'SHARK' ? 35 : (h.type === 'MINE' ? 25 : 15);
          this.oxygen -= dmg;
          this.combo = 1.0;
          this.comboCount = 0;
          this.sound.playDamage();
          this.particles.addSparkles(this.player.x, this.player.y, '#ff3366', 25);

          if (h.type === 'MINE') this.hazards.splice(i, 1); // Mine detonates
        } else {
          // Shield deflected hazard!
          this.sound.playShield();
          this.particles.addSparkles(h.x, h.y, '#00f5d4', 10);
        }
      }
    }

    this.updateHUD();
  }

  updateHUD() {
    const oxyFill = document.getElementById('oxygen-bar-fill');
    const oxyText = document.getElementById('oxygen-percent');
    const oxyVal = Math.max(0, Math.round(this.oxygen));

    oxyFill.style.width = `${oxyVal}%`;
    oxyText.textContent = `${oxyVal}%`;

    if (oxyVal < 25) {
      oxyFill.classList.add('critical');
      document.getElementById('vital-status').textContent = '⚠️ Critical Oxygen Warning!';
    } else {
      oxyFill.classList.remove('critical');
      document.getElementById('vital-status').textContent = 'Vitals Nominal';
    }

    document.getElementById('hud-relics-count').textContent = `${this.relicsStored} / ${this.targetRelics}`;
    document.getElementById('hud-timer').textContent = `${Math.ceil(this.levelTimeRemaining)}s`;
    document.getElementById('hud-score').textContent = this.score.toLocaleString();
    document.getElementById('hud-combo-badge').textContent = `🔥 COMBO x${this.combo.toFixed(1)}`;
    document.getElementById('hud-sonar-badge').textContent = `🔊 SONAR: ${this.sonarCharges}`;

    // Carry indicator pill
    const carryPill = document.getElementById('carry-indicator');
    carryPill.style.display = this.carriedTreasure ? 'flex' : 'none';
  }

  updateGestureUI() {
    const badge = document.getElementById('pip-gesture-badge');
    const activeIcon = document.querySelector('.gesture-icon');
    const activeName = document.querySelector('.gesture-state-name');
    const activeHint = document.querySelector('.gesture-state-hint');
    const activePill = document.getElementById('hud-active-gesture');

    if (this.vision.isPinching) {
      badge.textContent = '🤏 Pinch Active (Grab)';
      activeIcon.textContent = '🤏';
      activeName.textContent = 'PINCH DETECTED';
      activeHint.textContent = 'Grabbing relic or selecting menu button';
      activePill.className = 'active-gesture-pill highlight';
    } else if (this.vision.isTwoFingers) {
      badge.textContent = '✌️ Two Fingers (Sonar)';
      activeIcon.textContent = '✌️';
      activeName.textContent = 'SONAR RECON';
      activeHint.textContent = 'Expanding acoustic pulse reveals hidden relics';
      activePill.className = 'active-gesture-pill';
    } else if (this.vision.isOpenPalm) {
      badge.textContent = '✋ Open Palm (Current)';
      activeIcon.textContent = '✋';
      activeName.textContent = 'WATER CURRENT';
      activeHint.textContent = 'Unleashing surging water stream';
      activePill.className = 'active-gesture-pill';
    } else if (this.vision.isFist) {
      badge.textContent = '✊ Clenched Fist (Shield)';
      activeIcon.textContent = '✊';
      activeName.textContent = 'ENERGY SHIELD';
      activeHint.textContent = 'Protective dome active against hazards';
      activePill.className = 'active-gesture-pill danger';
    } else if (this.vision.isDetected) {
      badge.textContent = '🖐 Tracking Palm';
      activeIcon.textContent = '🖐';
      activeName.textContent = 'HAND DETECTED';
      activeHint.textContent = 'Moving swimmer across deep sea';
      activePill.className = 'active-gesture-pill';
    } else {
      badge.textContent = this.vision.forceMouseMode ? '🖱️ Mouse Mode' : 'Searching Hand...';
      activeIcon.textContent = '🖱️';
      activeName.textContent = this.vision.forceMouseMode ? 'MOUSE MODE' : 'SEARCHING HAND';
      activeHint.textContent = 'Use mouse or bring hand in camera view';
      activePill.className = 'active-gesture-pill';
    }
  }

  // ==============================================================================
  // 8. Custom Underwater Hand Cursor Rendering
  // ==============================================================================
  _renderHandCursor(ctx) {
    const cx = this.vision.normX * window.innerWidth;
    const cy = this.vision.normY * window.innerHeight;

    ctx.save();
    ctx.translate(cx, cy);

    const isPinch = this.vision.isPinching;
    const ringRadius = isPinch ? 12 : 20;

    // Glowing Halo
    ctx.beginPath();
    ctx.arc(0, 0, ringRadius, 0, Math.PI * 2);
    ctx.strokeStyle = isPinch ? '#ffd166' : '#00f5d4';
    ctx.lineWidth = isPinch ? 3.5 : 2.0;
    ctx.shadowColor = isPinch ? '#ffd166' : '#00f5d4';
    ctx.shadowBlur = 12;
    ctx.stroke();

    // Center targeting pip
    ctx.beginPath();
    ctx.arc(0, 0, 3, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.fill();

    // Crosshairs
    if (!isPinch) {
      ctx.strokeStyle = 'rgba(0, 245, 212, 0.7)';
      ctx.lineWidth = 1.5;
      const len = 6;
      ctx.beginPath();
      ctx.moveTo(-ringRadius - len, 0); ctx.lineTo(-ringRadius + 2, 0);
      ctx.moveTo(ringRadius - 2, 0); ctx.lineTo(ringRadius + len, 0);
      ctx.moveTo(0, -ringRadius - len); ctx.lineTo(0, -ringRadius + 2);
      ctx.moveTo(0, ringRadius - 2); ctx.lineTo(0, ringRadius + len);
      ctx.stroke();
    }

    ctx.restore();
  }

  // ==============================================================================
  // 9. Main 60 FPS Render Loop
  // ==============================================================================
  _loop(time) {
    const dt = Math.min((time - this.lastTime) / 1000, 0.1);
    this.lastTime = time;

    this._update(dt);

    // Deep Ocean Radial Background
    const ctx = this.ctx;
    const grad = ctx.createRadialGradient(
      window.innerWidth / 2, window.innerHeight * 0.25, 50,
      window.innerWidth / 2, window.innerHeight * 0.75, window.innerWidth * 0.85
    );
    grad.addColorStop(0, '#0a224a');
    grad.addColorStop(0.5, '#061329');
    grad.addColorStop(1, '#020815');

    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);

    // Render Ocean Seafloor
    ctx.fillStyle = '#030b1c';
    ctx.beginPath();
    ctx.moveTo(0, window.innerHeight - 30);
    ctx.quadraticCurveTo(window.innerWidth * 0.35, window.innerHeight - 45, window.innerWidth * 0.7, window.innerHeight - 32);
    ctx.quadraticCurveTo(window.innerWidth * 0.85, window.innerHeight - 25, window.innerWidth, window.innerHeight - 35);
    ctx.lineTo(window.innerWidth, window.innerHeight);
    ctx.lineTo(0, window.innerHeight);
    ctx.closePath();
    ctx.fill();

    // Render Entities
    this.particles.render(ctx);
    this.vault.render(ctx);
    this.treasures.forEach((t) => t.render(ctx));
    this.hazards.forEach((h) => h.render(ctx));
    this.player.render(ctx, this.vision.shieldActive);

    // Render Custom Underwater Hand Cursor atop all elements
    this._renderHandCursor(ctx);

    requestAnimationFrame((t) => this._loop(t));
  }
}

// Start Game Instance upon DOM Ready
let game = null;
window.addEventListener('DOMContentLoaded', () => {
  game = new GameEngine();
});
