/**
 * VesselDbView - Complete Vessel Database & Archive Manager View
 * Allows browsing, searching, filtering, loading, exporting, and managing persistent vessel designs
 */

let vesselDbCache = [];
let vesselDbFilterType = 'all';
let vesselDbSearchQuery = '';
let vesselDbSortBy = 'updated_at';

async function fetchVesselsList() {
  try {
    const res = await fetch('/api/vessels');
    const data = await res.json();
    if (data.status === 'ok') {
      vesselDbCache = data.vessels || [];
      return vesselDbCache;
    }
  } catch (err) {
    console.error('Error fetching vessels list:', err);
  }
  return [];
}

async function renderVesselDb() {
  const container = document.getElementById('tab-content-vessel-db');
  if (!container) return;

  container.innerHTML = `
    <div class="p-8 text-center text-xs text-slate-500 bg-white border border-slate-200">
      Loading vessel database records...
    </div>
  `;

  const vessels = await fetchVesselsList();
  renderVesselDbContent(vessels);
}

function renderVesselDbContent(vessels) {
  const container = document.getElementById('tab-content-vessel-db');
  if (!container) return;

  vessels = vessels || vesselDbCache || [];

  // Filter by query
  let filtered = vessels;
  if (vesselDbSearchQuery) {
    const q = vesselDbSearchQuery.toLowerCase().trim();
    filtered = filtered.filter(v => 
      (v.vessel_name && v.vessel_name.toLowerCase().includes(q)) ||
      (v.owner && v.owner.toLowerCase().includes(q)) ||
      (v.yard_ref && v.yard_ref.toLowerCase().includes(q)) ||
      (v.vessel_type && v.vessel_type.toLowerCase().includes(q)) ||
      (v.notes && v.notes.toLowerCase().includes(q))
    );
  }

  // Filter by type
  if (vesselDbFilterType !== 'all') {
    filtered = filtered.filter(v => 
      v.vessel_type && v.vessel_type.toLowerCase().includes(vesselDbFilterType.toLowerCase())
    );
  }

  // Sort
  filtered.sort((a, b) => {
    if (vesselDbSortBy === 'vessel_name') {
      return (a.vessel_name || '').localeCompare(b.vessel_name || '');
    } else if (vesselDbSortBy === 'lbp') {
      return (b.particulars?.lbp || 0) - (a.particulars?.lbp || 0);
    } else if (vesselDbSortBy === 'lightship') {
      return (b.results_summary?.lightship_tonnes || 0) - (a.results_summary?.lightship_tonnes || 0);
    } else {
      // updated_at
      return new Date(b.updated_at || 0) - new Date(a.updated_at || 0);
    }
  });

  // Calculate statistics
  const totalCount = vessels.length;
  const compliantCount = vessels.filter(v => v.results_summary?.status === 'COMPLIANT').length;
  const avgLength = totalCount > 0 
    ? (vessels.reduce((acc, v) => acc + (parseFloat(v.particulars?.lbp) || 0), 0) / totalCount).toFixed(1)
    : '0.0';

  container.innerHTML = `
    <!-- Top Header Bar -->
    <div class="bg-white p-3.5 rounded border border-slate-200 mb-4 flex flex-wrap items-center justify-between gap-3 shadow-xs">
      <div>
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded bg-blue-600 flex items-center justify-center text-white font-black text-xs">
            DB
          </div>
          <div class="compact-title compact-title-primary mb-0">VESSEL DATABASE: ARCHIVED SHIP CALCULATIONS</div>
        </div>
        <div class="text-[11px] text-slate-500 mt-0.5">
          Persistent vessel engineering archive • Search, compare, and restore calculated vessel projects
        </div>
      </div>

      <div class="flex items-center gap-2">
        <button 
          onclick="openSaveVesselModal()" 
          class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-bold transition flex items-center gap-1.5 shadow-xs cursor-pointer"
          title="Save the currently active calculation as a new vessel in database"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          <span>Save Current Vessel to DB</span>
        </button>

        <label 
          class="px-3 py-1.5 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded text-xs font-semibold transition flex items-center gap-1.5 cursor-pointer"
          title="Import external .dos or .json vessel file into database"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>
          <span>Import Vessel File</span>
          <input type="file" accept=".dos,.json" class="hidden" onchange="handleVesselDbImport(this)" />
        </label>
      </div>
    </div>

    <!-- Quick Stats Cards (4 Columns) -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
      <div class="bg-white p-3 rounded border border-slate-200 shadow-2xs">
        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Stored Vessels</div>
        <div class="text-xl font-black text-slate-800 mt-1 font-mono">${totalCount} <span class="text-xs font-normal text-slate-500">vessels</span></div>
        <div class="text-[10px] text-slate-500 mt-0.5">Available in database</div>
      </div>

      <div class="bg-white p-3 rounded border border-slate-200 shadow-2xs">
        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Rule Compliance</div>
        <div class="text-xl font-black text-emerald-700 mt-1 font-mono">${compliantCount} / ${totalCount} <span class="text-xs font-semibold text-emerald-600">(${totalCount > 0 ? Math.round((compliantCount / totalCount) * 100) : 0}%)</span></div>
        <div class="text-[10px] text-slate-500 mt-0.5">DOS Statutory Verified</div>
      </div>

      <div class="bg-white p-3 rounded border border-slate-200 shadow-2xs">
        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Average Vessel Length</div>
        <div class="text-xl font-black text-blue-900 mt-1 font-mono">${avgLength} <span class="text-xs font-normal text-slate-500">meters LBP</span></div>
        <div class="text-[10px] text-slate-500 mt-0.5">Fleet mean dimension</div>
      </div>

      <div class="bg-white p-3 rounded border border-slate-200 shadow-2xs">
        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Storage Engine</div>
        <div class="text-xl font-black text-slate-700 mt-1 font-mono">JSON DB <span class="text-xs font-normal text-emerald-600 font-bold">LIVE</span></div>
        <div class="text-[10px] text-slate-500 mt-0.5">Atomic persistent files</div>
      </div>
    </div>

    <!-- Search, Filters, and Sorting Controls -->
    <div class="bg-white p-3 rounded border border-slate-200 mb-4 flex flex-wrap items-center justify-between gap-3 shadow-xs">
      
      <!-- Search Input -->
      <div class="relative flex-1 min-w-[220px]">
        <input 
          type="text" 
          id="vessel-db-search-input"
          class="compact-input w-full pl-8 pr-3 py-1.5 border rounded text-xs text-slate-800 bg-white border-slate-300 focus:border-blue-600"
          placeholder="Search by vessel name, owner, yard reference, or notes..."
          value="${vesselDbSearchQuery}"
          oninput="vesselDbSearchQuery = this.value; renderVesselDbContent();"
        />
        <svg class="w-4 h-4 text-slate-400 absolute left-2.5 top-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
      </div>

      <!-- Type Filter Pills -->
      <div class="flex items-center gap-1 overflow-x-auto text-xs">
        ${['all', 'Cargo', 'Tanker', 'Ferry', 'Container'].map(t => `
          <button 
            type="button"
            onclick="vesselDbFilterType = '${t}'; renderVesselDbContent();"
            class="px-2.5 py-1 rounded font-medium transition cursor-pointer text-[11px] ${
              vesselDbFilterType === t 
                ? 'bg-blue-600 text-white font-bold shadow-2xs' 
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }"
          >
            ${t === 'all' ? 'All Types' : t}
          </button>
        `).join('')}
      </div>

      <!-- Sort Dropdown -->
      <div class="flex items-center gap-1.5 text-xs">
        <span class="text-slate-500 font-medium">Sort:</span>
        <select 
          class="compact-select text-xs py-1 border rounded border-slate-300 bg-white text-slate-800 font-medium"
          onchange="vesselDbSortBy = this.value; renderVesselDbContent();"
        >
          <option value="updated_at" ${vesselDbSortBy === 'updated_at' ? 'selected' : ''}>Recently Modified</option>
          <option value="vessel_name" ${vesselDbSortBy === 'vessel_name' ? 'selected' : ''}>Vessel Name (A-Z)</option>
          <option value="lbp" ${vesselDbSortBy === 'lbp' ? 'selected' : ''}>Length (LBP)</option>
          <option value="lightship" ${vesselDbSortBy === 'lightship' ? 'selected' : ''}>Lightship Weight</option>
        </select>
      </div>

    </div>

    <!-- Vessel List Grid -->
    ${filtered.length > 0 ? `
      <div class="grid grid-cols-1 gap-3.5">
        ${filtered.map(v => renderVesselCard(v)).join('')}
      </div>
    ` : `
      <div class="bg-white p-10 text-center rounded border border-slate-200 shadow-2xs space-y-3">
        <div class="text-slate-400 text-sm font-semibold">No vessels match your search criteria.</div>
        <div class="text-xs text-slate-500">You can clear filters or save the active calculation into the database.</div>
        <button 
          onclick="vesselDbSearchQuery = ''; vesselDbFilterType = 'all'; renderVesselDbContent();"
          class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-xs font-semibold transition"
        >
          Clear Filters
        </button>
      </div>
    `}
  `;
}

