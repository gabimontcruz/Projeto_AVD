// app.js - Lógica Front-end, Integração PokéAPI (Sprites Showdown & Cries) e K-Means

let currentFilterType = 'all';
let currentSearch = '';
let currentCluster = 'all';
let currentGen = 'all';
let currentPokemonForCry = null;

const ALL_TYPES = ['Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Steel', 'Fairy', 'Dark'];

const CLUSTER_COLORS = {
  0: '#3b82f6', // Azul - Básico
  1: '#10b981', // Verde - Tanque
  2: '#f59e0b', // Âmbar - Sweeper
  3: '#f43f5e'  // Rosa/Rubi - Titã
};

const CLUSTER_NAMES = {
  0: 'Básico / Little Cup',
  1: 'Tanque / Muralha',
  2: 'Sweeper / Ágil',
  3: 'Titã / Lendário'
};

const CLUSTER_STATS_MEAN = {
  0: { hp: 51.2, atk: 53.4, def: 49.8, spa: 50.1, spd: 49.2, spe: 51.4 },
  1: { hp: 78.4, atk: 82.1, def: 112.5, spa: 66.8, spd: 88.4, spe: 44.2 },
  2: { hp: 71.3, atk: 99.4, def: 70.8, spa: 96.2, spd: 74.1, spe: 94.8 },
  3: { hp: 96.8, atk: 122.5, def: 104.2, spa: 124.8, spd: 106.1, spe: 98.4 }
};

let activeLabClusters = [0, 1, 2, 3];

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
  setupTypePills();
  setupEventListeners();
  setupBattleOptions();
  renderGrid();
  drawLabRadar();
});

// Setup dos botões de tipo
function setupTypePills() {
  const container = document.getElementById('type-pills');
  ALL_TYPES.forEach(t => {
    const btn = document.createElement('button');
    btn.className = `type-pill px-3 py-1 rounded-lg font-bold transition-all border border-transparent type-${t} opacity-80 hover:opacity-100`;
    btn.innerText = t;
    btn.onclick = () => setTypeFilter(t);
    container.appendChild(btn);
  });
}

function setTypeFilter(type) {
  currentFilterType = type;
  document.querySelectorAll('.type-pill').forEach(b => {
    if ((type === 'all' && b.innerText === 'Todos') || b.innerText === type) {
      b.classList.add('ring-2', 'ring-white', 'opacity-100');
    } else {
      b.classList.remove('ring-2', 'ring-white');
      b.classList.add('opacity-80');
    }
  });
  renderGrid();
}

function setupEventListeners() {
  document.getElementById('search-input').addEventListener('input', (e) => {
    currentSearch = e.target.value.toLowerCase().trim();
    renderGrid();
  });

  document.getElementById('filter-cluster').addEventListener('change', (e) => {
    currentCluster = e.target.value;
    renderGrid();
  });

  document.getElementById('filter-gen').addEventListener('change', (e) => {
    currentGen = e.target.value;
    renderGrid();
  });
}

// Filtro e Renderização da Grid
function getFilteredData() {
  return POKEMON_DATA.filter(p => {
    const matchSearch = currentSearch === '' || 
      p.name.toLowerCase().includes(currentSearch) || 
      p.id.toString() === currentSearch;

    const matchType = currentFilterType === 'all' || 
      p.type1 === currentFilterType || 
      p.type2 === currentFilterType;

    const matchCluster = currentCluster === 'all' || 
      p.cluster.toString() === currentCluster;

    const matchGen = currentGen === 'all' || 
      p.gen.toString() === currentGen;

    return matchSearch && matchType && matchCluster && matchGen;
  });
}

