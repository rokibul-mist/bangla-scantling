/**
 * CalcBrainView - Renders Statutory Calculation Brain & Math Derivations Drawer
 * Displays dynamic table interpolations with live bounding rows, columns, and node badges.
 */

let calcBrainSearchQuery = '';
let calcBrainGroupFilter = 'ALL';
let calcBrainExpandAll = false;

function cleanText(str) {
  if (str === null || str === undefined) return '';
  return String(str).replace(/\*\*/g, '').replace(/\$/g, '').trim();
}

function renderDerivationTable(derivation) {
  if (!derivation || !derivation.table_view) return '';
  const tv = derivation.table_view;
  if (!tv.headers || !tv.rows || tv.rows.length === 0) return '';

  const activeRows = new Set(tv.active_row_indices || []);
  const activeCol = tv.active_col_index;
  const activeCols = new Set(tv.active_col_indices && tv.active_col_indices.length > 0 ? tv.active_col_indices : (activeCol !== null && activeCol !== undefined ? [activeCol] : []));
  const boundingMap = new Map();
  (tv.bounding_cells || []).forEach(bc => {
    boundingMap.set(`${bc.row}:${bc.col}`, bc.val);
  });

  return `
    <div class="mt-3 pt-3 border-t border-slate-200">
      <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
        <div class="flex items-center gap-2">
          <span class="font-bold text-slate-800 text-xs">Statutory Empirical Table:</span>
          <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-blue-100 text-blue-800 border border-blue-300">
            ${cleanText(tv.table_no)}: ${cleanText(tv.title)}
          </span>
          <span class="text-[11px] text-slate-500 font-mono">(${cleanText(tv.ref) || 'Statutory Schedule'})</span>
        </div>
        <div class="flex items-center gap-3 text-[10.5px]">
          <span class="inline-flex items-center gap-1.5 text-amber-900 font-medium">
            <span class="w-3 h-3 rounded bg-amber-200 border border-amber-400 inline-block"></span> Bounding Rows
          </span>
          <span class="inline-flex items-center gap-1.5 text-blue-900 font-medium">
            <span class="w-3 h-3 rounded bg-blue-100 border border-blue-300 inline-block"></span> Active Parameter Col
          </span>
          <span class="inline-flex items-center gap-1.5 text-amber-900 font-bold">
            <span class="px-1.5 py-0.2 bg-amber-500 text-white rounded text-[9px] font-mono">Node</span> Interpolation Point
          </span>
        </div>
      </div>

      <div class="overflow-x-auto max-h-64 border border-slate-300 rounded shadow-inner bg-white">
        <table class="w-full text-left text-[11px] border-collapse font-mono">
          <thead class="sticky top-0 bg-slate-100 text-slate-700 font-semibold border-b border-slate-300 shadow-xs z-10">
            <tr>
              ${tv.headers.map((h, cIdx) => {
                const isColActive = activeCols.has(cIdx);
                return `
                  <th class="px-2.5 py-1.5 whitespace-nowrap border-r border-slate-200 ${isColActive ? 'bg-blue-100 text-blue-900 font-bold border-b-2 border-blue-500' : 'bg-slate-100'}">
                    ${cleanText(h)}
                  </th>
                `;
              }).join('')}
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200">
            ${tv.rows.map((row, rIdx) => {
              const isRowActive = activeRows.has(rIdx);
              return `
                <tr class="${isRowActive ? 'bg-amber-100/90 font-bold border-l-4 border-amber-500 text-amber-950' : (rIdx % 2 === 1 ? 'bg-slate-50/70 hover:bg-slate-100/80' : 'bg-white hover:bg-slate-50')} transition-colors">
                  ${row.map((cell, cIdx) => {
                    const isColActive = activeCols.has(cIdx);
                    const cellKey = `${rIdx}:${cIdx}`;
                    const isBounding = boundingMap.has(cellKey);
                    return `
                      <td class="px-2.5 py-1 whitespace-nowrap border-r border-slate-200 ${isBounding ? 'bg-amber-200 text-amber-950 font-black ring-1 ring-amber-400' : (isRowActive ? '' : (isColActive ? 'bg-blue-50/50 text-blue-950 font-semibold' : ''))}">
                        ${isBounding ? `
                          <div class="inline-flex items-center gap-1.5">
                            <span>${cleanText(cell)}</span>
                            <span class="px-1 py-0.2 bg-amber-600 text-white rounded text-[9px] font-bold shadow-xs">Node</span>
                          </div>
                        ` : cleanText(cell)}
                      </td>
                    `;
                  }).join('')}
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>

      ${tv.notes ? `
        <div class="mt-1.5 text-[10.5px] text-slate-600 bg-slate-50 p-2 rounded border border-slate-200">
          <span class="font-bold text-slate-700">Statutory Notes:</span> ${Array.isArray(tv.notes) ? tv.notes.map(cleanText).join(' • ') : cleanText(tv.notes)}
        </div>
      ` : ''}
    </div>
  `;
}

function toggleCalcBrainDerivation(id) {
  const row = document.getElementById(`derivation-row-${id}`);
  const btn = document.getElementById(`btn-derivation-${id}`);
  if (!row) return;
  const tableCont = document.getElementById('calc-brain-table-container');
  if (tableCont) tableCont.scrollLeft = 0;
  const isHidden = row.classList.contains('hidden');
  if (isHidden) {
    row.classList.remove('hidden');
    if (btn) {
      btn.innerHTML = 'Details ▴';
      btn.classList.add('bg-blue-600', 'text-white', 'border-blue-600');
      btn.classList.remove('bg-blue-50', 'text-blue-700', 'border-blue-200');
    }
  } else {
    row.classList.add('hidden');
    if (btn) {
      btn.innerHTML = 'Details ▾';
      btn.classList.remove('bg-blue-600', 'text-white', 'border-blue-600');
      btn.classList.add('bg-blue-50', 'text-blue-700', 'border-blue-200');
    }
  }
}

function setCalcBrainExpandAll(expand) {
  calcBrainExpandAll = expand;
  const rows = document.querySelectorAll('[id^="derivation-row-"]');
  rows.forEach(r => {
    if (expand) r.classList.remove('hidden');
    else r.classList.add('hidden');
  });
  const btns = document.querySelectorAll('[id^="btn-derivation-"]');
  btns.forEach(b => {
    b.innerHTML = expand ? 'Details ▴' : 'Details ▾';
    if (expand) {
      b.classList.add('bg-blue-600', 'text-white', 'border-blue-600');
      b.classList.remove('bg-blue-50', 'text-blue-700', 'border-blue-200');
    } else {
      b.classList.remove('bg-blue-600', 'text-white', 'border-blue-600');
      b.classList.add('bg-blue-50', 'text-blue-700', 'border-blue-200');
    }
  });
  const expBtn = document.getElementById('btn-calc-expand-all');
  if (expBtn) {
    expBtn.innerHTML = expand ? '▼ Collapse All Derivations' : '▶ Expand All Derivations';
    expBtn.className = expand
      ? 'px-2.5 py-1 text-xs border border-blue-600 bg-blue-50 text-blue-700 rounded font-semibold'
      : 'px-2.5 py-1 text-xs border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 rounded font-medium';
  }
}

function onCalcBrainGroupFilter(val) {
  calcBrainGroupFilter = val;
  renderCalcBrain();
}

function onCalcBrainSearch(query) {
  calcBrainSearchQuery = (query || '').toLowerCase().trim();
  renderCalcBrain();
}

function renderCalcBrain() {
  const container = document.getElementById('tab-content-calc-brain');
  if (!container) return;

  const brain = appState.calculation_brain || [];
  const stats = appState.summary_stats || {};
  const inputs = appState.dashboard_inputs || {};

  // Extract distinct groups for dropdown
  const allGroups = [];
  brain.forEach(b => {
    const g = b.category || b.group;
    if (g && !allGroups.includes(g)) allGroups.push(g);
  });

  // Filter items
  const filtered = brain.filter(b => {
    const g = b.category || b.group;
    if (calcBrainGroupFilter !== 'ALL' && g !== calcBrainGroupFilter) return false;
    if (calcBrainSearchQuery) {
      const q = calcBrainSearchQuery.toLowerCase();
      const matchDesc = (b.name || b.desc || '').toLowerCase().includes(q);
      const matchRule = (b.rule || b.table_ref || '').toLowerCase().includes(q);
      const matchFormula = (b.formula || '').toLowerCase().includes(q);
      const matchGroup = (b.category || b.group || '').toLowerCase().includes(q);
      const itemStr = String(b.item || b.id || '').toLowerCase();
      if (!matchDesc && !matchRule && !matchFormula && !matchGroup && itemStr !== q) return false;
    }
    return true;
  });

  container.innerHTML = `
    <!-- Top Controls & Summary Bar -->
    <div class="bg-white p-3 rounded border border-slate-200 mb-4 flex flex-wrap items-center justify-between gap-3 shadow-sm">
      <div class="flex items-center gap-2.5">
        <div class="compact-title compact-title-primary mb-0">STATUTORY AUDIT & CALCULATION BRAIN (RULES 8 - 147)</div>
        <span class="text-xs text-slate-500">Showing <b>${filtered.length}</b> of <b>${brain.length}</b> Components</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="badge-comp text-xs px-3 py-1 font-bold">${stats.compliant_items || brain.length} / ${stats.total_items || brain.length} COMPLIANT (${stats.compliance_pct || 100}%)</span>
        <button id="btn-calc-expand-all" onclick="setCalcBrainExpandAll(!calcBrainExpandAll)" class="px-2.5 py-1 text-xs border ${calcBrainExpandAll ? 'border-blue-600 bg-blue-50 text-blue-700 font-semibold' : 'border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-medium'} rounded transition-colors">
          ${calcBrainExpandAll ? '▼ Collapse All Derivations' : '▶ Expand All Derivations'}
        </button>
      </div>
    </div>

    <!-- Filter & Search Toolbar -->
    <div class="bg-white p-2.5 rounded border border-slate-200 mb-4 flex flex-wrap items-center justify-between gap-2.5 shadow-sm">
      <div class="flex items-center gap-2 flex-1 min-w-[280px]">
        <span class="text-xs font-semibold text-slate-700 whitespace-nowrap">Filter Group:</span>
        <select id="calc-brain-group-select" onchange="onCalcBrainGroupFilter(this.value)" class="border border-slate-300 rounded px-2.5 py-1 text-xs text-slate-800 bg-slate-50 hover:bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 max-w-[340px] truncate">
          <option value="ALL" ${calcBrainGroupFilter === 'ALL' ? 'selected' : ''}>All Statutory Groups (${brain.length} Components)</option>
          ${allGroups.map((g) => `
            <option value="${g}" ${calcBrainGroupFilter === g ? 'selected' : ''}>${(g || '').split('(')[0].replace(/GROUP \d+:\s*/i, '').trim()}</option>
          `).join('')}
        </select>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-xs font-semibold text-slate-700 whitespace-nowrap">Search:</span>
        <div class="relative">
          <input 
            type="text" 
            placeholder="Search rule (e.g. Table 1, Table 13), component..." 
            value="${calcBrainSearchQuery}"
            oninput="onCalcBrainSearch(this.value)"
            class="border border-slate-300 rounded px-2.5 py-1 text-xs text-slate-800 w-72 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          ${calcBrainSearchQuery ? `
            <button onclick="onCalcBrainSearch('')" class="absolute right-2 top-1 text-xs text-slate-400 hover:text-slate-600">×</button>
          ` : ''}
        </div>
      </div>
    </div>

    <!-- Main Scantling Audit Table with Mathematical Derivations (Unnumbered) -->
    <div id="calc-brain-table-container" class="bg-white p-3 rounded border border-slate-200 overflow-x-auto shadow-sm">
      <table class="compact-table w-full">
        <thead>
          <tr>
            <th style="min-width: 180px;">Component / Structural Member</th>
            <th style="width: 85px;" class="text-center">Rule Ref</th>
            <th style="width: 95px;" class="text-center">Table Ref</th>
            <th style="min-width: 180px;">Governing Formula</th>
            <th style="width: 65px;" class="text-right">Baseline</th>
            <th style="width: 45px;" class="text-center">Factor</th>
            <th style="width: 70px;" class="text-right">Required</th>
            <th style="width: 70px;" class="text-right">Provided</th>
            <th style="width: 35px;" class="text-center">Unit</th>
            <th style="width: 60px;" class="text-right">Margin</th>
            <th style="width: 80px;" class="text-center">Status</th>
            <th style="width: 85px;" class="text-center">Derivation</th>
          </tr>
        </thead>
        <tbody>
          ${filtered.length === 0 ? `
            <tr>
              <td colspan="12" class="text-center py-6 text-slate-500 italic">No statutory components match your filter criteria.</td>
            </tr>
          ` : filtered.map(b => {
            const isComp = b.status === 'COMPLIANT';
            const deriv = b.derivation || null;

            return `
              <!-- Main Row -->
              <tr class="hover:bg-slate-50/80 transition-colors border-b border-slate-100">
                <td class="font-medium text-slate-800">
                  <div class="font-semibold text-slate-900">${b.name || b.desc || ''}</div>
                  <div class="text-[10px] text-slate-400 font-normal truncate max-w-xs" title="${b.category || b.group || ''}">${(b.category || b.group || '').split('(')[0].replace(/GROUP \d+:\s*/i, '').trim()}</div>
                </td>
                <td class="text-center">
                  <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-bold bg-blue-50 text-blue-700 border border-blue-200 whitespace-nowrap">
                    ${b.table_ref || b.rule || 'Rule 8'}
                  </span>
                </td>
                <td class="text-center">
                  <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-bold ${b.table_ref ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-slate-50 text-slate-600 border border-slate-200'} whitespace-nowrap">
                    ${b.table_ref ? b.table_ref : (deriv?.table_no || 'Direct Rule')}
                  </span>
                </td>
                <td>
                  <code class="font-mono text-[11px] text-slate-800 bg-slate-50 px-1 py-0.5 rounded border border-slate-200 block truncate max-w-xs" title="${deriv?.formula_desc || b.notes || b.formula || ''}">
                    ${deriv?.formula_desc || b.notes || b.formula || 'Statutory rule baseline'}
                  </code>
                </td>
                <td class="text-right font-mono text-[11.5px] text-slate-600">${typeof b.baseline === 'number' ? b.baseline.toFixed(2) : (b.baseline || '-')}</td>
                <td class="text-center font-mono font-bold text-[11.5px] text-blue-700">${typeof b.factor === 'number' ? b.factor.toFixed(2) : (b.factor || (deriv && deriv.factor ? (typeof deriv.factor === 'number' ? deriv.factor.toFixed(2) : deriv.factor) : '1.00'))}</td>
                <td class="text-right font-mono font-medium text-[11.5px] text-slate-800">${typeof b.rreq === 'number' ? b.rreq.toFixed(2) : (b.rreq || '-')}</td>
                <td class="text-right font-mono font-bold text-[11.5px] text-slate-900">${typeof b.dact === 'number' ? b.dact.toFixed(2) : (b.dact || '-')}</td>
                <td class="text-center text-[10.5px] font-mono text-slate-500">${b.unit || ''}</td>
                <td class="text-right font-mono text-[11.5px] font-semibold ${isComp ? 'text-emerald-700' : 'text-rose-700'}">
                  ${typeof b.margin === 'number' ? (b.margin >= 0 ? '+' : '') + b.margin.toFixed(2) : (b.margin || '')}
                </td>
                <td class="text-center">
                  <span class="${isComp ? 'badge-comp' : 'badge-def'}">
                    ${b.status}
                  </span>
                </td>
                <td class="text-center">
                  <button 
                    onclick="toggleCalcBrainDerivation('${b.id || b.item}')" 
                    id="btn-derivation-${b.id || b.item}"
                    class="px-2 py-0.5 text-[11px] font-medium border border-blue-200 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded transition"
                  >
                    Details ▾
                  </button>
                </td>
              </tr>
              <!-- Expandable Math Derivation Row -->
              <tr id="derivation-row-${b.id || b.item}" class="${calcBrainExpandAll ? '' : 'hidden'} bg-slate-50/50">
                <td colspan="12" class="p-4 border-b border-slate-200">
                  <div class="bg-white p-4 rounded-lg border border-slate-300 space-y-3 text-xs shadow-sm sticky left-0 min-w-full">
                    <div class="font-bold text-slate-800 flex flex-wrap items-center justify-between gap-2">
                      <div class="flex items-center gap-2">
                        <span class="text-sm font-bold text-slate-900">${b.name || b.desc} &bull; Statutory Derivation</span>
                        ${deriv?.extrapolated ? `
                          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300 shadow-xs">
                            Extrapolated beyond statutory table bounds
                          </span>
                        ` : ''}
                      </div>
                      <span class="text-slate-500 font-normal">Table Reference: <b>${b.table_ref || deriv?.table_no || 'Statutory Schedule'}</b></span>
                    </div>

                    ${deriv?.derivation_text ? `
                      <div class="text-[11px] font-mono text-blue-900 bg-blue-50/70 p-2.5 rounded border border-blue-200">
                        <span class="font-bold text-blue-950">Calculation Step:</span> ${deriv.derivation_text}
                      </div>
                    ` : ''}

                    ${(deriv && deriv.components && deriv.components.length > 0) ? `
                      <div class="pt-2 border-t border-slate-100">
                        <div class="font-bold text-slate-800 text-xs mb-1.5 flex flex-wrap items-center justify-between gap-2">
                          <span class="flex items-center gap-1.5 text-blue-950">
                            <span class="w-2 h-2 rounded-full bg-blue-600 inline-block"></span>
                            Statutory Multi-Criterion Verification (${deriv.components.length} Checks):
                          </span>
                          <span class="text-[11px] font-bold px-2 py-0.5 rounded ${isComp ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-rose-100 text-rose-800 border border-rose-300'}">
                            Overall Member Status: ${b.status}
                          </span>
                        </div>
                        <div class="overflow-x-auto border border-slate-200 rounded shadow-xs mb-2 max-w-4xl">
                          <table class="w-full text-[11px] font-mono text-left bg-white">
                            <thead class="bg-slate-100 text-slate-700 border-b border-slate-200">
                              <tr>
                                <th class="p-1.5 w-[210px]">Statutory Parameter</th>
                                <th class="p-1.5 text-right w-[95px]">Table Base</th>
                                <th class="p-1.5 text-center w-[75px]">Factor (k)</th>
                                <th class="p-1.5 text-right w-[110px]">Rule Required</th>
                                <th class="p-1.5 text-right w-[125px] bg-blue-50/60">Provided Scantling</th>
                                <th class="p-1.5 text-right w-[105px]">Safety Margin</th>
                                <th class="p-1.5 text-center w-[85px]">Status</th>
                              </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                              ${deriv.components.map(c => {
                                const pass = (c.status === 'COMPLIANT' || c.margin >= 0);
                                return `
                                  <tr class="${pass ? 'hover:bg-slate-50' : 'bg-rose-50/60 font-semibold'}">
                                    <td class="p-1.5 font-medium text-slate-900">${c.name}</td>
                                    <td class="p-1.5 text-right text-slate-600">${c.base} ${c.unit}</td>
                                    <td class="p-1.5 text-center text-blue-800 font-semibold">${c.factor || 1.0}</td>
                                    <td class="p-1.5 text-right font-bold text-slate-900">${c.rreq} ${c.unit}</td>
                                    <td class="p-1.5 text-right font-bold text-blue-900 bg-blue-50/40">${c.prov !== undefined ? c.prov : '-'} ${c.unit}</td>
                                    <td class="p-1.5 text-right font-bold ${pass ? 'text-emerald-700' : 'text-rose-700'}">
                                      ${c.margin >= 0 ? '+' : ''}${c.margin} ${c.unit}
                                    </td>
                                    <td class="p-1.5 text-center">
                                      <span class="px-2 py-0.5 rounded text-[10px] font-bold ${pass ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-rose-100 text-rose-800 border border-rose-300'}">
                                        ${pass ? 'PASS' : 'FAIL'}
                                      </span>
                                    </td>
                                  </tr>
                                `;
                              }).join('')}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    ` : `
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 border-t border-slate-100">
                      <div>
                        <div class="font-semibold text-slate-700 mb-1">Interpolation & Requirements:</div>
                        <div class="font-mono text-slate-600 bg-slate-50 p-2 rounded border border-slate-100 text-[11px] space-y-0.5">
                          <div>Baseline Scantling: <b class="text-slate-800">${b.baseline} ${b.unit}</b></div>
                          <div>Statutory Factor Multiplier: <b class="text-blue-700">k = ${(b.factor !== undefined && b.factor !== null) ? (typeof b.factor === 'number' ? b.factor.toFixed(2) : b.factor) : (deriv && deriv.factor ? (typeof deriv.factor === 'number' ? deriv.factor.toFixed(2) : deriv.factor) : (deriv && deriv.inputs_used && (deriv.inputs_used.factor || deriv.inputs_used.kt || deriv.inputs_used.kz) ? (typeof (deriv.inputs_used.factor || deriv.inputs_used.kt || deriv.inputs_used.kz) === 'number' ? (deriv.inputs_used.factor || deriv.inputs_used.kt || deriv.inputs_used.kz).toFixed(2) : (deriv.inputs_used.factor || deriv.inputs_used.kt || deriv.inputs_used.kz)) : '1.00'))}</b></div>
                          <div>Rule Minimum Required: <b class="text-slate-900">${b.rreq} ${b.unit}</b></div>
                          ${deriv?.spacing_correction && deriv.spacing_correction !== 1.0 ? `
                            <div class="text-amber-800">Frame Spacing Correction Ratio: <b>${deriv.spacing_correction}</b></div>
                          ` : ''}
                        </div>
                      </div>
                      <div>
                        <div class="font-semibold text-slate-700 mb-1">Provided Geometry & Compliance:</div>
                        <div class="font-mono text-slate-600 bg-slate-50 p-2 rounded border border-slate-100 text-[11px] space-y-0.5">
                          <div>Actual / Provided: <b class="text-slate-900">${b.dact} ${b.unit}</b></div>
                          <div>Safety Margin: <b class="${b.margin >= 0 ? 'text-emerald-700' : 'text-rose-700'}">${b.margin >= 0 ? '+' : ''}${b.margin} ${b.unit}</b></div>
                          <div>Compliance Status: <b class="${isComp ? 'text-emerald-700' : 'text-rose-700'}">${b.status}</b></div>
                        </div>
                      </div>
                    </div>
                    `}

                    <!-- Full Statutory Table Visualization with Dynamic Row & Cell Highlights -->
                    ${renderDerivationTable(deriv)}
                  </div>
                </td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

async function resetToDefaults() {
  if (confirm('Reset all values to default Excel master state?')) {
    try {
      localStorage.removeItem('bangla_scantling_saved_state');
      await fetch('/api/reset-state', { method: 'POST' });
    } catch (e) {
      console.warn('Error resetting state:', e);
    }
    await loadInitialState();
    renderApp();
    updateSealUI();
    const statusText = document.getElementById('save-status-text');
    const dot = document.getElementById('save-status-dot');
    if (dot) dot.className = 'w-1.5 h-1.5 rounded-full bg-emerald-500';
    if (statusText) statusText.textContent = 'Reset to master defaults';
  }
}

// Window exports
window.calcBrainView = { render: renderCalcBrain };
window.toggleCalcBrainDerivation = toggleCalcBrainDerivation;
window.setCalcBrainExpandAll = setCalcBrainExpandAll;
window.onCalcBrainGroupFilter = onCalcBrainGroupFilter;
window.onCalcBrainSearch = onCalcBrainSearch;
window.resetToDefaults = resetToDefaults;
