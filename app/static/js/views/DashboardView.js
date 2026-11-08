let dashTableGroupFilter = 'ALL';
let dashTableSearchQuery = '';

function onDashTableGroupFilter(val) {
  dashTableGroupFilter = val;
  renderDashboard();
}

function onDashTableSearch(val) {
  dashTableSearchQuery = val;
  renderDashboard();
}

/**
 * DashboardView - Renders Vessel Particulars, Classification Cards, and Statutory Audit Table
 */
let dashBrainGroupFilter = 'ALL';
let dashBrainSearchQuery = '';
let dashBrainExpandAll = false;
let sheet2BrainGroupFilter = 'ALL';
let sheet2BrainSearchQuery = '';
let sheet2BrainExpandAll = false;
let sheet2ActiveTab = 'sheet2';

function updateTopStats() {
  const inputs = appState.dashboard_inputs || {};
  
  const vNameEl = document.getElementById('top-vessel-name');
  if (vNameEl) vNameEl.textContent = inputs.vessel_name || 'Vessel';
}

// ================= SHARED 76-ITEMS STATUTORY AUDIT ENGINE =================
function onDashBrainGroupFilter(val) {
  dashBrainGroupFilter = val;
  renderDashboard();
}

function onDashBrainSearch(val) {
  dashBrainSearchQuery = val;
  renderDashboard();
}

function setDashBrainExpandAll(val) {
  dashBrainExpandAll = val;
  renderDashboard();
}

function onSheet2BrainGroupFilter(val) {
  sheet2BrainGroupFilter = val;
  renderSheet2Calc();
}

function onSheet2BrainSearch(val) {
  sheet2BrainSearchQuery = val;
  renderSheet2Calc();
}

function setSheet2BrainExpandAll(val) {
  sheet2BrainExpandAll = val;
  renderSheet2Calc();
}

function setSheet2ActiveTab(tab) {
  sheet2ActiveTab = tab;
  renderSheet2Calc();
}

function toggleGeneralDerivation(prefix, itemNo) {
  const row = document.getElementById(`${prefix}-derivation-row-${itemNo}`);
  const chev = document.getElementById(`${prefix}-chevron-${itemNo}`);
  if (!row) return;
  if (row.classList.contains('hidden')) {
    row.classList.remove('hidden');
    if (chev) chev.textContent = '▼';
  } else {
    row.classList.add('hidden');
    if (chev) chev.textContent = '▶';
  }
}