function renderGrid() {
  const container = document.getElementById('pokemon-grid');
  const filtered = getFilteredData();
  document.getElementById('visible-count').innerText = filtered.length;

  // Limitar renderização aos primeiros 60 para performance super rápida
  const toShow = filtered.slice(0, 60);

  container.innerHTML = toShow.map(p => {
    const isHolo = p.legendary || p.cluster === 3;
    const holoClass = isHolo ? 'holo-card ring-1 ring-amber-400/40' : '';
    const clusterColor = CLUSTER_COLORS[p.cluster];

    // URL Showdown animado com fallback para artwork oficial
    const showdownUrl = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/${p.id}.gif`;
    const artworkUrl = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${p.id}.png`;

    return `
      <div onclick="openModal(${p.id})" class="pokemon-card ${holoClass} p-4 cursor-pointer group flex flex-col justify-between">
        
        <!-- Header do Card -->
        <div class="flex items-center justify-between z-10">
          <span class="text-xs font-mono font-bold text-slate-400">#${String(p.id).padStart(3, '0')}</span>
          <span class="text-[10px] font-bold px-2 py-0.5 rounded-full" style="background-color: ${clusterColor}25; color: ${clusterColor}; border: 1px solid ${clusterColor}40">
            ${p.cluster_name.split('/')[0].trim()}
          </span>
        </div>

        <!-- Sprite Pokémon Animado com Fallback -->
        <div class="relative py-4 flex items-center justify-center h-36 z-10">
          <img src="${showdownUrl}" 
               onerror="this.onerror=null; this.src='${artworkUrl}';"
               class="max-h-24 max-w-[90px] object-contain drop-shadow-[0_8px_12px_rgba(0,0,0,0.5)] group-hover:scale-115 transition-transform duration-300"
               loading="lazy" 
               alt="${p.name}">
        </div>

        <!-- Informações e Tipagem -->
        <div class="z-10 space-y-2">
          <div class="flex items-center justify-between">
            <h4 class="font-black text-sm text-white group-hover:text-rose-400 transition-colors">${p.name}</h4>
            ${p.legendary ? '<i class="fa-solid fa-crown text-amber-400 text-xs" title="Pokémon Lendário"></i>' : ''}
          </div>

          <div class="flex gap-1">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold type-${p.type1}">${p.type1}</span>
            ${p.type2 ? `<span class="px-2 py-0.5 rounded text-[10px] font-bold type-${p.type2}">${p.type2}</span>` : ''}
          </div>

          <!-- Total Base Stat Bar -->
          <div class="pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono">
            <span class="text-slate-400">Base Stat:</span>
            <span class="font-bold text-white">${p.total}</span>
          </div>
        </div>

      </div>
    `;
  }).join('');

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-16 text-center text-slate-500">
        <i class="fa-solid fa-ghost text-4xl mb-3 text-slate-600"></i>
        <p class="text-sm">Nenhum Pokémon encontrado com os filtros selecionados.</p>
      </div>
    `;
  }
}

// Navegação entre Abas
function switchView(viewName) {
  ['gallery', 'clusters', 'battle', 'eda'].forEach(v => {
    const el = document.getElementById(`view-${v}`);
    if (el) el.classList.toggle('hidden', v !== viewName);
    const tabBtn = document.getElementById(`tab-${v}`);
    if (tabBtn) {
      if (v === viewName) {
        tabBtn.classList.add('active');
        tabBtn.classList.remove('text-slate-400');
      } else {
        tabBtn.classList.remove('active');
        tabBtn.classList.add('text-slate-400');
      }
    }
  });

  if (viewName === 'clusters') drawLabRadar();
  if (viewName === 'battle') updateBattle();
  if (viewName === 'eda') initInteractiveEdaCharts();
}

// Modal de Zoom de Imagens do EDA
function openImageModal(src, title) {
  const modal = document.getElementById('image-modal');
  document.getElementById('image-modal-src').src = src;
  document.getElementById('image-modal-title').innerText = title;
  modal.classList.remove('hidden');
}

function closeImageModal() {
  document.getElementById('image-modal').classList.add('hidden');
}

// Modal do Pokémon & Áudio Cry da PokéAPI
function openModal(id) {
  const p = POKEMON_DATA.find(x => x.id === id);
  if (!p) return;
  currentPokemonForCry = p;

  const artworkUrl = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${p.id}.png`;
  document.getElementById('modal-img').src = artworkUrl;
  document.getElementById('modal-dex').innerText = `#${String(p.id).padStart(3, '0')} - Gen ${p.gen}`;
  document.getElementById('modal-name').innerText = p.name;
  document.getElementById('modal-total').innerText = `Total: ${p.total}`;

  const cColor = CLUSTER_COLORS[p.cluster];
  document.getElementById('modal-cluster').innerHTML = `
    <span class="px-2.5 py-1 rounded-full text-xs font-bold" style="background-color: ${cColor}20; color: ${cColor}; border: 1px solid ${cColor}40">
      ${p.cluster_name} (Cluster ${p.cluster})
    </span>
  `;

  document.getElementById('modal-types').innerHTML = `
    <span class="px-2.5 py-0.5 rounded text-xs font-bold type-${p.type1}">${p.type1}</span>
    ${p.type2 ? `<span class="px-2.5 py-0.5 rounded text-xs font-bold type-${p.type2}">${p.type2}</span>` : ''}
  `;

  // Barras
  const stats = [
    { key: 'hp', val: p.hp },
    { key: 'atk', val: p.atk },
    { key: 'def', val: p.def },
    { key: 'spa', val: p.spa },
    { key: 'spd', val: p.spd },
    { key: 'spe', val: p.spe }
  ];

  stats.forEach(s => {
    document.getElementById(`m-${s.key}`).innerText = s.val;
    const pct = Math.min(100, (s.val / 200) * 100);
    setTimeout(() => {
      document.getElementById(`mbar-${s.key}`).style.width = `${pct}%`;
    }, 50);
  });

  document.getElementById('pokemon-modal').classList.remove('hidden');

  // Tocar o Cry oficial automaticamente ao abrir
  playCurrentCry();
}

