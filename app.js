// ─── I18N ─────────────────────────────────────────────────────────
let lang = localStorage.getItem('ai-catalog-lang') || 'en';
document.documentElement.lang = lang;

const T = {
  en: {
    searchPlaceholder: 'Search model, provider or tag...',
    searchFilter:      'Search',
    heroTag:        'Updated daily',
    heroTitle:      'Where to get <em>any AI model</em> via API?',
    heroSub:        'Complete API provider catalog. Compare prices, capabilities and availability — from LLM to video and audio generation.',
    statModels:     'models in catalog',
    statProviders:  'API providers',
    statCategories: 'categories',
    filterCategory: 'Category',
    filterAll:      'All',
    filterProvider: 'Provider',
    filterCapabilities: 'Capabilities',
    filterOptions:  'Options',
    optionMulti:    'Price comparison only',
    optionAffiliate:'Affiliate links only',
    optionOpenSource:'Open-source / local only',
    optionFreeApi:  'Free API available',
    optionApiOnly:  'API only',
    resetFilters:   'Reset filters',
    sortAZ:         'A-Z',
    sortNewest:     'Newest first',
    sortPriceAsc:   'Price: ascending',
    sortPriceDesc:  'Price: descending',
    sortProviders:  'Most providers',
    models:         'models',
    noResults:      'No results',
    noResultsSub:   'Try changing filters or searching a different phrase.',
    bestPrice:      'Best price',
    compare:        'Compare',
    providerComparison: 'Provider comparison',
    thProvider:     'Provider',
    thPrice:        'Price',
    thUnit:         'Unit',
    thNotes:        'Notes',
    typeAggregator: 'aggregator',
    typeDirect:     'direct',
    cheapest:       '✓ cheapest',
    unavailable:    'unavailable',
    visitLink:      'Visit',
    dataFrom:       'Updated:',
    navOpenSource:  'Open source',
    copyLink:       'Copy link',
    copied:         'Copied!',
    footerCopy:     'Catalog maintained by',
    footerNote:     "Prices are approximate — verify on provider's website before use.",
    versionsLabel:  'Versions:',
    prevLabel:      'prev:',
    contextTokens:  'token context',
    updatedLabel:   'Updated:',
    compareNav:     'Compare prices',
    compareTitle:   'Compare model prices',
    compareSub:     'Select a preset or build your own comparison. Best price per provider shown.',
    compareEmpty:   'Select a preset or add models to compare',
    compareAddModel:'+ Add model',
    compareSearchPh:'Search model...',
    backToCatalog:  'Back to catalog',
    presetFlagship: 'Flagship models',
    presetCoding:   'Best for coding',
    presetReasoning:'Reasoning models',
    presetBudget:   'Budget LLMs',
    presetImage:    'Image generation',
    presetVideo:    'Video generation',
    presetEmbedding:'Embeddings',
    reportError:    'Report error',
    reportErrorSub: 'Wrong price or missing provider? Let us know.',
    thModel:        'Model',
    thInputPrice:   'Input / 1M',
    thOutputPrice:  'Output / 1M',
    thContext:      'Context',
    thCapabilities: 'Capabilities',
    priceUnits: {
      perImage:   '/image',
      perSec:     '/sec',
      perVideo:   '/video',
      perVideo5s: '/5s clip',
      perVideo6s: '/6s clip',
      perSong:    '/song',
      perMP:      '/MP',
      per1Mtoken: '/1M tokens (in)',
      per1Mchars: '/1M chars',
      perMin:     '/minute',
    },
  },
  pl: {
    searchPlaceholder: 'Szukaj modelu, dostawcy lub tagu...',
    searchFilter:      'Szukaj',
    heroTag:        'Aktualizowany codziennie',
    heroTitle:      'Gdzie dostać <em>dowolny model AI</em> przez API?',
    heroSub:        'Kompletny katalog dostawców API. Porównaj ceny, możliwości i dostępność — od LLM po generowanie wideo i audio.',
    statModels:     'modeli w katalogu',
    statProviders:  'dostawców API',
    statCategories: 'kategorii',
    filterCategory: 'Kategoria',
    filterAll:      'Wszystkie',
    filterProvider: 'Dostawca',
    filterCapabilities: 'Możliwości',
    filterOptions:  'Opcje',
    optionMulti:    'Tylko z porównaniem cen',
    optionAffiliate:'Tylko z affiliate link',
    optionOpenSource:'Tylko open-source / lokalne',
    optionFreeApi:  'Tylko z darmowym API',
    optionApiOnly:  'Tylko przez API',
    resetFilters:   'Resetuj filtry',
    sortAZ:         'A-Z',
    sortNewest:     'Najnowsze',
    sortPriceAsc:   'Cena: rosnąco',
    sortPriceDesc:  'Cena: malejąco',
    sortProviders:  'Najwięcej dostawców',
    models:         'modeli',
    noResults:      'Brak wyników',
    noResultsSub:   'Spróbuj zmienić filtry lub wyszukać po innej frazie.',
    bestPrice:      'Najlepsza cena',
    compare:        'Porównaj',
    providerComparison: 'Porównanie dostawców',
    thProvider:     'Dostawca',
    thPrice:        'Cena',
    thUnit:         'Jednostka',
    thNotes:        'Uwagi',
    typeAggregator: 'agregator',
    typeDirect:     'bezpośredni',
    cheapest:       '✓ najtaniej',
    unavailable:    'niedostępny',
    visitLink:      'Przejdź',
    dataFrom:       'Aktualizacja:',
    navOpenSource:  'Open source',
    copyLink:       'Kopiuj link',
    copied:         'Skopiowano!',
    footerCopy:     'Katalog utrzymywany przez',
    footerNote:     'Ceny są orientacyjne — weryfikuj na stronie dostawcy przed użyciem.',
    versionsLabel:  'Wersje:',
    prevLabel:      'poprz.:',
    contextTokens:  'tokenów kontekstu',
    updatedLabel:   'Aktualizacja:',
    compareNav:     'Porównaj ceny',
    compareTitle:   'Porównanie cen modeli',
    compareSub:     'Wybierz preset lub zbuduj własne porównanie. Najlepsza cena od danego dostawcy.',
    compareEmpty:   'Wybierz preset lub dodaj modele do porównania',
    compareAddModel:'+ Dodaj model',
    compareSearchPh:'Szukaj modelu...',
    backToCatalog:  'Powrót do katalogu',
    presetFlagship: 'Flagowe modele',
    presetCoding:   'Najlepsze do kodu',
    presetReasoning:'Modele rozumowania',
    presetBudget:   'Budżetowe LLM',
    presetImage:    'Generowanie obrazów',
    presetVideo:    'Generowanie wideo',
    presetEmbedding:'Embeddingi',
    reportError:    'Zgłoś błąd',
    reportErrorSub: 'Błędna cena lub brak dostawcy? Daj nam znać.',
    thModel:        'Model',
    thInputPrice:   'Input / 1M',
    thOutputPrice:  'Output / 1M',
    thContext:      'Kontekst',
    thCapabilities: 'Możliwości',
    priceUnits: {
      perImage:   '/ obraz',
      perSec:     '/ sekunda',
      perVideo:   '/ wideo',
      perVideo5s: '/ klip 5s',
      perVideo6s: '/ klip 6s',
      perSong:    '/ utwór',
      perMP:      '/ megapiksel',
      per1Mtoken: '/ 1M tokenów (in)',
      per1Mchars: '/ 1M znaków',
      perMin:     '/ minutę',
    },
  }
};

// Apply translations immediately so the page renders in the correct language
// without waiting for the data fetch. English is skipped because the HTML
// ships English defaults — avoids an innerHTML mutation that would push LCP.
if (lang !== 'en') applyTranslations();

function t(key) {
  return T[lang]?.[key] ?? T['en']?.[key] ?? key;
}

function getModelDesc(model) {
  if (lang === 'pl') return model.description_pl || model.description || '';
  return model.description_en || model.description || '';
}

// Umami custom event tracking. Safe no-op if umami didn't load.
function trackEvent(name, props) {
  try {
    if (typeof window.umami !== 'undefined' && typeof window.umami.track === 'function') {
      window.umami.track(name, props || {});
    }
  } catch (_) { /* silent */ }
}