function renderVesselCard(v) {
  const p = v.particulars || {};
  const r = v.results_summary || {};

  const isCompliant = r.status === 'COMPLIANT';
  const updatedDateStr = v.updated_at ? new Date(v.updated_at).toLocaleString() : 'Recent';

  const lbp = parseFloat(p.lbp || 0).toFixed(2);
  const breadth = parseFloat(p.breadth || 0).toFixed(2);
  const depth = parseFloat(p.depth || 0).toFixed(2);
  const draft = parseFloat(p.draft || 0).toFixed(2);

  const netSteelT = parseFloat(r.net_steel_tonnes || 0).toFixed(2);
  const lightshipT = parseFloat(r.lightship_tonnes || 0).toFixed(2);

  return `
    <div class="bg-white rounded border border-slate-200 hover:border-blue-300 transition-all shadow-xs p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
      
      <!-- Left Column: Vessel Identity & Particulars -->
      <div class="space-y-2 flex-1">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-sm font-bold text-slate-900 tracking-tight">${v.vessel_name || 'Unnamed Vessel'}</span>
          <span class="text-[10px] px-2 py-0.5 rounded font-bold bg-blue-50 text-blue-800 border border-blue-200">
            ${v.vessel_type || 'Cargo Vessel'}
          </span>
          <span class="text-[10px] px-2 py-0.5 rounded font-medium bg-slate-100 text-slate-700 border border-slate-200">
            ${v.hull_type || 'Single Hull'}
          </span>
          <span class="text-[10px] px-2 py-0.5 rounded font-medium bg-slate-100 text-slate-700 border border-slate-200">
            ${v.route || 'Inland'}
          </span>
        </div>

        <!-- Particulars Strip -->
        <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-600 font-mono">
          <div>LBP: <b class="text-slate-900 font-bold">${lbp} m</b></div>
          <div>B: <b class="text-slate-900 font-bold">${breadth} m</b></div>
          <div>D: <b class="text-slate-900 font-bold">${depth} m</b></div>
          <div>d: <b class="text-slate-900 font-bold">${draft} m</b></div>
          ${p.frame_spacing ? `<div>Spacing: <b class="text-slate-900 font-bold">${p.frame_spacing} mm</b></div>` : ''}
          ${p.cb ? `<div>Cb: <b class="text-slate-900 font-bold">${p.cb}</b></div>` : ''}
        </div>

        <!-- Owner & Notes -->
        ${(v.owner || v.yard_ref || v.notes) ? `
          <div class="text-[11.5px] text-slate-500 pt-0.5 flex flex-wrap items-center gap-3">
            ${v.owner ? `<span>Client: <b class="text-slate-700">${v.owner}</b></span>` : ''}
            ${v.yard_ref ? `<span>Ref: <b class="text-slate-700">${v.yard_ref}</b></span>` : ''}
            ${v.notes ? `<span class="italic truncate max-w-md text-slate-600" title="${v.notes}">"${v.notes}"</span>` : ''}
          </div>
        ` : ''}

        <div class="text-[10px] text-slate-400">
          Last saved: ${updatedDateStr} &nbsp;•&nbsp; ID: <code class="font-mono text-slate-500">${v.id}</code>
        </div>
      </div>

      <!-- Center Column: Key Results Badges -->
      <div class="flex items-center gap-3 border-y md:border-y-0 md:border-x border-slate-100 py-2 md:py-0 md:px-4 shrink-0">
        <div class="text-center px-2">
          <div class="text-[9.5px] uppercase font-bold text-slate-400">Net Steel</div>
          <div class="text-sm font-black text-blue-900 font-mono mt-0.5">${netSteelT} <span class="text-[10px] font-normal">T</span></div>
        </div>

        <div class="text-center px-2">
          <div class="text-[9.5px] uppercase font-bold text-slate-400">Lightship</div>
          <div class="text-sm font-black text-emerald-900 font-mono mt-0.5">${lightshipT} <span class="text-[10px] font-normal">T</span></div>
        </div>

        <div class="text-center px-2">
          <div class="text-[9.5px] uppercase font-bold text-slate-400">Compliance</div>
          <div class="mt-0.5">
            <span class="text-[10px] px-2 py-0.5 rounded font-bold ${
              isCompliant 
                ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' 
                : 'bg-rose-100 text-rose-800 border border-rose-300'
            }">
              ${isCompliant ? 'COMPLIANT' : 'NON-COMPLIANT'}
            </span>
          </div>
        </div>
      </div>

      <!-- Right Column: Actions -->
      <div class="flex items-center gap-2 shrink-0">
        <button 
          onclick="handleLoadVesselToWorkspace('${v.id}')"
          class="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-bold transition flex items-center gap-1.5 shadow-xs cursor-pointer"
          title="Load this vessel into the active workspace to edit or generate reports"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
          <span>Open in Calculator</span>
        </button>

        <button 
          onclick="handleExportVesselDos('${v.id}')"
          class="p-1.5 border border-slate-300 hover:bg-slate-100 text-slate-700 rounded transition cursor-pointer"
          title="Download as .dos project file"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
        </button>

        <button 
          onclick="handleDuplicateVessel('${v.id}')"
          class="p-1.5 border border-slate-300 hover:bg-slate-100 text-slate-700 rounded transition cursor-pointer"
          title="Duplicate this vessel design"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
        </button>

        <button 
          onclick="handleDeleteVessel('${v.id}', '${v.vessel_name || 'this vessel'}')"
          class="p-1.5 border border-slate-300 hover:bg-rose-50 hover:text-rose-600 text-slate-500 rounded transition cursor-pointer"
          title="Delete vessel from database"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
        </button>
      </div>

    </div>
  `;
}

