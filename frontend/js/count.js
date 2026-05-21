const GAME_TYPE = 'count';
let loading = false;
const SCORE_STORAGE_TTL_MS = 10 * 60 * 1000;
const SCORE_STORAGE_KEY = `quiz_score_cache_${GAME_TYPE}`;

const $grid = document.getElementById('imageGrid');
const $question = document.getElementById('question');
const $options = document.getElementById('options');
const $feedback = document.getElementById('feedback');
const $streak = document.getElementById('streakNum');
const $body = document.body;

function loadStoredStreak() {
  try {
    const raw = localStorage.getItem(SCORE_STORAGE_KEY);
    if (!raw) return 0;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed.streak !== 'number' || typeof parsed.expiresAt !== 'number') {
      localStorage.removeItem(SCORE_STORAGE_KEY);
      return 0;
    }
    if (Date.now() > parsed.expiresAt) {
      localStorage.removeItem(SCORE_STORAGE_KEY);
      return 0;
    }
    return parsed.streak;
  } catch {
    return 0;
  }
}

function persistStreak(streak) {
  try {
    localStorage.setItem(SCORE_STORAGE_KEY, JSON.stringify({
      streak,
      expiresAt: Date.now() + SCORE_STORAGE_TTL_MS,
    }));
  } catch {
    // no-op when storage is unavailable
  }
}

$streak.textContent = loadStoredStreak();

function scatter(els) {
  els.forEach((el, i) => {
    const r = (Math.random() - .5) * 8;
    const x = (Math.random() - .5) * 6;
    const y = (Math.random() - .5) * 6;
    el.style.setProperty('--r', r + 'deg');
    el.style.animationDelay = (i * 0.08) + 's';
    el.style.transform = `rotate(${r}deg) translate(${x}px, ${y}px)`;
  });
}

function renderImages(images) {
  const count = images.length;
  const perRow = count <= 4 ? count : Math.min(6, Math.ceil(Math.sqrt(count * 2)));
  const gridW = 420;
  const gap = 12;
  const imgSize = Math.max(60, Math.min(160, Math.floor((gridW - (perRow - 1) * gap) / perRow * 1.25)));
  $grid.style.setProperty('--img-size', imgSize + 'px');

  $grid.innerHTML = images
    .map((img, i) =>
      `<img src="${img.url}" alt="${img.filename}" loading="lazy" width="${imgSize}" height="${imgSize}"
            style="animation-delay:${i * 0.08}s"
            onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 200 200%22%3E%3Crect width=%22200%22 height=%22200%22 rx=%2224%22 fill=%22%23FFE8D6%22/%3E%3Ccircle cx=%22100%22 cy=%2285%22 r=%2230%22 fill=%22%23FFD93D%22 opacity=%22.5%22/%3E%3Ccircle cx=%2270%22 cy=%22120%22 r=%2220%22 fill=%22%23FF6B35%22 opacity=%22.4%22/%3E%3Ccircle cx=%22130%22 cy=%22120%22 r=%2220%22 fill=%22%234ECDC4%22 opacity=%22.4%22/%3E%3C/svg%3E';this.style.objectFit='contain'">`)
    .join('');
  const imgs = $grid.querySelectorAll('img');
  scatter(imgs);
  imgs.forEach((_, i) => setTimeout(() => Audio.playPop(), i * 100));
}

function renderOptions(options, correctAnswer, onClick) {
  $options.innerHTML = options
    .map(v => `<button class="opt" data-val="${v}">${v}</button>`)
    .join('');
  $options.querySelectorAll('.opt').forEach(b => {
    b.addEventListener('click', () => {
      if (loading) return;
      const val = parseInt(b.dataset.val, 10);
      onClick(val, b);
    });
  });
}

function disable() {
  $options.querySelectorAll('.opt').forEach(b => b.disabled = true);
}

function reveal(correct, wrong) {
  document.querySelectorAll('.opt').forEach(b => {
    if (parseInt(b.dataset.val, 10) === correct) b.classList.add('reveal');
  });
  if (wrong) wrong.classList.add('ko');
}

function confetti() {
  const colors = ['#FF6B35','#FFD93D','#4ECDC4','#6BCB77','#FF6B6B','#FF8FAB','#4D96FF'];
  const c = document.createElement('div');
  c.className = 'confetti-container';
  for (let i = 0; i < 40; i++) {
    const p = document.createElement('div');
    p.className = 'confetti';
    const color = colors[Math.floor(Math.random() * colors.length)];
    const size = 6 + Math.random() * 8;
    const left = Math.random() * 100;
    const delay = Math.random() * 0.5;
    const dur = 1.2 + Math.random() * 0.8;
    const shape = Math.random() > 0.5 ? '50%' : '2px';
    Object.assign(p.style, {
      left: left + '%',
      width: size + 'px',
      height: size * (0.5 + Math.random()) + 'px',
      background: color,
      borderRadius: shape,
      animationDelay: delay + 's',
      animationDuration: dur + 's',
    });
    c.appendChild(p);
  }
  document.body.appendChild(c);
  setTimeout(() => c.remove(), 3000);
}

async function loadQuiz() {
  loading = true;
  $feedback.textContent = '';
  $feedback.className = 'feedback';
  $body.className = '';
  $grid.className = 'image-grid stagger';
  Audio.startMusic();

  try {
    const data = await API.getQuiz(GAME_TYPE);
    renderImages(data.images);
    $question.textContent = '¿Cuántas imágenes ves?';

    renderOptions(data.options, data.correct_answer, (answer, btn) => {
      if (loading) return;
      Audio.playClick();
      loading = true;
      disable();
      verifyAnswer(answer, data.correct_answer, btn);
    });
  } catch (err) {
    $feedback.textContent = 'Error al cargar 😢';
    $feedback.className = 'feedback ko';
  } finally {
    loading = false;
  }
}

async function verifyAnswer(answer, correctAnswer, btn) {
  try {
    const result = await API.verifyAnswer(GAME_TYPE, answer);
    $streak.textContent = result.streak;
    persistStreak(result.streak);
    reveal(correctAnswer, result.correct ? null : btn);

    if (result.correct) {
      $feedback.className = 'feedback ok';
      $feedback.innerHTML = '<span class="celebrate">⭐</span> ¡Correcto!';
      $body.className = 'success';
      Audio.playCorrect();
      confetti();
    } else {
      $feedback.className = 'feedback ko';
      $feedback.innerHTML = '😅 ¡Sigue intentando!';
      $body.className = 'error';
      Audio.playWrong();
    }

    setTimeout(loadQuiz, 1500);
  } catch (err) {
    $feedback.textContent = 'Error 😢';
    $feedback.className = 'feedback ko';
    loading = false;
  }
}

loadQuiz();
window.addEventListener('beforeunload', () => Audio.stopMusic());