// Delegated click handler: any element with data-track-event fires Umami event
document.addEventListener('click', (e) => {
  const a = e.target.closest('[data-track-event]');
  if (!a) return;
  const eventName = a.dataset.trackEvent;
  const props = {};
  for (const key in a.dataset) {
    if (key.startsWith('trackProp')) {
      const propKey = key.slice('trackProp'.length).replace(/^[A-Z]/, c => c.toLowerCase());
      props[propKey] = a.dataset[key];
    }
  }
  trackEvent(eventName, props);
});

function getCatName(cat) {
  if (lang === 'pl') return cat.name_pl || cat.name || cat.id;
  return cat.name_en || cat.name || cat.id;
}

function setLang(newLang) {
  lang = newLang;
  localStorage.setItem('ai-catalog-lang', lang);
  document.documentElement.lang = lang;
  applyTranslations();
  // Rebuild dynamic UI
  buildCategoryPills();
  buildProviderList();
  buildHeroPresetLinks();
  render();
  updateNavCount();
}

function applyTranslations() {
  document.documentElement.lang = lang;
  document.getElementById('search').placeholder = t('searchPlaceholder');
  document.getElementById('search').setAttribute('aria-label', t('searchPlaceholder'));
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    const val = t(key);
    if (val !== key && el.innerHTML !== val) el.innerHTML = val;
  });
  // Sort select options
  document.querySelectorAll('#sort-select option[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
  // Lang buttons
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });
}

function updateNavCount() {
  const el = document.getElementById('nav-count');
  if (el && allModels.length) el.textContent = allModels.length + ' ' + t('models');
}

// ─── STATE ───────────────────────────────────────────────────────
let allModels = [];
let allProviders = {};
let allCategories = [];
let filters = {
  category: 'all',
  providers: new Set(),
  search: '',
  capVision: false,
  capReasoning: false,
  capFunctions: false,
  capSearch: false,
  multiProvider: false,
  affiliate: false,
  openSource: false,
  apiOnly: false,
  freeApi: false,
  sort: 'name'
};

// ─── LOAD DATA ────────────────────────────────────────────────────
async function loadData() {
  try {
    const [modelsRes, providersRes, categoriesRes] = await Promise.all([
      fetch('data/models.json'),
      fetch('data/providers.json'),
      fetch('data/categories.json')
    ]);

    const modelsData = await modelsRes.json();
    const providersData = await providersRes.json();
    const categoriesData = await categoriesRes.json();

    allModels = modelsData.models;
    allCategories = categoriesData.categories;
    allProviders = {};
    providersData.providers.forEach(p => { allProviders[p.id] = p; });

    document.getElementById('footer-date').textContent = t('dataFrom') + ' ' + modelsData.updated_at;
    const sourcesEl = document.getElementById('footer-sources');
    const srcNames = {
      fal: 'fal.ai', openrouter: 'OpenRouter', litellm: 'LiteLLM',
      replicate: 'Replicate', fireworks: 'Fireworks AI', huggingface: 'HuggingFace',
      aimlapi: 'AIMLAPI', bedrock: 'AWS Bedrock', opencode: 'OpenCode',
      wavespeed: 'WaveSpeed', minimax: 'MiniMax', piapi: 'piapi.ai',
      runway: 'Runway', manual: 'curated'
    };
    if (modelsData.source_counts) {
      const order = ['fal','openrouter','litellm','replicate','fireworks','huggingface','aimlapi','bedrock','opencode','wavespeed','minimax','piapi','runway','manual'];
      const counts = modelsData.source_counts;
      const sorted = Object.keys(counts).sort((a,b) => (order.indexOf(a)+1||99) - (order.indexOf(b)+1||99));
      sourcesEl.innerHTML = sorted.map(src =>
        `<span class="footer-src-badge">${srcNames[src]||src}</span>`
      ).join('');
    }
    const stats = modelsData.update_stats;
    if (stats && (stats.added || stats.updated || stats.removed)) {
      const parts = [];
      if (stats.added)   parts.push(`<span class="footer-src-badge footer-src-added">+${stats.added} ${lang==='pl'?'nowych':'new'}</span>`);
      if (stats.updated) parts.push(`<span class="footer-src-badge footer-src-updated">~${stats.updated} ${lang==='pl'?'zmienionych':'updated'}</span>`);
      if (stats.removed) parts.push(`<span class="footer-src-badge footer-src-removed">-${stats.removed} ${lang==='pl'?'usuniętych':'removed'}</span>`);
      sourcesEl.innerHTML += '<span class="footer-src-sep"></span>' + parts.join('');
    }
    document.getElementById('stat-models').textContent = allModels.length;
    document.getElementById('stat-providers').textContent = providersData.providers.length;
    updateNavCount();

    buildCategoryPills();
    buildProviderList();
    buildHeroPresetLinks();
    render();

    // Deep link: open model or compare from URL hash on load
    const hash = location.hash.slice(1);
    if (hash === 'compare') {
      toggleCompare();
    } else if (hash.startsWith('compare/')) {
      toggleCompare();
      const presetId = hash.slice(8);
      // Wait for presets to build, then select
      requestAnimationFrame(() => {
        if (compareState.resolvedPresets[presetId]) {
          selectPreset(presetId);
        }
      });
    } else if (hash) {
      const m = allModels.find(m => m.id === hash);
      if (m) openModal(m.id);
    }
  } catch (err) {
    document.getElementById('grid').innerHTML = `<div style="padding:40px;color:var(--text-3);text-align:center;">
      <p style="margin-bottom:8px;">Błąd ładowania danych.</p>
      <code style="font-size:12px;font-family:monospace;">${err.message}</code>
      <p style="margin-top:12px;font-size:13px;">Upewnij się, że strona jest serwowana przez serwer HTTP (nie file://).</p>
    </div>`;
  }
}

// ─── BUILD UI ────────────────────────────────────────────────────
function buildCategoryPills() {
  const container = document.getElementById('cat-pills');
  // Clear except "All" pill
  const allPill = container.querySelector('[data-cat="all"]');
  container.innerHTML = '';
  container.appendChild(allPill);
  // Update "All" pill text
  allPill.querySelector('span:not(.cat-icon):not(.cat-count)').textContent = t('filterAll');

  // Count per category
  const counts = { all: allModels.length };
  allCategories.forEach(c => {
    counts[c.id] = allModels.filter(m => m.category === c.id).length;
  });
  document.getElementById('count-all').textContent = allModels.length;

  allCategories.forEach(cat => {
    if (!counts[cat.id]) return;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'cat-pill';
    btn.dataset.cat = cat.id;
    btn.innerHTML = `
      <span class="cat-icon" aria-hidden="true">${cat.icon}</span>
      <span>${getCatName(cat)}</span>
      <span class="cat-count" aria-hidden="true">${counts[cat.id]}</span>
    `;
    btn.addEventListener('click', () => {
      filters.category = cat.id;
      document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      render();
    });
    container.appendChild(btn);
  });

  document.querySelector('.cat-pill[data-cat="all"]').addEventListener('click', () => {
    filters.category = 'all';
    document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
    document.querySelector('.cat-pill[data-cat="all"]').classList.add('active');
    render();
  });
}

function buildProviderList() {
  const container = document.getElementById('provider-list');
  container.innerHTML = '';
  // Collect providers actually used in models
  const usedProviders = new Set();
  allModels.forEach(m => m.providers.forEach(p => usedProviders.add(p.provider_id)));

  Array.from(usedProviders).sort().forEach(pid => {
    const prov = allProviders[pid];
    if (!prov) return;
    const div = document.createElement('div');
    div.className = 'provider-item';
    div.innerHTML = `
      <input type="checkbox" id="prov-${pid}" value="${pid}">
      <div class="provider-dot" style="background:${prov.logo_color}"></div>
      <label for="prov-${pid}">${prov.name}</label>
    `;
    div.querySelector('input').addEventListener('change', (e) => {
      if (e.target.checked) filters.providers.add(pid);
      else filters.providers.delete(pid);
      render();
    });
    container.appendChild(div);
  });
}