function render76ItemsHtml(options = {}) {
  const {
    prefix = 'dash',
    groupFilter = 'ALL',
    searchQuery = '',
    expandAll = false,
    title = 'STATUTORY SCANTLINGS & COMPLIANCE AUDIT',
    subtitle = 'Comprehensive compliance audit across hull scantling, outfitting, machinery, rudder, equipment and piping rules',
    onGroupFilterFn = 'onDashBrainGroupFilter',
    onSearchFn = 'onDashBrainSearch',
    onExpandAllFn = 'setDashBrainExpandAll',
    onToggleDerivFn = 'toggleGeneralDerivation'
  } = options;

  const brain = appState?.calculation_brain || [];
  const stats = appState?.summary_stats || {};
  const inputs = appState?.dashboard_inputs || {};

  const allGroups = [];
  brain.forEach(b => {
    const g = b.category || b.group; if (g && !allGroups.includes(g)) allGroups.push(g);
  });

  const filtered = brain.filter(b => {
    if (groupFilter !== 'ALL' && (b.category || b.group) !== groupFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchDesc = (b.name || b.desc || '').toLowerCase().includes(q);
      const matchRule = (b.rule || '').toLowerCase().includes(q);
      const matchFormula = (b.formula || '').toLowerCase().includes(q);
      const matchGroup = (b.category || b.group || '').toLowerCase().includes(q);
      const itemStr = String(b.item);
      if (!matchDesc && !matchRule && !matchFormula && !matchGroup && itemStr !== q) return false;
    }
    return true;
  });

  return `
    <div class="bg-white p-3.5 rounded border border-slate-200 mb-4 shadow-xs">
      <!-- Header Controls Bar -->
      <div class="flex flex-wrap items-center justify-between gap-3 mb-3 pb-2.5 border-b border-slate-200">
        <div>
          <div class="compact-title compact-title-primary mb-0 flex items-center gap-2">
            <span>${title}</span>
            <span class="px-2 py-0.5 rounded text-[11px] font-bold bg-blue-100 text-blue-800">
              Rules 8 - 147 • 12 Statutory Groups
            </span>
          </div>
          <div class="text-[11px] text-slate-500">${subtitle} • <b>${filtered.length}</b> of <b>${brain.length}</b> Items Shown</div>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <span class="badge-comp text-xs px-2.5 py-1 font-bold">${stats.compliant_items || brain.length} / ${stats.total_items || brain.length} COMPLIANT (${stats.compliance_pct || 100}%)</span>
          <button onclick="${onExpandAllFn}(!${expandAll})" class="px-2.5 py-1 text-xs border ${expandAll ? 'border-blue-600 bg-blue-50 text-blue-700 font-semibold' : 'border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-medium'} rounded transition-colors">
            ${expandAll ? '▼ Collapse All Derivations' : '▶ Expand All Derivations'}
          </button>
        </div>
      </div>

      <!-- Filter & Search Toolbar -->
      <div class="bg-slate-50 p-2 rounded border border-slate-200 mb-3 flex flex-wrap items-center justify-between gap-2.5">
        <div class="flex items-center gap-2 flex-1 min-w-[260px]">
          <span class="text-xs font-semibold text-slate-700 whitespace-nowrap">Filter Group:</span>
          <select onchange="${onGroupFilterFn}(this.value)" class="border border-slate-300 rounded px-2.5 py-1 text-xs text-slate-800 bg-white hover:bg-slate-50 focus:outline-none focus:ring-1 focus:ring-blue-500 max-w-[320px] truncate">
            <option value="ALL" ${groupFilter === 'ALL' ? 'selected' : ''}>All Statutory Groups ( Components)</option>
            ${allGroups.map((g, idx) => `
              <option value="${g}" ${groupFilter === g ? 'selected' : ''}>Group ${idx + 1}: ${(g || '').split('(')[0].replace(/GROUP \d+:\s*/i, '').trim()}</option>
            `).join('')}
          </select>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs font-semibold text-slate-700 whitespace-nowrap">Search:</span>
          <div class="relative">
            <input 
              type="text" 
              placeholder="Search rule or component..." 
              value="${searchQuery}"
              oninput="${onSearchFn}(this.value)"
              class="border border-slate-300 rounded px-2.5 py-1 text-xs text-slate-800 w-64 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
            />
            ${searchQuery ? `
              <button onclick="${onSearchFn}('')" class="absolute right-2 top-1 text-xs text-slate-400 hover:text-slate-600">×</button>
            ` : ''}
          </div>
        </div>
      </div>

      <!-- Main Audit Table -->
      <div class="overflow-x-auto">
        <table class="compact-table w-full">
          <thead>
            <tr>
              <th style="width: 25px;" class="text-center">No.</th>
              <th style="min-width: 170px;">Component / Structural Member</th>
              <th style="width: 85px;" class="text-center">Rule Ref</th>
              <th style="width: 95px;" class="text-center">Table Ref</th>
              <th style="min-width: 180px;">Governing Formula / Basis</th>
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
                <td colspan="13" class="text-center py-6 text-slate-500 italic">No statutory components match your filter criteria.</td>
              </tr>
            ` : filtered.map(b => {
              const isComp = b.status === 'COMPLIANT';
              const d = (typeof getCalculationBrainDetails === 'function') 
                ? getCalculationBrainDetails(b.item, inputs, b)
                : {
                    item: b.item,
                    rule: b.rule,
                    table_no: null,
                    table_title: 'Statutory Scantling Rule',
                    formula: b.formula,
                    has_table: false,
                    inputs_used: [
                      { label: 'Length L', val: `${inputs.lbp || 69.85} m` },
                      { label: 'Spacing s', val: `${inputs.frame_spacing || 550} mm` },
                      { label: 'Factor kt', val: `${inputs.effective_kt || 1.20}` }
                    ],
                    bounding_nodes: null,
                    ratio_str: 'Direct Statutory Baseline Standard',
                    interp_math: `Base: ${b.baseline} ${b.unit}`,
                    correction_math: null,
                    factor_math: `Required = ${b.baseline} × ${b.factor || 1.0} = ${b.rreq} ${b.unit}`,
                    compliance_math: `Drawing Provided: ${b.dact} ${b.unit} vs Required: ${b.rreq} ${b.unit} (${b.status})`
                  };

              const drawerId = `${prefix}-derivation-row-${b.item}`;
              const chevronId = `${prefix}-chevron-${b.item}`;

              return `
                <tr class="hover:bg-slate-50/80 transition-colors border-b border-slate-100">
                  <td class="text-center text-slate-500 font-semibold">${b.item}</td>
                  <td class="font-medium text-slate-800">
                    <div class="font-semibold text-slate-900">${b.name || b.desc || ""}</div>
                    <div class="text-[10px] text-slate-400 font-normal truncate max-w-xs" title="${b.group}">${(b.group || b.category || '').split('(')[0].replace(/GROUP \d+:\s*/i, '').trim()}</div>
                  </td>
                  <td class="text-center">
                    <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-bold bg-blue-50 text-blue-700 border border-blue-200 whitespace-nowrap">
                      ${d.rule}
                    </span>
                  </td>
                  <td class="text-center">
                    <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-bold ${d.table_no ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-slate-50 text-slate-600 border border-slate-200'} whitespace-nowrap">
                      ${d.table_no ? `Table ${d.table_no}` : 'Direct Rule'}
                    </span>
                  </td>
                  <td>
                    <code class="font-mono text-[11px] text-slate-800 bg-slate-50 px-1 py-0.5 rounded border border-slate-200 block truncate max-w-xs" title="${d.formula}">
                      ${d.formula}
                    </code>
                  </td>
                  <td class="text-right font-mono">${typeof b.baseline === 'number' ? b.baseline.toFixed(2) : b.baseline}</td>
                  <td class="text-center font-mono font-medium">${typeof b.factor === 'number' ? b.factor.toFixed(2) : (b.factor || '1.0')}</td>
                  <td id="dash-main-req-${b.item}" class="text-right font-mono font-medium text-slate-700">${typeof b.rreq === 'number' ? b.rreq.toFixed(2) : b.rreq}</td>
                  <td class="text-center p-1 bg-slate-50/50">
                    <input 
                      type="number" 
                      step="0.1" 
                      id="dash-main-input-${b.item}" 
                      class="compact-input text-center font-mono font-bold text-slate-900 w-20 mx-auto" 
                      value="${b.dact !== undefined ? b.dact : 0}" 
                      oninput="handleLiveBrainItemChange(${b.item}, parseFloat(this.value) || 0)"
                    />
                  </td>
                  <td class="text-center text-slate-500 text-[11px]">${b.unit}</td>
                  <td id="dash-main-margin-${b.item}" class="text-right font-mono text-[11px] ${b.margin >= 0 ? 'text-emerald-700 font-medium' : 'text-rose-700 font-bold'}">
                    ${typeof b.margin === 'number' ? (b.margin >= 0 ? '+' : '') + b.margin.toFixed(2) : b.margin}
                  </td>
                  <td class="text-center">
                    <span id="dash-main-status-${b.item}" class="${isComp ? 'badge-comp' : 'badge-def'}">${b.status}</span>
                  </td>
                  <td class="text-center">
                    <button onclick="${onToggleDerivFn}('${prefix}', ${b.item})" class="border border-slate-200 hover:border-slate-300 rounded px-1.5 py-0.5 text-[11px] text-slate-700 hover:text-slate-900 hover:bg-slate-100 flex items-center justify-center gap-1 font-medium w-full transition-colors">
                      <span id="${chevronId}">${expandAll ? '▼' : '▶'}</span> Derivation
                    </button>
                  </td>
                </tr>

                <!-- Step-by-Step Derivation Drawer -->
                <tr id="${drawerId}" class="derivation-drawer bg-slate-50/60 border-b border-slate-200 ${expandAll ? '' : 'hidden'}">
                  <td colspan="13" class="p-0">
                    <div class="p-3 bg-white mx-3 my-2 rounded border border-slate-200 shadow-sm text-xs">
                      <div class="flex flex-wrap items-center justify-between pb-2 mb-2.5 border-b border-slate-100 gap-2">
                        <div class="flex items-center gap-2">
                          <span class="font-bold text-slate-900 flex items-center gap-1.5">
                            <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
                            MATHEMATICAL DERIVATION &amp; TABLE INTERPOLATION:
                          </span>
                          <span class="px-2 py-0.5 rounded text-[11px] font-bold bg-blue-100 text-blue-800">${d.rule}</span>
                          ${d.table_no ? `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-100 text-emerald-800">Table ${d.table_no}</span>` : ''}
                        </div>
                        <div class="text-[11px] text-slate-600 font-medium">${d.table_title}</div>
                      </div>

                      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div class="bg-slate-50 p-2.5 rounded border border-slate-200">
                          <div class="font-bold text-[11px] text-slate-700 uppercase tracking-wider mb-1.5">Vessel Inputs Used</div>
                          <div class="space-y-1">
                            ${d.inputs_used.map(inp => `
                              <div class="flex justify-between items-center text-[11px]">
                                <span class="text-slate-600">${inp.label}:</span>
                                <span class="font-mono font-semibold text-slate-900">${inp.val}</span>
                              </div>
                            `).join('')}
                          </div>
                        </div>

                        <div class="bg-slate-50 p-2.5 rounded border border-slate-200">
                          <div class="font-bold text-[11px] text-slate-700 uppercase tracking-wider mb-1.5">Table Nodes &amp; Ratio (λ)</div>
                          ${d.bounding_nodes ? `
                            <div class="space-y-1 text-[11px]">
                              <div class="flex justify-between">
                                <span class="text-slate-600">Lower Bound Node:</span>
                                <span class="font-mono font-semibold text-slate-900">${d.bounding_nodes.lower_node} → ${d.bounding_nodes.lower_val}</span>
                              </div>
                              <div class="flex justify-between">
                                <span class="text-slate-600">Upper Bound Node:</span>
                                <span class="font-mono font-semibold text-slate-900">${d.bounding_nodes.upper_node} → ${d.bounding_nodes.upper_val}</span>
                              </div>
                              <div class="mt-1 pt-1 border-t border-slate-200 text-slate-700 font-mono text-[11px]">
                                ${d.ratio_str}
                              </div>
                            </div>
                          ` : `
                            <div class="text-[11px] text-slate-600 space-y-1">
                              <div>Direct Statutory Formula Evaluation:</div>
                              <div class="font-mono text-slate-800 bg-white p-1 rounded border border-slate-200 text-[10.5px]">${d.formula}</div>
                              <div class="text-[10px] text-slate-500">Evaluated directly without empirical table interpolation.</div>
                            </div>
                          `}
                        </div>

                        <div class="bg-blue-50/40 p-2.5 rounded border border-blue-200/80">
                          <div class="font-bold text-[11px] text-blue-900 uppercase tracking-wider mb-1.5">Step-by-Step Calculation</div>
                          <div class="space-y-1 text-[11px]">
                            <div class="text-slate-800"><span class="font-semibold text-slate-900">1. Base:</span> ${d.interp_math}</div>
                            ${d.correction_math ? `<div class="text-slate-800"><span class="font-semibold text-slate-900">2. Adjustment:</span> ${d.correction_math}</div>` : ''}
                            <div class="text-slate-800"><span class="font-semibold text-slate-900">3. Factor:</span> ${d.factor_math}</div>
                            <div class="mt-1.5 pt-1 border-t border-blue-200/80 font-bold ${isComp ? 'text-emerald-800' : 'text-rose-800'}">
                              ✓ ${d.compliance_math}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    </div>

    <!-- 5. STATUTORY SCANTLINGS COMPLIANCE AUDIT (76 RULES BY CATEGORY) -->
    <div class="bg-white p-3.5 rounded border border-slate-200 mb-4">
      <div class="flex flex-wrap justify-between items-center gap-2 mb-3">
        <div>
          <div class="compact-title compact-title-primary mb-0.5">5. STATUTORY SCANTLINGS COMPLIANCE AUDIT (BY CATEGORY)</div>
          <div class="text-[11px] text-slate-500">Comprehensive statutory scan across all 12 structural, propulsion, auxiliary &amp; safety systems</div>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs font-semibold text-slate-600">Total Audit:</span>
          <span id="brain-summary-badge" class="px-2 py-0.5 rounded text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
            ${stats.compliant_items || brain.length} / ${stats.total_items || brain.length} COMPLIANT (${(typeof stats.compliance_pct === 'number' ? stats.compliance_pct.toFixed(1) : (stats.compliance_pct || '100.0'))}%)
          </span>
        </div>
      </div>

      <!-- Category Filter Pills & Search -->
      <div class="flex flex-wrap items-center justify-between gap-2 mb-3 bg-slate-50 p-2 rounded border border-slate-200">
        <div class="flex flex-wrap items-center gap-1.5" id="brain-category-pills">
          <button onclick="filterBrainCategory('all')" class="brain-cat-pill active px-2.5 py-1 rounded text-xs font-semibold bg-blue-600 text-white" data-cat="all">
            All Categories (${brain.length})
          </button>
          ${(() => {
            const brainItems = appState.calculation_brain || [];
            const grpSet = new Map();
            brainItems.forEach(b => {
              const cleanG = (b.category || b.group || 'Other').split('(')[0].trim();
              grpSet.set(cleanG, (grpSet.get(cleanG) || 0) + 1);
            });
            return Array.from(grpSet.entries()).map(([gName, count], idx) => `
              <button onclick="filterBrainCategory('${gName}')" class="brain-cat-pill px-2 py-1 rounded text-xs font-medium bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition" data-cat="${gName}">
                ${gName.replace('GROUP ', '').replace(':', '.')} (${count})
              </button>
            `).join('');
          })()}
        </div>
        <div class="w-full sm:w-auto">
          <input 
            type="text" 
            id="brain-search-input" 
            placeholder="Search component name or item #..." 
            class="compact-input text-xs w-full sm:w-64"
            oninput="handleBrainSearch(this.value)"
          />
        </div>
      </div>

      <!-- Category Group Cards Container -->
      <div id="brain-groups-container" class="space-y-3.5">
        ${renderBrainGroupsHtml(appState.calculation_brain || [])}
      </div>
    </div>
  `;
}

let currentBrainCategory = 'all';
let currentBrainSearch = '';

function renderBrainGroupsHtml(brainItems, activeCategory = 'all', searchQuery = '') {
  if (!brainItems || brainItems.length === 0) {
    return '<div class="p-4 text-center text-xs text-slate-500">No calculation brain items found.</div>';
  }

  const q = String(searchQuery || '').toLowerCase().trim();
  const filtered = brainItems.filter(b => {
    const cleanG = (b.category || b.group || 'Other').split('(')[0].trim();
    if (activeCategory !== 'all' && cleanG !== activeCategory) return false;
    if (q) {
      const matchDesc = String(b.desc || '').toLowerCase().includes(q);
      const matchNo = String(b.item || '').includes(q);
      const matchGroup = cleanG.toLowerCase().includes(q);
      return matchDesc || matchNo || matchGroup;
    }
    return true;
  });

  if (filtered.length === 0) {
    return `<div class="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded border border-dashed border-slate-300">No components match search "${searchQuery}".</div>`;
  }

  const groups = new Map();
  filtered.forEach(b => {
    const cleanG = (b.category || b.group || 'Other').split('(')[0].trim();
    if (!groups.has(cleanG)) groups.set(cleanG, []);
    groups.get(cleanG).push(b);
  });

  return Array.from(groups.entries()).map(([grpName, items]) => {
    const compCount = items.filter(it => it.status === 'COMPLIANT').length;
    const isAllComp = compCount === items.length;

    return `
      <div class="brain-group-card border border-slate-200 rounded overflow-hidden shadow-xs">
        <!-- Group Header Bar -->
        <div class="bg-slate-100/90 px-3 py-2 flex items-center justify-between border-b border-slate-200">
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-slate-800 tracking-wide">${grpName}</span>
            <span class="text-[10.5px] text-slate-500 font-medium">(${items.length} items)</span>
          </div>
          <span class="px-2 py-0.5 rounded text-[11px] font-bold ${isAllComp ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-amber-100 text-amber-800 border border-amber-200'}">
            ${compCount} / ${items.length} COMPLIED
          </span>
        </div>

        <!-- Group Table (Clean, NO Table Ref, NO Formula Derivation) -->
        <div class="overflow-x-auto">
          <table class="compact-table">
            <thead>
              <tr>
                <th style="width: 36px;" class="text-center">No.</th>
                <th>Scantling Component Description</th>
                <th style="width: 80px;" class="text-right">Baseline</th>
                <th style="width: 65px;" class="text-center">Factor (k)</th>
                <th style="width: 85px;" class="text-right">Required</th>
                <th style="width: 110px;" class="text-center bg-slate-100/60">Provided</th>
                <th style="width: 55px;" class="text-center">Unit</th>
                <th style="width: 80px;" class="text-right">Margin</th>
                <th style="width: 95px;" class="text-center">Status</th>
              </tr>
            </thead>
            <tbody>
              ${items.map(it => {
                const isComp = it.status === 'COMPLIANT';
                const baseVal = typeof it.baseline === 'number' ? it.baseline.toFixed(2) : (it.baseline || '-');
                const factVal = typeof it.factor === 'number' ? it.factor.toFixed(2) : (it.factor || '1.00');
                const reqVal = typeof it.rreq === 'number' ? it.rreq.toFixed(2) : (it.rreq || '-');
                const margVal = typeof it.margin === 'number' ? (it.margin >= 0 ? '+' : '') + it.margin.toFixed(2) : (it.margin || '-');

                return `
                  <tr id="brain-row-${it.item}">
                    <td class="text-center text-slate-400 font-semibold">${it.item}</td>
                    <td class="font-medium text-slate-800">${it.name || it.desc || ''}</td>
                    <td class="text-right text-slate-600 font-mono text-[11.5px]">${baseVal}</td>
                    <td class="text-center font-mono font-bold text-slate-700 text-[11.5px]">${factVal}</td>
                    <td class="text-right font-medium text-slate-700 font-mono text-[11.5px]">${reqVal}</td>
                    <td class="text-center p-1 bg-slate-50/50">
                      <input 
                        type="number" 
                        step="0.1" 
                        id="brain-input-${it.item}" 
                        class="compact-input text-center font-mono font-bold text-slate-900 w-24 mx-auto" 
                        value="${it.dact !== undefined ? it.dact : 0}" 
                        oninput="handleLiveBrainItemChange(${it.item}, parseFloat(this.value) || 0)"
                      />
                    </td>
                    <td class="text-center text-slate-500 text-[11px]">${it.unit || ''}</td>
                    <td id="brain-margin-${it.item}" class="text-right font-mono text-[11.5px] ${isComp ? 'text-emerald-700 font-semibold' : 'text-rose-700 font-semibold'}">
                      ${margVal}
                    </td>
                    <td class="text-center">
                      <span id="brain-status-${it.item}" class="${isComp ? 'badge-comp' : 'badge-def'}">
                        ${it.status || 'COMPLIANT'}
                      </span>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }).join('');
}

function handleLiveBrainItemChange(itemNo, val) {
  if (!appState || !appState.calculation_brain) return;
  const it = appState.calculation_brain.find(b => b.item === itemNo);
  if (!it) return;
  it.dact = val;

  // Persist in custom overrides so recalculateAll retains it
  if (!appState.custom_brain_dact) appState.custom_brain_dact = {};
  appState.custom_brain_dact[it.id] = val;

  // Sync to bound_plate_key or member id in dashboard_inputs
  if (it.bound_plate_key) {
    appState.dashboard_inputs[it.bound_plate_key] = val;
  }
  appState.dashboard_inputs[it.id] = val;

  // Sync to checklist if mapped
  const chkMapping = {
    't_keel': 1, 't_bottom': 2, 't_bilge': 3, 't_side': 4,
    't_deck_hatch': 5, 't_deck_all': 6, 't_bhd': 15,
    't_hatch_long': 17, 't_hatch_trans': 18, 't_hatch_cover': 19,
    't_inner_bottom': 21
  };
  const chkNo = chkMapping[it.bound_plate_key];
  if (chkNo) {
    const chkItem = (appState.scantling_checklist || []).find(c => c.no === chkNo);
    if (chkItem) chkItem.provided = val;
    const chkInput = document.getElementById('plate-input-' + chkNo);
    if (chkInput && document.activeElement !== chkInput) {
      chkInput.value = val;
    }
  }

  // Also sync dual inputs if both on screen (dash-main-input vs brain-input)
  const mainInp = document.getElementById(`dash-main-input-${it.item}`);
  if (mainInp && document.activeElement !== mainInp) {
    mainInp.value = val;
  }
  const brainInp = document.getElementById(`brain-input-${it.item}`);
  if (brainInp && document.activeElement !== brainInp) {
    brainInp.value = val;
  }

  recalculateAll(appState);
  updateTopStats();
  updateLiveDashboardDisplays();
  triggerAutosaveDebounced();
}

function filterBrainCategory(catName) {
  currentBrainCategory = catName;
  document.querySelectorAll('.brain-cat-pill').forEach(btn => {
    if (btn.getAttribute('data-cat') === catName) {
      btn.className = 'brain-cat-pill active px-2.5 py-1 rounded text-xs font-semibold bg-blue-600 text-white';
    } else {
      btn.className = 'brain-cat-pill px-2 py-1 rounded text-xs font-medium bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition';
    }
  });
  const container = document.getElementById('brain-groups-container');
  if (container) {
    container.innerHTML = renderBrainGroupsHtml(appState.calculation_brain || [], currentBrainCategory, currentBrainSearch);
  }
}

function handleBrainSearch(query) {
  currentBrainSearch = query;
  const container = document.getElementById('brain-groups-container');
  if (container) {
    container.innerHTML = renderBrainGroupsHtml(appState.calculation_brain || [], currentBrainCategory, currentBrainSearch);
  }
}

// ================= 1. DASHBOARD SECTION (ORGANIZED & HULL TYPE ADDED) =================
function renderDashboard() {
  const container = document.getElementById('tab-content-dashboard');
  if (!container) return;

  const inp = appState.dashboard_inputs || {};
  const stats = appState.summary_stats || {};
  const chk = appState.scantling_checklist || [];
  const profiles = appState.stiffener_profiles || [];
  const ls = appState.lightship_summary || {};
  const hType = inp.hull_type || 'Double Bottom';
  const vType = String(inp.vessel_type || 'Steel Body Cargo Vessel');
  const standardVesselTypes = [
    'Steel Body Cargo Vessel',
    'Ferry',
    'Oil Tanker',
    'Catamaran',
    'Container',
    'Passenger',
    'Barge'
  ];
  const mat = String(inp.hull_material || 'Steel (old)').toLowerCase();
  const matOther = ['steel (new)', 'steel (old)', 'wood', 'mixed', 'glass fiber', 'aluminum'].includes(mat) ? '' : (inp.hull_material || '');
  const rVal = String(inp.proposed_route || inp.route || 'Inland & bay crossing');
  const isBayCrossing = rVal.toLowerCase().includes('bay');
  const rOther = ['inland (calm water)', 'inland (partially smooth water)', 'inland (rough water)', 'inland (round seasonal water)', 'inland & bay crossing', 'inland & seasonal crossing'].includes(rVal.toLowerCase()) ? '' : rVal;
  const pTime = String(inp.plying_time || 'Day & Night');

  container.innerHTML = `
    <!-- Top Summary Banner -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
      <div class="bg-white p-3 rounded border border-slate-200">
        <div class="compact-title compact-title-primary">STATUTORY STATUS</div>
        <div id="summary-statutory-status" class="text-base font-bold text-slate-800">${stats.overall_status || 'COMPLIANT'}</div>
        <div id="summary-route-hull" class="text-[11px] text-slate-500">${inp.route || 'Bay Crossing'} • <b>${hType}</b></div>
      </div>
      <div class="bg-white p-3 rounded border border-slate-200">
        <div class="compact-title compact-title-success">CHECKLIST SCORECARD</div>
        <div id="summary-checklist-score" class="text-base font-bold text-emerald-700">${stats.checklist_complied} / ${stats.checklist_total} COMPLIED</div>
        <div class="text-[11px] text-slate-500">Hull Scantlings Audit (Rules 9-52)</div>
      </div>
      <div class="bg-white p-3 rounded border border-slate-200">
        <div class="compact-title">STATUTORY BRAIN</div>
        <div id="summary-brain-score" class="text-base font-bold text-slate-800">${stats.compliant_items} / ${stats.total_items} RULES PASS</div>
        <div id="summary-brain-pct" class="text-[11px] text-slate-500">Compliance Rate: ${stats.compliance_pct}%</div>
      </div>
      <div class="bg-white p-3 rounded border border-slate-200">
        <div class="compact-title">LIGHTSHIP ESTIMATE</div>
        <div id="summary-lightship-weight" class="text-base font-bold text-blue-700">${ls.total_lightship_tonne?.toFixed(1) || '903.8'} Tonnes</div>
        <div id="summary-steel-weight" class="text-[11px] text-slate-500">Steel Plating + Angles: ${ls.total_steel_tonne?.toFixed(1) || '579.3'} t</div>
      </div>
    </div>

    <!-- UNIFIED VESSEL PARTICULARS & STATUTORY INPUT TABLE (CONSOLIDATED) -->
    <div class="bg-white p-2.5 rounded border border-slate-200 mb-3 shadow-2xs">
      <div class="mb-2">
        <div class="compact-title compact-title-primary mb-0 text-[11px] font-bold">VESSEL PRINCIPAL PARTICULARS &amp; STATUTORY INPUT TABLE</div>
      </div>

      <!-- Unified Grid: Dimensions, Identification, Machinery & Signatories -->
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-1.5 text-xs mb-2">
        <!-- Row 1: Vessel Identification -->
        <div class="col-span-2 sm:col-span-3 md:col-span-6">
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Vessel Name</label>
          <input type="text" class="compact-input h-7 py-0.5 px-2 text-xs font-semibold" value="${inp.vessel_name || ''}" oninput="handleLiveInputChange('vessel_name', this.value)"/>
        </div>

        <!-- Row 2: Principal Dimensions -->
        <div>
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">LOA [m]</label>
          <input type="number" step="0.01" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.loa || 0}" oninput="handleLiveInputChange('loa', parseFloat(this.value) || 0)"/>
        </div>
        <div>
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">LBP [m]</label>
          <input type="number" step="0.01" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.lbp || 0}" oninput="handleLiveInputChange('lbp', parseFloat(this.value) || 0)"/>
        </div>
        <div>
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">LWL [m]</label>
          <input type="number" step="0.01" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.lwl || 53.61}" oninput="handleLiveInputChange('lwl', parseFloat(this.value) || 0)"/>
        </div>
        <div>
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Breadth (B) [m]</label>
          <input type="number" step="0.01" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.breadth || 0}" oninput="handleLiveInputChange('breadth', parseFloat(this.value) || 0)"/>
        </div>
        <div>
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">B EXT [m]</label>
          <input type="number" step="0.01" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.b_ext || 9.52}" oninput="handleLiveInputChange('b_ext', parseFloat(this.value) || 0)"/>
        </div>
        <div>
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Depth (D) [m]</label>
          <input type="number" step="0.01" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.depth || 0}" oninput="handleLiveInputChange('depth', parseFloat(this.value) || 0)"/>
        </div>

        <!-- Row 3: Depth EXT, Draft, Spacing, Displ, Cb, Propeller -->
        <div>
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Depth EXT [m]</label>
          <input type="number" step="0.01" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.depth_ext || 4.52}" oninput="handleLiveInputChange('depth_ext', parseFloat(this.value) || 0)"/>
        </div>
        <div>
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Draft (d) [m]</label>
          <input type="number" step="0.01" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.draft || 0}" oninput="handleLiveInputChange('draft', parseFloat(this.value) || 0)"/>
        </div>
        <div>
          <label class="block text-blue-700 text-[10px] font-bold leading-none mb-0.5">Frame Spacing [mm]</label>
          <input type="number" step="5" class="compact-input h-7 py-0.5 px-2 text-xs font-bold text-blue-700" value="${inp.frame_spacing || 550}" oninput="handleLiveInputChange('frame_spacing', parseFloat(this.value) || 0)"/>
        </div>
        <div>
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Displacement [t]</label>
          <input type="number" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.displacement || 0}" oninput="handleLiveInputChange('displacement', parseFloat(this.value) || 0)"/>
        </div>
        <div>
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Block Coeff (Cb)</label>
          <input type="number" step="0.001" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.block_coeff || 0}" oninput="handleLiveInputChange('block_coeff', parseFloat(this.value) || 0)"/>
        </div>
        <div>
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Propeller Nos</label>
          <input type="number" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.propeller_nos || 2}" oninput="handleLiveInputChange('propeller_nos', parseInt(this.value) || 0)"/>
        </div>

        <!-- Row 4: Machinery & Propulsion -->
        <div>
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Propeller Dia [mm]</label>
          <input type="number" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.prop_dia || 1505}" oninput="handleLiveInputChange('prop_dia', parseFloat(this.value) || 0)"/>
        </div>
        <div class="md:col-span-2">
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Engine Type</label>
          <input type="text" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.engine_type || ''}" oninput="handleLiveInputChange('engine_type', this.value)"/>
        </div>
        <div class="md:col-span-3">
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Power of Engines [HP]</label>
          <input type="text" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.power || ''}" oninput="handleLiveInputChange('power', this.value)"/>
        </div>

        <!-- Row 5: Owner, S/O, Address, Designer, Firm, Checker -->
        <div class="md:col-span-2">
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Registered Owner</label>
          <input type="text" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.owner || ''}" oninput="handleLiveInputChange('owner', this.value)"/>
        </div>
        <div class="md:col-span-2">
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Owner S/O</label>
          <input type="text" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.owner_so || ''}" oninput="handleLiveInputChange('owner_so', this.value)"/>
        </div>
        <div class="md:col-span-2">
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Owner Address</label>
          <input type="text" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.owner_address || ''}" oninput="handleLiveInputChange('owner_address', this.value)"/>
        </div>

        <div class="md:col-span-2">
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Designer Name</label>
          <input type="text" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.designer_name || ''}" oninput="handleLiveInputChange('designer_name', this.value)"/>
        </div>
        <div class="md:col-span-2">
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Designer Firm</label>
          <input type="text" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.designer_firm || ''}" oninput="handleLiveInputChange('designer_firm', this.value)"/>
        </div>
        <div class="md:col-span-2">
          <label class="block text-slate-500 text-[10px] font-medium leading-none mb-0.5">Checker Name</label>
          <input type="text" class="compact-input h-7 py-0.5 px-2 text-xs" value="${inp.checked_by || ''}" oninput="handleLiveInputChange('checked_by', this.value)"/>
        </div>
      </div>

      <!-- Integrated Statutory Classification (2. Type of Vessel, 3. Hull Construction, Material, 4. Proposed Route, 5. Plying Time) -->
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-1.5 pt-2 border-t border-slate-100">
        <!-- 2. Type of Vessel -->
        <div class="bg-slate-50/70 p-2 rounded border border-slate-200">
          <div class="text-[10px] font-bold text-slate-700 uppercase mb-1">2. Type of Vessel :</div>
          <div class="space-y-0.5 text-[11px]">
            ${standardVesselTypes.map(t => {
              const isSel = vType === t;
              return `
                <label class="flex items-center gap-1.5 cursor-pointer px-1 py-0.5 rounded hover:bg-slate-100 ${isSel ? 'font-bold text-blue-900 bg-blue-100/70' : 'text-slate-700'}">
                  <input type="radio" class="w-3 h-3 text-blue-600" name="vessel_type_radio" value="${t}" ${isSel ? 'checked' : ''} onchange="handleVesselTypeChange(this.value)"/>
                  <span class="truncate">${t}</span>
                </label>
              `;
            }).join('')}
          </div>
        </div>

        <!-- 3. Hull Construction -->
        <div class="bg-slate-50/70 p-2 rounded border border-slate-200">
          <div class="text-[10px] font-bold text-slate-700 uppercase mb-1">3. Hull Construction :</div>
          <div class="space-y-0.5 text-[11px]">
            ${[
              'Double Bottom',
              'Double Hull',
              'Single Hull',
              'Single Bottom'
            ].map(ht => {
              const isSel = (hType || '').toLowerCase() === ht.toLowerCase();
              return `
                <label class="flex items-center gap-1.5 cursor-pointer px-1 py-0.5 rounded hover:bg-slate-100 ${isSel ? 'font-bold text-blue-900 bg-blue-100/70' : 'text-slate-700'}">
                  <input type="radio" class="w-3 h-3 text-blue-600" name="hull_construction_radio" value="${ht}" ${isSel ? 'checked' : ''} onchange="handleHullTypeChange(this.value)"/>
                  <span>${ht}</span>
                </label>
              `;
            }).join('')}
          </div>
        </div>

        <!-- Material -->
        <div class="bg-slate-50/70 p-2 rounded border border-slate-200">
          <div class="text-[10px] font-bold text-slate-700 uppercase mb-1">Material - :</div>
          <div class="grid grid-cols-2 gap-0.5 text-[11px]">
            ${[
              'Steel (new)',
              'Steel (Old)',
              'Wood',
              'Mixed',
              'Glass fiber',
              'Aluminum'
            ].map(m => {
              const mLower = m.toLowerCase();
              const isSel = (mat === mLower) || (mLower.includes('old') && mat.includes('old')) || (mLower.includes('new') && mat.includes('new'));
              return `
                <label class="flex items-center gap-1.5 cursor-pointer px-1 py-0.5 rounded hover:bg-slate-100 ${isSel ? 'font-bold text-blue-900 bg-blue-100/70' : 'text-slate-700'}">
                  <input type="radio" class="w-3 h-3 text-blue-600" name="hull_material" value="${m}" ${isSel ? 'checked' : ''} onchange="handleLiveInputChange('hull_material', this.value)"/>
                  <span class="truncate">${m}</span>
                </label>
              `;
            }).join('')}
          </div>
        </div>

        <!-- 4. Proposed Route & Rule Factors Selection -->
        <div class="bg-slate-50/70 p-2 rounded border border-slate-200">
          <div class="text-[10px] font-bold text-slate-700 uppercase mb-1">4. Proposed Route :</div>
          <div class="space-y-0.5 text-[10.5px]">
            ${[
              'Inland (calm water)',
              'Inland (partially smooth water)',
              'Inland (rough water)',
              'Inland (round seasonal water)',
              'Inland & bay crossing',
              'Inland & seasonal crossing'
            ].map(rt => {
              const isSel = (rVal.toLowerCase() === rt.toLowerCase()) || (rt.includes('bay') && isBayCrossing);
              return `
                <label class="flex items-center gap-1.5 cursor-pointer px-1 py-0.5 rounded hover:bg-slate-100 ${isSel ? 'font-bold text-blue-900 bg-blue-100/70' : 'text-slate-700'}">
                  <input type="radio" class="w-3 h-3 text-blue-600" name="proposed_route" value="${rt}" ${isSel ? 'checked' : ''} onchange="handleRouteChange(this.value)"/>
                  <span class="truncate">${rt.replace('&', '&amp;')}</span>
                </label>
              `;
            }).join('')}
          </div>

          <!-- Rule Factors Display & Manual Input Control -->
          <div class="mt-1.5 pt-1.5 border-t border-slate-200">
            <div class="text-[9.5px] font-bold text-slate-700 flex items-center justify-between mb-1">
              <span>Rule Factors:</span>
              <span id="factor-rule-tag" class="text-[9px] text-blue-800 font-semibold bg-blue-50 px-1 py-0.2 rounded border border-blue-200 max-w-[130px] truncate" title="${inp.factor_rule_desc || 'SRO 308 (Bay Crossing)'}">
                ${inp.factor_rule_desc || 'SRO 308 (Bay Crossing)'}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-1 text-xs">
              <div>
                <label class="block text-slate-500 text-[9px] font-medium leading-none mb-0.5">kt (Plate)</label>
                <input 
                  type="number" 
                  step="0.01" 
                  min="0.5" 
                  max="3.0"
                  id="input-plate-factor"
                  value="${(inp.effective_kt !== undefined ? inp.effective_kt : 1.20).toFixed(2)}"
                  oninput="handleManualFactorChange('kt', this.value)"
                  class="compact-input h-6 py-0 px-1 text-center font-mono font-bold text-blue-800 bg-white text-xs hover:border-blue-400 focus:border-blue-600 focus:outline-none"
                  title="Factor for Plates kt (Applied to ALL plate members). Auto-selected by Route or edit manually."
                />
              </div>
              <div>
                <label class="block text-slate-500 text-[9px] font-medium leading-none mb-0.5">kz (Stiffener)</label>
                <input 
                  type="number" 
                  step="0.01" 
                  min="0.5" 
                  max="3.0"
                  id="input-stiffener-factor"
                  value="${(inp.effective_kz !== undefined ? inp.effective_kz : 1.25).toFixed(2)}"
                  oninput="handleManualFactorChange('kz', this.value)"
                  class="compact-input h-6 py-0 px-1 text-center font-mono font-bold text-emerald-800 bg-white text-xs hover:border-emerald-400 focus:border-emerald-600 focus:outline-none"
                  title="Factor for Stiffeners kz (Applied to ALL stiffener members). Auto-selected by Route or edit manually."
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 5. Plying time -->
        <div class="bg-slate-50/70 p-2 rounded border border-slate-200">
          <div class="text-[10px] font-bold text-slate-700 uppercase mb-1">5. Plying time :</div>
          <div class="space-y-0.5 text-[11px]">
            ${[
              'Day',
              'Night',
              'Day & Night'
            ].map(pt => {
              const isSel = (pTime === pt) || (pt === 'Day & Night' && pTime.includes('Night') && pTime.includes('Day'));
              return `
                <label class="flex items-center gap-1.5 cursor-pointer px-1 py-0.5 rounded hover:bg-slate-100 ${isSel ? 'font-bold text-blue-900 bg-blue-100/70' : 'text-slate-700'}">
                  <input type="radio" class="w-3 h-3 text-blue-600" name="plying_time" value="${pt}" ${isSel ? 'checked' : ''} onchange="handleLiveInputChange('plying_time', this.value)"/>
                  <span>${pt.replace('&', '&amp;')}</span>
                </label>
              `;
            }).join('')}
          </div>
        </div>
      </div>
    </div>
            <!-- 3. STATUTORY SCANTLINGS TABLES (ORGANIZED BY STATUTORY GROUP) -->
    <div class="mb-6 space-y-4">
      <!-- Group Filter & Search Toolbar (Exact dropdown structure from user image) -->
      <div class="bg-white p-3 rounded border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-2.5 flex-1 min-w-[280px]">
          <span class="text-xs font-bold text-slate-700 uppercase tracking-wide whitespace-nowrap">Filter Group:</span>
          <select 
            id="dash-group-filter-select" 
            onchange="onDashTableGroupFilter(this.value)" 
            class="border border-blue-300 rounded px-3 py-1.5 text-xs font-semibold text-slate-900 bg-blue-50/40 hover:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 max-w-[360px] truncate shadow-2xs"
          >
            <option value="ALL" ${dashTableGroupFilter === 'ALL' ? 'selected' : ''}>All Statutory Groups (${(appState.calculation_brain || []).length} Components)</option>
            ${(() => {
              const brain = appState.calculation_brain || [];
              const allGroups = [];
              brain.forEach(b => {
                const g = b.category || b.group;
                if (g && !allGroups.includes(g)) allGroups.push(g);
              });
              return allGroups.map(g => {
                const cleanName = (g || '').split('(')[0].replace(/GROUP \d+:\s*/i, '').trim();
                return `<option value="${g}" ${dashTableGroupFilter === g ? 'selected' : ''}>${cleanName}</option>`;
              }).join('');
            })()}
          </select>
        </div>

        <div class="flex items-center gap-3">
          <div class="relative">
            <input 
              type="text" 
              placeholder="Search component or rule..." 
              value="${dashTableSearchQuery}"
              oninput="onDashTableSearch(this.value)"
              class="border border-slate-300 rounded px-2.5 py-1 text-xs text-slate-800 w-64 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
            />
            ${dashTableSearchQuery ? `
              <button onclick="onDashTableSearch('')" class="absolute right-2 top-1 text-xs text-slate-400 hover:text-slate-600">×</button>
            ` : ''}
          </div>

          <span class="badge-comp text-xs px-2.5 py-1 font-bold">
            ${stats.compliant_items || (appState.calculation_brain || []).length} / ${stats.total_items || (appState.calculation_brain || []).length} COMPLIED (${stats.compliance_pct || 100}%)
          </span>
        </div>
      </div>

      <!-- Quick Group Navigation Horizontal Pills -->
      <div class="flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px]">
        <button 
          type="button" 
          onclick="onDashTableGroupFilter('ALL')" 
          class="px-2.5 py-1 rounded font-semibold whitespace-nowrap transition border ${dashTableGroupFilter === 'ALL' ? 'bg-blue-600 text-white border-blue-600 shadow-2xs' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'}"
        >
          All Groups (${(appState.calculation_brain || []).length})
        </button>
        ${(() => {
          const brain = appState.calculation_brain || [];
          const allGroups = [];
          brain.forEach(b => {
            const g = b.category || b.group;
            if (g && !allGroups.includes(g)) allGroups.push(g);
          });
          return allGroups.map((g, idx) => {
            const cleanName = (g || '').split('(')[0].replace(/GROUP \d+:\s*/i, '').trim();
            const isSel = (dashTableGroupFilter === g);
            return `
              <button 
                type="button" 
                onclick="onDashTableGroupFilter('${g.replace(/'/g, "\\'")}')" 
                class="px-2 py-1 rounded font-medium whitespace-nowrap transition border ${isSel ? 'bg-blue-600 text-white border-blue-600 shadow-2xs font-semibold' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}"
                title="${g}"
              >
                G${idx + 1}: ${cleanName}
              </button>
            `;
          }).join('');
        })()}
      </div>

      <!-- Dynamic Statutory Group Cards & Tables -->
      ${(() => {
        const brain = appState.calculation_brain || [];
        const allGroups = [];
        brain.forEach(b => {
          const g = b.category || b.group;
          if (g && !allGroups.includes(g)) allGroups.push(g);
        });

        // Filter groups according to user selection
        const targetGroups = (dashTableGroupFilter === 'ALL')
          ? allGroups
          : allGroups.filter(g => g === dashTableGroupFilter);

        if (targetGroups.length === 0) {
          return `<div class="p-6 text-center text-xs text-slate-500 bg-white rounded border border-slate-200">No statutory groups match the selected filter.</div>`;
        }

        return targetGroups.map(grpName => {
          let grpItems = brain.filter(b => (b.category || b.group) === grpName);

          // Search query filter
          if (dashTableSearchQuery) {
            const q = dashTableSearchQuery.toLowerCase();
            grpItems = grpItems.filter(b => {
              const nameMatch = (b.name || b.desc || '').toLowerCase().includes(q);
              const ruleMatch = (b.table_ref || b.rule || '').toLowerCase().includes(q);
              const idMatch = String(b.id || '').toLowerCase().includes(q);
              return nameMatch || ruleMatch || idMatch;
            });
          }

          if (grpItems.length === 0) return '';

          const compCount = grpItems.filter(it => it.status === 'COMPLIANT' || it.status === 'COMPLIED').length;
          const isAllComp = compCount === grpItems.length;
          const cleanGrpTitle = (grpName || '').split('(')[0].trim();
          const grpSlug = grpName.toLowerCase().replace(/[^a-z0-9]/g, '_');

          const plates = grpItems.filter(it => it.type === 'plate');
          const stiffs = grpItems.filter(it => it.type === 'stiffener');
          const others = grpItems.filter(it => it.type !== 'plate' && it.type !== 'stiffener');

          return `
            <div class="bg-white rounded border border-slate-200 overflow-hidden shadow-xs mb-4">
              <!-- Group Header Bar -->
              <div class="bg-slate-100/90 px-3.5 py-2.5 flex items-center justify-between border-b border-slate-200">
                <div class="flex items-center gap-2.5">
                  <span class="text-xs font-bold text-slate-800 tracking-wide">${cleanGrpTitle}</span>
                  <span class="text-[11px] text-slate-500 font-medium">(${grpItems.length} items)</span>
                </div>
                <span id="group-badge-${grpSlug}" class="px-2 py-0.5 rounded text-[11px] font-bold ${isAllComp ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-amber-100 text-amber-800 border border-amber-200'}">
                  ${compCount} / ${grpItems.length} COMPLIED
                </span>
              </div>

              <div class="p-3 space-y-4">
                <!-- 1. Plating Sub-Table (if group has plates) -->
                ${plates.length > 0 ? `
                  <div>
                    ${stiffs.length > 0 || others.length > 0 ? `
                      <div class="text-[11px] font-bold text-slate-700 uppercase tracking-wide mb-1.5 flex items-center gap-2">
                        <span class="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
                        Hull Plating Scantlings (${plates.length} Plates)
                      </div>
                    ` : ''}
                    <div class="overflow-x-auto">
                      <table class="compact-table w-full">
                        <thead>
                          <tr class="bg-slate-50">
                            <th style="width: 32px;" class="text-center">No.</th>
                            <th>Plating Member Description</th>
                            <th style="width: 85px;" class="text-center">Rule Ref</th>
                            <th style="width: 75px;" class="text-right">Baseline</th>
                            <th style="width: 55px;" class="text-center">Factor (kt)</th>
                            <th style="width: 80px;" class="text-right">Required</th>
                            <th style="width: 105px;" class="text-center bg-slate-100/60">Provided [mm]</th>
                            <th style="width: 50px;" class="text-center">Unit</th>
                            <th style="width: 80px;" class="text-right">Margin (+/-)</th>
                            <th style="width: 75px;" class="text-right">Margin %</th>
                            <th style="width: 85px;" class="text-center">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          ${plates.map((m, idx) => {
                            const isComp = (m.status === 'COMPLIANT' || m.status === 'COMPLIED');
                            const baseVal = typeof m.baseline === 'number' ? m.baseline.toFixed(2) : (m.baseline || '-');
                            const factVal = typeof m.factor === 'number' ? m.factor.toFixed(2) : (m.factor || (inp.effective_kt || 1.20).toFixed(2));
                            const reqVal = typeof m.rreq === 'number' ? m.rreq.toFixed(2) : (m.rreq || '-');
                            const provVal = m.dact !== undefined ? m.dact : (parseFloat(baseVal) || 0);
                            const margin = typeof m.margin === 'number' ? m.margin : (provVal - (parseFloat(reqVal) || 0));
                            const marginPct = (parseFloat(reqVal) > 0) ? ((margin / parseFloat(reqVal)) * 100).toFixed(1) + '%' : '-';

                            return `
                              <tr id="plate-row-${m.id}">
                                <td class="text-center text-slate-400 font-semibold">${idx + 1}</td>
                                <td class="font-medium text-slate-800">${m.name || m.desc || ''}</td>
                                <td class="text-center text-slate-500 text-[11px] font-mono">${m.table_ref || m.rule || '-'}</td>
                                <td id="plate-baseline-${m.id}" class="text-right text-slate-600 font-mono">${baseVal}</td>
                                <td id="plate-factor-${m.id}" class="text-center font-mono font-bold text-slate-700">${factVal}</td>
                                <td id="plate-req-${m.id}" class="text-right font-medium text-slate-700 font-mono">${reqVal}</td>
                                <td class="text-center p-1 bg-slate-50/50">
                                  <input 
                                    type="number" 
                                    step="0.5" 
                                    id="plate-input-${m.id}" 
                                    class="compact-input text-center font-mono font-bold text-slate-900 w-24 mx-auto" 
                                    value="${provVal}" 
                                    oninput="handleLivePlateProvidedChange('${m.id}', this.value)"
                                  />
                                </td>
                                <td class="text-center text-slate-500 text-[11px]">${m.unit || 'mm'}</td>
                                <td id="plate-margin-${m.id}" class="text-right font-mono text-[11px] ${margin >= 0 ? 'text-emerald-700 font-semibold' : 'text-rose-700 font-semibold'}">
                                  ${(margin >= 0 ? '+' : '') + margin.toFixed(2)}
                                </td>
                                <td id="plate-margin-pct-${m.id}" class="text-right font-mono text-[11px] text-slate-600">
                                  ${marginPct}
                                </td>
                                <td class="text-center">
                                  <span id="plate-status-${m.id}" class="${isComp ? 'badge-comp' : 'badge-def'}">
                                    ${isComp ? 'COMPLIED' : 'DEFICIENT'}
                                  </span>
                                </td>
                              </tr>
                            `;
                          }).join('')}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ` : ''}

                <!-- 2. Stiffeners Sub-Table (if group has stiffeners) -->
                ${stiffs.length > 0 ? `
                  <div>
                    ${plates.length > 0 || others.length > 0 ? `
                      <div class="text-[11px] font-bold text-slate-700 uppercase tracking-wide mb-1.5 flex items-center gap-2">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                        Stiffeners &amp; Framing Specifications (${stiffs.length} Profiles)
                      </div>
                    ` : ''}
                    <div class="overflow-x-auto">
                      <table class="compact-table w-full">
                        <thead>
                          <tr class="bg-slate-50">
                            <th style="width: 32px;" class="text-center">No.</th>
                            <th>Stiffener Member Description</th>
                            <th style="width: 80px;" class="text-center">Rule Ref</th>
                            <th style="width: 65px;" class="text-center">Profile</th>
                            <th style="width: 85px;" class="text-center">Web Depth [mm]</th>
                            <th style="width: 75px;" class="text-center">Web Thk [mm]</th>
                            <th style="width: 85px;" class="text-center">Flange Width [mm]</th>
                            <th style="width: 75px;" class="text-center">Flange Thk [mm]</th>
                            <th style="width: 65px;" class="text-center">Plate tp</th>
                            <th style="width: 55px;" class="text-center">Factor (kz)</th>
                            <th style="width: 85px;" class="text-right">Req SM [cm³]</th>
                            <th style="width: 100px;" class="text-right bg-blue-50/50">Provided SM [cm³]</th>
                            <th style="width: 80px;" class="text-right">Margin (+/-)</th>
                            <th style="width: 85px;" class="text-center">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          ${stiffs.map((m, idx) => {
                            const isComp = (m.status === 'COMPLIANT' || m.status === 'COMPLIED');
                            const reqSm = typeof m.rreq === 'number' ? m.rreq : (parseFloat(m.rreq) || 0);
                            const provSm = typeof m.dact === 'number' ? m.dact : (parseFloat(m.dact) || 0);
                            const margin = typeof m.margin === 'number' ? m.margin : (provSm - reqSm);
                            const kFactor = typeof m.factor === 'number' ? m.factor.toFixed(2) : (m.factor || (inp.effective_kz || 1.25).toFixed(2));
                            const pType = m.profile_type || 'L';
                            const isFB = pType === 'FB';

                            return `
                              <tr id="stiff-row-${m.id}">
                                <td class="text-center text-slate-400 font-semibold">${idx + 1}</td>
                                <td class="font-medium text-slate-800">${m.name || m.desc || ''}</td>
                                <td class="text-center text-slate-500 text-[11px] font-mono">${m.table_ref || m.rule || '-'}</td>
                                <td class="text-center p-0.5">
                                  <select 
                                    class="compact-select text-center font-bold font-mono text-xs w-14 mx-auto py-0.5" 
                                    onchange="handleLiveStiffenerTypeChange('${m.id}', this.value)"
                                  >
                                    <option value="L" ${pType === 'L' ? 'selected' : ''}>L</option>
                                    <option value="T" ${pType === 'T' ? 'selected' : ''}>T</option>
                                    <option value="FB" ${pType === 'FB' ? 'selected' : ''}>FB</option>
                                  </select>
                                </td>
                                <td>
                                  <input 
                                    type="number" 
                                    step="5" 
                                    id="stiff-hw-${m.id}" 
                                    class="compact-input text-center font-mono font-semibold" 
                                    value="${m.web_depth || 150}" 
                                    oninput="handleLiveStiffenerDimChange('${m.id}', 'web_depth', this.value)"
                                  />
                                </td>
                                <td>
                                  <input 
                                    type="number" 
                                    step="0.5" 
                                    id="stiff-tw-${m.id}" 
                                    class="compact-input text-center font-mono font-semibold" 
                                    value="${m.web_thk || 10}" 
                                    oninput="handleLiveStiffenerDimChange('${m.id}', 'web_thk', this.value)"
                                  />
                                </td>
                                <td>
                                  <input 
                                    type="number" 
                                    step="5" 
                                    id="stiff-bf-${m.id}" 
                                    class="compact-input text-center font-mono font-semibold ${isFB ? 'opacity-40 bg-slate-100 cursor-not-allowed' : ''}" 
                                    ${isFB ? 'disabled' : ''} 
                                    value="${isFB ? 0 : (m.flange_width || 100)}" 
                                    oninput="handleLiveStiffenerDimChange('${m.id}', 'flange_width', this.value)"
                                  />
                                </td>
                                <td>
                                  <input 
                                    type="number" 
                                    step="0.5" 
                                    id="stiff-tf-${m.id}" 
                                    class="compact-input text-center font-mono font-semibold ${isFB ? 'opacity-40 bg-slate-100 cursor-not-allowed' : ''}" 
                                    ${isFB ? 'disabled' : ''} 
                                    value="${isFB ? 0 : (m.flange_thk || 10)}" 
                                    oninput="handleLiveStiffenerDimChange('${m.id}', 'flange_thk', this.value)"
                                  />
                                </td>
                                <td id="stiff-tp-${m.id}" class="text-center font-mono text-[11px] text-slate-600">
                                  ${m.welded_plate_thickness !== undefined ? m.welded_plate_thickness.toFixed(1) : '-'}
                                </td>
                                <td id="stiff-factor-${m.id}" class="text-center font-mono text-[11px] font-bold text-slate-700">${kFactor}</td>
                                <td id="stiff-req-${m.id}" class="text-right font-mono font-medium text-slate-700">${reqSm.toFixed(2)}</td>
                                <td id="stiff-prov-${m.id}" class="text-right font-mono font-bold text-blue-700 bg-blue-50/40">${provSm.toFixed(2)}</td>
                                <td id="stiff-margin-${m.id}" class="text-right font-mono text-[11px] ${margin >= 0 ? 'text-emerald-700 font-semibold' : 'text-rose-700 font-semibold'}">
                                  ${(margin >= 0 ? '+' : '') + margin.toFixed(2)}
                                </td>
                                <td class="text-center">
                                  <span id="stiff-status-${m.id}" class="${isComp ? 'badge-comp' : 'badge-def'}" ${m.components && m.components.length > 0 ? `title="${m.components.map(c => `${c.name}: Prov ${c.prov !== undefined ? c.prov : '-' } vs Req ${c.rreq} ${c.unit} (${c.margin >= 0 ? '+' : ''}${c.margin}) [${c.status}]`).join(' | ')}"` : ''}>
                                    ${isComp ? 'COMPLIED' : 'DEFICIENT'}
                                  </span>
                                </td>
                              </tr>
                            `;
                          }).join('')}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ` : ''}

                <!-- 3. Statutory Dimensions & Equipment Sub-Table (if group has other items) -->
                ${others.length > 0 ? `
                  <div>
                    ${plates.length > 0 || stiffs.length > 0 ? `
                      <div class="text-[11px] font-bold text-slate-700 uppercase tracking-wide mb-1.5 flex items-center gap-2">
                        <span class="w-1.5 h-1.5 rounded-full bg-amber-600"></span>
                        Statutory Rules, Limits &amp; Equipment (${others.length} Components)
                      </div>
                    ` : ''}
                    <div class="overflow-x-auto">
                      <table class="compact-table w-full">
                        <thead>
                          <tr class="bg-slate-50">
                            <th style="width: 32px;" class="text-center">No.</th>
                            <th>Component / Rule Description</th>
                            <th style="width: 85px;" class="text-center">Rule Ref</th>
                            <th style="width: 80px;" class="text-right">Baseline</th>
                            <th style="width: 55px;" class="text-center">Factor</th>
                            <th style="width: 80px;" class="text-right">Required</th>
                            <th style="width: 105px;" class="text-center bg-slate-100/60">Provided</th>
                            <th style="width: 50px;" class="text-center">Unit</th>
                            <th style="width: 80px;" class="text-right">Margin (+/-)</th>
                            <th style="width: 85px;" class="text-center">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          ${others.map((m, idx) => {
                            const isComp = (m.status === 'COMPLIANT' || m.status === 'COMPLIED');
                            const baseVal = typeof m.baseline === 'number' ? m.baseline.toFixed(2) : (m.baseline || '-');
                            const factVal = typeof m.factor === 'number' ? m.factor.toFixed(2) : (m.factor || '1.00');
                            const reqVal = typeof m.rreq === 'number' ? m.rreq.toFixed(2) : (m.rreq || '-');
                            const provVal = m.dact !== undefined ? m.dact : (parseFloat(baseVal) || 0);
                            const margin = typeof m.margin === 'number' ? m.margin : (provVal - (parseFloat(reqVal) || 0));

                            return `
                              <tr id="other-row-${m.id}">
                                <td class="text-center text-slate-400 font-semibold">${idx + 1}</td>
                                <td class="font-medium text-slate-800">${m.name || m.desc || ''}</td>
                                <td class="text-center text-slate-500 text-[11px] font-mono">${m.table_ref || m.rule || '-'}</td>
                                <td id="other-baseline-${m.id}" class="text-right text-slate-600 font-mono">${baseVal}</td>
                                <td id="other-factor-${m.id}" class="text-center font-mono font-bold text-slate-700">${factVal}</td>
                                <td id="other-req-${m.id}" class="text-right font-medium text-slate-700 font-mono">${reqVal}</td>
                                <td class="text-center p-1 bg-slate-50/50">
                                  <input 
                                    type="number" 
                                    step="0.1" 
                                    id="other-input-${m.id}" 
                                    class="compact-input text-center font-mono font-bold text-slate-900 w-24 mx-auto" 
                                    value="${provVal}" 
                                    oninput="handleLiveOtherProvidedChange('${m.id}', this.value)"
                                  />
                                </td>
                                <td class="text-center text-slate-500 text-[11px]">${m.unit || ''}</td>
                                <td id="other-margin-${m.id}" class="text-right font-mono text-[11px] ${margin >= 0 ? 'text-emerald-700 font-semibold' : 'text-rose-700 font-semibold'}">
                                  ${(margin >= 0 ? '+' : '') + margin.toFixed(2)}
                                </td>
                                <td class="text-center">
                                  <span id="other-status-${m.id}" class="${isComp ? 'badge-comp' : 'badge-def'}">
                                    ${isComp ? 'COMPLIED' : 'DEFICIENT'}
                                  </span>
                                </td>
                              </tr>
                            `;
                          }).join('')}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ` : ''}
              </div>
            </div>
          `;
        }).join('');
      })()}
    </div>
  `;
}

// Live In-Place Calculations & Updates (No input blur or focus loss)
function handleVesselTypeChange(val) {
  appState.dashboard_inputs.vessel_type = val;
  const sel = document.getElementById('select-vessel-type');
  if (sel && sel.value !== val) sel.value = val;
  const vtRadios = document.querySelectorAll('input[name="vessel_type_radio"]');
  vtRadios.forEach(r => {
    r.checked = (r.value === val);
  });
  recalculateAll(appState);
  renderDashboard();
  triggerAutosaveDebounced();
}

function handleLiveInputChange(field, val) {
  appState.dashboard_inputs[field] = val;
  if (field === 'hull_material') {
    delete appState.dashboard_inputs.custom_kt;
    delete appState.dashboard_inputs.custom_kz;
    appState.dashboard_inputs.factor_mode = 'auto';
  }
  if (field === 'vessel_type') {
    const sel = document.getElementById('select-vessel-type');
    if (sel && sel.value !== val) sel.value = val;
    const vtRadios = document.querySelectorAll('input[name="vessel_type_radio"]');
    vtRadios.forEach(r => {
      r.checked = (r.value === val);
    });
  }
  recalculateAll(appState);
  updateTopStats();
  updateLiveDashboardDisplays();
  triggerAutosaveDebounced();
}

function handleInputChange(field, val) {
  handleLiveInputChange(field, val);
}

function handleHullTypeChange(val) {
  if (val === 'Single Bottom') val = 'Single Hull';
  appState.dashboard_inputs.hull_type = val;
  recalculateAll(appState);
  renderDashboard();
  triggerAutosaveDebounced();
}

function handleRouteChange(val) {
  appState.dashboard_inputs.route = val;
  appState.dashboard_inputs.proposed_route = val;
  appState.dashboard_inputs.factor_mode = 'auto';
  delete appState.dashboard_inputs.custom_kt;
  delete appState.dashboard_inputs.custom_kz;

  const mat = String(appState.dashboard_inputs.hull_material || '').toLowerCase();
  const isOldSteel = mat.includes('old');
  const rLower = String(val).toLowerCase();
  let kt = 1.00;
  let kz = 1.00;
  let ruleDesc = "Inland Calm Water (1.00 / 1.00)";

  if (isOldSteel) {
    kt = 1.40;
    kz = 1.40;
    ruleDesc = "Statutory Rule for Steel (Old): kt=1.40, kz=1.40";
  } else if (rLower.includes('bay') || rLower.includes('coastal')) {
    kt = 1.20;
    kz = 1.25;
    ruleDesc = "Rule 4(3) SRO 308 (Bay: 1.20 / 1.25)";
  } else if (rLower.includes('seasonal crossing')) {
    kt = 1.15;
    kz = 1.20;
    ruleDesc = "Seasonal Coastal Crossing (1.15 / 1.20)";
  } else if (rLower.includes('rough')) {
    kt = 1.10;
    kz = 1.15;
    ruleDesc = "Inland Rough Water (1.10 / 1.15)";
  } else if (rLower.includes('round seasonal')) {
    kt = 1.05;
    kz = 1.10;
    ruleDesc = "Round Seasonal Regulation (1.05 / 1.10)";
  } else {
    kt = 1.00;
    kz = 1.00;
    ruleDesc = "Inland Calm Water (1.00 / 1.00)";
  }

  appState.dashboard_inputs.effective_kt = kt;
  appState.dashboard_inputs.effective_kz = kz;
  appState.dashboard_inputs.factor_rule_desc = ruleDesc;

  recalculateAll(appState);
  updateTopStats();
  updateLiveDashboardDisplays();
  triggerAutosaveDebounced();
}

function handleManualFactorChange(which, val) {
  const num = parseFloat(val);
  if (isNaN(num) || num <= 0) return;

  appState.dashboard_inputs.factor_mode = 'manual';
  if (which === 'kt') {
    appState.dashboard_inputs.effective_kt = num;
    appState.dashboard_inputs.custom_kt = num;
  } else if (which === 'kz') {
    appState.dashboard_inputs.effective_kz = num;
    appState.dashboard_inputs.custom_kz = num;
  }
  const currKt = appState.dashboard_inputs.effective_kt || 1.20;
  const currKz = appState.dashboard_inputs.effective_kz || 1.25;
  appState.dashboard_inputs.factor_rule_desc = `Manual Override (${currKt.toFixed(2)} / ${currKz.toFixed(2)})`;

  recalculateAll(appState);
  updateTopStats();
  updateLiveDashboardDisplays();
  triggerAutosaveDebounced();
}

function handleFactorRuleChange(val) {
  handleRouteChange(val);
}

function handleLiveProfileChange(profileId, prop, val) {
  const p = appState.stiffener_profiles.find(x => x.id === profileId);
  if (p) {
    p[prop] = val;
    // Live-sync dimensions to linked lightship angle items
    (appState.lightship_angles || []).forEach(a => {
      if (a.profile_id === profileId && !a.dim_customized) {
        if (prop === 'web_depth') a.l_dim = val;
        else if (prop === 'flange_width') a.b_dim = val;
        else if (prop === 'web_thk') a.t = val;
      }
    });
    recalculateAll(appState);
    updateTopStats();
    updateLiveDashboardDisplays();
    if (typeof updateLiveLightshipDisplays === 'function') {
      updateLiveLightshipDisplays();
    } else if (typeof renderLightship === 'function' && typeof currentTab !== 'undefined' && currentTab === 'lightship') {
      renderLightship();
    }
    triggerAutosaveDebounced();
  }
}

function handleProfileChange(profileId, prop, val) {
  handleLiveProfileChange(profileId, prop, val);
}

function handleLiveOtherProvidedChange(memberId, rawVal) {
  if (!appState) return;
  const s = String(rawVal).trim().replace(',', '.');
  const num = (s === '' || s === '-' || s === '.') ? 0 : (parseFloat(s) || 0);

  if (!appState.custom_brain_dact) appState.custom_brain_dact = {};
  appState.custom_brain_dact[memberId] = num;
  appState.dashboard_inputs[memberId] = num;

  const brain = appState.calculation_brain || [];
  const m = brain.find(x => x.id === memberId);
  if (m) {
    m.dact = num;
  }

  recalculateAll(appState);
  updateTopStats();
  updateLiveDashboardDisplays();
  triggerAutosaveDebounced();
}

function handleLivePlateProvidedChange(memberId, rawVal) {
  if (!appState) return;
  const s = String(rawVal).trim().replace(',', '.');
  const num = (s === '' || s === '-' || s === '.') ? 0 : (parseFloat(s) || 0);

  if (!appState.custom_brain_dact) appState.custom_brain_dact = {};
  appState.custom_brain_dact[memberId] = num;
  appState.dashboard_inputs[memberId] = num;

  const brain = appState.calculation_brain || [];
  const m = brain.find(x => x.id === memberId);
  if (m) {
    if (m.bound_plate_key) {
      appState.dashboard_inputs[m.bound_plate_key] = num;
      const chk = appState.scantling_checklist || [];
      const chkItem = chk.find(c => c.bound_plate_key === m.bound_plate_key);
      if (chkItem) chkItem.provided = num;
    }
    m.dact = num;
  }

  recalculateAll(appState);
  updateTopStats();
  updateLiveDashboardDisplays();
  triggerAutosaveDebounced();
}

function handleLiveStiffenerTypeChange(memberId, typeVal) {
  if (!appState || !memberId) return;
  appState.stiffener_custom_dims = appState.stiffener_custom_dims || {};
  appState.stiffener_custom_dims[memberId] = appState.stiffener_custom_dims[memberId] || {};
  appState.stiffener_custom_dims[memberId].profile_type = typeVal;

  if (typeVal === 'FB') {
    appState.stiffener_custom_dims[memberId].flange_width = 0;
    appState.stiffener_custom_dims[memberId].flange_thk = 0;
  } else {
    const curBf = appState.stiffener_custom_dims[memberId].flange_width;
    const curTf = appState.stiffener_custom_dims[memberId].flange_thk;
    if (!curBf || curBf <= 0) {
      appState.stiffener_custom_dims[memberId].flange_width = 100;
    }
    if (!curTf || curTf <= 0) {
      appState.stiffener_custom_dims[memberId].flange_thk = 10;
    }
  }

  recalculateAll(appState);
  updateTopStats();
  renderDashboard();
  triggerAutosaveDebounced();
}

function handleLiveStiffenerDimChange(memberId, field, rawVal) {
  if (!appState || !memberId) return;
  appState.stiffener_custom_dims = appState.stiffener_custom_dims || {};
  appState.stiffener_custom_dims[memberId] = appState.stiffener_custom_dims[memberId] || {};

  const s = String(rawVal).trim().replace(',', '.');
  const num = (s === '' || s === '-' || s === '.') ? 0 : (parseFloat(s) || 0);

  appState.stiffener_custom_dims[memberId][field] = num;
  delete appState.stiffener_custom_dims[memberId].custom_z;

  recalculateAll(appState);
  updateTopStats();
  updateLiveDashboardDisplays();
  triggerAutosaveDebounced();
}

function handleLiveProvidedScantlingChange(no, val) {
  const mapping = {
    1: 't_keel', 2: 't_bottom', 3: 't_bilge', 4: 't_side',
    5: 't_deck_hatch', 6: 't_deck_all', 15: 't_bhd',
    17: 't_hatch_long', 18: 't_hatch_trans', 19: 't_hatch_cover',
    21: 't_inner_bottom'
  };
  const key = mapping[no];
  if (key) {
    appState.dashboard_inputs[key] = val;
  }
  const item = (appState.scantling_checklist || []).find(c => c.no === no);
  if (item) item.provided = val;

  // Sync to matching brain item
  if (key && appState.calculation_brain) {
    const bItem = appState.calculation_brain.find(b => b.bound_plate_key === key);
    if (bItem) {
      bItem.dact = val;
      if (!appState.custom_brain_dact) appState.custom_brain_dact = {};
      appState.custom_brain_dact[bItem.id] = val;
      const bInp = document.getElementById(`brain-input-${bItem.item}`);
      if (bInp && document.activeElement !== bInp) bInp.value = val;
      const mInp = document.getElementById(`dash-main-input-${bItem.item}`);
      if (mInp && document.activeElement !== mInp) mInp.value = val;
    }
  }

  recalculateAll(appState);
  updateTopStats();
  updateLiveDashboardDisplays();
  triggerAutosaveDebounced();
}

function handleProvidedScantlingChange(no, val) {
  handleLiveProvidedScantlingChange(no, val);
}

function updateLiveDashboardDisplays() {
  if (!appState) return;
  const inp = appState.dashboard_inputs || {};
  const stats = appState.summary_stats || {};
  const chk = appState.scantling_checklist || [];
  const profiles = appState.stiffener_profiles || [];
  const ls = appState.lightship_summary || {};
  const hType = inp.hull_type || 'Double Bottom';
  const isSingleHull = hType === 'Single Hull';
  const brainItems = appState.calculation_brain || [];

  // 1. Top Summary Banner
  const statStatus = document.getElementById('summary-statutory-status');
  if (statStatus) statStatus.textContent = stats.overall_status || 'COMPLIANT';

  // Sync radio selections and active styles dynamically
  const vtVal = inp.vessel_type || 'Steel Body Cargo Vessel';
  const vtRadios = document.querySelectorAll('input[name="vessel_type_radio"]');
  vtRadios.forEach(r => {
    const isSel = (r.value === vtVal);
    r.checked = isSel;
    const parentLabel = r.closest('label');
    if (parentLabel) {
      parentLabel.className = isSel
        ? 'flex items-center gap-1.5 cursor-pointer p-0.5 rounded font-bold text-blue-900 bg-blue-100/60 px-1 py-0.5'
        : 'flex items-center gap-1.5 cursor-pointer p-0.5 rounded hover:bg-slate-100 text-slate-700';
    }
  });

  const hcRadios = document.querySelectorAll('input[name="hull_construction_radio"]');
  hcRadios.forEach(r => {
    const isSel = (r.value.toLowerCase() === (hType || '').toLowerCase());
    r.checked = isSel;
    const parentLabel = r.closest('label');
    if (parentLabel) {
      parentLabel.className = isSel
        ? 'flex items-center gap-1.5 cursor-pointer p-0.5 rounded font-bold text-blue-900 bg-blue-100/60 px-1 py-0.5'
        : 'flex items-center gap-1.5 cursor-pointer p-0.5 rounded hover:bg-slate-100 text-slate-700';
    }
  });

  const matVal = String(inp.hull_material || 'Steel (old)').toLowerCase();
  const matRadios = document.querySelectorAll('input[name="hull_material"]');
  matRadios.forEach(r => {
    const rVal = r.value.toLowerCase();
    const isSel = (matVal === rVal) || (rVal.includes('old') && matVal.includes('old')) || (rVal.includes('new') && matVal.includes('new'));
    r.checked = isSel;
    const parentLabel = r.closest('label');
    if (parentLabel) {
      parentLabel.className = isSel
        ? 'flex items-center gap-1.5 cursor-pointer p-0.5 rounded font-bold text-blue-900 bg-blue-100/60 px-1 py-0.5'
        : 'flex items-center gap-1.5 cursor-pointer p-0.5 rounded hover:bg-slate-100 text-slate-700';
    }
  });

  const routeVal = String(inp.proposed_route || inp.route || 'Inland & bay crossing');
  const isBay = routeVal.toLowerCase().includes('bay');
  const routeRadios = document.querySelectorAll('input[name="proposed_route"]');
  routeRadios.forEach(r => {
    const rLower = r.value.toLowerCase();
    const isSel = (rLower === routeVal.toLowerCase()) || (rLower.includes('bay') && isBay);
    r.checked = isSel;
    const parentLabel = r.closest('label');
    if (parentLabel) {
      parentLabel.className = isSel
        ? 'flex items-center gap-1.5 cursor-pointer p-0.5 rounded font-bold text-blue-900 bg-blue-100/60 px-1 py-0.5'
        : 'flex items-center gap-1.5 cursor-pointer p-0.5 rounded hover:bg-slate-100 text-slate-700';
    }
  });

  const plyVal = String(inp.plying_time || 'Day & Night');
  const plyRadios = document.querySelectorAll('input[name="plying_time"]');
  plyRadios.forEach(r => {
    const isSel = (r.value === plyVal) || (r.value.includes('&') && plyVal.includes('Day') && plyVal.includes('Night'));
    r.checked = isSel;
    const parentLabel = r.closest('label');
    if (parentLabel) {
      parentLabel.className = isSel
        ? 'flex items-center gap-2 cursor-pointer p-1 rounded font-bold text-blue-900 bg-blue-100/60'
        : 'flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-slate-100 text-slate-700';
    }
  });

  const routeHull = document.getElementById('summary-route-hull');
  if (routeHull) routeHull.innerHTML = `${inp.route || 'Bay Crossing'} • <b>${hType}</b>`;

  const chkScore = document.getElementById('summary-checklist-score');
  if (chkScore) chkScore.textContent = `${stats.checklist_complied} / ${stats.checklist_total} COMPLIED`;

  const brainScore = document.getElementById('summary-brain-score');
  if (brainScore) brainScore.textContent = `${stats.compliant_items} / ${stats.total_items} RULES PASS`;

  const brainPct = document.getElementById('summary-brain-pct');
  if (brainPct) brainPct.textContent = `Compliance Rate: ${stats.compliance_pct}%`;

  const lsWeight = document.getElementById('summary-lightship-weight');
  if (lsWeight) lsWeight.textContent = `${ls.total_lightship_tonne?.toFixed(1) || '903.8'} Tonnes`;

  const steelWeight = document.getElementById('summary-steel-weight');
  if (steelWeight) steelWeight.textContent = `Steel Plating + Angles: ${ls.total_steel_tonne?.toFixed(1) || '579.3'} t`;

  // 2. In-Place Live Updates for All Structural Members in Grouped Tables
  brainItems.forEach(m => {
    const isComp = (m.status === 'COMPLIANT' || m.status === 'COMPLIED');
    const reqVal = typeof m.rreq === 'number' ? m.rreq.toFixed(2) : (m.rreq || '-');
    const provVal = m.dact !== undefined ? m.dact : 0;
    const margVal = typeof m.margin === 'number' ? (m.margin >= 0 ? '+' : '') + m.margin.toFixed(2) : (m.margin || '-');

    if (m.type === 'plate') {
      const baseEl = document.getElementById(`plate-baseline-${m.id}`);
      if (baseEl) baseEl.textContent = typeof m.baseline === 'number' ? m.baseline.toFixed(2) : (m.baseline || '-');

      const factEl = document.getElementById(`plate-factor-${m.id}`);
      if (factEl) factEl.textContent = typeof m.factor === 'number' ? m.factor.toFixed(2) : (m.factor || '1.20');

      const reqEl = document.getElementById(`plate-req-${m.id}`);
      if (reqEl) reqEl.textContent = reqVal;

      const inputEl = document.getElementById(`plate-input-${m.id}`);
      if (inputEl && document.activeElement !== inputEl) inputEl.value = provVal;

      const margEl = document.getElementById(`plate-margin-${m.id}`);
      if (margEl) {
        margEl.textContent = margVal;
        margEl.className = `text-right font-mono text-[11px] ${m.margin >= 0 ? 'text-emerald-700 font-semibold' : 'text-rose-700 font-semibold'}`;
      }

      const pctEl = document.getElementById(`plate-margin-pct-${m.id}`);
      if (pctEl) {
        const pReq = parseFloat(reqVal);
        pctEl.textContent = pReq > 0 ? ((m.margin / pReq) * 100).toFixed(1) + '%' : '-';
      }

      const statEl = document.getElementById(`plate-status-${m.id}`);
      if (statEl) {
        statEl.textContent = isComp ? 'COMPLIED' : 'DEFICIENT';
        statEl.className = isComp ? 'badge-comp' : 'badge-def';
      }
    } else if (m.type === 'stiffener') {
      const factEl = document.getElementById(`stiff-factor-${m.id}`);
      if (factEl) factEl.textContent = typeof m.factor === 'number' ? m.factor.toFixed(2) : (m.factor || '1.25');

      const reqEl = document.getElementById(`stiff-req-${m.id}`);
      if (reqEl) reqEl.textContent = reqVal;

      const provEl = document.getElementById(`stiff-prov-${m.id}`);
      if (provEl) provEl.textContent = typeof m.dact === 'number' ? m.dact.toFixed(2) : (m.dact || '0.00');

      const tpEl = document.getElementById(`stiff-tp-${m.id}`);
      if (tpEl) tpEl.textContent = m.welded_plate_thickness !== undefined ? m.welded_plate_thickness.toFixed(1) : '-';

      const hwInp = document.getElementById(`stiff-hw-${m.id}`);
      if (hwInp && document.activeElement !== hwInp) hwInp.value = m.web_depth || 150;

      const twInp = document.getElementById(`stiff-tw-${m.id}`);
      if (twInp && document.activeElement !== twInp) twInp.value = m.web_thk || 10;

      const bfInp = document.getElementById(`stiff-bf-${m.id}`);
      if (bfInp && document.activeElement !== bfInp) bfInp.value = m.profile_type === 'FB' ? 0 : (m.flange_width || 100);

      const tfInp = document.getElementById(`stiff-tf-${m.id}`);
      if (tfInp && document.activeElement !== tfInp) tfInp.value = m.profile_type === 'FB' ? 0 : (m.flange_thk || 10);

      const margEl = document.getElementById(`stiff-margin-${m.id}`);
      if (margEl) {
        margEl.textContent = margVal;
        margEl.className = `text-right font-mono text-[11px] ${m.margin >= 0 ? 'text-emerald-700 font-semibold' : 'text-rose-700 font-semibold'}`;
      }

      const statEl = document.getElementById(`stiff-status-${m.id}`);
      if (statEl) {
        statEl.textContent = isComp ? 'COMPLIED' : 'DEFICIENT';
        statEl.className = isComp ? 'badge-comp' : 'badge-def';
        if (m.components && m.components.length > 0) {
          statEl.title = m.components.map(c => `${c.name}: Prov ${c.prov !== undefined ? c.prov : '-' } vs Req ${c.rreq} ${c.unit} (${c.margin >= 0 ? '+' : ''}${c.margin}) [${c.status}]`).join(' | ');
        } else {
          statEl.removeAttribute('title');
        }
      }
    } else {
      const baseEl = document.getElementById(`other-baseline-${m.id}`);
      if (baseEl) baseEl.textContent = typeof m.baseline === 'number' ? m.baseline.toFixed(2) : (m.baseline || '-');

      const factEl = document.getElementById(`other-factor-${m.id}`);
      if (factEl) factEl.textContent = typeof m.factor === 'number' ? m.factor.toFixed(2) : (m.factor || '1.00');

      const reqEl = document.getElementById(`other-req-${m.id}`);
      if (reqEl) reqEl.textContent = reqVal;

      const inputEl = document.getElementById(`other-input-${m.id}`);
      if (inputEl && document.activeElement !== inputEl) inputEl.value = provVal;

      const margEl = document.getElementById(`other-margin-${m.id}`);
      if (margEl) {
        margEl.textContent = margVal;
        margEl.className = `text-right font-mono text-[11px] ${m.margin >= 0 ? 'text-emerald-700 font-semibold' : 'text-rose-700 font-semibold'}`;
      }

      const statEl = document.getElementById(`other-status-${m.id}`);
      if (statEl) {
        statEl.textContent = isComp ? 'COMPLIED' : 'DEFICIENT';
        statEl.className = isComp ? 'badge-comp' : 'badge-def';
      }
    }
  });

  // 3. Update Group Card Badges
  const allGroups = [];
  brainItems.forEach(b => {
    const g = b.category || b.group;
    if (g && !allGroups.includes(g)) allGroups.push(g);
  });
  allGroups.forEach(g => {
    const gSlug = g.toLowerCase().replace(/[^a-z0-9]/g, '_');
    const badgeEl = document.getElementById(`group-badge-${gSlug}`);
    if (badgeEl) {
      const gItems = brainItems.filter(b => (b.category || b.group) === g);
      const gComp = gItems.filter(b => b.status === 'COMPLIANT' || b.status === 'COMPLIED').length;
      badgeEl.textContent = `${gComp} / ${gItems.length} COMPLIED`;
      badgeEl.className = `px-2 py-0.5 rounded text-[11px] font-bold ${gComp === gItems.length ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-amber-100 text-amber-800 border border-amber-200'}`;
    }
  });

  // 4. Global Score & Factor Inputs
  const brainBadge = document.getElementById('brain-summary-badge');
  if (brainBadge) {
    const pctStr = typeof stats.compliance_pct === 'number' ? stats.compliance_pct.toFixed(1) : (stats.compliance_pct || '100.0');
    brainBadge.textContent = `${stats.compliant_items || 0} / ${stats.total_items || 0} COMPLIANT (${pctStr}%)`;
  }

  const ktInp = document.getElementById('input-plate-factor');
  if (ktInp && document.activeElement !== ktInp) {
    ktInp.value = (inp.effective_kt !== undefined ? inp.effective_kt : 1.20).toFixed(2);
  }
  const kzInp = document.getElementById('input-stiffener-factor');
  if (kzInp && document.activeElement !== kzInp) {
    kzInp.value = (inp.effective_kz !== undefined ? inp.effective_kz : 1.25).toFixed(2);
  }
  const factorTag = document.getElementById('factor-rule-tag');
  if (factorTag) {
    factorTag.textContent = inp.factor_rule_desc || 'SRO 308 (Bay Crossing)';
  }
}