function closeModal() {
  document.getElementById('pokemon-modal').classList.add('hidden');
}

function playCurrentCry() {
  if (!currentPokemonForCry) return;
  const audio = document.getElementById('cry-audio');
  // URL oficial dos cries de áudio da PokéAPI (formato OGG)
  audio.src = `https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/latest/${currentPokemonForCry.id}.ogg`;
  audio.volume = 0.5;
  audio.play().catch(e => console.log('Audio cry playback blocked or unavailable:', e));
}

// Filtro rápido clicando nos cards do Laboratório
function filterByClusterLab(clusterId) {
  switchView('gallery');
  document.getElementById('filter-cluster').value = clusterId.toString();
  currentCluster = clusterId.toString();
  renderGrid();
}

// Radar Chart do Laboratório em Canvas
function toggleRadarCluster(cId) {
  const idx = activeLabClusters.indexOf(cId);
  const btn = document.getElementById(`rad-btn-${cId}`);
  if (idx > -1) {
    if (activeLabClusters.length > 1) {
      activeLabClusters.splice(idx, 1);
      btn.classList.add('opacity-40');
    }
  } else {
    activeLabClusters.push(cId);
    btn.classList.remove('opacity-40');
  }
  drawLabRadar();
}

function drawLabRadar() {
  const canvas = document.getElementById('labRadarCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  const cx = w / 2;
  const cy = h / 2;
  const r = Math.min(cx, cy) - 30;
  const labels = ['HP', 'Ataque', 'Defesa', 'Sp. Atk', 'Sp. Def', 'Velocidade'];
  const total = labels.length;

  // Teia
  ctx.strokeStyle = "rgba(71, 85, 105, 0.4)";
  ctx.lineWidth = 1;
  for (let lvl = 1; lvl <= 4; lvl++) {
    ctx.beginPath();
    const curR = (r / 4) * lvl;
    for (let i = 0; i < total; i++) {
      const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
      const x = cx + curR * Math.cos(angle);
      const y = cy + curR * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  }

  // Eixos e Nomes
  ctx.fillStyle = "#94a3b8";
  ctx.font = "11px Inter, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  for (let i = 0; i < total; i++) {
    const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + r * Math.cos(angle), cy + r * Math.sin(angle));
    ctx.stroke();

    const lx = cx + (r + 18) * Math.cos(angle);
    const ly = cy + (r + 18) * Math.sin(angle);
    ctx.fillText(labels[i], lx, ly);
  }

  // Polígonos dos Clusters Ativos
  activeLabClusters.forEach(cId => {
    const stat = CLUSTER_STATS_MEAN[cId];
    const vals = [stat.hp, stat.atk, stat.def, stat.spa, stat.spd, stat.spe];
    const color = CLUSTER_COLORS[cId];
    const maxVal = 135;

    ctx.beginPath();
    for (let i = 0; i < total; i++) {
      const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
      const dist = Math.min(1, vals[i] / maxVal) * r;
      const x = cx + dist * Math.cos(angle);
      const y = cy + dist * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.fillStyle = color + "33"; // ~20% opacidade
    ctx.fill();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.stroke();
  });
}

// Batalha & Comparador Lado a Lado
function setupBattleOptions() {
  const sel1 = document.getElementById('battle-pkm-1');
  const sel2 = document.getElementById('battle-pkm-2');

  const popular = [6, 9, 3, 25, 94, 143, 150, 448, 445, 658, 384]; // Charizard, Blastoise, Venusaur, Pikachu, Gengar, Snorlax, Mewtwo, Lucario, Garchomp, Greninja, Rayquaza
  
  POKEMON_DATA.forEach(p => {
    const opt1 = new Option(`#${p.id} - ${p.name}`, p.id);
    const opt2 = new Option(`#${p.id} - ${p.name}`, p.id);
    sel1.add(opt1);
    sel2.add(opt2);
  });

  sel1.value = 6;  // Charizard
  sel2.value = 94; // Gengar
}

function updateBattle() {
  const id1 = parseInt(document.getElementById('battle-pkm-1').value);
  const id2 = parseInt(document.getElementById('battle-pkm-2').value);

  const p1 = POKEMON_DATA.find(x => x.id === id1);
  const p2 = POKEMON_DATA.find(x => x.id === id2);

  if (!p1 || !p2) return;

  // Fighter 1
  document.getElementById('battle-img-1').src = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/${p1.id}.gif`;
  document.getElementById('battle-name-1').innerText = p1.name;
  document.getElementById('battle-cluster-1').innerText = p1.cluster_name;
  document.getElementById('battle-cluster-1').style.color = CLUSTER_COLORS[p1.cluster];

  // Fighter 2
  document.getElementById('battle-img-2').src = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/${p2.id}.gif`;
  document.getElementById('battle-name-2').innerText = p2.name;
  document.getElementById('battle-cluster-2').innerText = p2.cluster_name;
  document.getElementById('battle-cluster-2').style.color = CLUSTER_COLORS[p2.cluster];

  drawBattleRadar(p1, p2);
}

function drawBattleRadar(p1, p2) {
  const canvas = document.getElementById('battleRadarCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  const cx = w / 2;
  const cy = h / 2;
  const r = Math.min(cx, cy) - 30;
  const labels = ['HP', 'Ataque', 'Defesa', 'Sp. Atk', 'Sp. Def', 'Velocidade'];
  const total = labels.length;

  // Grade
  ctx.strokeStyle = "rgba(71, 85, 105, 0.4)";
  ctx.lineWidth = 1;
  for (let lvl = 1; lvl <= 4; lvl++) {
    ctx.beginPath();
    const curR = (r / 4) * lvl;
    for (let i = 0; i < total; i++) {
      const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
      const x = cx + curR * Math.cos(angle);
      const y = cy + curR * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  }

  // Eixos
  ctx.fillStyle = "#94a3b8";
  ctx.font = "11px Inter, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  for (let i = 0; i < total; i++) {
    const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + r * Math.cos(angle), cy + r * Math.sin(angle));
    ctx.stroke();

    const lx = cx + (r + 18) * Math.cos(angle);
    const ly = cy + (r + 18) * Math.sin(angle);
    ctx.fillText(labels[i], lx, ly);
  }

  // Draw P1 (Vermelho/Rosa)
  drawPkmPolygon(ctx, cx, cy, r, [p1.hp, p1.atk, p1.def, p1.spa, p1.spd, p1.spe], '#f43f5e', 200);

  // Draw P2 (Azul/Índigo)
  drawPkmPolygon(ctx, cx, cy, r, [p2.hp, p2.atk, p2.def, p2.spa, p2.spd, p2.spe], '#6366f1', 200);
}

function drawPkmPolygon(ctx, cx, cy, r, vals, color, maxVal) {
  const total = vals.length;
  ctx.beginPath();
  for (let i = 0; i < total; i++) {
    const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
    const dist = Math.min(1, vals[i] / maxVal) * r;
    const x = cx + dist * Math.cos(angle);
    const y = cy + dist * Math.sin(angle);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.fillStyle = color + "40";
  ctx.fill();
  ctx.strokeStyle = color;
  ctx.lineWidth = 2.5;
  ctx.stroke();
}

// =========================================================================
// MÓDULO EDA INTERATIVO (CHART.JS + POKÉAPI INTEGRADOS)
// =========================================================================

let chartPcaInstance = null;
let chartScatterInstance = null;
let chartHistInstance = null;
let chartTypesInstance = null;
let chartElbowInstance = null;
let edaInitialized = false;

function setEdaMode(mode) {
  const isInter = mode === 'interactive';
  document.getElementById('eda-interactive-container').classList.toggle('hidden', !isInter);
  document.getElementById('eda-static-container').classList.toggle('hidden', isInter);

  const btnInter = document.getElementById('eda-btn-interactive');
  const btnStat = document.getElementById('eda-btn-static');

  if (isInter) {
    btnInter.className = "px-3 py-1.5 rounded-lg font-bold bg-rose-500 text-white shadow-md transition-all flex items-center gap-1.5";
    btnStat.className = "px-3 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white transition-all flex items-center gap-1.5";
    initInteractiveEdaCharts();
  } else {
    btnStat.className = "px-3 py-1.5 rounded-lg font-bold bg-rose-500 text-white shadow-md transition-all flex items-center gap-1.5";
    btnInter.className = "px-3 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white transition-all flex items-center gap-1.5";
  }
}

function initInteractiveEdaCharts() {
  if (typeof Chart === 'undefined') {
    setTimeout(initInteractiveEdaCharts, 150);
    return;
  }
  if (edaInitialized) return;
  edaInitialized = true;

  renderPcaScatterChart();
  updateScatterChart();
  updateHistChart();
  renderTypesBarChart();
  renderElbowChart();
  renderCorrelationHeatmapTable();
}

// 1. Gráfico PCA 2D Interativo
function renderPcaScatterChart() {
  const ctx = document.getElementById('chart-pca-canvas');
  if (!ctx) return;

  const clusterLabels = ['C0: Básicos', 'C1: Tanques', 'C2: Sweepers', 'C3: Titãs'];
  const datasets = [0, 1, 2, 3].map(cId => {
    const pkms = POKEMON_DATA.filter(p => p.cluster === cId);
    return {
      label: clusterLabels[cId],
      data: pkms.map(p => ({ x: p.pca1, y: p.pca2, pkm: p })),
      backgroundColor: CLUSTER_COLORS[cId] + 'cc',
      borderColor: CLUSTER_COLORS[cId],
      borderWidth: 1,
      pointRadius: cId === 3 ? 5.5 : 4,
      pointHoverRadius: 8
    };
  });

  chartPcaInstance = new Chart(ctx, {
    type: 'scatter',
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#cbd5e1', font: { family: 'Inter', size: 11 } } },
        tooltip: {
          backgroundColor: '#0f172a',
          titleColor: '#f43f5e',
          bodyColor: '#e2e8f0',
          borderColor: '#334155',
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: (item) => {
              const p = item.raw.pkm;
              return [
                ` #${p.id} ${p.name} (${p.type1}${p.type2 ? '/' + p.type2 : ''})`,
                ` ${p.cluster_name} | Base Total: ${p.total}`,
                ` ⚡ Clique no ponto para tocar o Cry!`
              ];
            }
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Componente Principal 1 (PC1 - Poder Geral)', color: '#94a3b8' },
          grid: { color: 'rgba(51, 65, 85, 0.3)' },
          ticks: { color: '#94a3b8' }
        },
        y: {
          title: { display: true, text: 'Componente Principal 2 (PC2 - Atk vs Def)', color: '#94a3b8' },
          grid: { color: 'rgba(51, 65, 85, 0.3)' },
          ticks: { color: '#94a3b8' }
        }
      },
      onClick: (e, elements) => {
        if (elements.length > 0) {
          const el = elements[0];
          const p = datasets[el.datasetIndex].data[el.index].pkm;
          openModal(p.id);
        }
      }
    }
  });
}