// ─── FILTER + RENDER ─────────────────────────────────────────────
function getFilteredModels() {
  let result = allModels;

  if (filters.category !== 'all') {
    result = result.filter(m => m.category === filters.category);
  }

  if (filters.providers.size > 0) {
    result = result.filter(m =>
      m.providers.some(p => filters.providers.has(p.provider_id))
    );
  }

  if (filters.search) {
    const normalize = s => (s || '').toLowerCase().replace(/[-_./]+/g, ' ').replace(/\s+/g, ' ').trim();
    const q = normalize(filters.search);
    result = result.filter(m =>
      normalize(m.id).includes(q) ||
      normalize(m.name).includes(q) ||
      normalize(m.description).includes(q) ||
      normalize(m.description_pl).includes(q) ||
      normalize(m.description_en).includes(q) ||
      (m.tags || []).some(tag => normalize(tag).includes(q)) ||
      m.providers.some(p => {
        const prov = allProviders[p.provider_id];
        return prov && normalize(prov.name).includes(q);
      })
    );
  }

  if (filters.capVision)    result = result.filter(m => m.capabilities.includes('vision'));
  if (filters.capReasoning) result = result.filter(m => m.capabilities.includes('reasoning'));
  if (filters.capFunctions) result = result.filter(m => m.capabilities.includes('function_calling'));
  if (filters.capSearch)    result = result.filter(m => m.capabilities.includes('web_search'));

  if (filters.multiProvider) {
    result = result.filter(m => m.providers.length >= 2);
  }

  if (filters.affiliate) {
    result = result.filter(m => m.providers.some(p => p.affiliate_url));
  }

  if (filters.openSource) {
    result = result.filter(m => m.open_source === true);
  }

  if (filters.freeApi) {
    result = result.filter(m => m.providers.some(p => p.free_api && p.available));
  }

  if (filters.apiOnly) {
    result = result.filter(m => m.providers.some(p => p.available));
  }

  // Sort
  result = [...result];
  if (filters.sort === 'name') {
    result.sort((a, b) => a.name.localeCompare(b.name));
  } else if (filters.sort === 'newest') {
    const addedAt = m => m.first_seen_at || m.updated_at || '';
    result.sort((a, b) => {
      const cmp = addedAt(b).localeCompare(addedAt(a));
      return cmp !== 0 ? cmp : a.name.localeCompare(b.name);
    });
  } else if (filters.sort === 'price-asc') {
    result.sort((a, b) => getBestPriceNum(a) - getBestPriceNum(b));
  } else if (filters.sort === 'price-desc') {
    result.sort((a, b) => getBestPriceNum(b) - getBestPriceNum(a));
  } else if (filters.sort === 'providers-desc') {
    result.sort((a, b) => b.providers.length - a.providers.length);
  }

  return result;
}

function getBestPriceNum(model) {
  let min = Infinity;
  model.providers.forEach(p => {
    if (!p.available) return;
    const price = getPriceValue(p.pricing, model.category);
    if (price !== null && price < min) min = price;
  });
  return min === Infinity ? 999999 : min;
}

function getPriceValue(pricing, category) {
  if (!pricing) return null;
  if (pricing.per_image !== undefined) return pricing.per_image;
  if (pricing.per_second !== undefined) return pricing.per_second;
  if (pricing.per_video_5s !== undefined) return pricing.per_video_5s;
  if (pricing.per_video_6s !== undefined) return pricing.per_video_6s;
  if (pricing.per_video !== undefined) return pricing.per_video;
  if (pricing.per_song !== undefined) return pricing.per_song;
  if (pricing.input_per_1m !== undefined) return pricing.input_per_1m;
  if (pricing.per_1m_chars !== undefined) return pricing.per_1m_chars;
  if (pricing.per_minute !== undefined) return pricing.per_minute;
  if (pricing.per_megapixel !== undefined) return pricing.per_megapixel;
  return null;
}

function formatPrice(pricing, category, short = false) {
  if (!pricing) return { value: '—', unit: '' };
  const u = T[lang]?.priceUnits || T['en'].priceUnits;

  if (pricing.per_image !== undefined) {
    return { value: '$' + pricing.per_image.toFixed(3), unit: short ? '/img' : u.perImage };
  }
  if (pricing.per_second !== undefined) {
    return { value: '$' + pricing.per_second.toFixed(3), unit: short ? '/s' : u.perSec };
  }
  if (pricing.per_video_5s !== undefined) {
    return { value: '$' + pricing.per_video_5s.toFixed(3), unit: short ? '/5s' : u.perVideo5s };
  }
  if (pricing.per_video_6s !== undefined) {
    return { value: '$' + pricing.per_video_6s.toFixed(3), unit: short ? '/6s' : u.perVideo6s };
  }
  if (pricing.per_video !== undefined) {
    return { value: '$' + pricing.per_video.toFixed(2), unit: short ? '/vid' : u.perVideo };
  }
  if (pricing.per_song !== undefined) {
    return { value: '$' + pricing.per_song.toFixed(3), unit: short ? '/song' : u.perSong };
  }
  if (pricing.per_megapixel !== undefined) {
    return { value: '$' + pricing.per_megapixel.toFixed(4), unit: short ? '/MP' : u.perMP };
  }
  if (pricing.input_per_1m !== undefined) {
    return { value: '$' + pricing.input_per_1m.toFixed(2), unit: short ? '/1M in' : u.per1Mtoken };
  }
  if (pricing.per_1m_chars !== undefined) {
    return { value: '$' + pricing.per_1m_chars.toFixed(0), unit: short ? '/1M ch' : u.per1Mchars };
  }
  if (pricing.per_minute !== undefined) {
    return { value: '$' + pricing.per_minute.toFixed(4), unit: short ? '/min' : u.perMin };
  }
  if (pricing.notes) {
    return { value: '~', unit: pricing.notes, isNote: true };
  }
  return { value: '—', unit: '' };
}

function getBestProvider(model) {
  let best = null;
  let bestVal = Infinity;
  model.providers.forEach(p => {
    if (!p.available) return;
    const val = getPriceValue(p.pricing, model.category);
    if (val !== null && val < bestVal) {
      bestVal = val;
      best = p;
    }
  });
  return best || model.providers[0];
}

function getCategoryInfo(catId) {
  return allCategories.find(c => c.id === catId) || { name: catId, icon: '◦' };
}

const PAGE_SIZE = 48;
let currentPage = 1;
let currentModels = [];

function attachCardHandlers(cards) {
  cards.forEach(card => {
    card.addEventListener('click', () => openModal(card.dataset.id));
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openModal(card.dataset.id);
      }
    });
  });
}

function renderLoadMore() {
  const existing = document.getElementById('load-more-btn');
  if (existing) existing.remove();
  const shown = Math.min(currentPage * PAGE_SIZE, currentModels.length);
  if (shown >= currentModels.length) return;
  const remaining = currentModels.length - shown;
  const btn = document.createElement('div');
  btn.id = 'load-more-btn';
  btn.style.cssText = 'grid-column:1/-1;display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 0 8px;';
  btn.innerHTML = `
    <button onclick="loadMore()" style="padding:10px 28px;background:var(--surface-2);border:1px solid var(--border-md);border-radius:8px;color:var(--text-2);font-family:'DM Sans',sans-serif;font-size:14px;cursor:pointer;transition:border-color .15s,color .15s" onmouseover="this.style.borderColor='var(--accent)';this.style.color='var(--accent)'" onmouseout="this.style.borderColor='var(--border-md)';this.style.color='var(--text-2)'">
      Pokaż więcej <span style="color:var(--text-3);font-size:12px">(${remaining} pozostałych)</span>
    </button>
    <div style="font-size:11px;color:var(--text-3)">${shown} z ${currentModels.length}</div>`;
  document.getElementById('grid').appendChild(btn);
}

function loadMore() {
  currentPage++;
  const start = (currentPage - 1) * PAGE_SIZE;
  const slice = currentModels.slice(start, currentPage * PAGE_SIZE);
  const grid = document.getElementById('grid');
  const btn = document.getElementById('load-more-btn');
  if (btn) btn.remove();
  const tmp = document.createElement('div');
  tmp.innerHTML = slice.map((m, i) => renderCard(m, start + i)).join('');
  const newCards = Array.from(tmp.children);
  newCards.forEach(c => grid.appendChild(c));
  attachCardHandlers(grid.querySelectorAll('.model-card:not([data-bound])'));
  grid.querySelectorAll('.model-card:not([data-bound])').forEach(c => c.dataset.bound = '1');
  renderLoadMore();
}

