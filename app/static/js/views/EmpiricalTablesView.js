/**
 * EmpiricalTablesView - Renders 68 Statutory Empirical Rule Tables Browser
 */
function renderEmpiricalTables() {
  const container = document.getElementById('tab-content-empirical-tables');
  if (!container) return;

  const tables = appState.empirical_tables || [];
  const query = empiricalSearchQuery.toLowerCase().trim();
  const currentPart = empiricalFilterPart || 'all';

  const partsMeta = [
    { id: 'all', name_en: 'All Tables (1-67)' },
    { id: '1', name_en: 'Part 1: Plating & Stem (1-12)' },
    { id: '2', name_en: 'Part 2: Bottom & Frames (13-19)' },
    { id: '3', name_en: 'Part 3: Beams, Pillars, BHD (20-28)' },
    { id: '4', name_en: 'Part 4: Engine Room & Hatch (29-36)' },
    { id: '5', name_en: 'Part 5: Girders & Steering (37-44)' },
    { id: '6', name_en: 'Part 6: Anchors & Bulwarks (45-51)' },
    { id: '7', name_en: 'Part 7: Profiles & Electrical (52-67)' },
  ];

  const filtered = tables.filter(t => {
    if (currentPart !== 'all' && String(t.part_id) !== String(currentPart)) {
      return false;
    }
    if (query) {
      const idStr = String(t.id || '').toLowerCase();
      const matchTitle = (t.title || '').toLowerCase().includes(query);
      const matchTitleEn = (t.title_en || '').toLowerCase().includes(query);
      const matchRef = (t.ref || '').toLowerCase().includes(query);
      const matchPart = (t.part_name_en || '').toLowerCase().includes(query);
      const matchHeader = (t.headers || []).some(h => (h || '').toLowerCase().includes(query));
      if (!matchTitle && !matchTitleEn && !matchRef && !matchPart && !matchHeader && !idStr.includes(query)) {
        return false;
      }
    }
    return true;
  });

  container.innerHTML = `
    <!-- Top Action & Filter Bar -->
    <div class="bg-white p-3.5 rounded border border-slate-200 mb-4 shadow-sm">
      <div class="flex flex-wrap justify-between items-center gap-3 mb-3">
        <div>
          <div class="compact-title compact-title-primary mb-0">INLAND SHIPPING RULES 2001 — STATUTORY TABLES (TABLES 1 TO 67)</div>
          <div class="text-xs text-slate-500">
            Government Gazette Schedule (Pages 139 – 179) • Showing <b>${filtered.length}</b> of ${tables.length} Statutory Tables
          </div>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <!-- Jump to Table Dropdown -->
          <select 
            class="compact-select text-xs font-semibold border-slate-300 max-w-xs"
            onchange="jumpToEmpiricalTable(this.value)"
          >
            <option value="">Jump to Table (1 - 67)...</option>
            ${tables.map(t => `
              <option value="table-card-${t.id}">
                Table ${t.id} : ${t.title_en ? (t.title_en.length > 35 ? t.title_en.slice(0, 35) + '...' : t.title_en) : t.title}
              </option>
            `).join('')}
          </select>

          <!-- Search Input -->
          <div class="relative">
            <input 
              type="text" 
              placeholder="Search by rule, title, component..." 
              class="compact-input w-64 text-xs pr-6" 
              value="${empiricalSearchQuery}" 
              oninput="empiricalSearchQuery = this.value; renderEmpiricalTables();"
            />
            ${empiricalSearchQuery ? `
              <button onclick="empiricalSearchQuery = ''; renderEmpiricalTables();" class="absolute right-2 top-1 text-slate-400 hover:text-slate-600 text-xs">×</button>
            ` : ''}
          </div>
        </div>
      </div>

      <!-- Part Filter Pills -->
      <div class="flex items-center gap-1.5 overflow-x-auto pb-1 pt-1 border-t border-slate-100 text-xs scrollbar-thin">
        ${partsMeta.map(p => {
          const isActive = String(currentPart) === String(p.id);
          return `
            <button 
              onclick="empiricalFilterPart = '${p.id}'; renderEmpiricalTables();" 
              class="px-2.5 py-1 rounded-full whitespace-nowrap font-medium transition-colors text-[11px] ${
                isActive 
                  ? 'bg-blue-600 text-white font-bold shadow-xs' 
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900'
              }"
            >
              ${p.name_en}
            </button>
          `;
        }).join('')}
      </div>
    </div>

    <!-- Tables List -->
    <div class="space-y-4">
      ${filtered.length === 0 ? `
        <div class="bg-white p-8 rounded border border-slate-200 text-center text-slate-500 italic text-sm">
          No statutory scantling tables match your search query "${empiricalSearchQuery}".
        </div>
      ` : filtered.map(t => `
        <div id="table-card-${t.id}" class="bg-white p-4 rounded border border-slate-200 shadow-xs hover:border-slate-300 transition-colors scroll-mt-20">
          <!-- Card Header -->
          <div class="flex flex-wrap justify-between items-start gap-2 mb-2 pb-2 border-b border-slate-100">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="px-2 py-0.5 rounded text-[10.5px] font-bold bg-blue-100 text-blue-800">
                  Table ${t.id}
                </span>
                <span class="px-2 py-0.5 rounded text-[10.5px] font-medium bg-slate-100 text-slate-600">
                  ${t.part_name_en || ('Part ' + t.part_id)}
                </span>
                ${t.page ? `
                  <span class="text-[10.5px] text-slate-400 font-mono">
                    ${t.page}
                  </span>
                ` : ''}
              </div>
              <h3 class="text-sm font-bold text-slate-900 leading-snug">
                ${t.title_en || t.title}
              </h3>
            </div>
            ${t.ref ? `
              <span class="text-[11px] text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
                ${t.ref}
              </span>
            ` : ''}
          </div>

          <!-- Table Content -->
          <div class="overflow-x-auto my-2.5">
            <table class="compact-table w-full">
              ${t.headers && t.headers.length ? `
                <thead>
                  <tr class="bg-slate-50">
                    ${t.headers.map(h => `<th class="text-slate-700 font-bold text-[11px] py-1.5 px-2">${h}</th>`).join('')}
                  </tr>
                </thead>
              ` : ''}
              <tbody>
                ${t.rows && t.rows.length ? t.rows.map(r => `
                  <tr class="hover:bg-slate-50/60 border-b border-slate-100">
                    ${r.map((c, colIdx) => `
                      <td class="text-xs py-1.5 px-2 font-mono ${colIdx === 0 ? 'font-semibold text-slate-900' : 'text-slate-700'}">
                        ${c}
                      </td>
                    `).join('')}
                  </tr>
                `).join('') : `
                  <tr><td class="text-center py-2 text-slate-400 italic">No structured data rows</td></tr>
                `}
              </tbody>
            </table>
          </div>

          <!-- Notes & Conditions -->
          ${t.notes && t.notes.filter(n => !['**Statutory Notes & Guidelines:**', '**Guidelines:**', '**Notes:**'].includes(n.trim())).length ? `
            <div class="mt-2.5 text-[11px] text-slate-600 bg-amber-50/50 p-2.5 rounded border border-amber-200/60 space-y-1">
              <div class="font-bold text-amber-900 flex items-center gap-1">
                <span>Statutory Notes &amp; Guidelines:</span>
              </div>
              ${t.notes
                .filter(n => !['**Statutory Notes & Guidelines:**', '**Guidelines:**', '**Notes:**'].includes(n.trim()))
                .map(n => `<div class="pl-4 text-slate-700">• ${n}</div>`).join('')}
            </div>
          ` : ''}
        </div>
      `).join('')}
    </div>
  `;
}

function jumpToEmpiricalTable(elementId) {
  if (!elementId) return;
  const el = document.getElementById(elementId);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    el.classList.add('ring-2', 'ring-blue-500');
    setTimeout(() => {
      el.classList.remove('ring-2', 'ring-blue-500');
    }, 2000);
  }
}

window.jumpToEmpiricalTable = jumpToEmpiricalTable;

// Calculation brain logic is modularized in CalcBrainView.js


window.empiricalTablesView = { render: renderEmpiricalTables };