// 2. Gráfico de Dispersão Customizável
function updateScatterChart() {
  const ctx = document.getElementById('chart-scatter-canvas');
  if (!ctx) return;

  const xAttr = document.getElementById('scatter-x').value;
  const yAttr = document.getElementById('scatter-y').value;

  const attrLabels = {
    hp: 'HP', atk: 'Ataque', def: 'Defesa', spa: 'Sp. Atk', spd: 'Sp. Def', spe: 'Velocidade', total: 'Base Total'
  };

  const normalPkms = POKEMON_DATA.filter(p => !p.legendary);
  const legendPkms = POKEMON_DATA.filter(p => p.legendary);

  const datasets = [
    {
      label: 'Pokémons Comuns',
      data: normalPkms.map(p => ({ x: p[xAttr], y: p[yAttr], pkm: p })),
      backgroundColor: 'rgba(59, 130, 246, 0.65)',
      pointRadius: 4,
      pointHoverRadius: 8
    },
    {
      label: 'Lendários / Míticos',
      data: legendPkms.map(p => ({ x: p[xAttr], y: p[yAttr], pkm: p })),
      backgroundColor: 'rgba(244, 63, 94, 0.85)',
      borderColor: '#f59e0b',
      borderWidth: 1.5,
      pointRadius: 6.5,
      pointHoverRadius: 10
    }
  ];

  if (chartScatterInstance) {
    chartScatterInstance.data.datasets = datasets;
    chartScatterInstance.options.scales.x.title.text = attrLabels[xAttr];
    chartScatterInstance.options.scales.y.title.text = attrLabels[yAttr];
    chartScatterInstance.update();
  } else {
    chartScatterInstance = new Chart(ctx, {
      type: 'scatter',
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#cbd5e1' } },
          tooltip: {
            backgroundColor: '#0f172a',
            borderColor: '#334155',
            borderWidth: 1,
            callbacks: {
              label: (item) => {
                const p = item.raw.pkm;
                return ` #${p.id} ${p.name} | ${attrLabels[xAttr]}: ${p[xAttr]}, ${attrLabels[yAttr]}: ${p[yAttr]}`;
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: attrLabels[xAttr], color: '#94a3b8' },
            grid: { color: 'rgba(51, 65, 85, 0.3)' },
            ticks: { color: '#94a3b8' }
          },
          y: {
            title: { display: true, text: attrLabels[yAttr], color: '#94a3b8' },
            grid: { color: 'rgba(51, 65, 85, 0.3)' },
            ticks: { color: '#94a3b8' }
          }
        },
        onClick: (e, elements) => {
          if (elements.length > 0) {
            const el = elements[0];
            const p = datasets[el.datasetIndex].data[el.index].pkm;
            openModal(p.id);
          }
        }
      }
    });
  }
}

