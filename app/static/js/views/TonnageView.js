/**
 * TonnageView.js - Statutory Gross Tonnage (GT) & Net Tonnage (NT) Calculation View
 * Strictly compliant with:
 * - Inland Shipping Ordinance, 1976 (Ordinance No. 72 of 1976)
 * - The Inland Ships (Tonnage Measurement) Rules, 2001 (Book 12 / S.R.O. No. 308-Law/2001)
 *   * Rule 10: Definitions of Upper Deck, Moulded Depth, Breadth, Enclosed & Excluded Spaces
 *   * Rule 11: Gross Tonnage Formula: GT = K1 * V, where K1 = 0.2 + 0.02 * log10(V)
 *   * Rule 12: Net Tonnage Formula: NT = K2 * Vc * (4d/3D)^2 + K3 * (N1 + N2/10)
 *   * Rule 14: Boundary measurement & appendages inclusion
 *   * Appendix 1: Bangladesh Inland Ship Tonnage Measurement Certificate
 *   * Appendix 3: Table of Coefficients K1 and K2
 */

// Initialize default tonnage configuration if not present
function getTonnageState() {
  if (!window.appState) window.appState = {};
  if (!window.appState.tonnage_config) {
    const inputs = window.appState.dashboard_inputs || {};
    const cb = parseFloat(inputs.block_coeff) || 0.721;
    window.appState.tonnage_config = {
      underdeck_coeff: cb,
      v_underdeck_custom: null,
      cargo_percent: 68.0,
      cargo_volume_vc: null,
      passengers_cabin_n1: 0,
      passengers_other_n2: 0,
      superstructures: [
        { id: 'sup-1', name: 'Wheelhouse / Nav Bridge', length: 5.0, breadth: 4.5, height: 2.4, volume: 54.0, is_enclosed: true },
        { id: 'sup-2', name: 'Aft Deckhouse (Crew Accommodation)', length: 14.0, breadth: 9.0, height: 2.4, volume: 302.4, is_enclosed: true },
        { id: 'sup-3', name: 'Machinery / Engine Casing', length: 8.5, breadth: 4.0, height: 2.2, volume: 74.8, is_enclosed: true },
        { id: 'sup-4', name: 'Forecastle Erection', length: 7.5, breadth: 6.5, height: 1.8, volume: 74.5, is_enclosed: true }
      ],
      appendages: [
        { id: 'app-1', name: 'Rudder Blade & Skeg', volume: 14.5 },
        { id: 'app-2', name: 'Propeller Bossings & Stern Appendages', volume: 8.0 }
      ],
      excluded_spaces: [
        { id: 'ex-1', name: 'Open Poop Deck Walkway (Rule 10(5)(b))', volume: 18.0 }
      ]
    };
  }
  return window.appState.tonnage_config;
}

function calculateClientTonnage() {
  const inputs = (window.appState && window.appState.dashboard_inputs) || {};
  const tState = getTonnageState();

  const loa = parseFloat(inputs.loa) || 76.21;
  const lbp = parseFloat(inputs.lbp) || (loa * 0.95);
  const breadth = parseFloat(inputs.breadth) || 15.24;
  const depth = parseFloat(inputs.depth) || 4.87;
  const draft = parseFloat(inputs.draft) || 4.0;
  const cb = parseFloat(inputs.block_coeff) || 0.721;
  const cv = parseFloat(tState.underdeck_coeff) || cb;

  // 1. Underdeck Volume
  let v_underdeck = 0;
  if (tState.v_underdeck_custom && parseFloat(tState.v_underdeck_custom) > 0) {
    v_underdeck = parseFloat(tState.v_underdeck_custom);
  } else {
    v_underdeck = lbp * breadth * depth * cv;
  }
  v_underdeck = Math.round(v_underdeck * 100) / 100;

  // 2. Superstructures
  let v_superstructures = 0;
  (tState.superstructures || []).forEach(s => {
    let vol = parseFloat(s.volume);
    if (isNaN(vol) || vol <= 0) {
      vol = (parseFloat(s.length) || 0) * (parseFloat(s.breadth) || 0) * (parseFloat(s.height) || 0);
      s.volume = Math.round(vol * 100) / 100;
    }
    if (s.is_enclosed !== false) v_superstructures += (parseFloat(s.volume) || 0);
  });
  v_superstructures = Math.round(v_superstructures * 100) / 100;

  // 3. Appendages
  let v_appendages = 0;
  (tState.appendages || []).forEach(a => {
    v_appendages += (parseFloat(a.volume) || 0);
  });
  v_appendages = Math.round(v_appendages * 100) / 100;

  // 4. Excluded Spaces
  let v_excluded = 0;
  (tState.excluded_spaces || []).forEach(e => {
    v_excluded += (parseFloat(e.volume) || 0);
  });
  v_excluded = Math.round(v_excluded * 100) / 100;

  // Total Volume V
  let v_total = v_underdeck + v_superstructures + v_appendages - v_excluded;
  if (v_total <= 0) v_total = 1.0;
  v_total = Math.round(v_total * 100) / 100;

  // Rule 11: GT = K1 * V, K1 = 0.2 + 0.02 * log10(V)
  const logV = Math.log10(v_total);
  const k1 = Math.round((0.2 + 0.02 * logV) * 10000) / 10000;
  const gt = Math.round((k1 * v_total) * 100) / 100;

  // Rule 12: Net Tonnage (NT)
  const cargo_pct = parseFloat(tState.cargo_percent) || 68.0;
  let vc = tState.cargo_volume_vc ? parseFloat(tState.cargo_volume_vc) : (v_underdeck * (cargo_pct / 100.0));
  if (vc <= 0) vc = 1.0;
  vc = Math.round(vc * 100) / 100;

  const logVc = Math.log10(vc);
  const k2 = Math.round((0.2 + 0.02 * logVc) * 10000) / 10000;

  // (4d / 3D)^2 <= 1.0
  const raw_draft_factor = depth > 0 ? (4.0 * draft) / (3.0 * depth) : 1.0;
  const draft_factor_sq = Math.round((raw_draft_factor * raw_draft_factor) * 10000) / 10000;
  const draft_factor_applied = Math.min(1.0, draft_factor_sq);

  // Cargo term with 0.25 GT floor (Rule 12(1)(b))
  const raw_cargo_term = k2 * vc * draft_factor_applied;
  const cargo_min = 0.25 * gt;
  const cargo_floor_applied = raw_cargo_term < cargo_min;
  const effective_cargo_term = Math.round(Math.max(raw_cargo_term, cargo_min) * 100) / 100;

  // Passenger term (Rule 12(1))
  const n1 = parseInt(tState.passengers_cabin_n1) || 0;
  const n2 = parseInt(tState.passengers_other_n2) || 0;
  const pax_zeroed = (n1 + n2) < 13;
  const eff_n1 = pax_zeroed ? 0 : n1;
  const eff_n2 = pax_zeroed ? 0 : n2;

  const k3 = Math.round((1.25 * (gt + 10000.0) / 10000.0) * 10000) / 10000;
  const pax_term = Math.round((k3 * (eff_n1 + eff_n2 / 10.0)) * 100) / 100;

  const nt_pre = effective_cargo_term + pax_term;
  const nt_min = 0.30 * gt;
  const min_floor_applied = nt_pre < nt_min;
  const nt = Math.round(Math.max(nt_pre, nt_min) * 100) / 100;

  return {
    loa, lbp, breadth, depth, draft, cb, cv,
    v_underdeck, v_superstructures, v_appendages, v_excluded, v_total,
    superstructures: tState.superstructures,
    appendages: tState.appendages,
    excluded_spaces: tState.excluded_spaces,
    k1, logV: Math.round(logV * 10000) / 10000, gt,
    vc, logVc: Math.round(logVc * 10000) / 10000, k2,
    raw_draft_factor: Math.round(raw_draft_factor * 10000) / 10000,
    draft_factor_sq, draft_factor_applied,
    raw_cargo_term: Math.round(raw_cargo_term * 100) / 100,
    cargo_min: Math.round(cargo_min * 100) / 100,
    cargo_floor_applied, effective_cargo_term,
    n1, n2, eff_n1, eff_n2, pax_zeroed, k3, pax_term,
    nt_pre: Math.round(nt_pre * 100) / 100,
    nt_min: Math.round(nt_min * 100) / 100,
    min_floor_applied, nt
  };
}

