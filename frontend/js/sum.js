const GAME_TYPE = 'sum';
let loading = false;
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
      expiresAt: Date.now() + MIRROR_TTL_MS,
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

function renderImages(images, placeholderUrl) {
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
               onerror="this.onerror=null;this.src='${placeholderUrl}';this.style.objectFit='contain'">
          <span class="sticker">${img.value}</span>
        </div>`;
      if (i === 0) return wrap;
      return acc + `<span class="plus">+</span>` + wrap;
    }, '');
  const wraps = $grid.querySelectorAll('.img-wrap');
  scatter(wraps);
  wraps.forEach((_, i) => setTimeout(() => Audio.playPop(), i * 100));
}

function renderOptions(optionImages, placeholderUrl, onClick) {
  $options.innerHTML = optionImages
    .map(({ value: v, url }) => {
      return `<button class="opt" data-val="${v}">
        <img src="${url}" alt="${v}" loading="lazy" class="opt-img"
             onerror="this.onerror=null;this.src='${placeholderUrl}';this.style.objectFit='contain'">
        <span class="opt-num">${v}</span>
      </button>`;
    })
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
    $streak.textContent = data.streak;
    persistStreak(data.streak);
    renderImages(data.images, data.placeholder_url);
    if (data.reto_active) {
      $question.textContent = `🔥 ¡Reto! ¿Cuánto es ${data.base_value} repetido ${data.repeats} veces?`;
      $body.classList.add('reto-mode');
    } else {
      $question.textContent = '¿Cuánto suman todas las imágenes?';
      $body.classList.remove('reto-mode');
    }

    renderOptions(data.option_images, data.placeholder_url, (answer, btn) => {
      if (loading) return;
      Audio.playClick();
      loading = true;
      disable();
      verifyAnswer(answer, data, btn);
    });
  } catch (err) {
    $feedback.textContent = 'Error al cargar 😢';
    $feedback.className = 'feedback ko';
  } finally {
    loading = false;
  }
}

async function verifyAnswer(answer, data, btn) {
  try {
    const result = await API.verifyAnswer(GAME_TYPE, answer);
    $streak.textContent = result.streak;
    persistStreak(result.streak);
    reveal(result.correct_answer, result.correct ? null : btn);

    if (result.correct) {
      $feedback.className = 'feedback ok';
      $feedback.innerHTML = result.reto_active ? '' : '<span class="celebrate">🎉</span> ';
      $feedback.append(result.message);

      showResultOverlay(data.images, result.correct_answer, data.correct_image_url, data.placeholder_url);

      $body.className = 'success';
      Audio.playCorrect();
      setTimeout(confetti, 1000);
    } else {
      $feedback.className = 'feedback ko';
      $feedback.textContent = result.message;
      $body.className = 'error';
      Audio.playWrong();
    }

    setTimeout(loadQuiz, 3000);
  } catch (err) {
    $feedback.textContent = 'Error 😢';
    $feedback.className = 'feedback ko';
    loading = false;
  }
}

function showResultOverlay(images, total, correctImageUrl, placeholderUrl) {
  const existing = document.querySelector('.clash-overlay');
  if (existing) existing.remove();

  const mid = Math.ceil(images.length / 2);
  const leftImages = images.slice(0, mid);
  const rightImages = images.slice(mid);

  function buildGroup(arr) {
    return arr.map((img, i) =>
      `<img src="${img.url}" alt="${img.value}" class="cimg" onerror="this.onerror=null;this.src='${placeholderUrl}'">` +
      (i < arr.length - 1 ? '<span class="cop">+</span>' : '')
    ).join('');
  }

  const haveRight = rightImages.length > 0;
  const centerOp = haveRight ? '<span class="cop center-op">+</span>' : '';

  const icons = ['✦','✧','⭐','✨','💥','⚡','🔸','🔹','🌟','💫'];
  let stars = '';
  for (let i = 0; i < 16; i++) {
    const icon = icons[Math.floor(Math.random() * icons.length)];
    const angle = Math.random() * 360;
    const dist = 60 + Math.random() * 140;
    const rad = angle * Math.PI / 180;
    stars += `<span class="istar" style="--tx:${Math.cos(rad) * dist}px;--ty:${Math.sin(rad) * dist}px;font-size:${14 + Math.random() * 18}px;animation-delay:${0.6 + Math.random() * 0.19}s;animation-duration:${0.63 + Math.random() * 0.38}s">${icon}</span>`;
  }

  const overlay = document.createElement('div');
  overlay.className = 'clash-overlay';
  overlay.innerHTML = `
    <div class="clash-inner">
      <div class="cside cside-left">${buildGroup(leftImages)}</div>
      ${centerOp}
      ${haveRight ? `<div class="cside cside-right">${buildGroup(rightImages)}</div>` : ''}
      <div class="iring"></div>
      <div class="iflash"></div>
      <div class="istars">${stars}</div>
      <div class="cresult">
        <img src="${correctImageUrl}" alt="${total}" class="cresult-img" onerror="this.onerror=null;this.src='${placeholderUrl}'">
        <span class="cresult-label">${total}</span>
      </div>
    </div>`;
  document.body.appendChild(overlay);

  setTimeout(() => Audio.playSumResult(total), 1000);

  setTimeout(() => {
    overlay.classList.add('out');
    setTimeout(() => overlay.remove(), 250);
  }, 2500);
}

loadQuiz();
window.addEventListener('beforeunload', () => Audio.stopMusic());