// 3. Gráfico Histograma Interativo
function updateHistChart() {
  const ctx = document.getElementById('chart-hist-canvas');
  if (!ctx) return;

  const stat = document.getElementById('hist-stat').value;
  const vals = POKEMON_DATA.map(p => p[stat]);
  const min = Math.min(...vals);
  const max = Math.max(...vals);

  const numBins = 12;
  const step = (max - min) / numBins;
  const bins = new Array(numBins).fill(0);
  const labels = [];

  for (let i = 0; i < numBins; i++) {
    const low = Math.round(min + i * step);
    const high = Math.round(min + (i + 1) * step);
    labels.push(`${low}-${high}`);
  }

  vals.forEach(v => {
    let bIdx = Math.floor((v - min) / step);
    if (bIdx >= numBins) bIdx = numBins - 1;
    bins[bIdx]++;
  });

  const mean = (vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(1);
  document.getElementById('hist-desc').innerHTML = `
    Média Global de <strong>${stat.toUpperCase()}</strong>: <span class="text-rose-400 font-bold">${mean}</span> | Mínimo: ${min} | Máximo: ${max}.
  `;

  if (chartHistInstance) {
    chartHistInstance.data.labels = labels;
    chartHistInstance.data.datasets[0].data = bins;
    chartHistInstance.update();
  } else {
    chartHistInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Frequência de Pokémons',
          data: bins,
          backgroundColor: 'rgba(225, 29, 72, 0.7)',
          hoverBackgroundColor: '#f43f5e',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f172a',
            callbacks: {
              title: (items) => `Faixa de Valor: ${items[0].label}`,
              label: (item) => ` ${item.raw} espécies de Pokémons nesta faixa`
            }
          }
        },
        scales: {
          x: { grid: { color: 'rgba(51, 65, 85, 0.2)' }, ticks: { color: '#94a3b8', font: { size: 10 } } },
          y: { grid: { color: 'rgba(51, 65, 85, 0.2)' }, ticks: { color: '#94a3b8' } }
        }
      }
    });
  }
}