function render() {
  currentModels = getFilteredModels();
  currentPage = 1;
  const grid = document.getElementById('grid');
  const empty = document.getElementById('empty');
  const countEl = document.getElementById('result-count');

  countEl.textContent = currentModels.length;

  if (currentModels.length === 0) {
    grid.innerHTML = '';
    empty.style.display = 'block';
  } else {
    empty.style.display = 'none';
    const slice = currentModels.slice(0, PAGE_SIZE);
    grid.innerHTML = slice.map((m, i) => renderCard(m, i)).join('');
    // Add click + keyboard handlers
    grid.querySelectorAll('.model-card').forEach(card => {
      card.dataset.bound = '1';
      card.addEventListener('click', () => openModal(card.dataset.id));
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openModal(card.dataset.id);
        }
      });
    });
    renderLoadMore();
  }

  updateActiveFilters();
}

function renderVersionBadge(model) {
  if (!model.versions || model.versions.length < 2) return '';
  const current = model.versions.find(v => v.is_current) || model.versions[0];
  const prev = model.versions.filter(v => !v.is_current)[0];
  return `<div class="version-row">
    <span class="version-tag current">v${escHtml(current.version)}</span>
    ${prev ? `<span class="version-tag">${t('prevLabel')} v${escHtml(prev.version)}</span>` : ''}
  </div>`;
}

function renderCard(model, idx) {
  const cat = getCategoryInfo(model.category);
  const bestProv = getBestProvider(model);
  const bestPrice = bestProv ? formatPrice(bestProv.pricing, model.category, true) : { value: '—', unit: '', isNote: false };

  const capBadges = [];
  if ((model.capabilities || []).includes('vision'))       capBadges.push('<span class="badge-cap vision">vision</span>');
  if ((model.capabilities || []).includes('reasoning'))    capBadges.push('<span class="badge-cap reason">reasoning</span>');
  if ((model.capabilities || []).includes('web_search'))   capBadges.push('<span class="badge-cap search">web search</span>');
  if ((model.capabilities || []).includes('text_to_video'))  capBadges.push('<span class="badge-cap">text→video</span>');
  if ((model.capabilities || []).includes('image_to_video')) capBadges.push('<span class="badge-cap">image→video</span>');
  if ((model.capabilities || []).includes('image_editing'))  capBadges.push('<span class="badge-cap">img edit</span>');
  if (model.open_source)      capBadges.push('<span class="badge-cap oss">OSS</span>');
  if (model.local_available)  capBadges.push(`<span class="badge-cap local" title="${escHtml(model.local_tool||'')}">local ✓</span>`);
  const freeProvider = model.providers.find(p => p.free_api && p.available);
  if (freeProvider) {
    const isTier = freeProvider.free_type === 'tier';
    capBadges.push(`<span class="badge-cap free${isTier ? ' tier' : ''}" title="${isTier ? 'Darmowy tier z limitami — płatna wersja też dostępna' : 'Całkowicie bezpłatny dostęp przez API'}">${isTier ? 'FREE tier' : 'FREE'}</span>`);
  }

  const availableProviders = model.providers.filter(p => p.available);
  const providerCount = availableProviders.length;
  const localOnly = providerCount === 0;
  const delay = `animation-delay:${Math.min(idx * 0.03, 0.5)}s`;
  const catName = getCatName(cat);
  const desc = getModelDesc(model);

  const providerCountHtml = localOnly
    ? `<span class="provider-count local-only" title="Brak publicznego API — dostępny lokalnie${model.local_tool ? ' via ' + model.local_tool : ''}">tylko lokalnie</span>`
    : `<span class="provider-count">${providerCount} ${providerCount === 1 ? t('thProvider').toLowerCase() : t('filterProvider').toLowerCase()}</span>`;

  const bottomHtml = localOnly
    ? `<div class="best-price"><span class="price-label">uruchom lokalnie</span><span class="price-value unknown">${escHtml(model.local_tool || 'open source')}</span></div>`
    : `<div class="best-price">
        <span class="price-label">${t('bestPrice')}</span>
        <span class="price-value ${bestPrice.isNote ? 'unknown' : ''}">${bestPrice.value}</span>
        <span class="price-unit">${bestPrice.unit}</span>
      </div>`;

  return `
  <div class="model-card${localOnly ? ' local-only-card' : ''}" data-id="${model.id}" style="${delay}" role="button" tabindex="0" aria-label="${escHtml(model.name)} — ${escHtml(catName)}, ${t('compare')}">
    <div class="card-top">
      <div class="card-badges">
        <span class="badge-cat">${cat.icon} ${catName}</span>
        ${capBadges.join('')}
      </div>
      ${providerCountHtml}
    </div>

    ${renderVersionBadge(model)}
    <div class="card-name">${escHtml(model.name)}</div>
    <div class="card-desc">${escHtml(desc)}</div>

    <div class="card-bottom">
      ${bottomHtml}
      <div class="card-cta" aria-hidden="true">
        ${t('compare')}
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true" focusable="false"><path d="m9 18 6-6-6-6"/></svg>
      </div>
    </div>
  </div>`;
}

// ─── MODAL ───────────────────────────────────────────────────────
let lastFocusBeforeModal = null;