function handleTonnageConfigChange(key, val) {
  const tState = getTonnageState();
  tState[key] = val;
  renderTonnage();
  if (typeof triggerAutosaveDebounced === 'function') triggerAutosaveDebounced();
}

function handleSuperstructureChange(index, field, val) {
  const tState = getTonnageState();
  if (tState.superstructures && tState.superstructures[index]) {
    const item = tState.superstructures[index];
    item[field] = (field === 'name' || field === 'is_enclosed') ? val : (parseFloat(val) || 0);
    if (field === 'length' || field === 'breadth' || field === 'height') {
      item.volume = Math.round((parseFloat(item.length) || 0) * (parseFloat(item.breadth) || 0) * (parseFloat(item.height) || 0) * 100) / 100;
    }
  }
  renderTonnage();
  if (typeof triggerAutosaveDebounced === 'function') triggerAutosaveDebounced();
}

function addSuperstructureRow() {
  const tState = getTonnageState();
  tState.superstructures.push({
    id: 'sup-' + Date.now(),
    name: 'New Deck Erection',
    length: 6.0,
    breadth: 4.0,
    height: 2.2,
    volume: 52.8,
    is_enclosed: true
  });
  renderTonnage();
  if (typeof triggerAutosaveDebounced === 'function') triggerAutosaveDebounced();
}

function removeSuperstructureRow(index) {
  const tState = getTonnageState();
  if (tState.superstructures && tState.superstructures.length > index) {
    tState.superstructures.splice(index, 1);
  }
  renderTonnage();
  if (typeof triggerAutosaveDebounced === 'function') triggerAutosaveDebounced();
}

function addAppendageRow() {
  const tState = getTonnageState();
  tState.appendages.push({
    id: 'app-' + Date.now(),
    name: 'Additional Appendage',
    volume: 5.0
  });
  renderTonnage();
  if (typeof triggerAutosaveDebounced === 'function') triggerAutosaveDebounced();
}

function removeAppendageRow(index) {
  const tState = getTonnageState();
  if (tState.appendages && tState.appendages.length > index) {
    tState.appendages.splice(index, 1);
  }
  renderTonnage();
  if (typeof triggerAutosaveDebounced === 'function') triggerAutosaveDebounced();
}

function printTonnageCertificate() {
  window.print();
}

function openStatutoryTonnageBook() {
  if (window.statutoryDrawer) {
    window.statutoryDrawer.open();
    // Select Book 12 (Inland Ships Tonnage Measurement Rules, 2001)
    setTimeout(() => {
      const bookSel = document.getElementById('statutory-book-select');
      if (bookSel) {
        bookSel.value = '12';
        bookSel.dispatchEvent(new Event('change'));
      }
    }, 200);
  }
}