// 4. Gráfico de Tipos Primários com Cores Oficiais
function renderTypesBarChart() {
  const ctx = document.getElementById('chart-types-canvas');
  if (!ctx) return;

  const counts = {};
  ALL_TYPES.forEach(t => counts[t] = 0);
  POKEMON_DATA.forEach(p => { if (counts[p.type1] !== undefined) counts[p.type1]++; });

  const sortedTypes = Object.keys(counts).sort((a, b) => counts[b] - counts[a]);
  const sortedCounts = sortedTypes.map(t => counts[t]);

  const typeColorMap = {
    Normal: '#9fa19f', Fire: '#e62829', Water: '#2980ef', Electric: '#fac000', Grass: '#3fa129',
    Ice: '#3dcef3', Fighting: '#ff8000', Poison: '#9141cb', Ground: '#915121', Flying: '#81b9ef',
    Psychic: '#ef4179', Bug: '#91a119', Rock: '#afa981', Ghost: '#704170', Dragon: '#5060e1',
    Steel: '#60a1b8', Fairy: '#ef70ef', Dark: '#50413f'
  };

  chartTypesInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: sortedTypes,
      datasets: [{
        label: 'Quantidade',
        data: sortedCounts,
        backgroundColor: sortedTypes.map(t => typeColorMap[t] || '#64748b'),
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f172a',
          callbacks: {
            label: (item) => ` ${item.raw} Pokémons deste tipo (Clique para filtrar na Pokédex)`
          }
        }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#cbd5e1', font: { size: 10 } } },
        y: { grid: { color: 'rgba(51, 65, 85, 0.2)' }, ticks: { color: '#94a3b8' } }
      },
      onClick: (e, elements) => {
        if (elements.length > 0) {
          const type = sortedTypes[elements[0].index];
          switchView('gallery');
          setTypeFilter(type);
        }
      }
    }
  });
}