async function handleLoadVesselToWorkspace(vesselId) {
  try {
    const res = await fetch(`/api/vessels/${vesselId}/load`, {
      method: 'POST'
    });
    const data = await res.json();
    if (!res.ok || data.status !== 'ok') {
      throw new Error(data.detail || data.message || 'Failed to load vessel');
    }

    // Update client appState with evaluated state
    window.appState = data.state;
    if (window.appStore && typeof window.appStore.setData === 'function') {
      window.appStore.setData(data.state);
    }

    // Sync header
    const topNameEl = document.getElementById('top-vessel-name');
    if (topNameEl && data.state.dashboard_inputs) {
      topNameEl.textContent = data.state.dashboard_inputs.vessel_name || 'Vessel';
    }

    if (typeof showToastNotification === 'function') {
      showToastNotification(`Vessel '${data.state.dashboard_inputs?.vessel_name}' loaded successfully!`, 'success');
    }

    // Re-render dashboard and views
    if (typeof renderDashboard === 'function') {
      renderDashboard();
    }
    if (typeof updateLiveDashboardDisplays === 'function') {
      updateLiveDashboardDisplays();
    }
    if (typeof updateTopStats === 'function') {
      updateTopStats();
    }

    // Switch to Dashboard tab
    if (typeof switchTab === 'function') {
      switchTab('dashboard');
    } else if (window.navigation) {
      window.navigation.switchTab('dashboard');
    }

  } catch (err) {
    console.error('Error loading vessel:', err);
    alert(`Could not load vessel: ${err.message}`);
  }
}