function openModal(modelId) {
  const model = allModels.find(m => m.id === modelId);
  if (!model) return;

  const cat = getCategoryInfo(model.category);

  // Badges
  const badges = [`<span class="badge-cat">${cat.icon} ${cat.name}</span>`];
  if (model.capabilities.includes('vision'))         badges.push('<span class="badge-cap vision">vision</span>');
  if (model.capabilities.includes('reasoning'))      badges.push('<span class="badge-cap reason">reasoning</span>');
  if (model.capabilities.includes('function_calling'))badges.push('<span class="badge-cap">function calling</span>');
  if (model.capabilities.includes('web_search'))     badges.push('<span class="badge-cap search">web search</span>');
  if (model.capabilities.includes('prompt_caching')) badges.push('<span class="badge-cap">cache</span>');
  if (model.capabilities.includes('text_to_video'))  badges.push('<span class="badge-cap">text→video</span>');
  if (model.capabilities.includes('image_to_video')) badges.push('<span class="badge-cap">image→video</span>');
  if (model.capabilities.includes('image_editing'))  badges.push('<span class="badge-cap">img edit</span>');
  if (model.open_source)     badges.push('<span class="badge-cap oss">OSS</span>');
  if (model.local_available) badges.push(`<span class="badge-cap local" title="${escHtml(model.local_tool||'')}">local ✓ ${model.local_tool ? '· '+escHtml(model.local_tool) : ''}</span>`);
  document.getElementById('modal-badges').innerHTML = badges.join('');

  document.getElementById('modal-name').textContent = model.name;
  document.getElementById('modal-desc').textContent = getModelDesc(model);

  // Meta
  const meta = [];
  if (model.context_k) {
    meta.push(`<div class="meta-item"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" focusable="false"><path d="M4 6h16M4 12h16M4 18h10"/></svg><strong>${model.context_k}k</strong> ${t('contextTokens')}</div>`);
  }
  meta.push(`<div class="meta-item"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>${t('updatedLabel')} <strong>${model.updated_at}</strong></div>`);
  // Versions
  if (model.versions && model.versions.length > 0) {
    const vHtml = model.versions.map(v =>
      `<span class="version-pill ${v.is_current ? 'current' : ''}">v${escHtml(v.version)}${v.released ? ' <span style="opacity:.5">'+escHtml(v.released)+'</span>' : ''}</span>`
    ).join('');
    meta.push(`<div class="meta-item">${t('versionsLabel')} ${vHtml}</div>`);
  }
  if (model.tags && model.tags.length > 0) {
    meta.push(`<div class="meta-item">${model.tags.map(t => `<span style="padding:2px 6px;background:var(--surface-3);border-radius:4px;font-size:11px;color:var(--text-3)">${t}</span>`).join('')}</div>`);
  }
  document.getElementById('modal-meta').innerHTML = meta.join('');

  // Find best price for comparison
  let bestVal = Infinity;
  model.providers.forEach(p => {
    if (!p.available) return;
    const v = getPriceValue(p.pricing, model.category);
    if (v !== null && v < bestVal) bestVal = v;
  });

  // Table rows
  const tbody = document.getElementById('modal-tbody');
  tbody.innerHTML = '';
  model.providers.forEach(p => {
    const prov = allProviders[p.provider_id] || { name: p.provider_id, logo_color: '#666', type: '' };
    const formatted = formatPrice(p.pricing, model.category);
    const priceVal = getPriceValue(p.pricing, model.category);
    const isBest = priceVal !== null && priceVal === bestVal && p.available;

    const linkUrl = p.affiliate_url || p.url;
    const isAffiliate = !!p.affiliate_url;

    const row = document.createElement('tr');
    if (!p.available) row.classList.add('unavailable');

    let priceHtml;
    if (formatted.isNote) {
      priceHtml = `<td><div class="price-cell notes">${escHtml(formatted.value)}</div><div class="price-note">${escHtml(formatted.unit)}</div></td><td></td>`;
    } else {
      priceHtml = `
        <td><div class="price-cell" style="${p.available ? '' : 'color:var(--text-3)'}">${escHtml(formatted.value)}${isBest ? ` <span class="best-badge">${t('cheapest')}</span>` : ''}</div></td>
        <td><span style="font-size:12px;color:var(--text-3);font-family:'JetBrains Mono',monospace;">${escHtml(formatted.unit)}</span></td>
      `;
    }

    // Notes / secondary price
    let notesHtml = '';
    if (!formatted.isNote && p.pricing && p.pricing.notes) {
      notesHtml = `<div class="price-note">${escHtml(p.pricing.notes)}</div>`;
    }
    if (p.notes) {
      notesHtml += `<div class="price-note">${escHtml(p.notes)}</div>`;
    }
    // For LLM also show output price
    let outputHtml = '';
    if (p.pricing && p.pricing.output_per_1m !== undefined) {
      outputHtml = `<div class="price-note">out: <span style="font-family:'JetBrains Mono',monospace;">$${p.pricing.output_per_1m.toFixed(2)}</span> / 1M</div>`;
    }

    row.innerHTML = `
      <td>
        <div class="prov-name-cell">
          <div class="prov-dot" style="background:${prov.logo_color || '#666'}"></div>
          <div>
            <div class="prov-name">${escHtml(prov.name)}</div>
            <div class="prov-type">${prov.type === 'aggregator' ? t('typeAggregator') : prov.type === 'direct' ? t('typeDirect') : ''}</div>
          </div>
        </div>
      </td>
      ${priceHtml}
      <td>${notesHtml}${outputHtml}</td>
      <td>
        ${linkUrl && p.available ? `<a href="${escAttr(linkUrl)}" target="_blank" rel="noopener" class="link-btn ${isAffiliate ? 'affiliate' : ''}"
          data-track-event="provider_click"
          data-track-prop-provider="${escAttr(p.provider_id)}"
          data-track-prop-model="${escAttr(model.id)}"
          data-track-prop-category="${escAttr(model.category)}"
          data-track-prop-affiliate="${isAffiliate ? '1' : '0'}">
          ${isAffiliate ? '★ ' : ''}${t('visitLink')}
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true" focusable="false"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><path d="M15 3h6v6"/><path d="m10 14 11-11"/></svg>
        </a>` : !p.available ? `<span style="font-size:11px;color:var(--text-3)">${t('unavailable')}</span>` : ''}
      </td>
    `;
    tbody.appendChild(row);
  });

  // Report error link
  const reportEl = document.getElementById('modal-report');
  const reportUrl = buildReportUrl(model);
  reportEl.innerHTML = `<a href="${escAttr(reportUrl)}" target="_blank" rel="noopener" class="report-link">
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg>
    ${t('reportError')}
  </a>`;

  lastFocusBeforeModal = document.activeElement;
  history.pushState({ modelId }, '', '#' + modelId);
  document.getElementById('modal-overlay').classList.add('open');
  document.body.style.overflow = 'hidden';
  // Ukryj zawartość za modalem dla screen readerów i przeglądarki
  document.querySelector('nav').inert = true;
  document.querySelector('.hero').inert = true;
  document.querySelector('.layout').inert = true;
  document.getElementById('compare-section').inert = true;
  document.querySelector('footer').inert = true;
  // Move focus into modal
  requestAnimationFrame(() => {
    const closeBtn = document.querySelector('.modal-close');
    if (closeBtn) closeBtn.focus();
  });
}

function closeModal(e) {
  if (e.target === document.getElementById('modal-overlay')) closeModalDirect();
}

function closeModalDirect() {
  document.getElementById('modal-overlay').classList.remove('open');
  document.body.style.overflow = '';
  if (location.hash) history.pushState({}, '', location.pathname + location.search);
  document.querySelector('nav').inert = false;
  document.querySelector('.hero').inert = false;
  document.querySelector('.layout').inert = false;
  document.getElementById('compare-section').inert = false;
  document.querySelector('footer').inert = false;
  if (lastFocusBeforeModal) {
    lastFocusBeforeModal.focus();
    lastFocusBeforeModal = null;
  }
}

// Copy link to current model
function copyModalLink() {
  const url = location.href;
  navigator.clipboard.writeText(url).then(() => {
    const btn = document.getElementById('modal-copy-link');
    const label = document.getElementById('modal-copy-label');
    btn.classList.add('copied');
    label.textContent = t('copied');
    setTimeout(() => {
      btn.classList.remove('copied');
      label.textContent = t('copyLink');
    }, 2000);
  });
}

// Browser back button closes modal
window.addEventListener('popstate', () => {
  const overlay = document.getElementById('modal-overlay');
  if (overlay.classList.contains('open')) {
    overlay.classList.remove('open');
    document.body.style.overflow = '';
    document.querySelector('nav').inert = false;
    document.querySelector('.hero').inert = false;
    document.querySelector('.layout').inert = false;
    document.querySelector('footer').inert = false;
  } else if (location.hash === '#compare') {
    if (!compareState.active) toggleCompare();
  } else if (location.hash) {
    if (compareState.active) toggleCompare();
    const m = allModels.find(m => m.id === location.hash.slice(1));
    if (m) openModal(m.id);
  } else if (compareState.active) {
    toggleCompare();
  }
});

// Close on Escape + modal focus trap
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModalDirect();
});

document.getElementById('modal').addEventListener('keydown', function(e) {
  if (e.key !== 'Tab') return;
  const modal = this;
  const focusable = Array.from(modal.querySelectorAll(
    'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
  ));
  if (!focusable.length) return;
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (e.shiftKey) {
    if (document.activeElement === first) { e.preventDefault(); last.focus(); }
  } else {
    if (document.activeElement === last) { e.preventDefault(); first.focus(); }
  }
});

// Toggle switch keyboard (Space/Enter to activate)
['toggle-multi', 'toggle-affiliate', 'toggle-opensource', 'toggle-freeapi', 'toggle-apionly'].forEach(id => {
  document.getElementById(id).addEventListener('keydown', function(e) {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      this.click();
    }
  });
});

// ─── ACTIVE FILTERS ───────────────────────────────────────────────
function updateActiveFilters() {
  const container = document.getElementById('active-filters');
  const chips = [];

  if (filters.category !== 'all') {
    const cat = getCategoryInfo(filters.category);
    chips.push(`<button type="button" class="filter-chip" onclick="clearCategory()" aria-label="Usuń filtr: ${getCatName(cat)}">${cat.icon} ${getCatName(cat)} ×</button>`);
  }
  if (filters.search) {
    chips.push(`<button type="button" class="filter-chip" onclick="clearSearch()" aria-label="Usuń wyszukiwanie">${t('searchFilter')}: "${escHtml(filters.search)}" ×</button>`);
  }
  filters.providers.forEach(pid => {
    const p = allProviders[pid];
    if (p) chips.push(`<button type="button" class="filter-chip" onclick="clearProvider('${pid}')" aria-label="Usuń filtr: ${p.name}">${p.name} ×</button>`);
  });
  if (filters.capVision)    chips.push(`<button type="button" class="filter-chip" onclick="clearCap('vision')" aria-label="Usuń filtr: Vision">Vision ×</button>`);
  if (filters.capReasoning) chips.push(`<button type="button" class="filter-chip" onclick="clearCap('reasoning')" aria-label="Usuń filtr: Reasoning">Reasoning ×</button>`);
  if (filters.capFunctions) chips.push(`<button type="button" class="filter-chip" onclick="clearCap('functions')" aria-label="Usuń filtr: Functions">Functions ×</button>`);
  if (filters.capSearch)    chips.push(`<button type="button" class="filter-chip" onclick="clearCap('search')" aria-label="Usuń filtr: Web Search">Web Search ×</button>`);
  if (filters.multiProvider) chips.push(`<button type="button" class="filter-chip" onclick="clearToggle('multi')" aria-label="Usuń filtr: ${t('optionMulti')}">${t('optionMulti')} ×</button>`);
  if (filters.affiliate)    chips.push(`<button type="button" class="filter-chip" onclick="clearToggle('affiliate')" aria-label="Usuń filtr: Affiliate">Affiliate ×</button>`);
  if (filters.openSource)   chips.push(`<button type="button" class="filter-chip" onclick="clearToggle('opensource')" aria-label="Usuń filtr: OSS">OSS ×</button>`);
  if (filters.freeApi)      chips.push(`<button type="button" class="filter-chip" onclick="clearToggle('freeapi')" aria-label="Usuń filtr: Free API">Free API ×</button>`);
  if (filters.apiOnly)      chips.push(`<button type="button" class="filter-chip" onclick="clearToggle('apionly')" aria-label="Usuń filtr: Tylko API">Tylko API ×</button>`);

  container.innerHTML = chips.join('');
}

