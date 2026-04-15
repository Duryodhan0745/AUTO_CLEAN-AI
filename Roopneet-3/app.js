// ── STATE ───────────────────────────────────────────────────────────────────
const state = {
  datasetId: null,
  profile: null,
  filename: null,
  mode: 'auto',
  config: {},
  result: null,
};

// ── NAV HELPERS ─────────────────────────────────────────────────────────────
function showPage(id) {
  console.log(`🔄 showPage called with id: ${id}`);
  document.querySelectorAll('.page-section').forEach(s => {
    s.classList.add('hidden');
  });
  const el = document.getElementById(id);
  console.log(`Found element for ${id}:`, el ? 'YES' : 'NO');
  if (el) { 
    el.classList.remove('hidden'); 
    el.classList.add('fade-in'); 
    console.log(`✅ Page ${id} is now visible`);
  } else {
    console.error(`❌ Could not find element with id: ${id}`);
  }
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showAlert(containerId, msg, type = 'error') {
  const el = document.getElementById(containerId);
  if (!el) return;
  const icons = { error: '⚠', success: '✓', info: 'ℹ' };
  el.innerHTML = `<div class="alert alert-${type}"><span>${icons[type] || '⚠'}</span>${msg}</div>`;
  el.classList.remove('hidden');
}

function clearAlert(containerId) {
  const el = document.getElementById(containerId);
  if (el) { el.innerHTML = ''; el.classList.add('hidden'); }
}

// ── UPLOAD PAGE ─────────────────────────────────────────────────────────────
function initUpload() {
  const zone = document.getElementById('upload-zone');
  const input = document.getElementById('file-input');
  const uploadBtn = document.getElementById('upload-btn');

  // Zone click opens file picker
  zone.addEventListener('click', () => input.click());

  // Upload button also opens file picker
  uploadBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    input.click();
  });

  // Drag and drop
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });

  // File input change — this is the main trigger
  input.addEventListener('change', () => {
    if (input.files[0]) handleFile(input.files[0]);
  });
}

async function handleFile(file) {
  clearAlert('upload-alert');
  if (!file || file.size === 0) {
    showAlert('upload-alert', 'Please select a valid file.');
    return;
  }

  const btn = document.getElementById('upload-btn');
  const zone = document.getElementById('upload-zone');
  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div> Uploading…';
  zone.classList.add('loading');

  try {
    console.log('Step 1: Uploading file', file.name);
    const result = await api.upload(file);
    console.log('Step 2: Upload result:', result);
    
    if (!result || !result.dataset_id) {
      throw new Error('Upload did not return dataset_id');
    }
    
    state.datasetId = result.dataset_id;
    state.filename = result.filename;
    console.log('Step 3: Set datasetId:', state.datasetId);

    btn.innerHTML = '<div class="spinner"></div> Profiling dataset…';

    console.log('Step 4: Calling profile API for', state.datasetId);
    const profile = await api.profile(state.datasetId);
    console.log('Step 5: Profile result:', profile);
    
    if (!profile) {
      throw new Error('Profile returned empty');
    }
    
    state.profile = profile;
    console.log('Step 6: State profile set');

    console.log('Step 7: Building dashboard...');
    buildDashboard();
    
    console.log('Step 8: Showing page-dashboard');
    showPage('page-dashboard');

    // Reset upload button for next time
    btn.disabled = false;
    btn.innerHTML = '⬆ Upload File';
    zone.classList.remove('loading');
    console.log('Step 9: Upload complete!');
  } catch (e) {
    console.error('ERROR at some step:', e.message);
    console.error('Full error:', e);
    showAlert('upload-alert', 'Error: ' + (e.message || 'Unknown error'));
    btn.disabled = false;
    btn.innerHTML = '⬆ Upload File';
    zone.classList.remove('loading');
  }
}

