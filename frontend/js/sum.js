const GAME_TYPE = 'sum';
let loading = false;

const $grid = document.getElementById('imageGrid');
const $question = document.getElementById('question');
const $options = document.getElementById('options');
const $feedback = document.getElementById('feedback');
const $streak = document.getElementById('streakNum');
const $body = document.body;

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
    .reduce((acc, img, i) => {
      const wrap = `<div class="img-wrap" style="animation-delay:${i * 0.08}s">
          <img src="${img.url}" alt="${img.filename}" loading="lazy"
               width="${imgSize}" height="${imgSize}"
               onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 200 200%22%3E%3Crect width=%22200%22 height=%22200%22 rx=%2224%22 fill=%22%23FFE8D6%22/%3E%3Ccircle cx=%22100%22 cy=%2285%22 r=%2230%22 fill=%22%23FFD93D%22 opacity=%22.5%22/%3E%3Ccircle cx=%2270%22 cy=%22120%22 r=%2220%22 fill=%22%23FF6B35%22 opacity=%22.4%22/%3E%3Ccircle cx=%22130%22 cy=%22120%22 r=%2220%22 fill=%22%234ECDC4%22 opacity=%22.4%22/%3E%3C/svg%3E';this.style.objectFit='contain'">
          <span class="sticker">${img.value}</span>
        </div>`;
      if (i === 0) return wrap;
      return acc + `<span class="plus">+</span>` + wrap;
    }, '');
  const wraps = $grid.querySelectorAll('.img-wrap');
  scatter(wraps);
  wraps.forEach((_, i) => setTimeout(() => Audio.playPop(), i * 100));
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
    $question.textContent = '¿Cuánto suman todas las imágenes?';

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
    reveal(correctAnswer, result.correct ? null : btn);

    if (result.correct) {
      $feedback.className = 'feedback ok';
      $feedback.innerHTML = '<span class="celebrate">🎉</span> ¡Correcto!';

      const resultImg = API_BASE + '/static/images/' + correctAnswer + '.jpg';
      showResultOverlay(resultImg, correctAnswer);
      Audio.playSumResult(correctAnswer);

      $body.className = 'success';
      confetti();
      Audio.playCorrect();
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

function showResultOverlay(src, label) {
  const existing = document.querySelector('.result-overlay');
  if (existing) existing.remove();

  const overlay = document.createElement('div');
  overlay.className = 'result-overlay';
  overlay.innerHTML = `
    <div class="result-overlay-inner">
      <img src="${src}" alt="${label}" onerror="this.style.display='none'" class="result-overlay-img">
      <span class="result-overlay-label">${label}</span>
    </div>`;
  document.body.appendChild(overlay);
  setTimeout(() => overlay.remove(), 1300);
}

loadQuiz();
window.addEventListener('beforeunload', () => Audio.stopMusic());
