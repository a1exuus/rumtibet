// ===== Sticky header =====
const header = document.getElementById('header');
const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 10);
onScroll();
window.addEventListener('scroll', onScroll, { passive: true });

// ===== Бургер-меню =====
const nav = document.getElementById('site-nav');
const navOpen = document.getElementById('nav-open');
const navClose = document.getElementById('nav-close');

const setNav = (open) => {
  nav.classList.toggle('is-open', open);
  navOpen.setAttribute('aria-expanded', open);
  document.body.classList.toggle('no-scroll', open);
};
navOpen.addEventListener('click', () => setNav(true));
navClose.addEventListener('click', () => setNav(false));
nav.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => setNav(false)));

// ===== Сворачиваемая форма в hero (mobile) =====
const heroToggle = document.getElementById('hero-toggle');
const heroForm = document.querySelector('.hero__form');
if (heroToggle) heroToggle.addEventListener('click', () => heroForm.classList.toggle('is-open'));

// ===== Нормализация ссылок YouTube =====
function toEmbedUrl(raw) {
  raw = (raw || '').trim();
  if (/^[\w-]{11}$/.test(raw)) {
    return 'https://www.youtube.com/embed/' + raw + '?autoplay=1&rel=0';
  }
  const m = raw.match(/(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([\w-]{11})/);
  const base = m ? 'https://www.youtube.com/embed/' + m[1] : raw;
  try {
    const url = new URL(base);
    url.searchParams.set('autoplay', '1');
    url.searchParams.set('rel', '0');
    return url.toString();
  } catch (e) {
    return base;
  }
}

// ===== Модальные окна =====
function openModal(id) {
  const modal = document.getElementById('modal-' + id);
  if (!modal) return;
  modal.classList.add('is-open');
  document.body.classList.add('no-scroll');
  if (id === 'video') {
    const opener = document.querySelector('[data-modal-open="video"]');
    document.getElementById('video-frame').src = toEmbedUrl(opener.dataset.videoSrc);
  }
}

function closeModal(modal) {
  modal.classList.remove('is-open');
  document.body.classList.remove('no-scroll');
  const frame = modal.querySelector('iframe');
  if (frame) frame.src = 'about:blank'; // корректно останавливает видео
}

document.querySelectorAll('[data-modal-open]').forEach((btn) =>
  btn.addEventListener('click', (e) => { e.preventDefault(); openModal(btn.dataset.modalOpen); })
);
document.querySelectorAll('[data-modal-close]').forEach((btn) =>
  btn.addEventListener('click', () => closeModal(btn.closest('.modal')))
);
document.querySelectorAll('.modal').forEach((modal) =>
  modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(modal); })
);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') document.querySelectorAll('.modal.is-open').forEach(closeModal);
});

// ===== Лайтбокс галереи =====
document.querySelectorAll('[data-lightbox]').forEach((btn) =>
  btn.addEventListener('click', () => {
    document.getElementById('lightbox-img').src = btn.querySelector('img').src;
    openModalLightbox();
  })
);
function openModalLightbox() {
  document.getElementById('lightbox').classList.add('is-open');
  document.body.classList.add('no-scroll');
}

// ===== Валидация форм =====
document.querySelectorAll('form[data-validate]').forEach((form) => {
  form.addEventListener('submit', (e) => {
    let valid = true;
    const fail = (ctrl, msg) => {
      valid = false;
      const err = ctrl.closest('.field')?.querySelector('.field__error');
      if (err) { err.textContent = msg; err.hidden = false; }
      ctrl.setAttribute('aria-invalid', 'true');
    };
    const clear = (ctrl) => {
      const err = ctrl.closest('.field')?.querySelector('.field__error');
      if (err) err.hidden = true;
    };

    form.querySelectorAll('input, select, textarea').forEach((ctrl) => {
      clear(ctrl);
      if (ctrl.type === 'checkbox') {
        if (!ctrl.checked) fail(ctrl, 'Необходимо согласие');
        return;
      }
      if (ctrl.hasAttribute('data-contact-pair')) return; // проверка ниже
      if (ctrl.required && !ctrl.value.trim()) fail(ctrl, 'Обязательное поле');
      else if (ctrl.value && !ctrl.checkValidity()) fail(ctrl, 'Некорректный формат');
    });

    // «телефон И/ИЛИ e-mail» в форме консультации
    const pair = form.querySelectorAll('[data-contact-pair]');
    if (pair.length && ![...pair].some((c) => c.value.trim())) {
      pair.forEach((c) => fail(c, 'Укажите телефон или e-mail'));
    }

    if (!valid) {
      e.preventDefault();
      form.querySelector('[aria-invalid="true"]')?.focus();
    }
  });
});