// ── DASHBOARD ────────────────────────────────────────────────────────────────
function buildDashboard() {
  try {
    console.log('buildDashboard called');
    const p = state.profile;
    console.log('Profile object:', p);
    
    if (!p) {
      throw new Error('Profile is null/undefined');
    }
    if (!p.columns) {
      throw new Error('Profile has no columns property. Keys: ' + Object.keys(p).join(', '));
    }
    if (!p.shape) {
      throw new Error('Profile has no shape property');
    }

    console.log('Building stats...');
    // Stats
    document.getElementById('stat-rows').textContent = p.shape.rows.toLocaleString();
    document.getElementById('stat-cols').textContent = p.shape.columns;
    const totalMissing = p.columns.reduce((a, c) => a + (c.missing || 0), 0);
    document.getElementById('stat-missing').textContent = totalMissing.toLocaleString();
    const numCols = p.columns.filter(c => c.type === 'numeric').length;
    const catCols = p.columns.filter(c => c.type === 'categorical').length;
    document.getElementById('stat-types').textContent = `${numCols}N / ${catCols}C`;
    document.getElementById('dash-filename').textContent = state.filename;

    console.log('Building selectors...');
    buildColumnSelector(p.columns);
    console.log('Building preview table...');
    buildPreviewTable(p);
    console.log('Building profiles...');
    buildColumnProfiles(p.columns);
    console.log('Building missing config...');
    buildPerColMissing(p.columns);
    console.log('Building RFE targets...');
    buildRFETargets(p.columns);
    console.log('Dashboard built successfully!');
  } catch (e) {
    console.error('Error in buildDashboard:', e.message);
    console.error('Stack:', e.stack);
    showAlert('dash-alert', 'Error loading dashboard: ' + e.message);
    showPage('page-upload');
  }
}

function buildColumnSelector(cols) {
  const el = document.getElementById('col-remove-list');
  el.innerHTML = '';
  cols.forEach(col => {
    const item = document.createElement('div');
    item.className = 'col-item';
    item.dataset.col = col.name;
    item.innerHTML = `
      <div>
        <div class="col-name">${escapeHtml(col.name)}</div>
      </div>
      <span class="type-badge ${col.type === 'numeric' ? 'type-numeric' : 'type-categorical'}">${col.type}</span>
    `;
    item.addEventListener('click', () => {
      item.classList.toggle('selected');
      updateRemoveCount();
    });
    el.appendChild(item);
  });
}

function updateRemoveCount() {
  const selected = document.querySelectorAll('#col-remove-list .col-item.selected').length;
  const el = document.getElementById('remove-count');
  if (el) el.textContent = selected > 0 ? `${selected} selected` : '';
}

