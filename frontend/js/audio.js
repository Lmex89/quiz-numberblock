const Audio = (() => {
  let ctx = null;
  let musicTimer = null;
  let musicPlaying = false;

  function getCtx() {
    if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }

  // ── Instruments ──────────────────────────

  function glock(freq, start, dur, vol) {
    const c = getCtx();
    const osc = c.createOscillator();
    const osc2 = c.createOscillator();
    const gain = c.createGain();
    osc.type = 'sine'; osc.frequency.value = freq;
    osc2.type = 'sine'; osc2.frequency.value = freq * 2.01;
    gain.gain.setValueAtTime(vol || 0.25, start);
    gain.gain.exponentialRampToValueAtTime(0.001, start + dur);
    osc.connect(gain); osc2.connect(gain); gain.connect(c.destination);
    osc.start(start); osc2.start(start);
    osc.stop(start + dur); osc2.stop(start + dur);
  }

  function pluck(freq, start, dur, vol) {
    const c = getCtx();
    const osc = c.createOscillator();
    const gain = c.createGain();
    osc.type = 'triangle'; osc.frequency.value = freq;
    gain.gain.setValueAtTime(vol || 0.2, start);
    gain.gain.exponentialRampToValueAtTime(0.001, start + dur);
    osc.connect(gain); gain.connect(c.destination);
    osc.start(start); osc.stop(start + dur);
  }

  function woodblock(start) {
    const c = getCtx();
    const buf = c.createBuffer(1, c.sampleRate * 0.06, c.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < data.length; i++)
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (c.sampleRate * 0.008));
    const src = c.createBufferSource(); src.buffer = buf;
    const gain = c.createGain();
    gain.gain.setValueAtTime(0.12, start);
    gain.gain.exponentialRampToValueAtTime(0.001, start + 0.06);
    src.connect(gain); gain.connect(c.destination);
    src.start(start);
  }

  function pizzBass(freq, start, dur) {
    const c = getCtx();
    const osc = c.createOscillator();
    const gain = c.createGain();
    osc.type = 'sine'; osc.frequency.value = freq;
    gain.gain.setValueAtTime(0.15, start);
    gain.gain.exponentialRampToValueAtTime(0.001, start + dur);
    osc.connect(gain); gain.connect(c.destination);
    osc.start(start); osc.stop(start + dur);
  }

  function softPad(freq, start, dur) {
    const c = getCtx();
    const osc = c.createOscillator();
    const gain = c.createGain();
    osc.type = 'sine'; osc.frequency.value = freq;
    gain.gain.setValueAtTime(0.04, start);
    gain.gain.linearRampToValueAtTime(0.06, start + dur * 0.3);
    gain.gain.linearRampToValueAtTime(0.001, start + dur);
    osc.connect(gain); gain.connect(c.destination);
    osc.start(start); osc.stop(start + dur);
  }

  const PENT = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25, 783.99];

  // ── Background music loop ────────────────
  // Original kids' game tune — catchy call-and-response, loops every ~4.8s

  function scheduleLoop() {
    const c = getCtx();
    const now = c.currentTime;
    const beat = 0.3;

    // Melody (glock) — pentatonic indices
    const melody = [5, 3, 5, 6, 5, 4, 3, 2, 3, 5, 6, 7, 6, 5, 3, 5];
    for (let i = 0; i < melody.length; i++) {
      const t = now + i * beat;
      const len = beat * 0.35;
      glock(PENT[melody[i]], t, len, 0.07);
      // harmony third above on every other note
      if (i % 2 === 0 && melody[i] + 2 < PENT.length) {
        glock(PENT[melody[i] + 2], t, len, 0.025);
      }
    }

    // Pluck response — fills the gaps
    for (let i = 0; i < 8; i++) {
      const t = now + i * beat * 2 + beat * 0.5;
      pluck(PENT[melody[i * 2]] / 2, t, beat * 0.4, 0.04);
    }

    // Bass — moves with harmony
    const bassNotes = [0, 3, 4, 3];
    for (let i = 0; i < bassNotes.length; i++) {
      pizzBass(PENT[bassNotes[i]] / 2, now + i * beat * 4, beat * 3.5);
    }

    // Percussion — bouncy pattern
    for (let i = 0; i < 16; i++) {
      if (i % 4 === 0 || i % 4 === 2) {
        woodblock(now + i * beat);
      }
      if (i % 8 === 0) {
        const t2 = now + i * beat;
        glock(PENT[0] * 4, t2, 0.03, 0.02);
      }
    }

    // Sustained pad
    softPad(PENT[0] / 2, now, beat * 8);
    softPad(PENT[2] / 2, now, beat * 8);
    softPad(PENT[4] / 2, now + beat * 8, beat * 8);

    const loopMs = melody.length * beat * 1000 - 50;
    if (musicPlaying) musicTimer = setTimeout(scheduleLoop, loopMs);
  }

  function startMusic() {
    if (musicPlaying) return;
    musicPlaying = true;
    getCtx();
    scheduleLoop();
  }

  function stopMusic() {
    musicPlaying = false;
    if (musicTimer) { clearTimeout(musicTimer); musicTimer = null; }
  }

  // ── Click sound ──────────────────────────

  function playClick() {
    const c = getCtx();
    const t = c.currentTime;
    glock(PENT[4] * 1.5, t, 0.06, 0.05);
    woodblock(t + 0.02);
  }

  // ── Correct ──────────────────────────────

  function playCorrect() {
    const c = getCtx(); const t = c.currentTime;
    for (let i = 0; i < 3; i++) woodblock(t + i * 0.12);
    glock(PENT[2], t + 0.1, 0.2); glock(PENT[4], t + 0.22, 0.25);
    glock(PENT[6], t + 0.34, 0.35); glock(PENT[8], t + 0.46, 0.5);
    pluck(PENT[2], t + 0.25, 0.15, 0.15); pluck(PENT[4], t + 0.35, 0.15, 0.15);
    pluck(PENT[6], t + 0.45, 0.18, 0.15);
    pizzBass(PENT[0] / 2, t + 0.1, 0.6); pizzBass(PENT[1] / 2, t + 0.3, 0.4);
    pizzBass(PENT[2] / 2, t + 0.5, 0.3);
    woodblock(t + 0.6);
  }

  // ── Wrong ────────────────────────────────

  function playWrong() {
    const c = getCtx(); const t = c.currentTime;
    pluck(392, t, 0.25, 0.15); pluck(349.23, t + 0.2, 0.35, 0.15);
  }

  // ── Pop (image appears) ──────────────────

  function playPop() {
    glock(880, getCtx().currentTime, 0.12, 0.08);
  }

  // ── Sum result count-up ──────────────────

  function playSumResult(n) {
    if (n < 1 || n > 20) return;
    const c = getCtx(); const t = c.currentTime;
    for (let i = 0; i < Math.min(n, 8); i++) {
      const ni = i % PENT.length;
      const off = i * 0.1;
      glock(PENT[ni], t + off, 0.3, 0.2);
      woodblock(t + off);
      if (i % 2 === 0) pizzBass(PENT[Math.min(i, 4)] / 2, t + off, 0.35);
    }
  }

  return { playCorrect, playWrong, playPop, playSumResult, playClick, startMusic, stopMusic };
})();