async function handleExportVesselDos(vesselId) {
  try {
    window.location.href = `/api/vessels/${vesselId}/export`;
  } catch (err) {
    console.error('Export error:', err);
  }
}

async function handleDuplicateVessel(vesselId) {
  const newName = prompt('Enter a name for the duplicated vessel:');
  if (newName === null) return; // user cancelled

  try {
    const res = await fetch(`/api/vessels/${vesselId}/duplicate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_name: newName.trim() || undefined })
    });
    const data = await res.json();
    if (!res.ok || data.status !== 'ok') {
      throw new Error(data.detail || data.message || 'Failed to duplicate vessel');
    }

    if (typeof showToastNotification === 'function') {
      showToastNotification(`Vessel duplicated as '${data.vessel?.vessel_name}'!`, 'success');
    }
    renderVesselDb();
  } catch (err) {
    console.error('Duplicate error:', err);
    alert(`Could not duplicate vessel: ${err.message}`);
  }
}

async function handleDeleteVessel(vesselId, vesselName) {
  if (!confirm(`Are you sure you want to permanently delete '${vesselName}' from the vessel database?`)) {
    return;
  }

  try {
    const res = await fetch(`/api/vessels/${vesselId}`, {
      method: 'DELETE'
    });
    const data = await res.json();
    if (!res.ok || data.status !== 'ok') {
      throw new Error(data.detail || data.message || 'Failed to delete vessel');
    }

    if (typeof showToastNotification === 'function') {
      showToastNotification(`Vessel '${vesselName}' deleted from database.`, 'info');
    }
    renderVesselDb();
  } catch (err) {
    console.error('Delete error:', err);
    alert(`Could not delete vessel: ${err.message}`);
  }
}

async function handleVesselDbImport(fileInput) {
  const file = fileInput.files && fileInput.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const payload = JSON.parse(e.target.result);
      const res = await fetch('/api/vessels/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok || data.status !== 'ok') {
        throw new Error(data.detail || data.message || 'Failed to import vessel');
      }

      if (typeof showToastNotification === 'function') {
        showToastNotification(`Vessel '${data.vessel?.vessel_name}' imported successfully!`, 'success');
      }
      fileInput.value = '';
      renderVesselDb();
    } catch (err) {
      console.error('Import error:', err);
      alert(`Invalid vessel file format: ${err.message}`);
      fileInput.value = '';
    }
  };
  reader.readAsText(file);
}

window.renderVesselDb = renderVesselDb;
window.handleLoadVesselToWorkspace = handleLoadVesselToWorkspace;
window.handleExportVesselDos = handleExportVesselDos;
window.handleDuplicateVessel = handleDuplicateVessel;
window.handleDeleteVessel = handleDeleteVessel;
window.handleVesselDbImport = handleVesselDbImport;