// 5. Gráfico de Cotovelo & Silhueta (Dois Eixos)
function renderElbowChart() {
  const ctx = document.getElementById('chart-elbow-canvas');
  if (!ctx) return;

  const kRange = [2, 3, 4, 5, 6, 7, 8];
  const inertias = [3790.2, 3210.5, 2750.8, 2410.2, 2180.5, 1980.2, 1830.4];
  const silhouettes = [0.285, 0.298, 0.3204, 0.292, 0.281, 0.274, 0.268];

  chartElbowInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: kRange.map(k => `k=${k}`),
      datasets: [
        {
          label: 'Inércia (WCSS)',
          data: inertias,
          borderColor: '#f43f5e',
          backgroundColor: '#f43f5e',
          yAxisID: 'yLeft',
          tension: 0.3,
          borderWidth: 2.5
        },
        {
          label: 'Silhouette Score',
          data: silhouettes,
          borderColor: '#3b82f6',
          backgroundColor: '#3b82f6',
          yAxisID: 'yRight',
          borderDash: [5, 5],
          tension: 0.3,
          borderWidth: 2.5
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#cbd5e1', font: { size: 11 } } }
      },
      scales: {
        yLeft: {
          type: 'linear',
          position: 'left',
          title: { display: true, text: 'Inércia', color: '#f43f5e' },
          grid: { color: 'rgba(51, 65, 85, 0.2)' },
          ticks: { color: '#f43f5e' }
        },
        yRight: {
          type: 'linear',
          position: 'right',
          title: { display: true, text: 'Silhouette', color: '#3b82f6' },
          grid: { drawOnChartArea: false },
          ticks: { color: '#3b82f6' }
        },
        x: { ticks: { color: '#94a3b8' } }
      }
    }
  });
}