// ================= 2. COVER PAGE SECTION =================
function renderCoverPage() {
  const container = document.getElementById('tab-content-cover-page');
  if (!container) return;

  const inp = appState.dashboard_inputs || {};

  container.innerHTML = `
    <div class="max-w-4xl mx-auto bg-white p-8 rounded border border-slate-200 shadow-sm print:shadow-none print:border-none">
      <div class="text-center mb-8 pt-4">
        <h1 class="text-xl font-black text-slate-900 tracking-tight uppercase">STATUTORY HULL SCANTLINGS &amp; SECTION MODULUS CALCULATIONS</h1>
      </div>

      <div class="bg-slate-50 p-4 rounded border border-slate-200 mb-6">
        <div class="compact-title compact-title-primary">VESSEL PRINCIPAL PARTICULARS</div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs mt-3">
          <div><span class="text-slate-500 block">Vessel Name:</span><b class="text-slate-800">${inp.vessel_name}</b></div>
          <div><span class="text-slate-500 block">Vessel Type:</span><b>${inp.vessel_type}</b></div>
          <div><span class="text-slate-500 block">Construction Type:</span><b class="text-blue-700">${inp.hull_type || 'Double Bottom'}</b></div>
          <div><span class="text-slate-500 block">Operating Route:</span><b>${inp.route}</b></div>
          <div><span class="text-slate-500 block">Length (LOA):</span><b>${inp.loa} m</b></div>
          <div><span class="text-slate-500 block">Length BP (Lbp):</span><b>${inp.lbp} m</b></div>
          <div><span class="text-slate-500 block">Breadth MLD (B):</span><b>${inp.breadth} m</b></div>
          <div><span class="text-slate-500 block">Depth MLD (D):</span><b>${inp.depth} m</b></div>
          <div><span class="text-slate-500 block">Loaded Draft (d):</span><b>${inp.draft} m</b></div>
          <div><span class="text-slate-500 block">Displacement (Δ):</span><b>${inp.displacement} tonnes</b></div>
          <div><span class="text-slate-500 block">Block Coeff (Cb):</span><b>${inp.block_coeff}</b></div>
          <div><span class="text-slate-500 block">Frame Spacing (s):</span><b>${inp.frame_spacing} mm</b></div>
          <div><span class="text-slate-500 block">Registered Owner:</span><b>${inp.owner}</b></div>
          <div class="col-span-2"><span class="text-slate-500 block">Designer / Firm:</span><b>${inp.designer_name} / ${inp.designer_firm}</b></div>
          <div><span class="text-slate-500 block">Checked By:</span><b>${inp.checked_by}</b></div>
        </div>
      </div>

      <div class="mb-6">
        <div class="compact-title mb-2">TECHNICAL CALCULATION INDEX (SHEETS 01 TO 20)</div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-1.5 text-xs text-slate-700 bg-white p-3 border border-slate-200 rounded">
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 01 :</b> Side Transverse Frames</span><span class="text-emerald-700 font-semibold">Z = 221.5 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 11 :</b> Engine Room Center Keelson Area</span><span class="text-emerald-700 font-semibold">A = 91.8 cm²</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 02 :</b> Bottom Construction &amp; Floor Plate</span><span class="text-emerald-700 font-semibold">Z = 2447.2 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 12 :</b> Engine Room Heavy Web Frames</span><span class="text-emerald-700 font-semibold">Z = 1662.8 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 03 :</b> Transverse Frame Spacing Rule</span><span class="text-emerald-700 font-semibold">s ≤ 589.7 mm</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 13 :</b> Cargo Hatch Coaming &amp; Auxiliaries</span><span class="text-emerald-700 font-semibold">Z = 72.2 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 04 :</b> Side Shell Longitudinal Stringers</span><span class="text-emerald-700 font-semibold">Z = 509.8 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 14 :</b> Cargo Hatchway Transverse Beams</span><span class="text-emerald-700 font-semibold">Z = 72.2 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 05 :</b> Strength Deck Longitudinal Beams</span><span class="text-emerald-700 font-semibold">Z = 172.6 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 15 :</b> Cargo Hatchway Side Long. Beams</span><span class="text-emerald-700 font-semibold">Z = 72.2 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 06 :</b> Strength Deck Transverse Web Beams</span><span class="text-emerald-700 font-semibold">Z = 349.7 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 16 :</b> Steel Weather-tight Hatch Covers</span><span class="text-emerald-700 font-semibold">Z = 72.2 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 07 :</b> Main Deck Center Longitudinal Girder</span><span class="text-emerald-700 font-semibold">Z = 1009.0 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 17 :</b> Superstructure &amp; Deckhouse Stiffeners</span><span class="text-emerald-700 font-semibold">Z = 20.3 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 08 :</b> Collision Bulkhead Statutory Location</span><span class="text-emerald-700 font-semibold">3.49 - 5.59 m</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 18 :</b> Engine Casing Structural Stiffeners</span><span class="text-emerald-700 font-semibold">Z = 20.3 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 09 :</b> Aft Peak Watertight Bulkhead Stiffeners</span><span class="text-emerald-700 font-semibold">Z = 111.6 cm³</span></div>
          <div class="flex justify-between py-1 border-b border-slate-100"><span><b>Sheet 19 :</b> Poop &amp; Accommodation Deck Beams</span><span class="text-emerald-700 font-semibold">Z = 44.4 cm³</span></div>
          <div class="flex justify-between py-1"><span><b>Sheet 10 :</b> Cargo Hold &amp; Other Bulkhead Stiffeners</span><span class="text-emerald-700 font-semibold">Z = 111.6 cm³</span></div>
          <div class="flex justify-between py-1"><span><b>Sheet 20 :</b> Poop Deck Longitudinal Girders</span><span class="text-emerald-700 font-semibold">Z = 200.2 cm³</span></div>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-6 mt-8 pt-6 border-t border-slate-200 text-xs">
        <div>
          <div class="text-slate-500 mb-1">Prepared by Designer:</div>
          <div class="font-bold text-slate-800 text-sm">${inp.designer_name}</div>
          <div class="text-slate-600">${inp.designer_firm}</div>
          <div class="text-slate-500">${inp.firm_address}</div>
        </div>
        <div class="text-right">
          <div class="text-slate-500 mb-1">Verified for Statutory Compliance:</div>
          <div class="font-bold text-slate-800 text-sm">${inp.checked_by}</div>
          <div class="text-slate-600">Consulting Naval Architect</div>
          <div class="text-slate-500">Department of Shipping Approved</div>
        </div>
      </div>
    </div>
  `;
}

window.dashboardView = { render: renderDashboard };