function clearCategory() {
  filters.category = 'all';
  document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
  document.querySelector('.cat-pill[data-cat="all"]').classList.add('active');
  render();
}

function clearSearch() {
  filters.search = '';
  document.getElementById('search').value = '';
  render();
}

function clearProvider(pid) {
  filters.providers.delete(pid);
  const checkbox = document.getElementById('prov-' + pid);
  if (checkbox) checkbox.checked = false;
  render();
}

function clearCap(cap) {
  if (cap === 'vision')    { filters.capVision = false;    document.getElementById('cap-vision').checked = false; }
  if (cap === 'reasoning') { filters.capReasoning = false; document.getElementById('cap-reasoning').checked = false; }
  if (cap === 'functions') { filters.capFunctions = false; document.getElementById('cap-functions').checked = false; }
  if (cap === 'search')    { filters.capSearch = false;    document.getElementById('cap-search').checked = false; }
  render();
}

function clearToggle(which) {
  if (which === 'multi') {
    filters.multiProvider = false;
    document.getElementById('toggle-multi').classList.remove('active');
    document.getElementById('toggle-multi').setAttribute('aria-checked', 'false');
  }
  if (which === 'affiliate') {
    filters.affiliate = false;
    document.getElementById('toggle-affiliate').classList.remove('active');
    document.getElementById('toggle-affiliate').setAttribute('aria-checked', 'false');
  }
  if (which === 'opensource') {
    filters.openSource = false;
    document.getElementById('toggle-opensource').classList.remove('active');
    document.getElementById('toggle-opensource').setAttribute('aria-checked', 'false');
  }
  if (which === 'freeapi') {
    filters.freeApi = false;
    document.getElementById('toggle-freeapi').classList.remove('active');
    document.getElementById('toggle-freeapi').setAttribute('aria-checked', 'false');
  }
  if (which === 'apionly') {
    filters.apiOnly = false;
    document.getElementById('toggle-apionly').classList.remove('active');
    document.getElementById('toggle-apionly').setAttribute('aria-checked', 'false');
  }
  render();
}

// ─── EVENT LISTENERS ─────────────────────────────────────────────
document.getElementById('search').addEventListener('input', (e) => {
  filters.search = e.target.value.trim();
  render();
});

document.getElementById('sort-select').addEventListener('change', (e) => {
  filters.sort = e.target.value;
  render();
});

document.getElementById('cap-vision').addEventListener('change', (e) => {
  filters.capVision = e.target.checked;
  render();
});

document.getElementById('cap-reasoning').addEventListener('change', (e) => {
  filters.capReasoning = e.target.checked;
  render();
});

document.getElementById('cap-functions').addEventListener('change', (e) => {
  filters.capFunctions = e.target.checked;
  render();
});

document.getElementById('cap-search').addEventListener('change', (e) => {
  filters.capSearch = e.target.checked;
  render();
});

document.getElementById('toggle-multi').addEventListener('click', function() {
  filters.multiProvider = !filters.multiProvider;
  this.classList.toggle('active', filters.multiProvider);
  this.setAttribute('aria-checked', filters.multiProvider);
  render();
});

document.getElementById('toggle-affiliate').addEventListener('click', function() {
  filters.affiliate = !filters.affiliate;
  this.classList.toggle('active', filters.affiliate);
  this.setAttribute('aria-checked', filters.affiliate);
  render();
});

document.getElementById('toggle-opensource').addEventListener('click', function() {
  filters.openSource = !filters.openSource;
  this.classList.toggle('active', filters.openSource);
  this.setAttribute('aria-checked', filters.openSource);
  render();
});

document.getElementById('toggle-freeapi').addEventListener('click', function() {
  filters.freeApi = !filters.freeApi;
  this.classList.toggle('active', filters.freeApi);
  this.setAttribute('aria-checked', filters.freeApi);
  render();
});

document.getElementById('toggle-apionly').addEventListener('click', function() {
  filters.apiOnly = !filters.apiOnly;
  this.classList.toggle('active', filters.apiOnly);
  this.setAttribute('aria-checked', filters.apiOnly);
  render();
});

document.getElementById('reset-btn').addEventListener('click', () => {
  filters.category = 'all';
  filters.providers = new Set();
  filters.search = '';
  filters.capVision = false;
  filters.capReasoning = false;
  filters.capFunctions = false;
  filters.capSearch = false;
  filters.multiProvider = false;
  filters.affiliate = false;
  filters.openSource = false;
  filters.freeApi = false;
  filters.apiOnly = false;
  filters.sort = 'name';

  document.getElementById('search').value = '';
  document.getElementById('sort-select').value = 'name';
  document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
  document.querySelector('.cat-pill[data-cat="all"]').classList.add('active');
  document.querySelectorAll('.provider-item input[type=checkbox]').forEach(c => c.checked = false);
  document.getElementById('cap-vision').checked = false;
  document.getElementById('cap-reasoning').checked = false;
  document.getElementById('cap-functions').checked = false;
  document.getElementById('cap-search').checked = false;
  document.getElementById('toggle-multi').classList.remove('active');
  document.getElementById('toggle-affiliate').classList.remove('active');
  document.getElementById('toggle-opensource').classList.remove('active');
  document.getElementById('toggle-freeapi').classList.remove('active');
  document.getElementById('toggle-apionly').classList.remove('active');

  render();
});

// ─── UTILS ───────────────────────────────────────────────────────
const REPO_URL = 'https://github.com/jurczykpawel/ai-api-catalog';

function buildReportUrl(model) {
  const providers = (model?.providers || [])
    .map(p => `${p.provider_id}${p.pricing?.input_per_1m != null ? ' ($' + p.pricing.input_per_1m + '/1M in)' : ''}`)
    .join(', ');
  const title = model
    ? `[Data error] ${model.name}`
    : 'Data error report';
  const body = model
    ? `**Model:** ${model.name}\n**ID:** ${model.id}\n**Category:** ${model.category}\n**Providers:** ${providers}\n\n**What's wrong?**\n\n<!-- Describe the issue: wrong price, missing provider, incorrect category, etc. -->`
    : `**What's wrong?**\n\n<!-- Describe the issue -->\n\n**Model (if applicable):**\n`;
  return `${REPO_URL}/issues/new?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}&labels=data-error`;
}

function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escAttr(str) {
  return escHtml(str);
}

// ─── COMPARE ──────────────────────────────────────────────────

// Preferred flagship model IDs per provider. Update when new flagship launches.
// Fallback: most capable non-reasoning LLM from that provider.
const FLAGSHIP_MODELS = {
  openai:    ['gpt-5-5-pro', 'gpt-5-4-pro', 'gpt-5', 'gpt-4-1', 'gpt-4o'],
  anthropic: ['claude-opus-4-6', 'claude-4-sonnet', 'claude-4-opus'],
  google:    ['vertex_ai-gemini-3-pro-preview', 'gemini-2-0-flash'],
  xai:       ['xai-grok-3-fast-beta', 'xai-grok-beta'],
  deepseek:  ['deepseek-deepseek-v4-pro', 'deepseek-deepseek-chat-v3-1', 'deepseek-deepseek-chat', 'deepseek-chat'],
  mistral:   ['mistral-mistral-large-latest', 'mistral-mistral-large-2402'],
};