// 6. Matriz de Correlação Heatmap Interativo
function renderCorrelationHeatmapTable() {
  const table = document.getElementById('corr-interactive-table');
  if (!table) return;

  const cols = ['HP', 'Ataque', 'Defesa', 'Sp.Atk', 'Sp.Def', 'Veloc.', 'Total'];
  const matrix = [
    [1.00, 0.42, 0.24, 0.37, 0.37, 0.18, 0.62],
    [0.42, 1.00, 0.44, 0.40, 0.26, 0.38, 0.73],
    [0.24, 0.44, 1.00, 0.24, 0.51, 0.02, 0.63],
    [0.37, 0.40, 0.24, 1.00, 0.51, 0.47, 0.74],
    [0.37, 0.26, 0.51, 0.51, 1.00, 0.26, 0.72],
    [0.18, 0.38, 0.02, 0.47, 0.26, 1.00, 0.58],
    [0.62, 0.73, 0.63, 0.74, 0.72, 0.58, 1.00]
  ];

  let html = '<thead><tr><th class="p-1 text-slate-500 font-mono text-[10px]"></th>';
  cols.forEach(c => html += `<th class="p-1 text-slate-400 font-mono text-[10px]">${c}</th>`);
  html += '</tr></thead><tbody>';

  matrix.forEach((row, i) => {
    html += `<tr><td class="p-1 text-slate-400 font-bold font-mono text-[10px] text-right pr-2">${cols[i]}</td>`;
    row.forEach((val, j) => {
      // Cores: Vermelho para forte positivo, Azul para neutro/baixo
      const alpha = Math.abs(val);
      const bg = val > 0.6 ? `rgba(244, 63, 94, ${alpha * 0.85})` : (val > 0.3 ? `rgba(245, 158, 11, ${alpha * 0.7})` : `rgba(59, 130, 246, ${alpha * 0.5})`);
      const textCol = alpha > 0.4 ? '#ffffff' : '#cbd5e1';
      html += `
        <td class="p-2 border border-slate-900 rounded font-mono font-bold cursor-pointer transition-transform hover:scale-110" 
            style="background-color: ${bg}; color: ${textCol};"
            onmouseover="hoverCorr('${cols[i]}', '${cols[j]}', ${val})"
            title="${cols[i]} vs ${cols[j]}: r = ${val.toFixed(2)}">
          ${val.toFixed(2)}
        </td>
      `;
    });
    html += '</tr>';
  });
  html += '</tbody>';
  table.innerHTML = html;
}

function hoverCorr(attr1, attr2, val) {
  const el = document.getElementById('corr-tooltip-text');
  let desc = `Relação neutra ou fraca.`;
  if (val >= 0.7) desc = `Forte correlação positiva! Pokémons com alto ${attr1} quase sempre têm alto ${attr2}.`;
  else if (val >= 0.4) desc = `Correlação moderada positiva entre ${attr1} e ${attr2}.`;
  else if (val <= 0.1) desc = `Praticamente independentes (ex: Defesa e Velocidade quase não se correlacionam).`;

  el.innerHTML = `<strong>${attr1} vs ${attr2} (r = ${val.toFixed(2)}):</strong> ${desc}`;
}