function renderTonnage() {
  const container = document.getElementById('tab-content-tonnage-calc');
  if (!container) return;

  const data = calculateClientTonnage();
  const inputs = (window.appState && window.appState.dashboard_inputs) || {};
  const vName = inputs.vessel_name || 'M. V. YOUNUS MOLLA-1';

  container.innerHTML = `
    <!-- Top Action & Statutory Header Banner -->
    <div class="bg-white p-3 rounded-lg border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-amber-600 text-white rounded-lg flex items-center justify-center font-black text-sm shadow-xs">
          GT
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-base font-bold text-slate-800 tracking-tight">STATUTORY TONNAGE MEASUREMENT (ISO 2001)</h1>
            <span class="text-[10px] bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded border border-amber-300">Book 12: Rules 10, 11, 12</span>
            <span class="text-[10px] bg-blue-100 text-blue-800 font-bold px-2 py-0.5 rounded border border-blue-300">S.R.O. 308-Law/2001</span>
          </div>
          <p class="text-xs text-slate-500 mt-0.5">
            Gross Tonnage (GT) and Net Tonnage (NT) as enacted under the Inland Shipping Ordinance, 1976 &amp; Department of Shipping (DOS) Rules
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button 
          onclick="openStatutoryTonnageBook()" 
          class="px-2.5 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 rounded text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
          title="Open Book 12 (Tonnage Measurement Rules) in Statutory Drawer"
        >
          <svg class="w-3.5 h-3.5 text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
          <span>Statutory Text (Rule 11/12)</span>
        </button>
        <button 
          onclick="printTonnageCertificate()" 
          class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-bold flex items-center gap-1.5 shadow-xs transition-colors cursor-pointer"
          title="Print Official Bangladesh Inland Ship Tonnage Certificate (Appendix 1)"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
          <span>Print Certificate</span>
        </button>
      </div>
    </div>

    <!-- 4 Statutory Scorecard Metric Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      <!-- Card 1: Gross Tonnage (GT) -->
      <div class="bg-gradient-to-br from-amber-50 to-white p-3.5 rounded-lg border border-amber-200 shadow-2xs">
        <div class="flex items-center justify-between text-xs text-amber-800 font-bold uppercase tracking-wider">
          <span>GROSS TONNAGE (GT)</span>
          <span class="bg-amber-200/80 text-amber-900 text-[10px] px-1.5 py-0.2 rounded font-mono">Rule 11</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <div class="text-2xl font-black text-slate-900 font-mono">${data.gt.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          <span class="text-xs font-bold text-slate-500">GT</span>
        </div>
        <div class="mt-1 text-[11px] text-amber-900 font-medium font-mono">
          GT = K₁ × V = ${data.k1} × ${data.v_total.toFixed(1)}
        </div>
        <div class="mt-2 text-[10px] text-slate-500 pt-1.5 border-t border-amber-100 flex items-center justify-between">
          <span>K₁ Factor: <b>${data.k1}</b></span>
          <span>Log₁₀(V): <b>${data.logV}</b></span>
        </div>
      </div>

      <!-- Card 2: Net Tonnage (NT) -->
      <div class="bg-gradient-to-br from-blue-50 to-white p-3.5 rounded-lg border border-blue-200 shadow-2xs">
        <div class="flex items-center justify-between text-xs text-blue-800 font-bold uppercase tracking-wider">
          <span>NET TONNAGE (NT)</span>
          <span class="bg-blue-200/80 text-blue-900 text-[10px] px-1.5 py-0.2 rounded font-mono">Rule 12</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <div class="text-2xl font-black text-slate-900 font-mono">${data.nt.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          <span class="text-xs font-bold text-slate-500">NT</span>
        </div>
        <div class="mt-1 text-[11px] text-blue-900 font-medium font-mono">
          Cargo: ${data.effective_cargo_term.toFixed(1)} + Pax: ${data.pax_term.toFixed(1)}
        </div>
        <div class="mt-2 text-[10px] text-slate-500 pt-1.5 border-t border-blue-100 flex items-center justify-between">
          <span>Floor (≥0.30 GT): <b>${data.nt_min.toFixed(1)}</b></span>
          <span class="${data.min_floor_applied ? 'text-amber-700 font-bold' : 'text-emerald-700 font-bold'}">
            ${data.min_floor_applied ? 'Floor Enforced' : 'Above Floor'}
          </span>
        </div>
      </div>

      <!-- Card 3: Total Enclosed Volume (V) -->
      <div class="bg-gradient-to-br from-emerald-50 to-white p-3.5 rounded-lg border border-emerald-200 shadow-2xs">
        <div class="flex items-center justify-between text-xs text-emerald-800 font-bold uppercase tracking-wider">
          <span>TOTAL ENCLOSED VOLUME (V)</span>
          <span class="bg-emerald-200/80 text-emerald-900 text-[10px] px-1.5 py-0.2 rounded font-mono">Rule 14</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <div class="text-2xl font-black text-slate-900 font-mono">${data.v_total.toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}</div>
          <span class="text-xs font-bold text-slate-500">m³</span>
        </div>
        <div class="mt-1 text-[11px] text-emerald-900 font-medium font-mono">
          Hull: ${data.v_underdeck.toFixed(1)} + Erections: ${data.v_superstructures.toFixed(1)}
        </div>
        <div class="mt-2 text-[10px] text-slate-500 pt-1.5 border-t border-emerald-100 flex items-center justify-between">
          <span>Appendages: <b>${data.v_appendages.toFixed(1)} m³</b></span>
          <span>Excluded: <b>${data.v_excluded.toFixed(1)} m³</b></span>
        </div>
      </div>

      <!-- Card 4: Cargo Spaces Volume (Vc) -->
      <div class="bg-gradient-to-br from-purple-50 to-white p-3.5 rounded-lg border border-purple-200 shadow-2xs">
        <div class="flex items-center justify-between text-xs text-purple-800 font-bold uppercase tracking-wider">
          <span>CARGO SPACES VOLUME (Vc)</span>
          <span class="bg-purple-200/80 text-purple-900 text-[10px] px-1.5 py-0.2 rounded font-mono">Rule 12(1)</span>
        </div>
        <div class="mt-2 flex items-baseline gap-2">
          <div class="text-2xl font-black text-slate-900 font-mono">${data.vc.toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}</div>
          <span class="text-xs font-bold text-slate-500">m³</span>
        </div>
        <div class="mt-1 text-[11px] text-purple-900 font-medium font-mono">
          K₂ = ${data.k2} | Draught: ${data.draft_factor_applied}
        </div>
        <div class="mt-2 text-[10px] text-slate-500 pt-1.5 border-t border-purple-100 flex items-center justify-between">
          <span>Cargo Floor (≥0.25 GT): <b>${data.cargo_min.toFixed(1)}</b></span>
          <span class="${data.cargo_floor_applied ? 'text-amber-700 font-bold' : 'text-emerald-700 font-bold'}">
            ${data.cargo_floor_applied ? '0.25 GT Applied' : 'Calculated'}
          </span>
        </div>
      </div>
    </div>

    <!-- Main Calculation Panels (2-Column Grid) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
      <!-- Left Column (7 cols): Interactive Volume Modeler -->
      <div class="lg:col-span-7 space-y-4">
        
        <!-- Panel 1: Underdeck Hull Volume (Rule 10 & 14) -->
        <div class="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
          <div class="flex items-center justify-between pb-2 border-b border-slate-100 mb-2.5">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 bg-blue-600 text-white rounded text-[10px] font-bold flex items-center justify-center">1</span>
              <h2 class="text-xs font-bold text-slate-800 uppercase tracking-wide">Under-Deck Hull Volume (V₁)</h2>
            </div>
            <span class="text-[10px] text-slate-500 font-medium">Rule 10(2), Rule 14(1)</span>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs mb-3">
            <div>
              <label class="block text-slate-500 text-[10px] font-medium leading-none mb-1">LBP (L) [m]</label>
              <input 
                type="number" 
                step="0.01" 
                class="compact-input h-7 py-0.5 px-2 text-xs font-semibold" 
                value="${data.lbp}" 
                oninput="handleLiveInputChange('lbp', parseFloat(this.value) || 0); renderTonnage();"
              />
            </div>
            <div>
              <label class="block text-slate-500 text-[10px] font-medium leading-none mb-1">Breadth (B) [m]</label>
              <input 
                type="number" 
                step="0.01" 
                class="compact-input h-7 py-0.5 px-2 text-xs font-semibold" 
                value="${data.breadth}" 
                oninput="handleLiveInputChange('breadth', parseFloat(this.value) || 0); renderTonnage();"
              />
            </div>
            <div>
              <label class="block text-slate-500 text-[10px] font-medium leading-none mb-1">Moulded Depth (D) [m]</label>
              <input 
                type="number" 
                step="0.01" 
                class="compact-input h-7 py-0.5 px-2 text-xs font-semibold" 
                value="${data.depth}" 
                oninput="handleLiveInputChange('depth', parseFloat(this.value) || 0); renderTonnage();"
              />
            </div>
            <div>
              <label class="block text-slate-500 text-[10px] font-medium leading-none mb-1">Underdeck Coeff (Cv)</label>
              <input 
                type="number" 
                step="0.005" 
                min="0.4" 
                max="1.0" 
                class="compact-input h-7 py-0.5 px-2 text-xs font-semibold font-mono text-blue-700" 
                value="${data.cv}" 
                oninput="handleTonnageConfigChange('underdeck_coeff', parseFloat(this.value) || 0.75)"
                title="Underdeck Volume Coefficient (Block coefficient applied to moulded volume)"
              />
            </div>
          </div>

          <div class="bg-slate-50 p-2.5 rounded border border-slate-200/80 flex items-center justify-between text-xs">
            <div>
              <span class="text-slate-600 font-medium">Underdeck Hull Volume Formula:</span>
              <div class="font-mono text-slate-800 text-[11px] mt-0.5">
                V₁ = LBP × B × D × Cv = ${data.lbp.toFixed(2)} × ${data.breadth.toFixed(2)} × ${data.depth.toFixed(2)} × ${data.cv.toFixed(3)}
              </div>
            </div>
            <div class="text-right">
              <span class="text-[10px] text-slate-500 uppercase block font-semibold">Underdeck Volume</span>
              <span class="text-sm font-bold font-mono text-blue-900">${data.v_underdeck.toLocaleString('en-US', { minimumFractionDigits: 2 })} m³</span>
            </div>
          </div>
        </div>

        <!-- Panel 2: Enclosed Superstructures & Deckhouses (Rule 10(4) & 14) -->
        <div class="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
          <div class="flex items-center justify-between pb-2 border-b border-slate-100 mb-2.5">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 bg-amber-600 text-white rounded text-[10px] font-bold flex items-center justify-center">2</span>
              <h2 class="text-xs font-bold text-slate-800 uppercase tracking-wide">Enclosed Superstructures &amp; Deckhouses (V₂)</h2>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-[10px] text-slate-500 font-medium">Rule 10(4), Rule 14</span>
              <button 
                onclick="addSuperstructureRow()" 
                class="px-2 py-0.5 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded text-[10.5px] font-bold flex items-center gap-1 cursor-pointer"
              >
                + Add Erection
              </button>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-xs text-left">
              <thead>
                <tr class="bg-slate-50 text-[10.5px] text-slate-600 border-b border-slate-200">
                  <th class="py-1 px-2 font-semibold">Erection / Structure Name</th>
                  <th class="py-1 px-1.5 font-semibold text-center w-16">Length [m]</th>
                  <th class="py-1 px-1.5 font-semibold text-center w-16">Breadth [m]</th>
                  <th class="py-1 px-1.5 font-semibold text-center w-16">Height [m]</th>
                  <th class="py-1 px-2 font-semibold text-right w-24">Volume [m³]</th>
                  <th class="py-1 px-2 font-semibold text-center w-16">Enclosed</th>
                  <th class="py-1 px-1 text-center w-8"></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 font-mono text-[11px]">
                ${(data.superstructures || []).map((s, idx) => `
                  <tr class="hover:bg-slate-50/50">
                    <td class="py-1 px-2 font-sans font-medium text-slate-800">
                      <input 
                        type="text" 
                        class="compact-input h-6 py-0 px-1.5 text-xs font-medium w-full" 
                        value="${s.name}" 
                        oninput="handleSuperstructureChange(${idx}, 'name', this.value)"
                      />
                    </td>
                    <td class="py-1 px-1.5 text-center">
                      <input 
                        type="number" 
                        step="0.1" 
                        class="compact-input h-6 py-0 px-1 text-xs text-center w-full" 
                        value="${s.length}" 
                        oninput="handleSuperstructureChange(${idx}, 'length', this.value)"
                      />
                    </td>
                    <td class="py-1 px-1.5 text-center">
                      <input 
                        type="number" 
                        step="0.1" 
                        class="compact-input h-6 py-0 px-1 text-xs text-center w-full" 
                        value="${s.breadth}" 
                        oninput="handleSuperstructureChange(${idx}, 'breadth', this.value)"
                      />
                    </td>
                    <td class="py-1 px-1.5 text-center">
                      <input 
                        type="number" 
                        step="0.1" 
                        class="compact-input h-6 py-0 px-1 text-xs text-center w-full" 
                        value="${s.height}" 
                        oninput="handleSuperstructureChange(${idx}, 'height', this.value)"
                      />
                    </td>
                    <td class="py-1 px-2 text-right font-bold text-slate-900">
                      <input 
                        type="number" 
                        step="0.1" 
                        class="compact-input h-6 py-0 px-1 text-xs text-right font-bold w-full bg-slate-50" 
                        value="${s.volume}" 
                        oninput="handleSuperstructureChange(${idx}, 'volume', this.value)"
                      />
                    </td>
                    <td class="py-1 px-2 text-center">
                      <input 
                        type="checkbox" 
                        class="w-3.5 h-3.5 text-blue-600 rounded" 
                        ${s.is_enclosed !== false ? 'checked' : ''} 
                        onchange="handleSuperstructureChange(${idx}, 'is_enclosed', this.checked)"
                        title="Tick to include in Total Enclosed Volume (V)"
                      />
                    </td>
                    <td class="py-1 px-1 text-center font-sans">
                      <button 
                        onclick="removeSuperstructureRow(${idx})" 
                        class="text-rose-500 hover:text-rose-700 text-xs px-1 cursor-pointer"
                        title="Delete this erection"
                      >
                        ×
                      </button>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
              <tfoot>
                <tr class="bg-amber-50/60 font-bold border-t border-slate-200 text-xs">
                  <td colspan="4" class="py-1.5 px-2 text-slate-700 font-sans">Total Superstructures &amp; Deckhouses Volume (V₂):</td>
                  <td class="py-1.5 px-2 text-right font-mono text-amber-900 font-bold">${data.v_superstructures.toFixed(2)} m³</td>
                  <td colspan="2"></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        <!-- Action Bar: Calculate Tonnage (Immediately after Underdeck & Superstructures) -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50/50 p-2.5 rounded-lg border border-blue-200/80 flex items-center justify-between shadow-2xs">
          <div class="text-xs">
            <span class="font-bold text-blue-950 block text-[11.5px]">ISO 2001 Tonnage Engine</span>
            <span class="text-[10px] text-slate-500">Recalculate Gross Tonnage (GT) and Net Tonnage (NT)</span>
          </div>
          <button 
            type="button" 
            id="btn-recalculate-tonnage"
            onclick="triggerTonnageCalculation(event)" 
            class="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 active:scale-95 text-white rounded text-xs font-bold shadow-xs hover:shadow transition-all flex items-center gap-1.5 cursor-pointer"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>
            <span id="btn-tonnage-text">Calculate Tonnage</span>
          </button>
        </div>

        <!-- Panel 3: Appendages & Excluded Spaces (Rule 14(2) & Rule 10(5)) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <!-- Appendages -->
          <div class="bg-white p-3 rounded-lg border border-slate-200 shadow-2xs">
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-100 mb-2">
              <span class="text-xs font-bold text-slate-800 uppercase">Appendages (V₃)</span>
              <button onclick="addAppendageRow()" class="text-[10px] text-blue-600 hover:text-blue-800 font-bold cursor-pointer">+ Add</button>
            </div>
            <div class="space-y-1.5 text-xs">
              ${(data.appendages || []).map((a, idx) => `
                <div class="flex items-center gap-1.5">
                  <input type="text" class="compact-input h-6 py-0 px-1 text-[11px] flex-1" value="${a.name}" oninput="getTonnageState().appendages[${idx}].name = this.value"/>
                  <input type="number" step="0.5" class="compact-input h-6 py-0 px-1 text-[11px] font-mono text-right w-16" value="${a.volume}" oninput="getTonnageState().appendages[${idx}].volume = parseFloat(this.value)||0; renderTonnage();"/>
                  <span class="text-[10px] text-slate-400">m³</span>
                  <button onclick="removeAppendageRow(${idx})" class="text-rose-500 hover:text-rose-700 text-xs px-0.5 cursor-pointer">×</button>
                </div>
              `).join('')}
            </div>
            <div class="mt-2 pt-1.5 border-t border-slate-100 flex items-center justify-between text-xs font-bold font-mono text-emerald-800">
              <span>Total Appendages:</span>
              <span>+${data.v_appendages.toFixed(2)} m³</span>
            </div>
          </div>

          <!-- Excluded Spaces -->
          <div class="bg-white p-3 rounded-lg border border-slate-200 shadow-2xs">
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-100 mb-2">
              <span class="text-xs font-bold text-slate-800 uppercase">Excluded Spaces (Rule 10(5))</span>
              <span class="text-[10px] text-slate-400">Deducted from V</span>
            </div>
            <div class="space-y-1.5 text-xs">
              ${(data.excluded_spaces || []).map((e, idx) => `
                <div class="flex items-center gap-1.5">
                  <input type="text" class="compact-input h-6 py-0 px-1 text-[11px] flex-1" value="${e.name}" oninput="getTonnageState().excluded_spaces[${idx}].name = this.value"/>
                  <input type="number" step="0.5" class="compact-input h-6 py-0 px-1 text-[11px] font-mono text-right w-16 text-rose-700" value="${e.volume}" oninput="getTonnageState().excluded_spaces[${idx}].volume = parseFloat(this.value)||0; renderTonnage();"/>
                  <span class="text-[10px] text-slate-400">m³</span>
                </div>
              `).join('')}
              ${(!data.excluded_spaces || data.excluded_spaces.length === 0) ? `
                <div class="text-[11px] text-slate-400 italic py-1">No excluded spaces declared.</div>
              ` : ''}
            </div>
            <div class="mt-2 pt-1.5 border-t border-slate-100 flex items-center justify-between text-xs font-bold font-mono text-rose-800">
              <span>Total Excluded:</span>
              <span>-${data.v_excluded.toFixed(2)} m³</span>
            </div>
          </div>
        </div>

      </div>

      <!-- Right Column (5 cols): Net Tonnage Inputs, Derivation & Certificate -->
      <div class="lg:col-span-5 space-y-4">
        
        <!-- Panel 4: Net Tonnage Parameters (Rule 12) -->
        <div class="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
          <div class="flex items-center justify-between pb-2 border-b border-slate-100 mb-2.5">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 bg-purple-600 text-white rounded text-[10px] font-bold flex items-center justify-center">3</span>
              <h2 class="text-xs font-bold text-slate-800 uppercase tracking-wide">Net Tonnage Parameters (Rule 12)</h2>
            </div>
            <span class="text-[10px] text-slate-500 font-medium">NT = K₂·Vc·(4d/3D)² + K₃(N₁+N₂/10)</span>
          </div>

          <div class="space-y-2.5 text-xs">
            <!-- Cargo Volume Setup -->
            <div class="bg-purple-50/50 p-2.5 rounded border border-purple-100">
              <label class="block text-purple-950 font-bold text-[11px] mb-1">Cargo Spaces Volume (Vc) [m³]</label>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <span class="block text-[10px] text-slate-500 mb-0.5">% of Underdeck Vol</span>
                  <input 
                    type="number" 
                    step="1" 
                    min="10" 
                    max="95" 
                    class="compact-input h-7 py-0.5 px-2 text-xs font-mono font-bold" 
                    value="${parseFloat(getTonnageState().cargo_percent) || 68}" 
                    oninput="handleTonnageConfigChange('cargo_percent', parseFloat(this.value) || 68)"
                  />
                </div>
                <div>
                  <span class="block text-[10px] text-slate-500 mb-0.5">Calculated Vc [m³]</span>
                  <div class="compact-input h-7 py-0.5 px-2 text-xs font-mono font-bold bg-white text-purple-900 flex items-center justify-end">
                    ${data.vc.toFixed(1)} m³
                  </div>
                </div>
              </div>
            </div>

            <!-- Draught & Moulded Depth Factor -->
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div>
                <label class="block text-slate-500 text-[10px] font-medium leading-none mb-1">Moulded Draught (d) [m]</label>
                <input 
                  type="number" 
                  step="0.01" 
                  class="compact-input h-7 py-0.5 px-2 text-xs font-semibold" 
                  value="${data.draft}" 
                  oninput="handleLiveInputChange('draft', parseFloat(this.value) || 0); renderTonnage();"
                />
              </div>
              <div>
                <label class="block text-slate-500 text-[10px] font-medium leading-none mb-1">Draught Ratio (4d/3D)²</label>
                <div class="compact-input h-7 py-0.5 px-2 text-xs font-mono font-bold bg-slate-50 text-slate-800 flex items-center justify-end" title="Capped <= 1.0 as per Rule 12(1)(a)">
                  ${data.draft_factor_applied} ${data.draft_factor_sq > 1.0 ? '(Capped 1.0)' : ''}
                </div>
              </div>
            </div>

            <!-- Passengers (N1 & N2) -->
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div>
                <label class="block text-slate-500 text-[10px] font-medium leading-none mb-1">N₁ (Cabin Berths ≤ 8)</label>
                <input 
                  type="number" 
                  step="1" 
                  min="0" 
                  class="compact-input h-7 py-0.5 px-2 text-xs font-semibold" 
                  value="${data.n1}" 
                  oninput="handleTonnageConfigChange('passengers_cabin_n1', parseInt(this.value) || 0)"
                />
              </div>
              <div>
                <label class="block text-slate-500 text-[10px] font-medium leading-none mb-1">N₂ (Other Passengers)</label>
                <input 
                  type="number" 
                  step="1" 
                  min="0" 
                  class="compact-input h-7 py-0.5 px-2 text-xs font-semibold" 
                  value="${data.n2}" 
                  oninput="handleTonnageConfigChange('passengers_other_n2', parseInt(this.value) || 0)"
                />
              </div>
            </div>
            ${data.pax_zeroed ? `
              <div class="text-[10px] text-amber-700 bg-amber-50 p-1.5 rounded border border-amber-200">
                <b>Rule 12(1) Provision:</b> Total passengers (${data.n1 + data.n2}) &lt; 13, therefore N₁ and N₂ are taken as zero.
              </div>
            ` : ''}
          </div>
        </div>

        <!-- Panel 5: Mathematical Verification Ledger -->
        <div class="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
          <div class="flex items-center justify-between pb-2 border-b border-slate-100 mb-2">
            <h2 class="text-xs font-bold text-slate-800 uppercase tracking-wide">Statutory Verification Ledger</h2>
            <span class="text-[10px] text-slate-400 font-mono">ISO 2001 Formulas</span>
          </div>

          <div class="space-y-1.5 text-xs font-mono text-[11px]">
            <div class="p-1.5 bg-slate-50 rounded flex justify-between items-center">
              <span class="text-slate-600 font-sans text-[11px]">Enclosed Volume (V):</span>
              <span class="font-bold text-slate-900">${data.v_total.toFixed(2)} m³</span>
            </div>
            <div class="p-1.5 bg-slate-50 rounded flex justify-between items-center">
              <span class="text-slate-600 font-sans text-[11px]">K₁ = 0.2 + 0.02·log₁₀(${data.v_total.toFixed(1)}):</span>
              <span class="font-bold text-amber-900">${data.k1}</span>
            </div>
            <div class="p-1.5 bg-amber-100/60 rounded flex justify-between items-center border border-amber-300">
              <span class="font-bold text-amber-950 font-sans text-xs">Gross Tonnage (GT = K₁·V):</span>
              <span class="font-bold text-amber-950 text-xs">${data.gt.toFixed(2)} GT</span>
            </div>

            <div class="p-1.5 bg-slate-50 rounded flex justify-between items-center mt-2">
              <span class="text-slate-600 font-sans text-[11px]">K₂ = 0.2 + 0.02·log₁₀(${data.vc.toFixed(1)}):</span>
              <span class="font-bold text-purple-900">${data.k2}</span>
            </div>
            <div class="p-1.5 bg-slate-50 rounded flex justify-between items-center">
              <span class="text-slate-600 font-sans text-[11px]">Cargo Term [Floor ≥ 0.25 GT]:</span>
              <span class="font-bold ${data.cargo_floor_applied ? 'text-amber-800' : 'text-slate-900'}">${data.effective_cargo_term.toFixed(2)}</span>
            </div>
            <div class="p-1.5 bg-slate-50 rounded flex justify-between items-center">
              <span class="text-slate-600 font-sans text-[11px]">Passenger Term K₃·(N₁+N₂/10):</span>
              <span class="font-bold text-slate-900">${data.pax_term.toFixed(2)}</span>
            </div>
            <div class="p-1.5 bg-blue-100/60 rounded flex justify-between items-center border border-blue-300">
              <span class="font-bold text-blue-950 font-sans text-xs">Net Tonnage (NT [Floor ≥ 0.30 GT]):</span>
              <span class="font-bold text-blue-950 text-xs">${data.nt.toFixed(2)} NT</span>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Panel 6: Official Bangladesh Inland Ship Tonnage Measurement Certificate Preview (Appendix 1) -->
    <div class="bg-white p-6 rounded-lg border border-slate-300 shadow-sm print:m-0 print:border-none print:shadow-none" id="tonnage-certificate-print-area">
      <!-- Certificate Header -->
      <div class="text-center pb-4 border-b-2 border-slate-800 mb-4">
        <div class="text-[11px] font-bold text-slate-600 uppercase tracking-widest">Government of the People's Republic of Bangladesh</div>
        <div class="text-base font-black text-slate-900 uppercase tracking-tight mt-0.5">DEPARTMENT OF SHIPPING</div>
        <div class="text-xs font-semibold text-slate-700">DHAKA, BANGLADESH</div>
        <div class="inline-block mt-2 px-4 py-1 bg-slate-100 border border-slate-400 rounded text-xs font-bold uppercase tracking-wider text-slate-900">
          Inland Ship Tonnage Measurement Certificate
        </div>
        <div class="text-[10px] text-slate-500 italic mt-1">
          Issued under the provisions of the Inland Ships (Tonnage Measurement) Rules, 2001 &mdash; Rule 7(3), Appendix-1
        </div>
      </div>

      <!-- Vessel Particulars Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs mb-4 pb-3 border-b border-slate-200">
        <div>
          <span class="text-slate-500 text-[10px] uppercase block">Name of Ship</span>
          <b class="text-slate-900 text-xs">${vName}</b>
        </div>
        <div>
          <span class="text-slate-500 text-[10px] uppercase block">Port of Registry</span>
          <b class="text-slate-900 text-xs">${inputs.port_of_registry || 'DHAKA'}</b>
        </div>
        <div>
          <span class="text-slate-500 text-[10px] uppercase block">Official Number</span>
          <b class="text-slate-900 text-xs">${inputs.official_no || 'M-10294'}</b>
        </div>
        <div>
          <span class="text-slate-500 text-[10px] uppercase block">Date Keel Laid</span>
          <b class="text-slate-900 text-xs">${inputs.date_keel_laid || '2024-03-15'}</b>
        </div>
      </div>

      <!-- Dimensions -->
      <div class="grid grid-cols-3 sm:grid-cols-6 gap-2 text-xs mb-4 pb-3 border-b border-slate-200 text-center font-mono">
        <div class="bg-slate-50 p-2 rounded">
          <span class="text-[10px] text-slate-500 uppercase block font-sans">LOA</span>
          <b>${data.loa.toFixed(2)} m</b>
        </div>
        <div class="bg-slate-50 p-2 rounded">
          <span class="text-[10px] text-slate-500 uppercase block font-sans">LBP</span>
          <b>${data.lbp.toFixed(2)} m</b>
        </div>
        <div class="bg-slate-50 p-2 rounded">
          <span class="text-[10px] text-slate-500 uppercase block font-sans">Breadth (B)</span>
          <b>${data.breadth.toFixed(2)} m</b>
        </div>
        <div class="bg-slate-50 p-2 rounded">
          <span class="text-[10px] text-slate-500 uppercase block font-sans">Depth (D)</span>
          <b>${data.depth.toFixed(2)} m</b>
        </div>
        <div class="bg-slate-50 p-2 rounded">
          <span class="text-[10px] text-slate-500 uppercase block font-sans">Draft (d)</span>
          <b>${data.draft.toFixed(2)} m</b>
        </div>
        <div class="bg-slate-50 p-2 rounded">
          <span class="text-[10px] text-slate-500 uppercase block font-sans">Block Coeff</span>
          <b>${data.cb.toFixed(3)}</b>
        </div>
      </div>

      <!-- Tonnage Results Box -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <div class="border-2 border-slate-800 rounded-lg p-4 text-center bg-slate-50/50">
          <div class="text-xs font-bold text-slate-600 uppercase tracking-wider">GROSS TONNAGE (GT)</div>
          <div class="text-3xl font-black text-slate-900 font-mono mt-1">${data.gt.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          <div class="text-[10.5px] text-slate-500 mt-1 font-mono">GT = K₁ × V (Rule 11)</div>
        </div>
        <div class="border-2 border-slate-800 rounded-lg p-4 text-center bg-slate-50/50">
          <div class="text-xs font-bold text-slate-600 uppercase tracking-wider">NET TONNAGE (NT)</div>
          <div class="text-3xl font-black text-slate-900 font-mono mt-1">${data.nt.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          <div class="text-[10.5px] text-slate-500 mt-1 font-mono">NT as per Rule 12(1)</div>
        </div>
      </div>

      <!-- Spaces Summary Breakdown Table -->
      <div class="mb-6">
        <div class="text-xs font-bold text-slate-700 uppercase mb-2">Summary Breakdown of Volumes (Rule 14 &amp; 15)</div>
        <table class="w-full text-xs border border-slate-300">
          <thead>
            <tr class="bg-slate-100 border-b border-slate-300 text-slate-700">
              <th class="py-1 px-3 text-left">Space Description</th>
              <th class="py-1 px-3 text-center">Statutory Reference</th>
              <th class="py-1 px-3 text-right">Volume (m³)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 font-mono text-[11px]">
            <tr>
              <td class="py-1 px-3 font-sans text-slate-800">Under-deck Volume of Hull</td>
              <td class="py-1 px-3 text-center font-sans text-slate-500">Rule 10(2), 14(1)</td>
              <td class="py-1 px-3 text-right font-bold">${data.v_underdeck.toFixed(2)}</td>
            </tr>
            <tr>
              <td class="py-1 px-3 font-sans text-slate-800">Enclosed Superstructures &amp; Deckhouses</td>
              <td class="py-1 px-3 text-center font-sans text-slate-500">Rule 10(4), 14</td>
              <td class="py-1 px-3 text-right font-bold">${data.v_superstructures.toFixed(2)}</td>
            </tr>
            <tr>
              <td class="py-1 px-3 font-sans text-slate-800">Appendages (Rudder, Skeg, Bossing)</td>
              <td class="py-1 px-3 text-center font-sans text-slate-500">Rule 14(2)</td>
              <td class="py-1 px-3 text-right font-bold">${data.v_appendages.toFixed(2)}</td>
            </tr>
            ${data.v_excluded > 0 ? `
              <tr>
                <td class="py-1 px-3 font-sans text-slate-500">Less Excluded Spaces</td>
                <td class="py-1 px-3 text-center font-sans text-slate-500">Rule 10(5)</td>
                <td class="py-1 px-3 text-right text-rose-700 font-bold">-${data.v_excluded.toFixed(2)}</td>
              </tr>
            ` : ''}
            <tr class="bg-slate-50 font-bold text-slate-900">
              <td class="py-1.5 px-3 font-sans uppercase">Total Enclosed Space Volume (V)</td>
              <td class="py-1.5 px-3 text-center font-sans">Rule 11</td>
              <td class="py-1.5 px-3 text-right font-mono">${data.v_total.toFixed(2)} m³</td>
            </tr>
            <tr class="bg-blue-50/50 font-bold text-blue-950">
              <td class="py-1.5 px-3 font-sans uppercase">Total Cargo Spaces Volume (Vc)</td>
              <td class="py-1.5 px-3 text-center font-sans">Rule 12(1)</td>
              <td class="py-1.5 px-3 text-right font-mono">${data.vc.toFixed(2)} m³</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Statutory Attestation & Signatures -->
      <div class="grid grid-cols-2 gap-8 pt-6 border-t border-slate-300 text-xs">
        <div class="text-center">
          <div class="h-16 flex items-end justify-center">
            <span class="font-signature text-base text-blue-900">${inputs.checked_by || 'AMITAVO CHOWDHURY WYE'}</span>
          </div>
          <div class="border-t border-slate-400 pt-1 font-bold text-slate-800">Naval Architect / Ship Surveyor</div>
          <div class="text-[10px] text-slate-500">Department of Shipping, Dhaka</div>
        </div>
        <div class="text-center">
          <div class="h-16 flex items-end justify-center">
            <span class="font-signature text-base text-slate-900 font-serif font-bold">REGISTRAR OF INLAND SHIPS</span>
          </div>
          <div class="border-t border-slate-400 pt-1 font-bold text-slate-800">Registrar of Inland Ships</div>
          <div class="text-[10px] text-slate-500">Government of the People's Republic of Bangladesh</div>
        </div>
      </div>
    </div>
  `;
}

window.renderTonnage = renderTonnage;
window.calculateClientTonnage = calculateClientTonnage;