const CODING_MODELS = {
  anthropic: ['claude-4-sonnet', 'claude-opus-4-6', 'claude-4-opus'],
  openai:    ['gpt-4-1', 'gpt-4o', 'gpt-5'],
  google:    ['vertex_ai-gemini-3-pro-preview', 'gemini-2-0-flash'],
  deepseek:  ['deepseek-deepseek-chat', 'deepseek-chat'],
  xai:       ['xai-grok-3-fast-beta'],
};

const REASONING_MODELS = {
  openai:    ['o3-pro', 'gpt-5-4-pro', 'o1-pro'],
  anthropic: ['claude-opus-4-6', 'claude-4-opus', 'claude-3-7-sonnet'],
  google:    ['gemini-2-5-pro', 'vertex_ai-gemini-3-pro-preview'],
  deepseek:  ['deepseek-reasoner', 'deepseek-deepseek-reasoner'],
  xai:       ['xai-grok-4-20-beta-0309-reasoning', 'xai-grok-3-mini-fast'],
};

const IMAGE_MODELS = [
  'openai-gpt-image-2', 'flux-2-pro', 'dalle-3', 'ideogram-v3',
  'nano-banana-2', 'gemini-gemini-2-5-flash-image', 'imagen-4', 'seedream-4-5',
];

const VIDEO_MODELS = [
  'sora-2', 'veo-3-1', 'runway-gen4', 'kling-3-0',
  'luma-ray-2', 'hailuo-2-3', 'seedance-2', 'wan-2-6',
];

// Resolve preferred models: try each candidate in order, return first that exists in data
function resolvePreferred(models, preferredMap) {
  const modelIds = new Set(models.map(m => m.id));
  const result = [];
  for (const [pid, candidates] of Object.entries(preferredMap)) {
    const found = candidates.find(id => modelIds.has(id));
    if (found) result.push(found);
  }
  return result;
}

// Resolve flat list of model IDs, filtering to those that exist in data
function resolveList(models, idList) {
  const modelIds = new Set(models.map(m => m.id));
  return idList.filter(id => modelIds.has(id));
}

const PRESET_RULES = [
  {
    id: 'flagship',
    icon: '🏆',
    nameKey: 'presetFlagship',
    resolve: (models) => resolvePreferred(models, FLAGSHIP_MODELS),
  },
  {
    id: 'coding',
    icon: '💻',
    nameKey: 'presetCoding',
    resolve: (models) => resolvePreferred(models, CODING_MODELS),
  },
  {
    id: 'reasoning',
    icon: '🧠',
    nameKey: 'presetReasoning',
    resolve: (models) => resolvePreferred(models, REASONING_MODELS),
  },
  {
    id: 'budget',
    icon: '💰',
    nameKey: 'presetBudget',
    resolve: (models) => {
      const candidates = [];
      for (const m of models) {
        if (m.category !== 'llm') continue;
        for (const p of m.providers) {
          if (!p.available || p.pricing?.input_per_1m == null) continue;
          if (p.provider_id === 'openrouter') continue;
          candidates.push({ id: m.id, price: p.pricing.input_per_1m, pid: p.provider_id });
        }
      }
      candidates.sort((a, b) => a.price - b.price);
      const result = [], seenProviders = new Set();
      for (const c of candidates) {
        if (seenProviders.has(c.pid) || result.includes(c.id)) continue;
        seenProviders.add(c.pid);
        result.push(c.id);
        if (result.length >= 6) break;
      }
      return result;
    }
  },
  {
    id: 'image',
    icon: '🖼️',
    nameKey: 'presetImage',
    resolve: (models) => resolveList(models, IMAGE_MODELS),
  },
  {
    id: 'video',
    icon: '🎬',
    nameKey: 'presetVideo',
    resolve: (models) => resolveList(models, VIDEO_MODELS),
  },
  {
    id: 'embedding',
    icon: '📐',
    nameKey: 'presetEmbedding',
    resolve: (models) => {
      const candidates = [];
      for (const m of models) {
        if (m.category !== 'embedding') continue;
        for (const p of m.providers) {
          if (!p.available || p.pricing?.input_per_1m == null) continue;
          if (p.provider_id === 'openrouter') continue;
          candidates.push({ id: m.id, price: p.pricing.input_per_1m, pid: p.provider_id });
        }
      }
      candidates.sort((a, b) => a.price - b.price);
      const result = [], seen = new Set();
      for (const c of candidates) {
        if (seen.has(c.id)) continue;
        seen.add(c.id);
        result.push(c.id);
        if (result.length >= 6) break;
      }
      return result;
    }
  },
];

let compareState = { active: false, models: [], preset: null, resolvedPresets: {} };

function toggleCompare() {
  compareState.active = !compareState.active;
  const section = document.getElementById('compare-section');
  const hero = document.querySelector('.hero');
  const layout = document.querySelector('.layout');
  const navBtn = document.getElementById('nav-compare');

  if (compareState.active) {
    section.classList.add('active');
    hero.style.display = 'none';
    layout.style.display = 'none';
    navBtn.classList.add('active');
    history.pushState({}, '', '#compare');
    if (!compareState._built) {
      buildPresets();
      compareState._built = true;
    }
  } else {
    section.classList.remove('active');
    hero.style.display = '';
    layout.style.display = '';
    navBtn.classList.remove('active');
    if (location.hash.startsWith('#compare')) {
      history.pushState({}, '', location.pathname + location.search);
    }
  }
}

function buildHeroPresetLinks() {
  const container = document.getElementById('hero-compare-links');
  if (!container || !allModels.length) return;
  const quickPresets = ['flagship', 'coding', 'reasoning', 'image', 'video'];
  container.innerHTML = quickPresets.map(id => {
    const preset = PRESET_RULES.find(p => p.id === id);
    if (!preset) return '';
    return `<a href="#compare/${id}" class="hero-preset-link"
      data-track-event="preset_click"
      data-track-prop-preset="${id}"
      data-track-prop-source="hero"
      onclick="event.preventDefault();goToPreset('${id}')">${preset.icon} ${t(preset.nameKey)}</a>`;
  }).join('');
}

function buildPresets() {
  const container = document.getElementById('compare-presets');
  container.innerHTML = '';

  for (const preset of PRESET_RULES) {
    const modelIds = preset.resolve(allModels);
    compareState.resolvedPresets[preset.id] = modelIds;
    if (modelIds.length < 2) continue;

    const dotsHtml = modelIds.slice(0, 6).map(id => {
      const m = allModels.find(x => x.id === id);
      if (!m) return '';
      const prov = m.providers.find(p => p.available) || m.providers[0];
      const provInfo = allProviders[prov?.provider_id] || {};
      return `<div class="preset-card-dot" style="background:${provInfo.logo_color || '#666'}"></div>`;
    }).join('');

    const card = document.createElement('div');
    card.className = 'preset-card';
    card.dataset.preset = preset.id;
    card.dataset.trackEvent = 'preset_click';
    card.dataset.trackPropPreset = preset.id;
    card.dataset.trackPropSource = 'page';
    card.innerHTML = `
      <div class="preset-card-icon">${preset.icon}</div>
      <div class="preset-card-name">${t(preset.nameKey)}</div>
      <div class="preset-card-count">${modelIds.length} ${t('models')}</div>
      <div class="preset-card-models">${dotsHtml}</div>
    `;
    card.addEventListener('click', () => selectPreset(preset.id));
    container.appendChild(card);
  }
}

function selectPreset(presetId) {
  const modelIds = compareState.resolvedPresets[presetId];
  if (!modelIds) return;
  compareState.models = [...modelIds];
  compareState.preset = presetId;
  history.replaceState({}, '', '#compare/' + presetId);
  document.querySelectorAll('.preset-card').forEach(c =>
    c.classList.toggle('active', c.dataset.preset === presetId)
  );
  renderCompareBar();
  renderCompareTable();
}

// Navigate to compare with a specific preset (from hero links)
function goToPreset(presetId) {
  if (!compareState.active) toggleCompare();
  // Presets may not be built yet on first toggle
  if (!compareState.resolvedPresets[presetId]) {
    requestAnimationFrame(() => selectPreset(presetId));
  } else {
    selectPreset(presetId);
  }
}

function addModelToCompare(modelId) {
  if (compareState.models.includes(modelId) || compareState.models.length >= 10) return;
  compareState.models.push(modelId);
  compareState.preset = null;
  document.querySelectorAll('.preset-card').forEach(c => c.classList.remove('active'));
  renderCompareBar();
  renderCompareTable();
}