function buildPreviewTable(p) {
  const wrap = document.getElementById('preview-table');
  if (!p.preview || !p.preview.length) {
    wrap.innerHTML = '<p class="text-muted text-sm">No preview available.</p>';
    return;
  }
  const cols = Object.keys(p.preview[0]);
  let html = '<div class="table-wrap"><table><thead><tr>';
  cols.forEach(c => { html += `<th>${escapeHtml(c)}</th>`; });
  html += '</tr></thead><tbody>';
  p.preview.slice(0, 8).forEach(row => {
    html += '<tr>';
    cols.forEach(c => {
      const val = row[c];
      html += `<td>${val === '' || val == null ? '<span class="null-val">—</span>' : escapeHtml(String(val))}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table></div>';
  wrap.innerHTML = html;
}

function buildColumnProfiles(cols) {
  const el = document.getElementById('col-profiles');
  el.innerHTML = '';
  cols.forEach(col => {
    const div = document.createElement('div');
    div.className = 'col-profile-item';
    let statsHtml = '';
    if (col.type === 'numeric') {
      statsHtml = `
        <div class="col-stats">
          <div class="col-stat">mean <span>${col.mean ?? '—'}</span></div>
          <div class="col-stat">std <span>${col.std ?? '—'}</span></div>
          <div class="col-stat">min <span>${col.min ?? '—'}</span></div>
          <div class="col-stat">max <span>${col.max ?? '—'}</span></div>
          ${col.outliers > 0 ? `<div class="col-stat outlier-stat">outliers <span>${col.outliers}</span></div>` : ''}
        </div>
        ${col.missing > 0 ? `
          <div class="mini-bar-label">Missing: ${col.missing_pct}%</div>
          <div class="mini-bar-wrap"><div class="mini-bar missing" style="width:${Math.max(col.missing_pct, 2)}%"></div></div>
        ` : ''}
      `;
    } else {
      const top = col.top_values ? Object.entries(col.top_values).slice(0, 3).map(([k,v]) => `${escapeHtml(k)}(${v})`).join(', ') : '';
      statsHtml = `
        <div class="col-stats">
          <div class="col-stat">unique <span>${col.unique}</span></div>
          ${top ? `<div class="col-stat">top <span title="${top}">${top.length > 40 ? top.slice(0,40)+'…' : top}</span></div>` : ''}
        </div>
      `;
    }
    div.innerHTML = `
      <div class="col-profile-header">
        <span class="col-profile-name">${escapeHtml(col.name)}</span>
        <div class="col-profile-meta">
          ${col.missing > 0 ? `<span class="null-badge">${col.missing_pct}% null</span>` : ''}
          <span class="type-badge ${col.type === 'numeric' ? 'type-numeric' : 'type-categorical'}">${col.type}</span>
        </div>
      </div>
      ${statsHtml}
    `;
    el.appendChild(div);
  });
}

function buildPerColMissing(cols) {
  const el = document.getElementById('per-col-missing');
  el.innerHTML = '';
  const strategies = ['mean', 'median', 'mode', 'drop_rows', 'drop_column'];
  cols.forEach(col => {
    const row = document.createElement('div');
    row.className = 'per-col-row';
    const availableStrategies = col.type === 'numeric' ? strategies : strategies.filter(s => !['mean','median'].includes(s));
    row.innerHTML = `
      <span class="col-tag" title="${escapeHtml(col.name)}">${escapeHtml(col.name)}</span>
      <div class="select-wrap">
        <select class="form-select per-col-strat" data-col="${escapeHtml(col.name)}">
          ${availableStrategies.map(s => `<option value="${s}">${s}</option>`).join('')}
        </select>
      </div>
    `;
    el.appendChild(row);
  });
}

function buildRFETargets(cols) {
  const sel = document.getElementById('rfe-target');
  if (!sel) return;
  sel.innerHTML = '<option value="">— None (skip RFE) —</option>';
  cols.filter(c => c.type === 'numeric').forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.name;
    opt.textContent = c.name;
    sel.appendChild(opt);
  });
}

// ── MODE SELECTION ───────────────────────────────────────────────────────────
function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll('.mode-card').forEach(c => c.classList.remove('active'));
  document.querySelector(`.mode-card[data-mode="${mode}"]`)?.classList.add('active');
  const customPanel = document.getElementById('custom-config-panel');
  if (customPanel) customPanel.classList.toggle('hidden', mode !== 'custom');
}

// ── BUILD CONFIG ─────────────────────────────────────────────────────────────
function buildConfig() {
  const cfg = {};

  const removed = [...document.querySelectorAll('#col-remove-list .col-item.selected')].map(el => el.dataset.col);
  cfg.remove_columns = removed;

  if (state.mode === 'auto') {
    cfg.missing_global = 'mean';
    cfg.missing = {};
    cfg.outliers = { strategy: 'cap' };
    cfg.encoding = { strategy: 'onehot' };
    cfg.scaling = { strategy: 'standard' };
    cfg.vif = { enabled: true, threshold: 10 };
    cfg.rfe = { enabled: false };
    cfg.pca = { enabled: false };
  } else {
    cfg.missing_global = document.getElementById('missing-global')?.value || 'mean';
    cfg.missing = {};
    document.querySelectorAll('.per-col-strat').forEach(sel => {
      cfg.missing[sel.dataset.col] = sel.value;
    });
    cfg.outliers = { strategy: document.getElementById('outlier-strategy')?.value || 'cap' };
    cfg.encoding = { strategy: document.getElementById('encoding-strategy')?.value || 'onehot' };
    cfg.scaling = { strategy: document.getElementById('scaling-strategy')?.value || 'standard' };

    const vifEnabled = document.getElementById('vif-toggle')?.checked ?? true;
    cfg.vif = {
      enabled: vifEnabled,
      threshold: parseFloat(document.getElementById('vif-threshold')?.value || '10')
    };

    const rfeEnabled = document.getElementById('rfe-toggle')?.checked ?? false;
    const rfeTarget = document.getElementById('rfe-target')?.value || '';
    const rfeN = parseInt(document.getElementById('rfe-n')?.value || '0');
    cfg.rfe = {
      enabled: rfeEnabled && !!rfeTarget,
      target: rfeTarget,
      n_features: rfeN || null
    };

    const pcaEnabled = document.getElementById('pca-toggle')?.checked ?? false;
    cfg.pca = { enabled: pcaEnabled, variance: 0.95 };
  }

  return cfg;
}

// ── PROCESSING ───────────────────────────────────────────────────────────────
const STEPS = [
  { key: 'column_removal', name: 'Column Removal', icon: '🗑' },
  { key: 'missing_values', name: 'Missing Values', icon: '🔧' },
  { key: 'outliers', name: 'Outlier Handling', icon: '📊' },
  { key: 'encoding', name: 'Encoding', icon: '🔢' },
  { key: 'scaling', name: 'Scaling', icon: '⚖️' },
  { key: 'vif', name: 'VIF Filter', icon: '🔗' },
  { key: 'rfe', name: 'Feature Selection', icon: '🎯' },
  { key: 'pca', name: 'PCA', icon: '🌀' },
];

function buildStepsList(containerId) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = '';
  STEPS.forEach((s, i) => {
    const div = document.createElement('div');
    div.className = 'step-item';
    div.id = `step-${s.key}`;
    div.innerHTML = `
      <div class="step-num">${i + 1}</div>
      <div class="step-info">
        <div class="step-name">${s.icon} ${s.name}</div>
        <div class="step-detail" id="step-detail-${s.key}">Pending…</div>
      </div>
      <span class="step-status" id="step-status-${s.key}">○</span>
    `;
    el.appendChild(div);
  });
}

async function runProcessing() {
  const config = buildConfig();
  state.config = config;
  console.log('Running pipeline with config:', config);
  showPage('page-processing');
  buildStepsList('processing-steps');

  const bar = document.getElementById('process-bar');
  if (bar) bar.style.width = '5%';

  try {
    console.log('Calling api.process...');
    const result = await api.process(state.datasetId, config);
    console.log('Process result:', result);
    state.result = result;

    // Animate steps with delay
    result.logs.forEach((log, i) => {
      setTimeout(() => {
        const stepKey = log.step;
        const stepEl = document.getElementById(`step-${stepKey}`);
        const detailEl = document.getElementById(`step-detail-${stepKey}`);
        const statusEl = document.getElementById(`step-status-${stepKey}`);

        if (stepEl) {
          const isSkipped = log.action.toLowerCase().includes('skipped');
          stepEl.className = isSkipped ? 'step-item skipped' : 'step-item done';
          if (detailEl) {
            const txt = log.action.length > 90 ? log.action.slice(0, 90) + '…' : log.action;
            detailEl.textContent = txt;
          }
          if (statusEl) statusEl.textContent = isSkipped ? '–' : '✓';
        }

        const pct = Math.round(((i + 1) / result.logs.length) * 100);
        if (bar) bar.style.width = `${pct}%`;

        if (i === result.logs.length - 1) {
          setTimeout(() => {
            buildResults();
            showPage('page-results');
          }, 700);
        }
      }, i * 250);
    });
  } catch (e) {
    console.error('Processing error:', e);
    showPage('page-dashboard');
    showAlert('dash-alert', `Processing failed: ${e.message}`);
  }
}

// ── RESULTS ──────────────────────────────────────────────────────────────────
function buildResults() {
  const r = state.result;

  document.getElementById('res-rows-before').textContent = r.rows_before.toLocaleString();
  document.getElementById('res-rows-after').textContent = r.rows_after.toLocaleString();
  document.getElementById('res-cols-before').textContent = r.cols_before;
  document.getElementById('res-cols-after').textContent = r.cols_after;

  const dlCsvBtn = document.getElementById('dl-csv-btn');
  const dlPipelineBtn = document.getElementById('dl-pipeline-btn');
  if (dlCsvBtn) dlCsvBtn.href = api.downloadUrl(state.datasetId);
  if (dlPipelineBtn) dlPipelineBtn.href = api.pipelineUrl(state.datasetId);

  // ydata-profiling report
  const reportCard = document.getElementById('report-card');
  if (reportCard) {
    if (r.report_available) {
      const reportIframe = document.getElementById('report-iframe');
      const dlReportBtn = document.getElementById('dl-report-btn');
      if (reportIframe) reportIframe.src = api.reportUrl(state.datasetId);
      if (dlReportBtn) dlReportBtn.href = api.downloadReportUrl(state.datasetId);
      reportCard.style.display = '';
    } else {
      reportCard.style.display = 'none';
    }
  }

  // Build logs
  const logsEl = document.getElementById('result-logs');
  if (logsEl) {
    logsEl.innerHTML = '';
    r.logs.forEach(log => {
      const div = document.createElement('div');
      const isSkipped = log.action.toLowerCase().includes('skipped') || log.action.toLowerCase().startsWith('no ');
      div.className = `log-entry ${isSkipped ? 'skipped' : 'success'}`;
      div.innerHTML = `
        <div class="log-step">${log.step.replace(/_/g, ' ')}</div>
        <div class="log-action">${escapeHtml(log.action)}</div>
        ${log.impact && log.impact !== 'None' ? `<div class="log-impact">${escapeHtml(log.impact)}</div>` : ''}
      `;
      logsEl.appendChild(div);
    });
  }
}

// ── UTILS ────────────────────────────────────────────────────────────────────
function escapeHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(String(str)));
  return div.innerHTML;
}

// ── INIT ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initUpload();
  showPage('page-upload');
  setMode('auto');

  // Run pipeline button
  document.getElementById('run-btn')?.addEventListener('click', runProcessing);

  // Back button
  document.getElementById('back-btn')?.addEventListener('click', () => showPage('page-upload'));

  // Restart button
  document.getElementById('restart-btn')?.addEventListener('click', () => {
    state.datasetId = null;
    state.profile = null;
    state.result = null;
    document.getElementById('file-input').value = '';
    clearAlert('upload-alert');
    showPage('page-upload');
  });

  // Mode cards
  document.querySelectorAll('.mode-card').forEach(card => {
    card.addEventListener('click', () => setMode(card.dataset.mode));
  });

  // VIF toggle
  document.getElementById('vif-toggle')?.addEventListener('change', function () {
    document.getElementById('vif-options')?.classList.toggle('hidden', !this.checked);
  });

  // RFE toggle
  document.getElementById('rfe-toggle')?.addEventListener('change', function () {
    document.getElementById('rfe-options')?.classList.toggle('hidden', !this.checked);
  });

  // Select all / clear columns
  document.getElementById('select-all-btn')?.addEventListener('click', () => {
    document.querySelectorAll('#col-remove-list .col-item').forEach(el => el.classList.add('selected'));
    updateRemoveCount();
  });

  document.getElementById('clear-sel-btn')?.addEventListener('click', () => {
    document.querySelectorAll('#col-remove-list .col-item').forEach(el => el.classList.remove('selected'));
    updateRemoveCount();
  });
});
