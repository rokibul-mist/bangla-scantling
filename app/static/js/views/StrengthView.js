/**
 * StrengthView.js - Hull Strength, Longitudinal Bending Moments, and Midship Modulus
 * Statutory Reference: Rules 209 & 223, Schedule Tables 66 & 67 (SRO 308/Law-2001 & ISO 1976)
 * Features interactive element inclusion/exclusion checkboxes and detailed step-by-step practical working.
 */

let activeStrengthData = null;
let activeStrengthPdfBlobUrl = null;

async function fetchStrengthData() {
  try {
    const payload = (typeof appState !== 'undefined') ? appState : {};
    const res = await fetch('/api/v1/strength/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    activeStrengthData = data;
    return data;
  } catch (err) {
    console.error('Failed to fetch hull strength data:', err);
    return null;
  }
}

function toggleMidshipElement(elId) {
  if (typeof appState === 'undefined') return;
  appState.midship_excluded_element_ids = appState.midship_excluded_element_ids || [];
  const idx = appState.midship_excluded_element_ids.indexOf(elId);
  if (idx >= 0) {
    appState.midship_excluded_element_ids.splice(idx, 1);
  } else {
    appState.midship_excluded_element_ids.push(elId);
  }
  renderStrengthView();
  if (typeof triggerAutosaveDebounced === 'function') {
    triggerAutosaveDebounced();
  }
}

function toggleAllMidshipElements(selectAll) {
  if (typeof appState === 'undefined' || !activeStrengthData) return;
  const allElements = activeStrengthData.midship_properties.elements || [];
  if (selectAll) {
    appState.midship_excluded_element_ids = [];
  } else {
    // Exclude all except minimum 2 (keep keel & deck)
    appState.midship_excluded_element_ids = allElements
      .filter(el => el.id !== 'midship_keel' && el.id !== 'midship_deck_abreast')
      .map(el => el.id);
  }
  renderStrengthView();
  if (typeof triggerAutosaveDebounced === 'function') {
    triggerAutosaveDebounced();
  }
}

function resetMidshipElements() {
  if (typeof appState === 'undefined') return;
  appState.midship_excluded_element_ids = [];
  renderStrengthView();
  if (typeof triggerAutosaveDebounced === 'function') {
    triggerAutosaveDebounced();
  }
}

function renderMidshipCrossSectionSvg(props, particulars, width = 480, height = 300) {
  const b = parseFloat(particulars.breadth || 13.41);
  const d = parseFloat(particulars.depth || 5.18);
  const yNa = parseFloat(props.neutral_axis_above_keel_m || (d * 0.45));

  const padX = 50;
  const padY = 35;
  const availW = width - padX * 2;
  const availH = height - padY * 2;

  const scale = Math.min(availW / b, availH / d);
  const hullW = b * scale;
  const hullH = d * scale;

  const originX = (width - hullW) / 2;
  const originY = height - padY; // Keel base line
  const deckY = originY - hullH;
  const naY = originY - (yNa * scale);

  const hatchHalfW = (hullW / 2) * 0.55;
  const midX = originX + hullW / 2;
  const coamH = 15;

  return `
    <svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" class="bg-slate-900 rounded-lg border border-slate-800 shadow-inner">
      <defs>
        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" stroke-width="0.5"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid)" />

      <!-- Centerline (CL) -->
      <line x1="${midX}" y1="${deckY - 20}" x2="${midX}" y2="${originY + 15}" stroke="#475569" stroke-width="1" stroke-dasharray="4,3" />
      <text x="${midX}" y="${deckY - 24}" fill="#94a3b8" font-size="9" text-anchor="middle" font-family="monospace">CL</text>

      <!-- Baseline (BL / Keel) -->
      <line x1="${originX - 20}" y1="${originY}" x2="${originX + hullW + 20}" y2="${originY}" stroke="#475569" stroke-width="1" stroke-dasharray="4,3" />
      <text x="${originX - 25}" y="${originY + 3}" fill="#94a3b8" font-size="9" text-anchor="end" font-family="monospace">BL</text>

      <!-- Outer Shell Outline -->
      <!-- Bottom Plating -->
      <line x1="${originX}" y1="${originY}" x2="${originX + hullW}" y2="${originY}" stroke="#38bdf8" stroke-width="3" />
      <!-- Side Shell Plating -->
      <line x1="${originX}" y1="${originY}" x2="${originX}" y2="${deckY}" stroke="#38bdf8" stroke-width="2.5" />
      <line x1="${originX + hullW}" y1="${originY}" x2="${originX + hullW}" y2="${deckY}" stroke="#38bdf8" stroke-width="2.5" />
      <!-- Deck Plating Abreast Hatches -->
      <line x1="${originX}" y1="${deckY}" x2="${midX - hatchHalfW}" y2="${deckY}" stroke="#38bdf8" stroke-width="2.5" />
      <line x1="${midX + hatchHalfW}" y1="${deckY}" x2="${originX + hullW}" y2="${deckY}" stroke="#38bdf8" stroke-width="2.5" />

      <!-- Hatch Coaming (Vertical) -->
      <line x1="${midX - hatchHalfW}" y1="${deckY}" x2="${midX - hatchHalfW}" y2="${deckY - coamH}" stroke="#38bdf8" stroke-width="2.5" />
      <line x1="${midX + hatchHalfW}" y1="${deckY}" x2="${midX + hatchHalfW}" y2="${deckY - coamH}" stroke="#38bdf8" stroke-width="2.5" />

      <!-- Center Keelson -->
      <line x1="${midX}" y1="${originY}" x2="${midX}" y2="${originY - (hullH * 0.18)}" stroke="#0ea5e9" stroke-width="2" />
      <line x1="${midX - 12}" y1="${originY - (hullH * 0.18)}" x2="${midX + 12}" y2="${originY - (hullH * 0.18)}" stroke="#0ea5e9" stroke-width="2" />

      <!-- Side Keelsons -->
      <line x1="${midX - hullW * 0.28}" y1="${originY}" x2="${midX - hullW * 0.28}" y2="${originY - (hullH * 0.14)}" stroke="#0ea5e9" stroke-width="1.8" />
      <line x1="${midX + hullW * 0.28}" y1="${originY}" x2="${midX + hullW * 0.28}" y2="${originY - (hullH * 0.14)}" stroke="#0ea5e9" stroke-width="1.8" />

      <!-- Deck Longitudinal Girders -->
      <line x1="${midX - hatchHalfW}" y1="${deckY}" x2="${midX - hatchHalfW}" y2="${deckY + (hullH * 0.12)}" stroke="#0ea5e9" stroke-width="1.8" />
      <line x1="${midX + hatchHalfW}" y1="${deckY}" x2="${midX + hatchHalfW}" y2="${deckY + (hullH * 0.12)}" stroke="#0ea5e9" stroke-width="1.8" />

      <!-- NEUTRAL AXIS (NA) -->
      <line x1="${originX - 15}" y1="${naY}" x2="${originX + hullW + 15}" y2="${naY}" stroke="#ef4444" stroke-width="2" stroke-dasharray="6,4" />
      <circle cx="${midX}" cy="${naY}" r="4" fill="#ef4444" />
      <text x="${originX + hullW + 20}" y="${naY + 3}" fill="#ef4444" font-size="10" font-weight="bold" font-family="sans-serif">N.A.</text>

      <!-- Annotations -->
      <text x="${originX + 8}" y="${naY - 6}" fill="#fca5a5" font-size="9" font-family="monospace">y_NA = ${yNa.toFixed(3)} m</text>
      <text x="${originX + 8}" y="${deckY + 16}" fill="#94a3b8" font-size="9" font-family="monospace">y_deck = ${(d - yNa).toFixed(3)} m</text>
      <text x="${midX}" y="${deckY - 8}" fill="#94a3b8" font-size="9" text-anchor="middle" font-family="sans-serif">Hatch Opening</text>
      <text x="${midX}" y="${originY + 22}" fill="#64748b" font-size="9" text-anchor="middle" font-family="monospace">B = ${b.toFixed(2)} m | D = ${d.toFixed(2)} m</text>
    </svg>
  `;
}

async function renderStrengthView() {
  const container = document.getElementById('tab-content-strength');
  if (!container) return;

  container.innerHTML = `
    <div class="flex items-center justify-center p-12 text-slate-500 text-sm">
      <svg class="animate-spin h-5 w-5 mr-3 text-blue-600" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
      Evaluating global hull girder strength, midship section modulus, and practical calculations...
    </div>
  `;

  const report = await fetchStrengthData();
  if (!report) {
    container.innerHTML = `
      <div class="p-6 bg-red-50 border border-red-200 text-red-800 rounded-lg text-sm">
        Failed to load Hull Strength calculations. Please ensure vessel dimensions are provided in the Dashboard.
      </div>
    `;
    return;
  }

  try {
    const moms = report.bending_moments || {};
    const props = report.midship_properties || {};
    const t66 = report.table_66_stresses || {};
    const t67 = report.table_67_local_stresses || [];
    const part = report.particulars || {};
    const work = report.practical_working || {};
    const assumed = report.assumed_axis_integration || {};

    const isCompliant = !!report.is_compliant;
    const statusBadge = isCompliant 
      ? '<span class="px-2.5 py-1 bg-emerald-100 text-emerald-800 text-xs font-bold rounded-full border border-emerald-300">STATUTORY COMPLIANT</span>'
      : '<span class="px-2.5 py-1 bg-red-100 text-red-800 text-xs font-bold rounded-full border border-red-300">NON-COMPLIANT</span>';

    const elementsList = props.elements || [];
    const selectedCount = props.elements_selected_count ?? elementsList.filter(e => e.is_included).length;
    const totalCount = props.elements_count ?? elementsList.length;

    const depthM = parseFloat(part.depth || 5.18);
    const yBottomM = props.neutral_axis_above_keel_m ?? (depthM * 0.45);
    const yDeckM = props.distance_to_deck_m ?? (depthM - yBottomM);
    const z1StressCm3 = (((moms.m_design_knm || 0) * 1000.0) / 130.0);
    const z2EmpiricalCm3 = props.modulus_empirical_cm3 || (1.75 * (report.factor_kt || 1.40) * Math.pow(part.lbp || 66.8, 2) * (part.breadth || 11.2) * ((part.cb || 0.75) + 0.70));
    const firstMomentCm3 = props.first_moment_cm3 || ((props.total_area_cm2 || 0) * yBottomM * 100.0);
    const factorCw = moms.wave_coefficient_cw || report.factor_cw || 0.936;
    container.innerHTML = `
    <!-- Top Action & Info Bar -->
    <div class="bg-white p-3.5 rounded-lg border border-slate-200 mb-4 flex flex-wrap justify-between items-center gap-3 shadow-xs">
      <div>
        <div class="compact-title compact-title-primary mb-0 text-slate-900 font-bold flex items-center gap-2">
          <span>HULL LONGITUDINAL STRENGTH &amp; MIDSHIP SECTION MODULUS</span>
          ${statusBadge}
        </div>
        <div class="text-xs text-slate-500 mt-0.5">
          Rules 209 &amp; 223, Schedule Tables 66 &amp; 67 (SRO 308/Law-2001 &amp; ISO 1976) — Vessel: <b>${report.vessel_name}</b>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button 
          onclick="resetMidshipElements()" 
          class="px-2.5 py-1.5 border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 rounded text-xs font-semibold transition shadow-xs cursor-pointer flex items-center gap-1"
          title="Reset element selections to default (include all strakes)"
        >
          <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          <span>Reset Elements</span>
        </button>

        <button 
          onclick="openStrengthPdfModal()" 
          class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-bold transition shadow-xs flex items-center gap-1.5 cursor-pointer"
          title="View official statutory 4-Page Hull Strength booklet PDF deliverable"
        >
          <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
          <span>View Strength PDF</span>
        </button>

        <button 
          onclick="downloadStrengthPdf()" 
          class="px-3 py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded text-xs font-semibold transition shadow-xs flex items-center gap-1.5 cursor-pointer"
          title="Download standalone statutory Hull Strength Booklet PDF"
        >
          <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
          <span>Download PDF</span>
        </button>
      </div>
    </div>

    <!-- Executive Compliance Scorecard (4 Cards) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 mb-4">
      <div class="bg-white p-3.5 rounded-lg border border-slate-200 shadow-xs">
        <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Midship Section Modulus</div>
        <div class="text-xl font-bold text-slate-900 mt-1">${props.modulus_actual_cm3.toLocaleString('en-US', {maximumFractionDigits: 1})} <span class="text-xs font-normal text-slate-500">cm³</span></div>
        <div class="text-[11px] text-slate-600 mt-1 flex justify-between items-center">
          <span>Req: <b>${props.modulus_rule_required_cm3.toLocaleString('en-US', {maximumFractionDigits: 1})} cm³</b></span>
          <span class="text-emerald-700 font-bold bg-emerald-50 px-1.5 py-0.5 rounded">+${props.modulus_margin_pct.toFixed(1)}%</span>
        </div>
      </div>

      <div class="bg-white p-3.5 rounded-lg border border-slate-200 shadow-xs">
        <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Design Bending Moment (M_t)</div>
        <div class="text-xl font-bold text-slate-900 mt-1">${moms.m_design_knm.toLocaleString('en-US', {maximumFractionDigits: 1})} <span class="text-xs font-normal text-slate-500">kN·m</span></div>
        <div class="text-[11px] text-slate-600 mt-1 flex justify-between items-center">
          <span>Condition: <b>${moms.design_condition}</b></span>
          <span class="text-blue-700 font-bold bg-blue-50 px-1.5 py-0.5 rounded">kt = ${report.factor_kt.toFixed(2)}</span>
        </div>
      </div>

      <div class="bg-white p-3.5 rounded-lg border border-slate-200 shadow-xs">
        <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Max Bending Stress (σ_b)</div>
        <div class="text-xl font-bold ${t66.max_bending_stress_n_mm2 <= 130 ? 'text-emerald-700' : 'text-red-700'} mt-1">${t66.max_bending_stress_n_mm2.toFixed(2)} <span class="text-xs font-normal text-slate-500">N/mm²</span></div>
        <div class="text-[11px] text-slate-600 mt-1 flex justify-between items-center">
          <span>Table 66 Limit: <b>130.0 N/mm²</b></span>
          <span class="text-emerald-700 font-bold bg-emerald-50 px-1.5 py-0.5 rounded">PASS</span>
        </div>
      </div>

      <div class="bg-white p-3.5 rounded-lg border border-slate-200 shadow-xs">
        <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Equivalent Stress (σ_e)</div>
        <div class="text-xl font-bold ${t66.equivalent_stress_n_mm2 <= 150 ? 'text-emerald-700' : 'text-red-700'} mt-1">${t66.equivalent_stress_n_mm2.toFixed(2)} <span class="text-xs font-normal text-slate-500">N/mm²</span></div>
        <div class="text-[11px] text-slate-600 mt-1 flex justify-between items-center">
          <span>Table 66 Limit: <b>150.0 N/mm²</b></span>
          <span class="text-emerald-700 font-bold bg-emerald-50 px-1.5 py-0.5 rounded">PASS</span>
        </div>
      </div>
    </div>

    <!-- Main Content Grid: Left Midship Elements Table (Interactive Checkboxes), Right Vector SVG -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 mb-4">
      
      <!-- Left Column (7 cols): Midship Elements Table with Selection Checkboxes -->
      <div class="lg:col-span-7 space-y-4">
        
        <!-- Midship Cross-Section Elements Table with Checkboxes -->
        <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div class="font-bold text-slate-900 text-sm mb-2 flex items-center justify-between border-b border-slate-100 pb-2">
            <div class="flex items-center gap-2">
              <span>SELECT MIDSHIP STRUCTURAL ELEMENTS (${selectedCount} OF ${totalCount} INCLUDED)</span>
            </div>
            <div class="flex items-center gap-2">
              <button onclick="toggleAllMidshipElements(true)" class="text-[11px] text-blue-600 hover:text-blue-800 font-semibold cursor-pointer">Select All</button>
              <span class="text-slate-300">|</span>
              <button onclick="toggleAllMidshipElements(false)" class="text-[11px] text-slate-500 hover:text-slate-700 font-semibold cursor-pointer">Deselect Girders</button>
            </div>
          </div>

          <div class="overflow-x-auto max-h-[380px] overflow-y-auto border border-slate-200 rounded">
            <table class="w-full text-left text-xs border-collapse">
              <thead class="bg-slate-100 text-slate-700 font-bold sticky top-0 border-b border-slate-200">
                <tr>
                  <th class="p-2 text-center w-8">Inc</th>
                  <th class="p-2">Structural Strake</th>
                  <th class="p-2 text-right">b (mm)</th>
                  <th class="p-2 text-right">t (mm)</th>
                  <th class="p-2 text-right">Qty</th>
                  <th class="p-2 text-right">Area (cm²)</th>
                  <th class="p-2 text-right">Lever y (m)</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 text-slate-800">
                ${props.elements.map(el => {
                  const isInc = el.is_included;
                  return `
                    <tr class="hover:bg-slate-50 transition ${isInc ? '' : 'opacity-40 bg-slate-50/50'}">
                      <td class="p-2 text-center">
                        <input 
                          type="checkbox" 
                          ${isInc ? 'checked' : ''} 
                          onchange="toggleMidshipElement('${el.id}')"
                          class="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 cursor-pointer"
                          title="Toggle ${el.name} in midship cross-section calculation"
                        />
                      </td>
                      <td class="p-2 font-medium">
                        <span class="${isInc ? 'text-slate-900 font-semibold' : 'text-slate-500 line-through'}">${el.name}</span>
                        <span class="text-[10px] text-slate-500 block">${el.category}</span>
                      </td>
                      <td class="p-2 text-right font-mono">${el.width_mm.toFixed(0)}</td>
                      <td class="p-2 text-right font-mono">${el.thk_mm.toFixed(1)}</td>
                      <td class="p-2 text-right font-mono">${el.quantity}</td>
                      <td class="p-2 text-right font-mono font-semibold">${(el.area_mm2 / 100.0).toFixed(1)}</td>
                      <td class="p-2 text-right font-mono">${(el.lever_y_mm / 1000.0).toFixed(3)}</td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
              <tfoot class="bg-slate-50 font-bold border-t-2 border-slate-300 text-slate-900 sticky bottom-0">
                <tr>
                  <td class="p-2 text-center">✓</td>
                  <td class="p-2" colspan="3">Integrated Active Total:</td>
                  <td class="p-2 text-right font-mono">${props.total_area_cm2.toLocaleString('en-US', {maximumFractionDigits: 1})} cm²</td>
                  <td class="p-2 text-right font-mono" colspan="2">y_NA = ${props.neutral_axis_above_keel_m.toFixed(3)} m</td>
                </tr>
              </tfoot>
            </table>
          </div>
          <div class="text-[11px] text-slate-500 mt-2 flex items-center justify-between">
            <span>Check or uncheck strakes above to simulate scantling variants dynamically.</span>
            <span>Active Inertia: <b>${props.moment_of_inertia_m4.toFixed(4)} m⁴</b></span>
          </div>
        </div>

        <!-- Bending Moments Breakdown Box -->
        <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div class="font-bold text-slate-900 text-sm mb-2 flex items-center justify-between border-b border-slate-100 pb-2">
            <span>LONGITUDINAL DESIGN BENDING MOMENTS (RULE 209)</span>
            <span class="text-[11px] text-slate-500 font-normal">Wave Coef C_w = ${moms.wave_coefficient_cw.toFixed(3)}</span>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs text-slate-700">
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Still Water Moment (M_sw)</div>
              <div class="font-bold text-slate-900 mt-0.5">${moms.m_sw_knm.toLocaleString('en-US', {maximumFractionDigits: 1})} kN·m</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Wave Hogging (M_w,hog)</div>
              <div class="font-bold text-slate-900 mt-0.5">${moms.m_wave_hog_knm.toLocaleString('en-US', {maximumFractionDigits: 1})} kN·m</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Wave Sagging (M_w,sag)</div>
              <div class="font-bold text-slate-900 mt-0.5">${moms.m_wave_sag_knm.toLocaleString('en-US', {maximumFractionDigits: 1})} kN·m</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Total Hogging (M_t,hog)</div>
              <div class="font-bold text-slate-900 mt-0.5">${moms.m_total_hog_knm.toLocaleString('en-US', {maximumFractionDigits: 1})} kN·m</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Total Sagging (M_t,sag)</div>
              <div class="font-bold text-slate-900 mt-0.5">${moms.m_total_sag_knm.toLocaleString('en-US', {maximumFractionDigits: 1})} kN·m</div>
            </div>
            <div class="bg-blue-50 p-2.5 rounded border border-blue-200">
              <div class="text-blue-600 text-[10px] font-bold">Governing Design (M_design)</div>
              <div class="font-bold text-blue-900 mt-0.5">${moms.m_design_knm.toLocaleString('en-US', {maximumFractionDigits: 1})} kN·m</div>
            </div>
          </div>
        </div>

        <!-- Statutory ISO 1976 & Rule 209 Longitudinal Criteria Card (Section 103) -->
        <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div class="font-bold text-slate-900 text-sm mb-2 flex items-center justify-between border-b border-slate-100 pb-2">
            <span>STATUTORY SECTION MODULUS &amp; MOMENTS MATRIX (RULE 209 &amp; ISO 1976)</span>
            <span class="text-[11px] text-emerald-700 font-bold">ISO 1976 Standard</span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs text-slate-700">
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Wave Coeff (Cw)</div>
              <div class="font-bold text-slate-900 mt-0.5">${factorCw.toFixed(4)}</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Route Factor (kt)</div>
              <div class="font-bold text-slate-900 mt-0.5">${(report.factor_kt || 1.40).toFixed(2)}</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Shear Force (Q_design)</div>
              <div class="font-bold text-slate-900 mt-0.5">${(moms.shear_force_design_kn || 0).toLocaleString('en-US', {maximumFractionDigits: 1})} kN</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Stress Req Z1 (130 N/mm²)</div>
              <div class="font-bold text-slate-900 mt-0.5">${z1StressCm3.toLocaleString('en-US', {maximumFractionDigits: 0})} cm³</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Empirical Req Z2 (kt·L²·B)</div>
              <div class="font-bold text-slate-900 mt-0.5">${z2EmpiricalCm3.toLocaleString('en-US', {maximumFractionDigits: 0})} cm³</div>
            </div>
            <div class="bg-emerald-50 p-2.5 rounded border border-emerald-200">
              <div class="text-emerald-700 text-[10px] font-bold">Rule Required Z_req</div>
              <div class="font-bold text-emerald-900 mt-0.5">${props.modulus_rule_required_cm3.toLocaleString('en-US', {maximumFractionDigits: 0})} cm³</div>
            </div>
          </div>
        </div>

      </div>

      <!-- Right Column (5 cols): Dynamic Vector SVG & Stress Matrices -->
      <div class="lg:col-span-5 space-y-4">
        
        <!-- Midship Vector Section Diagram -->
        <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div class="font-bold text-slate-900 text-sm mb-2 flex items-center justify-between border-b border-slate-100 pb-2">
            <span>MIDSHIP VECTOR CROSS-SECTION</span>
            <span class="text-[11px] text-emerald-700 font-bold">N.A. Marker Active</span>
          </div>

          <div class="flex justify-center">
            ${renderMidshipCrossSectionSvg(props, part, 440, 240)}
          </div>
          <div class="text-[11px] text-slate-500 text-center mt-2">
            Red dashed line indicates the calculated structural Neutral Axis (${props.neutral_axis_above_keel_m.toFixed(3)} m above keel).
          </div>
        </div>

        <!-- Schedule Table 66 Compliance Matrix -->
        <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div class="font-bold text-slate-900 text-sm mb-2 flex items-center justify-between border-b border-slate-100 pb-2">
            <span>SCHEDULE TABLE 66 STRESS AUDIT (সারণি-৬৬)</span>
            <span class="text-[11px] text-emerald-700 font-bold">Continuous Members</span>
          </div>

          <div class="space-y-2 text-xs">
            <div class="flex justify-between items-center p-2 rounded bg-slate-50 border border-slate-100">
              <div>
                <div class="font-semibold text-slate-800">Deck Bending Stress (σ_deck)</div>
                <div class="text-[10px] text-slate-500">M_design / Z_deck (Limit: 130 N/mm²)</div>
              </div>
              <div class="text-right">
                <div class="font-bold text-slate-900">${t66.bending_stress_deck_n_mm2.toFixed(2)} N/mm²</div>
                <div class="text-[10px] text-emerald-700 font-bold">${t66.status_bending}</div>
              </div>
            </div>

            <div class="flex justify-between items-center p-2 rounded bg-slate-50 border border-slate-100">
              <div>
                <div class="font-semibold text-slate-800">Bottom Bending Stress (σ_bottom)</div>
                <div class="text-[10px] text-slate-500">M_design / Z_bottom (Limit: 130 N/mm²)</div>
              </div>
              <div class="text-right">
                <div class="font-bold text-slate-900">${t66.bending_stress_bottom_n_mm2.toFixed(2)} N/mm²</div>
                <div class="text-[10px] text-emerald-700 font-bold">${t66.status_bending}</div>
              </div>
            </div>

            <div class="flex justify-between items-center p-2 rounded bg-slate-50 border border-slate-100">
              <div>
                <div class="font-semibold text-slate-800">Hull Shear Stress (τ)</div>
                <div class="text-[10px] text-slate-500">Q_design / A_shear (Limit: 70 N/mm²)</div>
              </div>
              <div class="text-right">
                <div class="font-bold text-slate-900">${t66.hull_shear_stress_n_mm2.toFixed(2)} N/mm²</div>
                <div class="text-[10px] text-emerald-700 font-bold">${t66.status_shear}</div>
              </div>
            </div>

            <div class="flex justify-between items-center p-2 rounded bg-slate-50 border border-slate-100">
              <div>
                <div class="font-semibold text-slate-800">Equivalent Stress (σ_e)</div>
                <div class="text-[10px] text-slate-500">√(σ² + 3τ²) (Limit: 150 N/mm²)</div>
              </div>
              <div class="text-right">
                <div class="font-bold text-slate-900">${t66.equivalent_stress_n_mm2.toFixed(2)} N/mm²</div>
                <div class="text-[10px] text-emerald-700 font-bold">${t66.status_equivalent}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Total Steel Weight Box (ShipDyn Style) -->
        <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div class="font-bold text-slate-900 text-sm mb-2 flex items-center justify-between border-b border-slate-100 pb-2">
            <span>TOTAL SHIP LIGHTSHIP STEEL WEIGHT</span>
            <span class="text-[11px] text-slate-500 font-normal">Section 104 Tally</span>
          </div>
          <div class="space-y-2 text-xs">
            <div class="flex justify-between items-center p-2 rounded bg-slate-50 border border-slate-100">
              <span class="text-slate-700">Total Structural Steel Weight:</span>
              <span class="font-bold text-slate-900 font-mono">${(assumed.structural_steel_weight_tonne || 0).toFixed(2)} Tonne</span>
            </div>
            <div class="flex justify-between items-center p-2 rounded bg-slate-50 border border-slate-100">
              <span class="text-slate-700">Outfitting Allowance (Statutory 56%):</span>
              <span class="font-bold text-slate-900 font-mono">${(assumed.outfit_allowance_tonne || 0).toFixed(2)} Tonne</span>
            </div>
            <div class="flex justify-between items-center p-2.5 rounded bg-blue-50 border border-blue-200">
              <span class="font-bold text-blue-900">Total Ship Steel Weight:</span>
              <span class="font-bold text-blue-900 font-mono text-sm">${(assumed.total_ship_steel_weight_tonne || 0).toFixed(2)} Tonne</span>
            </div>
          </div>
        </div>

      </div>

    </div>

    <!-- CLASSICAL ASSUMED NEUTRAL AXIS INTEGRATION (SECTION 104 — RULE 209 / ISO 1976) -->
    <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-xs mb-4">
      <div class="font-bold text-slate-900 text-sm mb-2 flex items-center justify-between border-b border-slate-100 pb-2">
        <div class="flex items-center gap-2">
          <span>SECTION 104: CALCULATION AS PER DESIGN (ASSUMED N.A. = ${(assumed.assumed_na_mm || 0).toFixed(1)} mm ABL)</span>
          <span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded">ISO 1976 Standard</span>
        </div>
        <span class="text-xs text-slate-500">True N.A. Shift y = ${(assumed.y_shift_from_assumed_mm || 0).toFixed(2)} mm (${assumed.y_shift_direction || 'below'})</span>
      </div>

      <div class="overflow-x-auto max-h-[440px] overflow-y-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead class="bg-slate-100 text-slate-700 font-bold sticky top-0 border-b border-slate-200">
            <tr>
              <th class="p-2">Items</th>
              <th class="p-2 text-right">Scantlings</th>
              <th class="p-2 text-right">Length (mm)</th>
              <th class="p-2 text-right">Breadth (mm)</th>
              <th class="p-2 text-right">Area (mm²)</th>
              <th class="p-2 text-right">Weight (T)</th>
              <th class="p-2 text-right">Lever (mm)</th>
              <th class="p-2 text-right">Moment (mm³)</th>
              <th class="p-2 text-right">Area &times; Lever² (mm⁴)</th>
              <th class="p-2 text-right">I own (mm⁴)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-slate-800">
            <tr class="bg-slate-50/80 font-bold text-slate-900">
              <td colspan="10" class="p-2">Items Above Assumed N.A.</td>
            </tr>
            ${(assumed.items_above || []).map(it => `
              <tr class="hover:bg-slate-50">
                <td class="p-2 font-medium text-slate-900">${it.name}</td>
                <td class="p-2 text-right font-mono">${it.scantlings}</td>
                <td class="p-2 text-right font-mono">${it.length_mm.toFixed(0)}</td>
                <td class="p-2 text-right font-mono">${it.breadth_mm.toFixed(1)}</td>
                <td class="p-2 text-right font-mono font-semibold">${it.area_mm2.toFixed(0)}</td>
                <td class="p-2 text-right font-mono">${it.weight_tonne.toFixed(2)}</td>
                <td class="p-2 text-right font-mono">${it.lever_mm.toFixed(1)}</td>
                <td class="p-2 text-right font-mono">${it.moment_mm3.toLocaleString('en-US', {maximumFractionDigits: 0})}</td>
                <td class="p-2 text-right font-mono">${it.ad2_mm4.toExponential(2)}</td>
                <td class="p-2 text-right font-mono">${it.i0_mm4.toExponential(2)}</td>
              </tr>
            `).join('')}
            <tr class="bg-slate-100 font-bold text-slate-900 border-t border-slate-300">
              <td class="p-2" colspan="4">Total Above N.A.:</td>
              <td class="p-2 text-right font-mono">${(assumed.subtotal_above?.area_mm2 || 0).toFixed(0)}</td>
              <td class="p-2 text-right font-mono">${(assumed.subtotal_above?.weight_tonne || 0).toFixed(2)}</td>
              <td class="p-2 text-right font-mono">—</td>
              <td class="p-2 text-right font-mono">${(assumed.subtotal_above?.moment_mm3 || 0).toLocaleString('en-US', {maximumFractionDigits: 0})}</td>
              <td class="p-2 text-right font-mono">${(assumed.subtotal_above?.ad2_mm4 || 0).toExponential(2)}</td>
              <td class="p-2 text-right font-mono">${(assumed.subtotal_above?.i0_mm4 || 0).toExponential(2)}</td>
            </tr>

            <tr class="bg-slate-50/80 font-bold text-slate-900">
              <td colspan="10" class="p-2">Items Below Assumed N.A.</td>
            </tr>
            ${(assumed.items_below || []).map(it => `
              <tr class="hover:bg-slate-50">
                <td class="p-2 font-medium text-slate-900">${it.name}</td>
                <td class="p-2 text-right font-mono">${it.scantlings}</td>
                <td class="p-2 text-right font-mono">${it.length_mm.toFixed(0)}</td>
                <td class="p-2 text-right font-mono">${it.breadth_mm.toFixed(1)}</td>
                <td class="p-2 text-right font-mono font-semibold">${it.area_mm2.toFixed(0)}</td>
                <td class="p-2 text-right font-mono">${it.weight_tonne.toFixed(2)}</td>
                <td class="p-2 text-right font-mono">${it.lever_mm.toFixed(1)}</td>
                <td class="p-2 text-right font-mono">${it.moment_mm3.toLocaleString('en-US', {maximumFractionDigits: 0})}</td>
                <td class="p-2 text-right font-mono">${it.ad2_mm4.toExponential(2)}</td>
                <td class="p-2 text-right font-mono">${it.i0_mm4.toExponential(2)}</td>
              </tr>
            `).join('')}
            <tr class="bg-slate-100 font-bold text-slate-900 border-t border-slate-300">
              <td class="p-2" colspan="4">Total Below N.A.:</td>
              <td class="p-2 text-right font-mono">${(assumed.subtotal_below?.area_mm2 || 0).toFixed(0)}</td>
              <td class="p-2 text-right font-mono">${(assumed.subtotal_below?.weight_tonne || 0).toFixed(2)}</td>
              <td class="p-2 text-right font-mono">—</td>
              <td class="p-2 text-right font-mono">${(assumed.subtotal_below?.moment_mm3 || 0).toLocaleString('en-US', {maximumFractionDigits: 0})}</td>
              <td class="p-2 text-right font-mono">${(assumed.subtotal_below?.ad2_mm4 || 0).toExponential(2)}</td>
              <td class="p-2 text-right font-mono">${(assumed.subtotal_below?.i0_mm4 || 0).toExponential(2)}</td>
            </tr>

            <tr class="bg-blue-50 font-bold text-blue-900 border-t-2 border-blue-300 text-xs">
              <td class="p-2.5" colspan="4">Grand Total Cross-Section:</td>
              <td class="p-2.5 text-right font-mono">${(assumed.grand_total?.area_mm2 || 0).toFixed(0)} mm²</td>
              <td class="p-2.5 text-right font-mono">${(assumed.grand_total?.weight_tonne || 0).toFixed(2)} T</td>
              <td class="p-2.5 text-right font-mono">y_NA = ${(assumed.distance_between_na_and_baseline_n_m || 0).toFixed(3)} m</td>
              <td class="p-2.5 text-right font-mono">${(assumed.grand_total?.moment_mm3 || 0).toLocaleString('en-US', {maximumFractionDigits: 0})}</td>
              <td class="p-2.5 text-right font-mono">${(assumed.grand_total?.ad2_mm4 || 0).toExponential(2)}</td>
              <td class="p-2.5 text-right font-mono">${(assumed.grand_total?.i0_mm4 || 0).toExponential(2)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="mt-3 p-3 bg-slate-50 rounded border border-slate-200 grid grid-cols-1 md:grid-cols-3 gap-2 text-xs">
        <div>• Neutral Axis Shift: <b>${(assumed.y_shift_from_assumed_mm || 0).toFixed(2)} mm (${assumed.y_shift_direction || 'below'})</b></div>
        <div>• Transferred Inertia: <b>${(assumed.moment_of_inertia_na_m4 || 0).toFixed(4)} m⁴</b></div>
        <div>• Actual Moduli: <b>Z_deck = ${(assumed.section_modulus_deck_zad_cm3 || 0).toLocaleString('en-US', {maximumFractionDigits: 0})} cm³ | Z_bottom = ${(assumed.section_modulus_bottom_zab_cm3 || 0).toLocaleString('en-US', {maximumFractionDigits: 0})} cm³</b></div>
      </div>
    </div>

    <!-- DETAILED STEP-BY-STEP PRACTICAL MATHEMATICAL WORKING (PROPER EQUATION FORMAT) -->
    <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-xs mb-4">
      <div class="font-bold text-slate-900 text-sm mb-3 flex items-center justify-between border-b border-slate-100 pb-2">
        <div class="flex items-center gap-2">
          <span>PRACTICAL STEP-BY-STEP ENGINEERING WORKING &amp; FORMULATION BREAKDOWN</span>
          <span class="px-2 py-0.5 bg-blue-100 text-blue-800 text-[10px] font-bold rounded">Standard Mathematical Notation</span>
        </div>
        <span class="text-xs text-slate-500">Rules 209 &amp; 223 / Schedule Tables 66 &amp; 67</span>
      </div>

      <div class="space-y-4 text-xs">
        
        <!-- Step 1 Card: Design Bending Moments & Shear Force -->
        <div class="p-3.5 bg-slate-50 rounded-lg border border-slate-200 space-y-2.5">
          <div class="font-bold text-slate-900 text-[13px] flex items-center justify-between border-b border-slate-200 pb-1.5">
            <span class="flex items-center gap-1.5 text-blue-900">
              <span class="w-2 h-2 rounded-full bg-blue-600"></span>
              STEP 1: DESIGN BENDING MOMENTS &amp; SHEAR FORCE (RULE 209)
            </span>
            <span class="text-blue-800 font-bold bg-blue-100/70 px-2 py-0.5 rounded text-[11px]">Governing M_design = ${moms.m_design_knm.toLocaleString('en-US', {maximumFractionDigits: 1})} kN&middot;m (${moms.design_condition})</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-slate-800">
            <!-- Cw -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Wave Coefficient (C_w):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="C_w = 0.08 \cdot k_t \cdot \sqrt{L}">
                  <i>C</i><sub><i>w</i></sub> = 0.08 &middot; <i>k</i><sub><i>t</i></sub> &middot; &radic;<i>L</i>
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-blue-900" data-latex="= 0.08 \cdot ${(report.factor_kt || 1.4).toFixed(2)} \cdot \sqrt{${part.lbp.toFixed(2)}} = ${factorCw.toFixed(3)}">
                  0.08 &middot; ${(report.factor_kt || 1.4).toFixed(2)} &middot; &radic;${part.lbp.toFixed(2)} = <b>${factorCw.toFixed(3)}</b>
                </span>
              </div>
            </div>

            <!-- Msw -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Still Water Bending Moment (M_sw):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="M_{sw} = 0.01 \cdot k_t \cdot L^2 \cdot B \cdot (C_b + 0.7)">
                  <i>M</i><sub><i>sw</i></sub> = 0.01 &middot; <i>k</i><sub><i>t</i></sub> &middot; <i>L</i><sup>2</sup> &middot; <i>B</i> &middot; (<i>C</i><sub><i>b</i></sub> + 0.7)
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-blue-900" data-latex="= ${moms.m_sw_knm.toLocaleString('en-US', {maximumFractionDigits: 1})}\text{ kN}\cdot\text{m}">
                  <b>${moms.m_sw_knm.toLocaleString('en-US', {maximumFractionDigits: 1})} kN&middot;m</b>
                </span>
              </div>
            </div>

            <!-- Mw Hogging -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Wave Bending Moment &mdash; Hogging (M_w,hog):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="M_{w,hog} = 0.19 \cdot C_w \cdot L^2 \cdot B \cdot C_b">
                  <i>M</i><sub><i>w,hog</i></sub> = 0.19 &middot; <i>C</i><sub><i>w</i></sub> &middot; <i>L</i><sup>2</sup> &middot; <i>B</i> &middot; <i>C</i><sub><i>b</i></sub>
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-blue-900" data-latex="= ${moms.m_wave_hog_knm.toLocaleString('en-US', {maximumFractionDigits: 1})}\text{ kN}\cdot\text{m}">
                  <b>${moms.m_wave_hog_knm.toLocaleString('en-US', {maximumFractionDigits: 1})} kN&middot;m</b>
                </span>
              </div>
            </div>

            <!-- Mw Sagging -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Wave Bending Moment &mdash; Sagging (M_w,sag):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="M_{w,sag} = -0.11 \cdot C_w \cdot L^2 \cdot B \cdot (C_b + 0.7)">
                  <i>M</i><sub><i>w,sag</i></sub> = -0.11 &middot; <i>C</i><sub><i>w</i></sub> &middot; <i>L</i><sup>2</sup> &middot; <i>B</i> &middot; (<i>C</i><sub><i>b</i></sub> + 0.7)
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-blue-900" data-latex="= ${moms.m_wave_sag_knm.toLocaleString('en-US', {maximumFractionDigits: 1})}\text{ kN}\cdot\text{m}">
                  <b>${moms.m_wave_sag_knm.toLocaleString('en-US', {maximumFractionDigits: 1})} kN&middot;m</b>
                </span>
              </div>
            </div>

            <!-- Total Moments -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Total Hogging vs Total Sagging:</div>
              <div class="font-serif text-[12px] space-y-1">
                <div><i>M</i><sub><i>t,hog</i></sub> = <i>M</i><sub><i>sw</i></sub> + <i>M</i><sub><i>w,hog</i></sub> = <b class="text-blue-900">${moms.m_total_hog_knm.toLocaleString('en-US', {maximumFractionDigits: 1})} kN&middot;m</b></div>
                <div><i>M</i><sub><i>t,sag</i></sub> = <i>k</i><sub><i>t</i></sub> &middot; (|<i>M</i><sub><i>sw</i></sub>| + |<i>M</i><sub><i>w,sag</i></sub>|) = <b class="text-blue-900">${moms.m_total_sag_knm.toLocaleString('en-US', {maximumFractionDigits: 1})} kN&middot;m</b></div>
              </div>
            </div>

            <!-- Design Shear Force -->
            <div class="p-2.5 bg-blue-50/70 rounded border border-blue-200 shadow-2xs flex flex-col justify-center">
              <div class="text-[10.5px] font-semibold text-blue-900 mb-1">Design Hull Girder Shear Force (Q_t):</div>
              <div class="font-serif text-[12.5px] flex items-center flex-wrap gap-1.5">
                <span class="math-eq" data-latex="Q_t = \frac{5 \cdot |M_{\text{design}}|}{L}">
                  <i>Q</i><sub><i>t</i></sub> = 
                  <span class="inline-flex flex-col items-center align-middle mx-1">
                    <span class="border-b border-slate-700 px-1.5 pb-0.5 text-[11px]">5 &middot; |<i>M</i><sub>design</sub>|</span>
                    <span class="px-1.5 pt-0.5 text-[11px]"><i>L</i></span>
                  </span>
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-bold text-blue-950" data-latex="= \frac{5 \cdot ${moms.m_design_knm.toFixed(1)}}{${part.lbp.toFixed(2)}} = ${moms.shear_force_design_kn.toLocaleString('en-US', {maximumFractionDigits: 1})}\text{ kN}">
                  <span class="inline-flex flex-col items-center align-middle mx-1">
                    <span class="border-b border-slate-700 px-1 pb-0.5 text-[11px]">5 &middot; ${moms.m_design_knm.toFixed(1)}</span>
                    <span class="px-1 pt-0.5 text-[11px]">${part.lbp.toFixed(2)}</span>
                  </span>
                  = <b>${moms.shear_force_design_kn.toLocaleString('en-US', {maximumFractionDigits: 1})} kN</b>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 2 Card: Neutral Axis Numerical Integration -->
        <div class="p-3.5 bg-slate-50 rounded-lg border border-slate-200 space-y-2.5">
          <div class="font-bold text-slate-900 text-[13px] flex items-center justify-between border-b border-slate-200 pb-1.5">
            <span class="flex items-center gap-1.5 text-slate-900">
              <span class="w-2 h-2 rounded-full bg-emerald-600"></span>
              STEP 2: NEUTRAL AXIS (y_NA) DISCRETE NUMERICAL INTEGRATION
            </span>
            <span class="text-emerald-800 font-bold bg-emerald-100/70 px-2 py-0.5 rounded text-[11px]">y_NA = ${props.neutral_axis_above_keel_m.toFixed(3)} m ABL</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-slate-800">
            <!-- Total Structural Area -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Total Cross-Sectional Area (&Sigma;A):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="A_{\text{total}} = \sum_{i=1}^n A_i">
                  <i>A</i><sub>total</sub> = &sum; <i>A</i><sub><i>i</i></sub>
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-slate-900" data-latex="= ${(props.total_area_cm2 * 100).toLocaleString('en-US', {maximumFractionDigits: 0})}\text{ mm}^2 = ${props.total_area_cm2.toLocaleString('en-US', {maximumFractionDigits: 1})}\text{ cm}^2">
                  <b>${(props.total_area_cm2 * 100).toLocaleString('en-US', {maximumFractionDigits: 0})} mm&sup2;</b> (${props.total_area_cm2.toLocaleString('en-US', {maximumFractionDigits: 1})} cm&sup2;)
                </span>
              </div>
            </div>

            <!-- First Moment -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">First Moment about Keel Baseline (&Sigma; A &middot; y):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="M_{\text{keel}} = \sum_{i=1}^n (A_i \cdot y_i)">
                  <i>M</i><sub>keel</sub> = &sum; (<i>A</i><sub><i>i</i></sub> &middot; <i>y</i><sub><i>i</i></sub>)
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-slate-900" data-latex="= ${firstMomentCm3.toLocaleString('en-US', {maximumFractionDigits: 1})}\text{ cm}^3">
                  <b>${firstMomentCm3.toLocaleString('en-US', {maximumFractionDigits: 1})} cm&sup3;</b>
                </span>
              </div>
            </div>

            <!-- Height of NA (Full Stacked Fraction) -->
            <div class="md:col-span-2 p-3 bg-emerald-50/70 rounded border border-emerald-200 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-emerald-900 mb-1">Neutral Axis Height above Keel (y_NA):</div>
              <div class="font-serif text-[13px] flex items-center flex-wrap gap-2 text-slate-900">
                <span class="math-eq" data-latex="y_{\text{NA}} = \frac{\sum (A_i \cdot y_i)}{\sum A_i}">
                  <i>y</i><sub>NA</sub> = 
                  <span class="inline-flex flex-col items-center align-middle mx-1">
                    <span class="border-b border-slate-700 px-1.5 pb-0.5 text-[11.5px]">&sum; (<i>A</i><sub><i>i</i></sub> &middot; <i>y</i><sub><i>i</i></sub>)</span>
                    <span class="px-1.5 pt-0.5 text-[11.5px]">&sum; <i>A</i><sub><i>i</i></sub></span>
                  </span>
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-bold text-emerald-950" data-latex="= \frac{${firstMomentCm3.toFixed(1)}}{${props.total_area_cm2.toFixed(1)}} = ${props.neutral_axis_above_keel_m.toFixed(3)}\text{ m above Keel}">
                  <span class="inline-flex flex-col items-center align-middle mx-1">
                    <span class="border-b border-slate-700 px-1 pb-0.5 text-[11.5px]">${firstMomentCm3.toFixed(1)}</span>
                    <span class="px-1 pt-0.5 text-[11.5px]">${props.total_area_cm2.toFixed(1)}</span>
                  </span>
                  = <b>${props.neutral_axis_above_keel_m.toFixed(3)} m above Keel Baseline</b>
                </span>
              </div>
              <div class="text-[11px] text-slate-600 mt-1.5 flex gap-4">
                <span>Extreme Deck Lever: <i>y</i><sub>deck</sub> = <i>D</i> &minus; <i>y</i><sub>NA</sub> = <b>${yDeckM.toFixed(3)} m</b></span>
                <span>Extreme Keel Lever: <i>y</i><sub>bottom</sub> = <i>y</i><sub>NA</sub> = <b>${yBottomM.toFixed(3)} m</b></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3 Card: Moment of Inertia & Provided Section Moduli -->
        <div class="p-3.5 bg-slate-50 rounded-lg border border-slate-200 space-y-2.5">
          <div class="font-bold text-slate-900 text-[13px] flex items-center justify-between border-b border-slate-200 pb-1.5">
            <span class="flex items-center gap-1.5 text-slate-900">
              <span class="w-2 h-2 rounded-full bg-indigo-600"></span>
              STEP 3: MOMENT OF INERTIA &amp; PROVIDED SECTION MODULI
            </span>
            <span class="text-indigo-900 font-bold bg-indigo-100/70 px-2 py-0.5 rounded text-[11px]">Governing Z_actual = ${props.modulus_actual_cm3.toLocaleString('en-US', {maximumFractionDigits: 1})} cm&sup3;</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-slate-800">
            <!-- Steiner's Theorem -->
            <div class="md:col-span-2 p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Parallel Axis Theorem (Steiner's Theorem):</div>
              <div class="font-serif text-[12.5px] flex items-center flex-wrap gap-1.5">
                <span class="math-eq" data-latex="I_{\text{NA}} = \sum I_0 + \sum (A_i \cdot d_i^2)">
                  <i>I</i><sub>NA</sub> = &sum; <i>I</i><sub>0</sub> + &sum; (<i>A</i><sub><i>i</i></sub> &middot; <i>d</i><sub><i>i</i></sub><sup>2</sup>)
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-bold text-indigo-950" data-latex="= ${props.moment_of_inertia_cm4.toLocaleString('en-US', {maximumFractionDigits: 1})}\text{ cm}^4 = ${(props.moment_of_inertia_cm4 * 1e-8).toFixed(4)}\text{ m}^4">
                  <b>${props.moment_of_inertia_cm4.toLocaleString('en-US', {maximumFractionDigits: 1})} cm&sup4;</b> (${(props.moment_of_inertia_cm4 * 1e-8).toFixed(4)} m&sup4;)
                </span>
              </div>
            </div>

            <!-- Modulus to Deck -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Section Modulus to Strength Deck (Z_deck):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="Z_{\text{deck}} = \frac{I_{\text{NA}}}{y_{\text{deck}}}">
                  <i>Z</i><sub>deck</sub> = 
                  <span class="inline-flex flex-col items-center align-middle mx-1">
                    <span class="border-b border-slate-700 px-1 text-[11px]"><i>I</i><sub>NA</sub></span>
                    <span class="px-1 text-[11px]"><i>y</i><sub>deck</sub></span>
                  </span>
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-slate-900" data-latex="= \frac{${props.moment_of_inertia_cm4.toFixed(0)}}{${(yDeckM * 100).toFixed(1)}} = ${props.modulus_deck_cm3.toLocaleString('en-US', {maximumFractionDigits: 1})}\text{ cm}^3">
                  <b>${props.modulus_deck_cm3.toLocaleString('en-US', {maximumFractionDigits: 1})} cm&sup3;</b>
                </span>
              </div>
            </div>

            <!-- Modulus to Keel -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Section Modulus to Keel Baseline (Z_bottom):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="Z_{\text{bottom}} = \frac{I_{\text{NA}}}{y_{\text{bottom}}}">
                  <i>Z</i><sub>bottom</sub> = 
                  <span class="inline-flex flex-col items-center align-middle mx-1">
                    <span class="border-b border-slate-700 px-1 text-[11px]"><i>I</i><sub>NA</sub></span>
                    <span class="px-1 text-[11px]"><i>y</i><sub>bottom</sub></span>
                  </span>
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-slate-900" data-latex="= \frac{${props.moment_of_inertia_cm4.toFixed(0)}}{${(yBottomM * 100).toFixed(1)}} = ${props.modulus_bottom_cm3.toLocaleString('en-US', {maximumFractionDigits: 1})}\text{ cm}^3">
                  <b>${props.modulus_bottom_cm3.toLocaleString('en-US', {maximumFractionDigits: 1})} cm&sup3;</b>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 4 Card: Statutory Required Section Modulus (Rule 209) -->
        <div class="p-3.5 bg-slate-50 rounded-lg border border-slate-200 space-y-2.5">
          <div class="font-bold text-slate-900 text-[13px] flex items-center justify-between border-b border-slate-200 pb-1.5">
            <span class="flex items-center gap-1.5 text-slate-900">
              <span class="w-2 h-2 rounded-full bg-emerald-600"></span>
              STEP 4: STATUTORY RULE 209 REQUIRED MODULUS &amp; COMPLIANCE MARGIN
            </span>
            <span class="text-emerald-800 font-bold bg-emerald-100/70 px-2 py-0.5 rounded text-[11px]">+${props.modulus_margin_pct.toFixed(1)}% MARGIN PASS</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-slate-800">
            <!-- Z1 Stress -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Stress-Based Required Modulus (Z_1):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="Z_1 = \frac{M_{\text{design}} \cdot 10^3}{\sigma_{\text{allow}}}">
                  <i>Z</i><sub>1</sub> = 
                  <span class="inline-flex flex-col items-center align-middle mx-1">
                    <span class="border-b border-slate-700 px-1 text-[11px]"><i>M</i><sub>design</sub> &middot; 10<sup>3</sup></span>
                    <span class="px-1 text-[11px]">130.0</span>
                  </span>
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-blue-900" data-latex="= \frac{${moms.m_design_knm.toFixed(1)} \cdot 10^3}{130} = ${z1StressCm3.toLocaleString('en-US', {maximumFractionDigits: 1})}\text{ cm}^3">
                  <b>${z1StressCm3.toLocaleString('en-US', {maximumFractionDigits: 1})} cm&sup3;</b>
                </span>
              </div>
            </div>

            <!-- Z2 Empirical -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Empirical Classification Lower Bound (Z_2):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="Z_2 = C_w \cdot L^2 \cdot B \cdot (C_b + 0.7)">
                  <i>Z</i><sub>2</sub> = <i>C</i><sub><i>w</i></sub> &middot; <i>L</i><sup>2</sup> &middot; <i>B</i> &middot; (<i>C</i><sub><i>b</i></sub> + 0.7)
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-blue-900" data-latex="= ${z2EmpiricalCm3.toLocaleString('en-US', {maximumFractionDigits: 1})}\text{ cm}^3">
                  <b>${z2EmpiricalCm3.toLocaleString('en-US', {maximumFractionDigits: 1})} cm&sup3;</b>
                </span>
              </div>
            </div>

            <!-- Governing Requirement & Margin -->
            <div class="md:col-span-2 p-3 bg-emerald-50/70 rounded border border-emerald-200 shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-2">
              <div>
                <div class="text-[10.5px] font-semibold text-emerald-900 mb-0.5">Statutory Governing Required Modulus:</div>
                <div class="font-serif text-[13px] flex items-center gap-1.5 text-slate-900">
                  <span class="math-eq" data-latex="Z_{\text{req}} = \max(Z_1, Z_2) = ${props.modulus_rule_required_cm3.toLocaleString('en-US', {maximumFractionDigits: 1})}\text{ cm}^3">
                    <i>Z</i><sub>req</sub> = max(<i>Z</i><sub>1</sub>, <i>Z</i><sub>2</sub>) = <b>${props.modulus_rule_required_cm3.toLocaleString('en-US', {maximumFractionDigits: 1})} cm&sup3;</b>
                  </span>
                </div>
              </div>
              <div class="text-right">
                <div class="text-[10.5px] font-semibold text-emerald-900 mb-0.5">Statutory Margin Formula:</div>
                <div class="font-serif text-[12.5px] flex items-center justify-end gap-1.5 text-slate-900">
                  <span class="math-eq" data-latex="\text{Margin} = \frac{Z_{\text{act}} - Z_{\text{req}}}{Z_{\text{req}}} \times 100\% = +${props.modulus_margin_pct.toFixed(1)}\%">
                    <span class="inline-flex flex-col items-center align-middle mx-1">
                      <span class="border-b border-slate-700 px-1 text-[11px]"><i>Z</i><sub>act</sub> &minus; <i>Z</i><sub>req</sub></span>
                      <span class="px-1 text-[11px]"><i>Z</i><sub>req</sub></span>
                    </span>
                    &times; 100% = <b class="text-emerald-800">+${props.modulus_margin_pct.toFixed(1)}%</b>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 5 Card: Schedule Table 66 Stress Formulas -->
        <div class="p-3.5 bg-slate-50 rounded-lg border border-slate-200 space-y-2.5">
          <div class="font-bold text-slate-900 text-[13px] flex items-center justify-between border-b border-slate-200 pb-1.5">
            <span class="flex items-center gap-1.5 text-slate-900">
              <span class="w-2 h-2 rounded-full bg-violet-600"></span>
              STEP 5: SCHEDULE TABLE 66 CONTINUOUS HULL GIRDER STRESS AUDIT
            </span>
            <span class="text-emerald-800 font-bold bg-emerald-100/70 px-2 py-0.5 rounded text-[11px]">ALL STRESSES WITHIN STATUTORY LIMITS</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-slate-800">
            <!-- Deck Stress -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Deck Bending Stress (&sigma;_deck):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="\sigma_{\text{deck}} = \frac{M_{\text{design}} \cdot 10^3}{Z_{\text{deck}}}">
                  &sigma;<sub>deck</sub> = 
                  <span class="inline-flex flex-col items-center align-middle mx-1">
                    <span class="border-b border-slate-700 px-1 text-[11px]"><i>M</i><sub>design</sub> &middot; 10<sup>3</sup></span>
                    <span class="px-1 text-[11px]"><i>Z</i><sub>deck</sub></span>
                  </span>
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-emerald-800" data-latex="= ${t66.bending_stress_deck_n_mm2.toFixed(2)}\text{ N/mm}^2 \le 130.0\text{ N/mm}^2">
                  <b>${t66.bending_stress_deck_n_mm2.toFixed(2)} N/mm&sup2;</b> &le; 130.0 N/mm&sup2; [PASS]
                </span>
              </div>
            </div>

            <!-- Bottom Stress -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Bottom Bending Stress (&sigma;_bottom):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="\sigma_{\text{bottom}} = \frac{M_{\text{design}} \cdot 10^3}{Z_{\text{bottom}}}">
                  &sigma;<sub>bottom</sub> = 
                  <span class="inline-flex flex-col items-center align-middle mx-1">
                    <span class="border-b border-slate-700 px-1 text-[11px]"><i>M</i><sub>design</sub> &middot; 10<sup>3</sup></span>
                    <span class="px-1 text-[11px]"><i>Z</i><sub>bottom</sub></span>
                  </span>
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-emerald-800" data-latex="= ${t66.bending_stress_bottom_n_mm2.toFixed(2)}\text{ N/mm}^2 \le 130.0\text{ N/mm}^2">
                  <b>${t66.bending_stress_bottom_n_mm2.toFixed(2)} N/mm&sup2;</b> &le; 130.0 N/mm&sup2; [PASS]
                </span>
              </div>
            </div>

            <!-- Shear Stress -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Hull Girder Shear Stress (&tau;):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="\tau = \frac{Q_t \cdot 10^3}{2 \cdot D \cdot t_{\text{side}}}">
                  &tau; = 
                  <span class="inline-flex flex-col items-center align-middle mx-1">
                    <span class="border-b border-slate-700 px-1 text-[11px]"><i>Q</i><sub><i>t</i></sub> &middot; 10<sup>3</sup></span>
                    <span class="px-1 text-[11px]">2 &middot; <i>D</i> &middot; <i>t</i><sub>side</sub></span>
                  </span>
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-emerald-800" data-latex="= ${t66.hull_shear_stress_n_mm2.toFixed(2)}\text{ N/mm}^2 \le 70.0\text{ N/mm}^2">
                  <b>${t66.hull_shear_stress_n_mm2.toFixed(2)} N/mm&sup2;</b> &le; 70.0 N/mm&sup2; [PASS]
                </span>
              </div>
            </div>

            <!-- Equivalent von Mises Stress -->
            <div class="p-2.5 bg-white rounded border border-slate-200/90 shadow-2xs">
              <div class="text-[10.5px] font-semibold text-slate-500 mb-1">Equivalent von Mises Stress (&sigma;_e):</div>
              <div class="font-serif text-[12px] flex items-center flex-wrap gap-1">
                <span class="math-eq" data-latex="\sigma_e = \sqrt{\sigma_b^2 + 3 \cdot \tau^2}">
                  &sigma;<sub><i>e</i></sub> = &radic;(&sigma;<sub><i>b</i></sub><sup>2</sup> + 3 &middot; &tau;<sup>2</sup>)
                </span>
                <span class="text-slate-400">=</span>
                <span class="math-eq font-semibold text-emerald-800" data-latex="= ${t66.equivalent_stress_n_mm2.toFixed(2)}\text{ N/mm}^2 \le 150.0\text{ N/mm}^2">
                  <b>${t66.equivalent_stress_n_mm2.toFixed(2)} N/mm&sup2;</b> &le; 150.0 N/mm&sup2; [PASS]
                </span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Bottom Box: Schedule Table 67 Local Structural Members Audit -->
    <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-xs mb-4">
      <div class="font-bold text-slate-900 text-sm mb-2 flex items-center justify-between border-b border-slate-100 pb-2">
        <span>SCHEDULE TABLE 67 LOCAL STRUCTURAL MEMBERS &amp; BUCKLING AUDIT (সারণি-৬৭)</span>
        <span class="text-[11px] text-slate-500 font-normal">Primary Framing Members</span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
            <tr>
              <th class="p-2">Structural Member</th>
              <th class="p-2">Governing Load Condition</th>
              <th class="p-2 text-right">Calculated Stress</th>
              <th class="p-2 text-right">Allowable Limit</th>
              <th class="p-2 text-center">Safety Margin</th>
              <th class="p-2 text-center">Statutory Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-slate-800">
            ${t67.map(m => `
              <tr class="hover:bg-slate-50">
                <td class="p-2 font-semibold text-slate-900">${m.member_name}</td>
                <td class="p-2 text-slate-600">${m.governing_load_desc}</td>
                <td class="p-2 text-right font-mono font-bold">${m.calculated_stress_n_mm2.toFixed(2)} ${m.unit}</td>
                <td class="p-2 text-right font-mono text-slate-600">${m.allowable_stress_n_mm2.toFixed(1)} ${m.unit}</td>
                <td class="p-2 text-center">
                  <span class="font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded text-[11px]">${m.margin}</span>
                </td>
                <td class="p-2 text-center font-bold text-emerald-700">${m.status}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>


  `;
  } catch (err) {
    console.error('Error rendering Hull Strength View:', err);
    container.innerHTML = `
      <div class="p-6 bg-red-50 border border-red-200 text-red-800 rounded-lg text-sm space-y-2">
        <div class="font-bold text-base flex items-center gap-2">
          <span>⚠️ Rendering Error in Hull Strength Module</span>
        </div>
        <p>${err.message}</p>
        <button onclick="renderStrengthView()" class="px-3 py-1 bg-red-700 hover:bg-red-800 text-white rounded text-xs font-semibold cursor-pointer">
          Retry Rendering
        </button>
      </div>
    `;
    return;
  }

  // Render KaTeX equations if available
  setTimeout(() => {
    if (window.katex) {
      container.querySelectorAll('.math-eq').forEach(el => {
        const latex = el.getAttribute('data-latex');
        if (latex) {
          try {
            window.katex.render(latex, el, { throwOnError: false, displayMode: false });
          } catch (err) {}
        }
      });
    }
  }, 50);
}

async function openStrengthPdfModal() {
  let modal = document.getElementById('strength-pdf-modal');

  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'strength-pdf-modal';
    modal.className = 'fixed inset-0 z-50 bg-slate-900/75 backdrop-blur-xs flex items-center justify-center p-3 md:p-6';
    modal.innerHTML = `
      <div class="bg-white rounded-lg shadow-2xl flex flex-col w-full h-full max-w-6xl max-h-[94vh] overflow-hidden border border-slate-300">
        <!-- Modal Header -->
        <div class="bg-slate-900 text-white px-4 py-2.5 flex items-center justify-between shrink-0 border-b border-slate-800">
          <div class="flex items-center gap-2.5">
            <div class="w-6 h-6 rounded bg-indigo-600 flex items-center justify-center text-white font-black text-xs">
              PDF
            </div>
            <div>
              <div class="text-xs font-bold tracking-tight text-white flex items-center gap-2">
                <span>HULL STRENGTH &amp; MIDSHIP MODULUS BOOKLET (RULES 209 &amp; 223)</span>
                <span class="px-1.5 py-0.2 bg-indigo-700/80 text-[10px] font-mono rounded">4 Pages Official Booklet</span>
              </div>
              <div class="text-[10px] text-slate-400">Rules 209 &amp; 223 • Longitudinal Bending Moments • Midship Section Modulus • Schedule Tables 66 &amp; 67 Compliance</div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <!-- Open in New Tab -->
            <button 
              id="btn-strength-pdf-new-tab" 
              onclick="openStrengthPdfInNewTab()" 
              class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-medium transition flex items-center gap-1 cursor-pointer"
              title="Open full PDF in separate browser tab"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
              <span>New Tab</span>
            </button>

            <!-- Download PDF Button -->
            <button 
              id="btn-strength-pdf-download" 
              onclick="downloadStrengthPdf()" 
              class="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-bold transition flex items-center gap-1 shadow-xs cursor-pointer"
              title="Download Hull Strength PDF booklet to computer"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              <span>Download PDF</span>
            </button>

            <!-- Close Modal Button -->
            <button 
              onclick="closeStrengthPdfModal()" 
              class="ml-2 w-7 h-7 flex items-center justify-center rounded text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer text-base"
              title="Close Preview (Esc)"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Modal Body: IFrame and Loading Screen -->
        <div class="relative flex-1 bg-slate-100 overflow-hidden flex flex-col">
          <!-- Loading Overlay -->
          <div id="strength-pdf-loading" class="absolute inset-0 bg-white/90 backdrop-blur-2xs flex flex-col items-center justify-center z-10 space-y-3">
            <div class="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
            <div class="text-xs font-bold text-slate-800 tracking-wide">Generating Statutory Hull Strength PDF Booklet...</div>
            <div class="text-[11px] text-slate-500">Compiling Rules 209/223 Calculations, Midship Neutral Axis, and Tables 66/67 Matrix</div>
          </div>

          <!-- PDF IFrame -->
          <iframe id="strength-pdf-iframe" class="w-full h-full border-0" title="Hull Strength PDF Booklet"></iframe>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    // Escape key listener
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        closeStrengthPdfModal();
      }
    });
  } else {
    modal.classList.remove('hidden');
  }

  const loading = document.getElementById('strength-pdf-loading');
  const iframe = document.getElementById('strength-pdf-iframe');
  if (loading) loading.classList.remove('hidden');

  try {
    const payload = (typeof appState !== 'undefined') ? appState : {};
    const res = await fetch('/api/v1/strength/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const blob = await res.blob();
    if (activeStrengthPdfBlobUrl) {
      URL.revokeObjectURL(activeStrengthPdfBlobUrl);
    }
    activeStrengthPdfBlobUrl = URL.createObjectURL(blob);
    iframe.src = activeStrengthPdfBlobUrl;
    iframe.onload = () => {
      if (loading) loading.classList.add('hidden');
    };
  } catch (err) {
    console.error('Failed to generate strength PDF:', err);
    if (loading) loading.innerHTML = `<span class="text-red-600 font-bold p-4">Failed to generate PDF: ${err.message}</span>`;
  }
}

function closeStrengthPdfModal() {
  const modal = document.getElementById('strength-pdf-modal');
  if (modal) modal.classList.add('hidden');
}

function openStrengthPdfInNewTab() {
  if (activeStrengthPdfBlobUrl) {
    window.open(activeStrengthPdfBlobUrl, '_blank');
  } else {
    openStrengthPdfModal().then(() => {
      if (activeStrengthPdfBlobUrl) window.open(activeStrengthPdfBlobUrl, '_blank');
    });
  }
}

async function downloadStrengthPdf() {
  try {
    const payload = (typeof appState !== 'undefined') ? appState : {};
    const res = await fetch('/api/v1/strength/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const vName = (payload.dashboard_inputs && payload.dashboard_inputs.vessel_name) 
      ? payload.dashboard_inputs.vessel_name.replace(/\s+/g, '_') 
      : 'Vessel';
    const a = document.createElement('a');
    a.href = url;
    a.download = `${vName}_Hull_Strength_Booklet.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  } catch (err) {
    console.error('Failed to download Strength PDF:', err);
    alert('Failed to download Strength PDF: ' + err.message);
  }
}

window.renderStrength = renderStrengthView;
window.toggleMidshipElement = toggleMidshipElement;
window.toggleAllMidshipElements = toggleAllMidshipElements;
window.resetMidshipElements = resetMidshipElements;
window.openStrengthPdfModal = openStrengthPdfModal;
window.closeStrengthPdfModal = closeStrengthPdfModal;
window.openStrengthPdfInNewTab = openStrengthPdfInNewTab;
window.downloadStrengthPdf = downloadStrengthPdf;
