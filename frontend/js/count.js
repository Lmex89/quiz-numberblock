const PER_PAGE = 50;

const $grid = document.getElementById('galleryGrid');
const $pageIndicator = document.getElementById('pageIndicator');
const $pageInfo = document.getElementById('pageInfo');
const $prevBtn = document.getElementById('prevBtn');
const $nextBtn = document.getElementById('nextBtn');
const $lightbox = document.getElementById('lightbox');
const $lightboxImg = document.getElementById('lightboxImg');
const $lightboxNum = document.getElementById('lightboxNum');
const $lightboxClose = document.getElementById('lightboxClose');
const $lightboxPrev = document.getElementById('lightboxPrev');
const $lightboxNext = document.getElementById('lightboxNext');

let currentPage = 1;
let totalPages = 1;
let currentImages = [];
let currentImageIndex = 0;

function renderGallery(images) {
  currentImages = images;
  $grid.innerHTML = images.map((img, i) => `
    <div class="gallery-item" data-index="${i}" data-value="${img.value}" style="animation-delay:${i * 0.04}s">
      <img src="${img.url}" alt="${img.value}" loading="lazy" class="gallery-img"
           onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 200 200%22%3E%3Crect width=%22200%22 height=%22200%22 rx=%2224%22 fill=%22%23FFE8D6%22/%3E%3Ccircle cx=%22100%22 cy=%2285%22 r=%2230%22 fill=%22%23FFD93D%22 opacity=%22.5%22/%3E%3Ccircle cx=%2270%22 cy=%22120%22 r=%2220%22 fill=%22%23FF6B35%22 opacity=%22.4%22/%3E%3Ccircle cx=%22130%22 cy=%22120%22 r=%2220%22 fill=%22%234ECDC4%22 opacity=%22.4%22/%3E%3C/svg%3E';this.style.objectFit='contain'">
      <span class="gallery-label">${img.value}</span>
    </div>
  `).join('');

  $grid.querySelectorAll('.gallery-item').forEach(item => {
    item.addEventListener('click', () => {
      const index = parseInt(item.dataset.index, 10);
      openLightbox(index);
    });
  });
}

function updatePagination() {
  $pageIndicator.textContent = `Página ${currentPage} de ${totalPages}`;
  $pageInfo.textContent = `${currentPage} / ${totalPages}`;
  $prevBtn.disabled = currentPage <= 1;
  $nextBtn.disabled = currentPage >= totalPages;
}

function openLightbox(index) {
  if (!currentImages[index]) return;
  currentImageIndex = index;
  const img = currentImages[index];
  $lightboxImg.src = img.url;
  $lightboxImg.alt = img.value;
  $lightboxNum.textContent = img.value;
  $lightbox.classList.add('open');
  spawnMiniConfetti();
}

function goNext() {
  if (currentImageIndex < currentImages.length - 1) {
    openLightbox(currentImageIndex + 1);
  } else if (currentPage < totalPages) {
    loadPage(currentPage + 1, () => openLightbox(0));
  }
}

function goPrev() {
  if (currentImageIndex > 0) {
    openLightbox(currentImageIndex - 1);
  } else if (currentPage > 1) {
    loadPage(currentPage - 1, () => openLightbox(currentImages.length - 1));
  }
}

function spawnMiniConfetti() {
  const colors = ['#FF6B35','#FFD93D','#4ECDC4','#6BCB77','#FF6B6B','#A78BFA'];
  for (let i = 0; i < 20; i++) {
    const el = document.createElement('div');
    el.style.cssText = `
      position:fixed; z-index:999; pointer-events:none;
      width:${6 + Math.random()*8}px; height:${6 + Math.random()*8}px;
      background:${colors[Math.floor(Math.random()*colors.length)]};
      border-radius:${Math.random() > .5 ? '50%' : '2px'};
      left:${40 + Math.random()*20}%; top:${40 + Math.random()*20}%;
      animation: confetti-fall ${1 + Math.random()}s linear forwards;
      animation-delay:${Math.random() * .3}s;
    `;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 2000);
  }
}

function closeLightbox() {
  $lightbox.classList.remove('open');
}

$lightboxClose.addEventListener('click', closeLightbox);
$lightbox.addEventListener('click', (e) => {
  if (e.target === $lightbox) closeLightbox();
});
$lightboxPrev.addEventListener('click', (e) => {
  e.stopPropagation();
  goPrev();
});
$lightboxNext.addEventListener('click', (e) => {
  e.stopPropagation();
  goNext();
});

document.addEventListener('keydown', (e) => {
  if (!$lightbox.classList.contains('open')) return;
  if (e.key === 'Escape') closeLightbox();
  if (e.key === 'ArrowLeft') goPrev();
  if (e.key === 'ArrowRight') goNext();
});

$prevBtn.addEventListener('click', () => {
  if (currentPage > 1) {
    currentPage--;
    loadPage(currentPage);
  }
});

$nextBtn.addEventListener('click', () => {
  if (currentPage < totalPages) {
    currentPage++;
    loadPage(currentPage);
  }
});

async function loadPage(page, callback) {
  try {
    const res = await fetch(`${API_BASE}/api/gallery?page=${page}&per_page=${PER_PAGE}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    currentPage = data.page;
    totalPages = data.total_pages;
    renderGallery(data.images);
    updatePagination();
    if (callback) {
      callback();
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  } catch (err) {
    $grid.innerHTML = '<p style="padding:40px;color:var(--red);font-size:1.2rem;">¡Ups! No se pudieron cargar las imágenes 😢</p>';
  }
}

loadPage(1);
