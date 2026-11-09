const WORKS = JSON.parse(document.getElementById('worksData').textContent);

let currentFilter = 'all';

const SECTION_ORDER = ['design', 'studies', 'rendered'];

function makeCard(w){
  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `
    <div class="imgwrap"><img src="${w.image}" alt="${escapeHtml(w.display_alt)}" loading="lazy"></div>
    <div class="card-meta">
      <h3>${escapeHtml(w.title)}</h3>
      <span class="tag">${escapeHtml(w.medium_label || w.medium)} · ${escapeHtml(w.date_display || '')}</span>
    </div>
  `;
  const img = card.querySelector('.imgwrap');
  img.setAttribute('role', 'button');
  img.setAttribute('tabindex', '0');
  img.setAttribute('aria-label', 'View ' + w.title);
  img.addEventListener('click', () => openLightbox(w));
  img.addEventListener('keydown', (e) => {
    if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); openLightbox(w); }
  });
  return card;
}

function renderGallery(){
  const host = document.getElementById('gallery');
  const works = WORKS.filter(w => currentFilter === 'all' || w.tags.includes(currentFilter));
  host.innerHTML = '';

  if(works.length === 0){
    host.innerHTML = '<div class="empty-msg">No pieces in this category yet.</div>';
    return;
  }

  // Unfiltered: keep the three sections visible, since the order is the argument.
  // Filtered: one flat grid, because the grouping would mostly be empty.
  if(currentFilter !== 'all'){
    host.className = 'gallery';
    works.forEach(w => host.appendChild(makeCard(w)));
    return;
  }

  host.className = 'gallery-sections';
  SECTION_ORDER.forEach(sec => {
    const inSection = works.filter(w => w.section === sec);
    if(inSection.length === 0) return;

    const head = document.createElement('div');
    head.className = 'group-head';
    head.innerHTML = `<h3>${escapeHtml(inSection[0].section_label || sec)}</h3>
      <span class="mono">${inSection.length} ${inSection.length === 1 ? 'piece' : 'pieces'}</span>`;
    host.appendChild(head);

    const grid = document.createElement('div');
    grid.className = 'gallery';
    inSection.forEach(w => grid.appendChild(makeCard(w)));
    host.appendChild(grid);
  });
}

function escapeHtml(str){
  const div = document.createElement('div');
  div.textContent = str || '';
  return div.innerHTML;
}

document.getElementById('filters').addEventListener('click', (e) => {
  const btn = e.target.closest('.filter-btn');
  if(!btn) return;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentFilter = btn.dataset.filter;
  renderGallery();
});

const lightbox = document.getElementById('lightbox');
function openLightbox(w){
  document.getElementById('lightboxImg').src = w.image;
  document.getElementById('lightboxImg').alt = w.display_alt;
  document.getElementById('lightboxTitle').textContent = w.title;
  document.getElementById('lightboxMeta').textContent =
    (w.medium_label || w.medium) + ' · ' + (w.date_display || '') +
    (w.description ? ' — ' + w.description : '');
  lightbox.classList.add('open');
}
document.getElementById('lightboxClose').addEventListener('click', () => lightbox.classList.remove('open'));
lightbox.addEventListener('click', (e) => { if(e.target === lightbox) lightbox.classList.remove('open'); });
document.addEventListener('keydown', (e) => { if(e.key === 'Escape') lightbox.classList.remove('open'); });

function setHeroImage(){
  if(WORKS.length === 0) return;
  const hero = WORKS[0];
  document.getElementById('heroImg').src = hero.image;
  document.getElementById('heroImg').alt = hero.display_alt;
  document.getElementById('heroMedium').textContent = (hero.medium_label || hero.medium) + ' on paper';
  document.getElementById('heroDate').textContent = hero.date_display || '';
}

setHeroImage();
renderGallery();