function removeModelFromCompare(modelId) {
  compareState.models = compareState.models.filter(id => id !== modelId);
  compareState.preset = null;
  document.querySelectorAll('.preset-card').forEach(c => c.classList.remove('active'));
  renderCompareBar();
  renderCompareTable();
}

function renderCompareBar() {
  const bar = document.getElementById('compare-bar');
  let html = '';

  for (const id of compareState.models) {
    const m = allModels.find(x => x.id === id);
    if (!m) continue;
    const bestProv = getBestProvider(m);
    const provInfo = allProviders[bestProv?.provider_id] || {};
    html += `<div class="compare-chip">
      <div class="compare-chip-dot" style="background:${provInfo.logo_color || '#666'}"></div>
      ${escHtml(m.name)}
      <button class="compare-chip-remove" onclick="removeModelFromCompare('${escAttr(id)}')" aria-label="Remove ${escHtml(m.name)}">×</button>
    </div>`;
  }

  html += `<div class="compare-add-btn" id="compare-add-btn" onclick="toggleCompareSearch(event)">
    ${t('compareAddModel')}
    <div class="compare-search-dropdown" id="compare-search-dropdown">
      <input type="text" class="compare-search-input" id="compare-search-input"
             placeholder="${t('compareSearchPh')}" onclick="event.stopPropagation()"
             oninput="filterCompareSearch(this.value)">
      <div id="compare-search-results"></div>
    </div>
  </div>`;

  bar.innerHTML = html;
}

function toggleCompareSearch(e) {
  e.stopPropagation();
  const dropdown = document.getElementById('compare-search-dropdown');
  const isOpen = dropdown.classList.contains('open');
  dropdown.classList.toggle('open');
  if (!isOpen) {
    const input = document.getElementById('compare-search-input');
    input.value = '';
    input.focus();
    filterCompareSearch('');
  }
}

document.addEventListener('click', () => {
  const dd = document.getElementById('compare-search-dropdown');
  if (dd) dd.classList.remove('open');
});

function filterCompareSearch(query) {
  const container = document.getElementById('compare-search-results');
  const normalize = s => (s || '').toLowerCase().replace(/[-_./]+/g, ' ').replace(/\s+/g, ' ').trim();
  const q = normalize(query);
  let catFilter = null;
  if (compareState.models.length > 0) {
    const firstModel = allModels.find(m => m.id === compareState.models[0]);
    if (firstModel) catFilter = firstModel.category;
  }

  let candidates = allModels.filter(m => {
    if (compareState.models.includes(m.id)) return false;
    if (catFilter && m.category !== catFilter) return false;
    if (!m.providers.some(p => p.available)) return false;
    if (!q) return true;
    return normalize(m.id).includes(q) ||
           normalize(m.name).includes(q) ||
           (m.tags || []).some(tag => normalize(tag).includes(q));
  });

  candidates.sort((a, b) => getBestPriceNum(a) - getBestPriceNum(b));
  candidates = candidates.slice(0, 20);

  container.innerHTML = candidates.map(m => {
    const bp = getBestProvider(m);
    const fp = bp ? formatPrice(bp.pricing, m.category, true) : { value: '—' };
    const provInfo = allProviders[bp?.provider_id] || {};
    return `<div class="compare-search-item" onclick="event.stopPropagation();addModelToCompare('${escAttr(m.id)}');document.getElementById('compare-search-dropdown').classList.remove('open')">
      <div class="compare-chip-dot" style="background:${provInfo.logo_color || '#666'};display:inline-block"></div>
      ${escHtml(m.name)}
      <span class="compare-search-item-price">${fp.value}</span>
    </div>`;
  }).join('') || `<div style="padding:12px;color:var(--text-3);font-size:13px">${t('noResults')}</div>`;
}

function renderCompareTable() {
  const wrap = document.getElementById('compare-table-wrap');

  if (compareState.models.length === 0) {
    wrap.innerHTML = `<div class="compare-empty">${t('compareEmpty')}</div>`;
    return;
  }

  const models = compareState.models.map(id => allModels.find(m => m.id === id)).filter(Boolean);
  const categories = [...new Set(models.map(m => m.category))];
  const isLLM = categories.length === 1 && categories[0] === 'llm';

  const rows = models.map(m => {
    const bestProv = getBestProvider(m);
    const provInfo = allProviders[bestProv?.provider_id] || {};
    const pricing = bestProv?.pricing || {};
    return { model: m, provider: bestProv, provInfo, pricing };
  });

  let cheapestInput = Infinity, cheapestOutput = Infinity, cheapestPrice = Infinity;
  for (const r of rows) {
    if (r.pricing.input_per_1m != null && r.pricing.input_per_1m < cheapestInput) cheapestInput = r.pricing.input_per_1m;
    if (r.pricing.output_per_1m != null && r.pricing.output_per_1m < cheapestOutput) cheapestOutput = r.pricing.output_per_1m;
    const pv = getPriceValue(r.pricing, r.model.category);
    if (pv != null && pv < cheapestPrice) cheapestPrice = pv;
  }

  let html = '<table class="compare-table"><thead><tr>';
  html += `<th>${t('thModel')}</th>`;

  if (isLLM) {
    html += `<th>${t('thInputPrice')}</th><th>${t('thOutputPrice')}</th><th>${t('thContext')}</th><th>${t('thCapabilities')}</th>`;
  } else {
    html += `<th>${t('thPrice')}</th><th>${t('thUnit')}</th><th>${t('thCapabilities')}</th>`;
  }
  html += '</tr></thead><tbody>';

  for (const r of rows) {
    const capBadges = (r.model.capabilities || []).slice(0, 4).map(c =>
      `<span class="compare-cap-badge">${c.replace(/_/g, ' ')}</span>`
    ).join('');

    html += '<tr>';
    html += `<td>
      <div class="compare-model-name" onclick="openModal('${escAttr(r.model.id)}')">${escHtml(r.model.name)}</div>
      <div class="compare-model-provider">
        <span class="compare-chip-dot" style="background:${r.provInfo.logo_color || '#666'};display:inline-block;vertical-align:middle;margin-right:4px"></span>
        ${escHtml(r.provInfo.name || r.provider?.provider_id || '—')}
        ${r.model.providers.length > 1 ? `<span style="color:var(--text-3);font-size:10px">+${r.model.providers.length - 1}</span>` : ''}
      </div>
    </td>`;

    if (isLLM) {
      const inp = r.pricing.input_per_1m;
      const isCheapestIn = inp != null && inp === cheapestInput && rows.length > 1;
      html += `<td><div class="compare-price${isCheapestIn ? ' cheapest-cell' : ''}">${inp != null ? '$' + inp.toFixed(2) : '—'}${isCheapestIn ? ' <span class="best-badge">' + t('cheapest') + '</span>' : ''}</div></td>`;

      const out = r.pricing.output_per_1m;
      const isCheapestOut = out != null && out === cheapestOutput && rows.length > 1;
      html += `<td><div class="compare-price${isCheapestOut ? ' cheapest-cell' : ''}">${out != null ? '$' + out.toFixed(2) : '—'}${isCheapestOut ? ' <span class="best-badge">' + t('cheapest') + '</span>' : ''}</div></td>`;

      html += `<td><span style="font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--text-2)">${r.model.context_k ? r.model.context_k + 'k' : '—'}</span></td>`;
      html += `<td>${capBadges}</td>`;
    } else {
      const formatted = formatPrice(r.pricing, r.model.category);
      const pv = getPriceValue(r.pricing, r.model.category);
      const isCheap = pv != null && pv === cheapestPrice && rows.length > 1;
      if (formatted.isNote) {
        html += `<td><span class="compare-price-na">${escHtml(formatted.unit)}</span></td><td></td>`;
      } else {
        html += `<td><div class="compare-price${isCheap ? ' cheapest-cell' : ''}">${formatted.value}${isCheap ? ' <span class="best-badge">' + t('cheapest') + '</span>' : ''}</div></td>`;
        html += `<td><span style="font-size:12px;color:var(--text-3)">${formatted.unit}</span></td>`;
      }
      html += `<td>${capBadges}</td>`;
    }
    html += '</tr>';
  }

  html += '</tbody></table>';
  wrap.innerHTML = html;
}

// ─── INIT ────────────────────────────────────────────────────────
loadData();
