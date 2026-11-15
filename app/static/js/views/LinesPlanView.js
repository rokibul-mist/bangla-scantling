/**
 * ShipLab-BD Lines Plan & Table of Offsets Generator View
 * Comprehensive multi-view naval architecture hull form designer,
 * frame of reference editor, design grid manager, 3D wireframe orbit projector,
 * interactive editable offset table, and CAD/Excel export suite.
 *
 * Prepared for Bangladesh Inland & Coastal Naval Architecture Suite.
 */

let activeLinesData = null;
let linesViewMode = 'quad'; // 'quad', 'body', 'sheer', 'halfbreadth', '3d', 'table'
let camera3D = { yaw: 0.75, pitch: 0.35, zoom: 1.0, panX: 0, panY: 0, isDragging: false, lastX: 0, lastY: 0, isPanning: false };

function renderLinesPlan() {
  const container = document.getElementById('tab-content-lines-plan');
  if (!container) return;

  // Initialize data if not yet loaded
  if (!activeLinesData) {
    const appData = window.appStore ? window.appStore.getState() : {};
    const inp = appData.dashboard_inputs || {};
    const lbp = parseFloat(inp.lbp) || 69.85;
    const beam = parseFloat(inp.breadth) || 13.41;
    const depth = parseFloat(inp.depth) || 5.18;
    const draft = parseFloat(inp.draft) || 4.00;
    const cb = parseFloat(inp.block_coeff) || 0.75;
    const cm = 0.98;

    activeLinesData = HullLinesEngine.generateParametricHull(lbp, beam, depth, draft, cb, cm, 'general_cargo');
    activeLinesData.vessel_name = inp.vessel_name || 'M. V. YOUNUS MOLLA-1';
  }

  container.innerHTML = `
    <div class="space-y-3 pb-8">
      <!-- 1. Enterprise Software Toolbar -->
      <div class="bg-white p-2.5 rounded border border-slate-200 shadow-2xs flex flex-wrap items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <div class="p-1.5 rounded bg-slate-100 border border-slate-200 text-slate-700">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"/></svg>
          </div>
          <div>
            <div class="text-[12px] font-bold text-slate-900 leading-tight">Lines Plan &amp; Table of Offsets Generator</div>
            <div class="text-[9.5px] text-slate-500">Hull Form Modeling • Reference Frame • Design Grid • Multi-View CAD • Hydrostatics</div>
          </div>
        </div>

        <!-- Center Controls: Preset Selector & Grid/Reference buttons -->
        <div class="flex items-center gap-1.5">
          <div class="flex items-center gap-1 bg-slate-50 px-1.5 py-0.5 rounded border border-slate-200 text-[10px]">
            <span class="text-slate-500 font-medium">Preset:</span>
            <select 
              id="lines-preset-select" 
              class="bg-transparent font-semibold text-slate-800 outline-none cursor-pointer"
              onchange="handleLinesPresetChange(this.value)"
            >
              <option value="general_cargo" ${activeLinesData.preset_type === 'general_cargo' ? 'selected' : ''}>General Cargo (Full Form)</option>
              <option value="oil_tanker" ${activeLinesData.preset_type === 'oil_tanker' ? 'selected' : ''}>Inland Oil Tanker (High Cb)</option>
              <option value="passenger_launch" ${activeLinesData.preset_type === 'passenger_launch' ? 'selected' : ''}>Passenger Launch (Fine Lines)</option>
              <option value="sand_barge" ${activeLinesData.preset_type === 'sand_barge' ? 'selected' : ''}>Sand / Deck Barge (Chine)</option>
            </select>
          </div>

          <button 
            onclick="openUploadHullModal()"
            class="px-2 py-1 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded text-[10px] font-semibold transition flex items-center gap-1 cursor-pointer"
            title="Upload existing hull geometry (.csv, .txt, .obj, .stl, .dxf)"
          >
            <svg class="w-3 h-3 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>
            <span>Upload Hull</span>
          </button>

          <button 
            onclick="openReferenceFrameModal()"
            class="px-2 py-1 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded text-[10px] font-semibold transition flex items-center gap-1 cursor-pointer"
            title="Configure Coordinate Origin, Baseline, Symmetry, Units"
          >
            <svg class="w-3 h-3 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/></svg>
            <span>Frame of Reference</span>
          </button>

          <button 
            onclick="openDesignGridModal()"
            class="px-2 py-1 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded text-[10px] font-semibold transition flex items-center gap-1 cursor-pointer"
            title="Configure Stations, Waterlines, and Buttocks Grid"
          >
            <svg class="w-3 h-3 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"/></svg>
            <span>Design Grid</span>
          </button>
        </div>

        <!-- Right Controls: View Switcher & Export Menu -->
        <div class="flex items-center gap-1.5">
          <div class="inline-flex rounded border border-slate-200 bg-slate-50 p-0.5">
            <button 
              onclick="setLinesViewMode('quad')" 
              class="px-2 py-0.5 text-[9.5px] font-semibold rounded ${linesViewMode === 'quad' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'} cursor-pointer"
              title="Quad Split View"
            >
              Quad View
            </button>
            <button 
              onclick="setLinesViewMode('body')" 
              class="px-2 py-0.5 text-[9.5px] font-semibold rounded ${linesViewMode === 'body' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'} cursor-pointer"
              title="Body Plan Only"
            >
              Body Plan
            </button>
            <button 
              onclick="setLinesViewMode('sheer')" 
              class="px-2 py-0.5 text-[9.5px] font-semibold rounded ${linesViewMode === 'sheer' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'} cursor-pointer"
              title="Sheer Profile Only"
            >
              Sheer
            </button>
            <button 
              onclick="setLinesViewMode('halfbreadth')" 
              class="px-2 py-0.5 text-[9.5px] font-semibold rounded ${linesViewMode === 'halfbreadth' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'} cursor-pointer"
              title="Half-Breadth Only"
            >
              Half-Breadth
            </button>
            <button 
              onclick="setLinesViewMode('3d')" 
              class="px-2 py-0.5 text-[9.5px] font-semibold rounded ${linesViewMode === '3d' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'} cursor-pointer"
              title="3D Wireframe Orbit"
            >
              3D Orbit
            </button>
            <button 
              onclick="setLinesViewMode('table')" 
              class="px-2 py-0.5 text-[9.5px] font-semibold rounded ${linesViewMode === 'table' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'} cursor-pointer"
              title="Table of Offsets Only"
            >
              Offset Table
            </button>
          </div>

          <!-- Export Dropdown -->
          <div class="relative inline-block text-left">
            <button 
              onclick="toggleLinesExportMenu()" 
              class="px-2 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded text-[10px] font-semibold transition flex items-center gap-1 cursor-pointer"
            >
              <span>Export</span>
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            <div id="lines-export-menu" class="hidden absolute right-0 mt-1 w-44 bg-white border border-slate-200 rounded shadow-md z-50 py-1 text-[10.5px]">
              <a href="javascript:void(0)" onclick="exportLinesDxf()" class="block px-3 py-1.5 text-slate-700 hover:bg-slate-50 font-medium">AutoCAD (.dxf) Lines Plan</a>
              <a href="javascript:void(0)" onclick="exportLinesExcel()" class="block px-3 py-1.5 text-slate-700 hover:bg-slate-50 font-medium">Excel (.xlsx) Table of Offsets</a>
              <a href="javascript:void(0)" onclick="exportLinesCsv()" class="block px-3 py-1.5 text-slate-700 hover:bg-slate-50 font-medium">CSV Table of Offsets</a>
            </div>
          </div>
        </div>
      </div>

      <!-- 1.5 Bentley MAXSURF Detected Settings Banner -->
      ${renderMaxsurfDetectedBanner(activeLinesData.maxsurf_settings)}

      <!-- 2. Integrated Hydrostatics KPI Bar -->
      ${renderHydrostaticsBar(activeLinesData.hydrostatics)}

      <!-- 3. Dynamic Multi-View Workspace -->
      ${renderWorkspacePanels()}

      <!-- 4. Interactive Table of Offsets Grid -->
      <div class="bg-white rounded border border-slate-200 shadow-2xs p-3 space-y-2">
        <div class="flex items-center justify-between pb-1.5 border-b border-slate-100">
          <div>
            <div class="text-[11.5px] font-bold text-slate-900">Table of Offsets (Molded Half-Breadths from Centerline [m])</div>
            <div class="text-[9px] text-slate-500">Edit any cell inline to re-fair hull curves and recalculate hydrostatic parameters in real-time.</div>
          </div>
          <div class="flex items-center gap-2 text-[9.5px]">
            <span class="text-slate-400">Ref: Molded Baseline &amp; AP</span>
            <button 
              onclick="recalculateHydrostaticsFromTable()"
              class="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded border border-slate-200 font-semibold cursor-pointer"
            >
              Re-Fair &amp; Calculate
            </button>
          </div>
        </div>
        ${renderOffsetTableHtml(activeLinesData)}
      </div>
    </div>

    <!-- Hidden Modals -->
    ${renderUploadHullModalHtml()}
    ${renderReferenceFrameModalHtml()}
    ${renderDesignGridModalHtml()}
  `;

  // Draw active canvases after DOM render
  setTimeout(() => {
    drawActiveCanvases();
  }, 30);
}

function renderMaxsurfDetectedBanner(ms) {
  if (!ms || !ms.is_maxsurf) return '';
  return `
    <div class="bg-blue-50/90 border border-blue-200 rounded p-2.5 shadow-2xs flex flex-wrap items-center justify-between gap-3 text-slate-800 animate-fadeIn">
      <div class="flex items-start gap-2.5">
        <div class="p-1.5 rounded bg-blue-600 text-white shrink-0 mt-0.5 shadow-xs">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-[12px] font-bold text-blue-950">Bentley MAXSURF Model Settings Detected</span>
            <span class="text-[8.5px] font-mono px-1.5 py-0.2 rounded bg-blue-100 text-blue-800 border border-blue-200 font-semibold uppercase">${ms.detected_via === 'com_automation' ? 'MAXSURF Modeler Engine' : 'Native Parser'}</span>
            <span class="text-[9.5px] text-slate-500 font-medium">Model: <b class="text-slate-800">${ms.model_name || 'Design.msd'}</b></span>
          </div>
          <div class="text-[10px] text-slate-600 mt-1 flex flex-wrap items-center gap-x-3 gap-y-0.5">
            <span><b>Frame of Reference:</b> AP: ${ms.fref_aft_perp}m | FP: ${ms.fref_fwd_perp}m | Mid: ${ms.fref_midship}m | Baseline: ${ms.fref_baseline}m | DWL: ${ms.fref_datum_wl}m</span>
            <span>•</span>
            <span><b>Design Grid:</b> ${ms.grid_sections_count} Stations | ${ms.grid_waterlines_count} Waterlines | ${ms.grid_buttocks_count} Buttocks</span>
            <span>•</span>
            <span><b>Particulars:</b> LBP: ${ms.lbp}m | Beam: ${ms.beam}m | Draft: ${ms.draft}m | Cb: ${ms.cb}</span>
          </div>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button 
          onclick="syncMaxsurfToDashboard()" 
          class="px-2.5 py-1.5 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white rounded text-[10px] font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-2xs"
          title="Apply detected LBP, Beam, Depth, Draft, and Cb to the main Scantling Dashboard"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          <span>Sync Dimensions to Dashboard</span>
        </button>
      </div>
    </div>
  `;
}

function syncMaxsurfToDashboard() {
  if (!activeLinesData || !activeLinesData.maxsurf_settings) {
    alert("No active MAXSURF settings available to synchronize.");
    return;
  }
  const ms = activeLinesData.maxsurf_settings;
  if (!window.appStore) return;

  const state = window.appStore.getState();
  const inp = state.dashboard_inputs || {};
  if (ms.lbp > 0) inp.lbp = ms.lbp;
  if (ms.beam > 0) inp.breadth = ms.beam;
  if (ms.depth > 0) inp.depth = ms.depth;
  if (ms.draft > 0) inp.draft = ms.draft;
  if (ms.cb > 0) inp.block_coeff = ms.cb;
  if (ms.model_name) {
    const cleanName = ms.model_name.replace(/\.[^/.]+$/, '').toUpperCase();
    inp.vessel_name = cleanName;
  }

  window.appStore.setState({ dashboard_inputs: inp });
  if (typeof updateLiveDashboardDisplays === 'function') updateLiveDashboardDisplays();
  if (typeof Navigation !== 'undefined' && Navigation.syncTopHeader) Navigation.syncTopHeader(state);
  alert(`Successfully synchronized MAXSURF settings to Dashboard:\n• Vessel: ${inp.vessel_name || 'MAXSURF Model'}\n• LBP: ${ms.lbp} m\n• Breadth: ${ms.beam} m\n• Depth: ${inp.depth || 5.18} m\n• Draft: ${ms.draft} m\n• Cb: ${ms.cb}`);
}

function renderHydrostaticsBar(h) {
  if (!h) return '';
  return `
    <div class="bg-white p-2.5 rounded border border-slate-200 shadow-2xs grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-2">
      <div class="bg-slate-50/70 p-1.5 rounded border border-slate-100">
        <div class="text-[8.5px] font-bold text-slate-500 uppercase tracking-wider">Design Draft</div>
        <div class="text-[13px] font-extrabold text-slate-900 font-mono">${(h.draft_m || 4.0).toFixed(2)} <span class="text-[9px] font-normal text-slate-500">m</span></div>
        <div class="text-[8px] text-slate-400">Baseline to DWL</div>
      </div>

      <div class="bg-slate-50/70 p-1.5 rounded border border-slate-100">
        <div class="text-[8.5px] font-bold text-slate-500 uppercase tracking-wider">Displacement</div>
        <div class="text-[13px] font-extrabold text-slate-900 font-mono">${(h.displacement_tonnes || 0).toLocaleString()} <span class="text-[9px] font-normal text-slate-500">t</span></div>
        <div class="text-[8px] text-slate-400">Vol: ${(h.volume_m3 || 0).toFixed(0)} m³</div>
      </div>

      <div class="bg-slate-50/70 p-1.5 rounded border border-slate-100">
        <div class="text-[8.5px] font-bold text-slate-500 uppercase tracking-wider">Block Coeff (Cb)</div>
        <div class="text-[13px] font-extrabold text-slate-900 font-mono">${(h.block_coefficient_cb || 0).toFixed(3)}</div>
        <div class="text-[8px] text-slate-400">Fullness coefficient</div>
      </div>

      <div class="bg-slate-50/70 p-1.5 rounded border border-slate-100">
        <div class="text-[8.5px] font-bold text-slate-500 uppercase tracking-wider">Midship (Cm)</div>
        <div class="text-[13px] font-extrabold text-slate-900 font-mono">${(h.midship_coefficient_cm || 0.98).toFixed(3)}</div>
        <div class="text-[8px] text-slate-400">Mid section ratio</div>
      </div>

      <div class="bg-slate-50/70 p-1.5 rounded border border-slate-100">
        <div class="text-[8.5px] font-bold text-slate-500 uppercase tracking-wider">Prismatic (Cp)</div>
        <div class="text-[13px] font-extrabold text-slate-900 font-mono">${(h.prismatic_coefficient_cp || 0).toFixed(3)}</div>
        <div class="text-[8px] text-slate-400">Cb / Cm ratio</div>
      </div>

      <div class="bg-slate-50/70 p-1.5 rounded border border-slate-100">
        <div class="text-[8.5px] font-bold text-slate-500 uppercase tracking-wider">Waterplane (Cwp)</div>
        <div class="text-[13px] font-extrabold text-slate-900 font-mono">${(h.waterplane_coefficient_cwp || 0).toFixed(3)}</div>
        <div class="text-[8px] text-slate-400">Area: ${(h.waterplane_area_m2 || 0).toFixed(0)} m²</div>
      </div>

      <div class="bg-slate-50/70 p-1.5 rounded border border-slate-100">
        <div class="text-[8.5px] font-bold text-slate-500 uppercase tracking-wider">LCB from AP</div>
        <div class="text-[13px] font-extrabold text-slate-900 font-mono">${(h.lcb_from_ap_m || 0).toFixed(2)} <span class="text-[9px] font-normal text-slate-500">m</span></div>
        <div class="text-[8px] text-slate-400">${(h.lcb_percent_lbp || 0).toFixed(1)}% of LBP</div>
      </div>

      <div class="bg-slate-50/70 p-1.5 rounded border border-slate-100">
        <div class="text-[8.5px] font-bold text-slate-500 uppercase tracking-wider">Transverse KM</div>
        <div class="text-[13px] font-extrabold text-slate-900 font-mono">${(h.kmt_m || 0).toFixed(2)} <span class="text-[9px] font-normal text-slate-500">m</span></div>
        <div class="text-[8px] text-slate-400">LCF: ${(h.lcf_from_ap_m || 0).toFixed(2)} m</div>
      </div>
    </div>
  `;
}

function renderWorkspacePanels() {
  if (linesViewMode === 'body') {
    return `
      <div class="bg-white p-3 rounded border border-slate-200 shadow-2xs">
        <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
          <span class="text-[11px] font-bold text-slate-800">Body Plan (Transverse Sections)</span>
          <button onclick="setLinesViewMode('quad')" class="text-[9.5px] text-blue-600 hover:underline">Quad View</button>
        </div>
        <canvas id="canvas-body-plan" width="1000" height="600" class="w-full h-[520px] bg-white border border-slate-200 rounded"></canvas>
      </div>
    `;
  }

  if (linesViewMode === 'sheer') {
    return `
      <div class="bg-white p-3 rounded border border-slate-200 shadow-2xs">
        <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
          <span class="text-[11px] font-bold text-slate-800">Sheer Plan (Profile Elevation)</span>
          <button onclick="setLinesViewMode('quad')" class="text-[9.5px] text-blue-600 hover:underline">Quad View</button>
        </div>
        <canvas id="canvas-sheer-plan" width="1200" height="500" class="w-full h-[520px] bg-white border border-slate-200 rounded"></canvas>
      </div>
    `;
  }

  if (linesViewMode === 'halfbreadth') {
    return `
      <div class="bg-white p-3 rounded border border-slate-200 shadow-2xs">
        <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
          <span class="text-[11px] font-bold text-slate-800">Half-Breadth Plan (Waterlines Plan View)</span>
          <button onclick="setLinesViewMode('quad')" class="text-[9.5px] text-blue-600 hover:underline">Quad View</button>
        </div>
        <canvas id="canvas-halfbreadth-plan" width="1200" height="500" class="w-full h-[520px] bg-white border border-slate-200 rounded"></canvas>
      </div>
    `;
  }

  if (linesViewMode === '3d') {
    return `
      <div class="bg-white p-3 rounded border border-slate-200 shadow-2xs">
        <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
          <span class="text-[11px] font-bold text-slate-800">3D Wireframe Orbit Perspective</span>
          <div class="flex items-center gap-2">
            <button onclick="resetCamera3D()" class="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded border border-slate-200 text-[9px] font-medium">Reset View</button>
            <button onclick="setLinesViewMode('quad')" class="text-[9.5px] text-blue-600 hover:underline">Quad View</button>
          </div>
        </div>
        <canvas id="canvas-3d-orbit" width="1100" height="600" class="w-full h-[520px] bg-slate-50 border border-slate-200 rounded cursor-grab active:cursor-grabbing"></canvas>
      </div>
    `;
  }

  if (linesViewMode === 'table') {
    return ''; // When table mode is chosen, the workspace collapses to just the table below
  }

  // Default: Quad Split View
  return `
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
      <!-- 1. Body Plan -->
      <div class="bg-white p-2.5 rounded border border-slate-200 shadow-2xs flex flex-col justify-between">
        <div class="flex items-center justify-between pb-1.5 mb-1.5 border-b border-slate-100">
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-blue-600"></span>
            <span class="text-[11px] font-bold text-slate-800">Body Plan (Sections)</span>
          </div>
          <button onclick="setLinesViewMode('body')" class="text-[9px] text-slate-500 hover:text-slate-800 border border-slate-200 px-1.5 py-0.2 rounded hover:bg-slate-50">Maximize</button>
        </div>
        <canvas id="canvas-body-plan" width="600" height="380" class="w-full h-[280px] bg-white border border-slate-100 rounded"></canvas>
      </div>

      <!-- 2. Sheer Plan -->
      <div class="bg-white p-2.5 rounded border border-slate-200 shadow-2xs flex flex-col justify-between">
        <div class="flex items-center justify-between pb-1.5 mb-1.5 border-b border-slate-100">
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-600"></span>
            <span class="text-[11px] font-bold text-slate-800">Sheer Plan (Profile Elevation)</span>
          </div>
          <button onclick="setLinesViewMode('sheer')" class="text-[9px] text-slate-500 hover:text-slate-800 border border-slate-200 px-1.5 py-0.2 rounded hover:bg-slate-50">Maximize</button>
        </div>
        <canvas id="canvas-sheer-plan" width="600" height="380" class="w-full h-[280px] bg-white border border-slate-100 rounded"></canvas>
      </div>

      <!-- 3. Half-Breadth Plan -->
      <div class="bg-white p-2.5 rounded border border-slate-200 shadow-2xs flex flex-col justify-between">
        <div class="flex items-center justify-between pb-1.5 mb-1.5 border-b border-slate-100">
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-indigo-600"></span>
            <span class="text-[11px] font-bold text-slate-800">Half-Breadth Plan (Waterlines)</span>
          </div>
          <button onclick="setLinesViewMode('halfbreadth')" class="text-[9px] text-slate-500 hover:text-slate-800 border border-slate-200 px-1.5 py-0.2 rounded hover:bg-slate-50">Maximize</button>
        </div>
        <canvas id="canvas-halfbreadth-plan" width="600" height="380" class="w-full h-[280px] bg-white border border-slate-100 rounded"></canvas>
      </div>

      <!-- 4. 3D Wireframe Orbit -->
      <div class="bg-white p-2.5 rounded border border-slate-200 shadow-2xs flex flex-col justify-between">
        <div class="flex items-center justify-between pb-1.5 mb-1.5 border-b border-slate-100">
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-amber-600"></span>
            <span class="text-[11px] font-bold text-slate-800">3D Hull Wireframe (Interactive Orbit)</span>
          </div>
          <div class="flex items-center gap-1">
            <button onclick="resetCamera3D()" class="text-[9px] text-slate-500 hover:text-slate-800 border border-slate-200 px-1.5 py-0.2 rounded hover:bg-slate-50">Reset</button>
            <button onclick="setLinesViewMode('3d')" class="text-[9px] text-slate-500 hover:text-slate-800 border border-slate-200 px-1.5 py-0.2 rounded hover:bg-slate-50">Maximize</button>
          </div>
        </div>
        <canvas id="canvas-3d-orbit" width="600" height="380" class="w-full h-[280px] bg-slate-50 border border-slate-100 rounded cursor-grab active:cursor-grabbing"></canvas>
      </div>
    </div>
  `;
}

function renderOffsetTableHtml(data) {
  const grid = data.design_grid;
  const stations = [...grid.stations].sort((a, b) => a.x_pos - b.x_pos);
  const waterlines = [...grid.waterlines].sort((a, b) => b.z_height - a.z_height); // Top to bottom

  return `
    <div class="overflow-x-auto">
      <table class="compact-table w-full border border-slate-200 text-center">
        <thead>
          <tr class="bg-slate-100 text-slate-700">
            <th class="p-1.5 text-left border-r border-slate-200" style="min-width: 140px;">Waterline / Level</th>
            <th class="p-1.5 text-center border-r border-slate-200" style="width: 70px;">Z Height [m]</th>
            ${stations.map(st => `
              <th class="p-1.5 text-center border-r border-slate-200" style="min-width: 65px;">
                <div class="font-bold">${st.label || `St ${st.station_num}`}</div>
                <div class="text-[8px] font-normal text-slate-400 font-mono">${st.x_pos.toFixed(1)}m</div>
              </th>
            `).join('')}
          </tr>
        </thead>
        <tbody>
          <!-- Deck at Side / Sheer Line Row -->
          <tr class="bg-emerald-50/50 font-medium">
            <td class="p-1 text-left font-bold text-emerald-800 border-r border-slate-200">Deck Half-Breadth</td>
            <td class="p-1 text-center font-mono text-emerald-700 border-r border-slate-200 text-[10px]">Sheer</td>
            ${stations.map(st => {
              const dp = (data.deck_profile || []).find(p => p.station_id === st.id);
              const val = dp ? dp.deck_half_breadth.toFixed(3) : '0.000';
              return `
                <td class="p-0.5 border-r border-slate-200">
                  <input 
                    type="number" 
                    step="0.005"
                    class="w-full text-center font-mono text-[10.5px] font-semibold text-emerald-800 bg-transparent outline-none focus:bg-white focus:ring-1 focus:ring-emerald-500 rounded px-0.5" 
                    value="${val}" 
                    onchange="handleDeckOffsetChange('${st.id}', this.value)"
                  />
                </td>
              `;
            }).join('')}
          </tr>

          <!-- Waterlines Rows (from Upper to Keel) -->
          ${waterlines.map(wl => {
            const isDwl = wl.is_dwl;
            return `
              <tr class="${isDwl ? 'bg-blue-50/60 font-semibold' : 'hover:bg-slate-50/80'}">
                <td class="p-1 text-left border-r border-slate-200 ${isDwl ? 'text-blue-800' : 'text-slate-800'}">
                  ${wl.label}
                </td>
                <td class="p-1 text-center font-mono border-r border-slate-200 ${isDwl ? 'text-blue-700' : 'text-slate-500'} text-[10px]">
                  ${wl.z_height.toFixed(2)}
                </td>
                ${stations.map(st => {
                  const hb = data.half_breadths[st.id]?.[wl.id] || 0.0;
                  return `
                    <td class="p-0.5 border-r border-slate-200">
                      <input 
                        type="number" 
                        step="0.005"
                        class="w-full text-center font-mono text-[10.5px] ${isDwl ? 'text-blue-900 font-bold' : 'text-slate-800'} bg-transparent outline-none focus:bg-white focus:ring-1 focus:ring-blue-500 rounded px-0.5" 
                        value="${hb.toFixed(3)}" 
                        onchange="handleCellOffsetChange('${st.id}', '${wl.id}', this.value)"
                      />
                    </td>
                  `;
                }).join('')}
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function drawActiveCanvases() {
  if (!activeLinesData) return;

  const bodyCanvas = document.getElementById('canvas-body-plan');
  if (bodyCanvas) HullLinesEngine.renderBodyPlan(bodyCanvas, activeLinesData);

  const sheerCanvas = document.getElementById('canvas-sheer-plan');
  if (sheerCanvas) HullLinesEngine.renderSheerPlan(sheerCanvas, activeLinesData);

  const hbCanvas = document.getElementById('canvas-halfbreadth-plan');
  if (hbCanvas) HullLinesEngine.renderHalfBreadthPlan(hbCanvas, activeLinesData);

  const orbitCanvas = document.getElementById('canvas-3d-orbit');
  if (orbitCanvas) {
    HullLinesEngine.render3DOrbit(orbitCanvas, activeLinesData, camera3D);
    attach3DOrbitEvents(orbitCanvas);
  }
}

function attach3DOrbitEvents(canvas) {
  if (canvas._hasOrbitEvents) return;
  canvas._hasOrbitEvents = true;

  canvas.addEventListener('mousedown', (e) => {
    camera3D.isDragging = true;
    camera3D.isPanning = (e.button === 2); // Right click
    camera3D.lastX = e.clientX;
    camera3D.lastY = e.clientY;
  });

  window.addEventListener('mousemove', (e) => {
    if (!camera3D.isDragging) return;
    const dx = e.clientX - camera3D.lastX;
    const dy = e.clientY - camera3D.lastY;
    camera3D.lastX = e.clientX;
    camera3D.lastY = e.clientY;

    if (camera3D.isPanning) {
      camera3D.panX += dx;
      camera3D.panY += dy;
    } else {
      camera3D.yaw += dx * 0.01;
      camera3D.pitch = Math.max(-1.4, Math.min(1.4, camera3D.pitch + dy * 0.01));
    }
    HullLinesEngine.render3DOrbit(canvas, activeLinesData, camera3D);
  });

  window.addEventListener('mouseup', () => {
    camera3D.isDragging = false;
    camera3D.isPanning = false;
  });

  canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    camera3D.zoom = Math.max(0.3, Math.min(5.0, camera3D.zoom * zoomFactor));
    HullLinesEngine.render3DOrbit(canvas, activeLinesData, camera3D);
  }, { passive: false });

  canvas.addEventListener('contextmenu', (e) => e.preventDefault());
}

function resetCamera3D() {
  camera3D = { yaw: 0.75, pitch: 0.35, zoom: 1.0, panX: 0, panY: 0, isDragging: false, lastX: 0, lastY: 0, isPanning: false };
  const orbitCanvas = document.getElementById('canvas-3d-orbit');
  if (orbitCanvas) HullLinesEngine.render3DOrbit(orbitCanvas, activeLinesData, camera3D);
}

function setLinesViewMode(mode) {
  linesViewMode = mode;
  renderLinesPlan();
}

function handleLinesPresetChange(preset) {
  const appData = window.appStore ? window.appStore.getState() : {};
  const inp = appData.dashboard_inputs || {};
  const lbp = parseFloat(inp.lbp) || 69.85;
  const beam = parseFloat(inp.breadth) || 13.41;
  const depth = parseFloat(inp.depth) || 5.18;
  const draft = parseFloat(inp.draft) || 4.00;

  activeLinesData = HullLinesEngine.generateParametricHull(lbp, beam, depth, draft, 0.75, 0.98, preset);
  activeLinesData.vessel_name = inp.vessel_name || 'M. V. YOUNUS MOLLA-1';
  renderLinesPlan();
}

function handleCellOffsetChange(stId, wlId, val) {
  if (!activeLinesData || !activeLinesData.half_breadths) return;
  const num = parseFloat(val) || 0.0;
  if (!activeLinesData.half_breadths[stId]) activeLinesData.half_breadths[stId] = {};
  activeLinesData.half_breadths[stId][wlId] = Math.max(0, num);

  // Re-fair and recalculate
  activeLinesData.hydrostatics = HullLinesEngine.calculateHydrostatics(activeLinesData);
  drawActiveCanvases();
  // Update hydrostatics numbers without full redraw
  const bar = document.querySelector('.grid-cols-2.sm\\:grid-cols-4');
  if (bar) {
    const parent = bar.parentElement;
    parent.innerHTML = renderHydrostaticsBar(activeLinesData.hydrostatics);
  }
}

function handleDeckOffsetChange(stId, val) {
  if (!activeLinesData || !activeLinesData.deck_profile) return;
  const num = parseFloat(val) || 0.0;
  const dp = activeLinesData.deck_profile.find(p => p.station_id === stId);
  if (dp) {
    dp.deck_half_breadth = Math.max(0, num);
  }
  drawActiveCanvases();
}

function recalculateHydrostaticsFromTable() {
  if (!activeLinesData) return;
  activeLinesData.hydrostatics = HullLinesEngine.calculateHydrostatics(activeLinesData);
  renderLinesPlan();
}

function toggleLinesExportMenu() {
  const menu = document.getElementById('lines-export-menu');
  if (menu) menu.classList.toggle('hidden');
}

// Close export menu when clicking outside
window.addEventListener('click', (e) => {
  const menu = document.getElementById('lines-export-menu');
  if (menu && !menu.contains(e.target) && !e.target.closest('button[onclick="toggleLinesExportMenu()"]')) {
    menu.classList.add('hidden');
  }
});

/**
 * Export AutoCAD DXF
 */
async function exportLinesDxf() {
  toggleLinesExportMenu();
  try {
    const res = await fetch('/api/v1/lines-plan/export/dxf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(activeLinesData)
    });
    if (!res.ok) throw new Error(`Export failed: ${res.statusText}`);
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(activeLinesData.vessel_name || 'Hull').replace(/[^a-zA-Z0-9_-]/g, '_')}_Lines_Plan.dxf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert(`AutoCAD DXF Export failed: ${err.message}`);
  }
}

/**
 * Export Excel XLSX Table of Offsets
 */
async function exportLinesExcel() {
  toggleLinesExportMenu();
  try {
    const res = await fetch('/api/v1/lines-plan/export/xlsx', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(activeLinesData)
    });
    if (!res.ok) throw new Error(`Export failed: ${res.statusText}`);
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(activeLinesData.vessel_name || 'Hull').replace(/[^a-zA-Z0-9_-]/g, '_')}_Table_of_Offsets.xlsx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert(`Excel Export failed: ${err.message}`);
  }
}

/**
 * Export CSV Table of Offsets
 */
function exportLinesCsv() {
  toggleLinesExportMenu();
  if (!activeLinesData) return;
  const grid = activeLinesData.design_grid;
  const stations = [...grid.stations].sort((a, b) => a.x_pos - b.x_pos);
  const waterlines = [...grid.waterlines].sort((a, b) => a.z_height - b.z_height);

  let csv = 'Waterline,Z_Height_m,' + stations.map(s => s.label).join(',') + '\n';
  for (const wl of waterlines) {
    const row = [
      `"${wl.label}"`,
      wl.z_height.toFixed(3),
      ...stations.map(st => (activeLinesData.half_breadths[st.id]?.[wl.id] || 0.0).toFixed(3))
    ];
    csv += row.join(',') + '\n';
  }

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${(activeLinesData.vessel_name || 'Hull').replace(/[^a-zA-Z0-9_-]/g, '_')}_Offsets.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Modals: Upload Hull, Frame of Reference, Design Grid
function renderUploadHullModalHtml() {
  return `
    <div id="modal-upload-hull" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs">
      <div class="bg-white rounded-lg border border-slate-200 shadow-xl w-full max-w-md p-4 space-y-3">
        <div class="flex items-center justify-between pb-2 border-b border-slate-100">
          <div class="flex items-center gap-1.5 font-bold text-slate-800 text-[12px]">
            <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/></svg>
            <span>Upload Hull Form Data</span>
          </div>
          <button onclick="closeUploadHullModal()" class="text-slate-400 hover:text-slate-600 font-bold text-sm cursor-pointer">✕</button>
        </div>

        <div class="space-y-2.5 text-[10.5px]">
          <div class="p-2 bg-blue-50/80 border border-blue-200 rounded text-blue-900 flex items-start gap-2">
            <span class="font-bold text-[9px] bg-blue-600 text-white px-1.5 py-0.5 rounded shrink-0 uppercase tracking-wider">MAXSURF</span>
            <div class="text-[9.5px] leading-tight">
              <b>Auto-Detection Enabled:</b> Upload a <b>.msd</b> or <b>.hmd</b> design. The software connects to Bentley MAXSURF and detects the exact Frame of Reference, Design Grids, and Hydrostatic parameters.
            </div>
          </div>
          <p class="text-slate-600">Supported formats: <b>.msd</b>, <b>.hmd</b> (MAXSURF Models), <b>.csv</b>, <b>.txt</b>, <b>.dat</b> (Offset Tables), <b>.obj</b>, <b>.stl</b>, <b>.dxf</b> (3D Mesh/CAD).</p>
          <div class="border-2 border-dashed border-slate-200 hover:border-blue-400 rounded-lg p-5 text-center cursor-pointer bg-slate-50/50">
            <input type="file" id="input-upload-hull-file" accept=".msd,.hmd,.csv,.txt,.dat,.obj,.stl,.dxf" class="hidden" onchange="handleHullFileSelected(event)"/>
            <label for="input-upload-hull-file" class="cursor-pointer block space-y-1">
              <svg class="w-6 h-6 mx-auto text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
              <div id="upload-hull-file-label" class="font-semibold text-slate-700">Choose MAXSURF (.msd) or geometry file</div>
              <div class="text-[9px] text-slate-400">Max size 50MB • Automatically extracts all MAXSURF settings</div>
            </label>
          </div>

          <div id="upload-maxsurf-hint" class="hidden p-1.5 bg-emerald-50 border border-emerald-200 rounded text-emerald-800 text-[9.5px] flex items-center gap-1.5 font-medium">
            <svg class="w-3.5 h-3.5 text-emerald-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            <span>Bentley MAXSURF design detected. Settings and grids will be extracted automatically.</span>
          </div>

          <div class="grid grid-cols-2 gap-2 pt-1">
            <div>
              <label class="block text-[9.5px] font-semibold text-slate-700 mb-0.5">Origin Reference</label>
              <select id="upload-origin-select" class="w-full bg-slate-50 border border-slate-200 rounded p-1 text-[10px] text-slate-800">
                <option value="ap">After Perpendicular (AP)</option>
                <option value="midship">Midship (LBP / 2)</option>
                <option value="fp">Forward Perpendicular (FP)</option>
                <option value="transom">Transom</option>
              </select>
            </div>
            <div>
              <label class="block text-[9.5px] font-semibold text-slate-700 mb-0.5">Scale / Unit Factor</label>
              <select id="upload-scale-select" class="w-full bg-slate-50 border border-slate-200 rounded p-1 text-[10px] text-slate-800">
                <option value="1.0">Meters (1.0)</option>
                <option value="0.001">Millimeters (0.001)</option>
                <option value="0.3048">Feet (0.3048)</option>
              </select>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
          <button onclick="closeUploadHullModal()" class="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[10px] font-medium cursor-pointer">Cancel</button>
          <button onclick="submitUploadHull()" id="btn-submit-upload-hull" class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-[10px] font-semibold transition cursor-pointer">Parse &amp; Import</button>
        </div>
      </div>
    </div>
  `;
}

function renderReferenceFrameModalHtml() {
  const rf = activeLinesData?.reference_frame || {};
  return `
    <div id="modal-reference-frame" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs">
      <div class="bg-white rounded-lg border border-slate-200 shadow-xl w-full max-w-sm p-4 space-y-3">
        <div class="flex items-center justify-between pb-2 border-b border-slate-100">
          <div class="flex items-center gap-1.5 font-bold text-slate-800 text-[12px]">
            <svg class="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/></svg>
            <span>Frame of Reference Settings</span>
          </div>
          <button onclick="closeReferenceFrameModal()" class="text-slate-400 hover:text-slate-600 font-bold text-sm cursor-pointer">✕</button>
        </div>

        <div class="space-y-2.5 text-[10.5px]">
          <div>
            <label class="block font-semibold text-slate-700 mb-0.5">Longitudinal Origin (X = 0)</label>
            <select id="rf-origin" class="w-full bg-slate-50 border border-slate-200 rounded p-1 text-[10px] text-slate-800 font-medium">
              <option value="ap" ${rf.origin === 'ap' ? 'selected' : ''}>After Perpendicular (AP) - Statutory Standard</option>
              <option value="midship" ${rf.origin === 'midship' ? 'selected' : ''}>Midship (Section 5)</option>
              <option value="fp" ${rf.origin === 'fp' ? 'selected' : ''}>Forward Perpendicular (FP)</option>
              <option value="transom" ${rf.origin === 'transom' ? 'selected' : ''}>Aft Transom</option>
            </select>
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-0.5">Vertical Baseline (Z = 0)</label>
            <select id="rf-baseline" class="w-full bg-slate-50 border border-slate-200 rounded p-1 text-[10px] text-slate-800 font-medium">
              <option value="molded" ${rf.baseline === 'molded' ? 'selected' : ''}>Molded Baseline (Top of Keel Plate)</option>
              <option value="keel" ${rf.baseline === 'keel' ? 'selected' : ''}>Bottom of Keel Plate</option>
            </select>
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-0.5">Centerline Transverse Symmetry</label>
            <select id="rf-symmetry" class="w-full bg-slate-50 border border-slate-200 rounded p-1 text-[10px] text-slate-800 font-medium">
              <option value="symmetric" ${rf.symmetry === 'symmetric' ? 'selected' : ''}>Port &amp; Starboard Symmetric (Standard)</option>
              <option value="asymmetric" ${rf.symmetry === 'asymmetric' ? 'selected' : ''}>Asymmetric Hull Form</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block font-semibold text-slate-700 mb-0.5">Units</label>
              <select id="rf-units" class="w-full bg-slate-50 border border-slate-200 rounded p-1 text-[10px] text-slate-800 font-medium">
                <option value="m" ${rf.units === 'm' ? 'selected' : ''}>Meters [m]</option>
                <option value="mm" ${rf.units === 'mm' ? 'selected' : ''}>Millimeters [mm]</option>
                <option value="ft" ${rf.units === 'ft' ? 'selected' : ''}>Feet [ft]</option>
              </select>
            </div>
            <div>
              <label class="block font-semibold text-slate-700 mb-0.5">Scale Factor</label>
              <input type="number" step="0.01" id="rf-scale" value="${rf.scale_factor || 1.0}" class="w-full bg-slate-50 border border-slate-200 rounded p-1 text-[10px] text-slate-800 font-mono font-medium"/>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
          <button onclick="closeReferenceFrameModal()" class="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[10px] font-medium cursor-pointer">Cancel</button>
          <button onclick="saveReferenceFrameModal()" class="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded text-[10px] font-semibold transition cursor-pointer">Apply Reference</button>
        </div>
      </div>
    </div>
  `;
}

function renderDesignGridModalHtml() {
  const grid = activeLinesData?.design_grid || {};
  return `
    <div id="modal-design-grid" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs">
      <div class="bg-white rounded-lg border border-slate-200 shadow-xl w-full max-w-md p-4 space-y-3">
        <div class="flex items-center justify-between pb-2 border-b border-slate-100">
          <div class="flex items-center gap-1.5 font-bold text-slate-800 text-[12px]">
            <svg class="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"/></svg>
            <span>Design Grid Planes Setup</span>
          </div>
          <button onclick="closeDesignGridModal()" class="text-slate-400 hover:text-slate-600 font-bold text-sm cursor-pointer">✕</button>
        </div>

        <div class="space-y-3 text-[10.5px]">
          <div class="p-2 rounded bg-slate-50 border border-slate-200 space-y-1.5">
            <span class="font-bold text-slate-800 block">1. Transverse Stations</span>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-[9px] text-slate-500">Number of Stations</label>
                <select id="grid-num-stations" class="w-full bg-white border border-slate-200 rounded p-1 text-[10px] font-medium text-slate-800">
                  <option value="11" ${grid.stations?.length === 11 ? 'selected' : ''}>11 Stations (0 to 10)</option>
                  <option value="21" ${grid.stations?.length === 21 ? 'selected' : ''}>21 Stations (0 to 20)</option>
                </select>
              </div>
              <div>
                <label class="block text-[9px] text-slate-500">Length Between Perp (LBP)</label>
                <input type="number" step="0.1" id="grid-lbp" value="${grid.lbp || 69.85}" class="w-full bg-white border border-slate-200 rounded p-1 text-[10px] font-mono text-slate-800 font-medium"/>
              </div>
            </div>
          </div>

          <div class="p-2 rounded bg-slate-50 border border-slate-200 space-y-1.5">
            <span class="font-bold text-slate-800 block">2. Horizontal Waterlines (WLs)</span>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-[9px] text-slate-500">Design Draft [m]</label>
                <input type="number" step="0.05" id="grid-draft" value="${grid.draft || 4.00}" class="w-full bg-white border border-slate-200 rounded p-1 text-[10px] font-mono text-slate-800 font-medium"/>
              </div>
              <div>
                <label class="block text-[9px] text-slate-500">Molded Depth [m]</label>
                <input type="number" step="0.05" id="grid-depth" value="${grid.depth || 5.18}" class="w-full bg-white border border-slate-200 rounded p-1 text-[10px] font-mono text-slate-800 font-medium"/>
              </div>
            </div>
          </div>

          <div class="p-2 rounded bg-slate-50 border border-slate-200 space-y-1.5">
            <span class="font-bold text-slate-800 block">3. Longitudinal Buttocks</span>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-[9px] text-slate-500">Molded Beam [m]</label>
                <input type="number" step="0.1" id="grid-beam" value="${grid.beam || 13.41}" class="w-full bg-white border border-slate-200 rounded p-1 text-[10px] font-mono text-slate-800 font-medium"/>
              </div>
              <div>
                <label class="block text-[9px] text-slate-500">Number of Buttocks</label>
                <select id="grid-num-buttocks" class="w-full bg-white border border-slate-200 rounded p-1 text-[10px] font-medium text-slate-800">
                  <option value="3" ${grid.buttocks?.length === 3 ? 'selected' : ''}>3 Buttocks</option>
                  <option value="4" ${grid.buttocks?.length === 4 ? 'selected' : ''}>4 Buttocks</option>
                  <option value="5" ${grid.buttocks?.length === 5 ? 'selected' : ''}>5 Buttocks</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
          <button onclick="closeDesignGridModal()" class="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[10px] font-medium cursor-pointer">Cancel</button>
          <button onclick="saveDesignGridModal()" class="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded text-[10px] font-semibold transition cursor-pointer">Update Grid</button>
        </div>
      </div>
    </div>
  `;
}

// Modal Handlers
function openUploadHullModal() {
  document.getElementById('modal-upload-hull')?.classList.remove('hidden');
}
function closeUploadHullModal() {
  document.getElementById('modal-upload-hull')?.classList.add('hidden');
}

function openReferenceFrameModal() {
  document.getElementById('modal-reference-frame')?.classList.remove('hidden');
}
function closeReferenceFrameModal() {
  document.getElementById('modal-reference-frame')?.classList.add('hidden');
}

function openDesignGridModal() {
  document.getElementById('modal-design-grid')?.classList.remove('hidden');
}
function closeDesignGridModal() {
  document.getElementById('modal-design-grid')?.classList.add('hidden');
}

function saveReferenceFrameModal() {
  if (!activeLinesData) return;
  activeLinesData.reference_frame = {
    origin: document.getElementById('rf-origin')?.value || 'ap',
    baseline: document.getElementById('rf-baseline')?.value || 'molded',
    symmetry: document.getElementById('rf-symmetry')?.value || 'symmetric',
    units: document.getElementById('rf-units')?.value || 'm',
    scale_factor: parseFloat(document.getElementById('rf-scale')?.value) || 1.0
  };
  closeReferenceFrameModal();
  renderLinesPlan();
}

function saveDesignGridModal() {
  if (!activeLinesData) return;
  const lbp = parseFloat(document.getElementById('grid-lbp')?.value) || 69.85;
  const beam = parseFloat(document.getElementById('grid-beam')?.value) || 13.41;
  const depth = parseFloat(document.getElementById('grid-depth')?.value) || 5.18;
  const draft = parseFloat(document.getElementById('grid-draft')?.value) || 4.00;
  const preset = activeLinesData.preset_type || 'general_cargo';

  activeLinesData = HullLinesEngine.generateParametricHull(lbp, beam, depth, draft, 0.75, 0.98, preset);
  closeDesignGridModal();
  renderLinesPlan();
}

let selectedHullFile = null;
function handleHullFileSelected(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  selectedHullFile = file;
  const label = document.getElementById('upload-hull-file-label');
  const isMs = file.name.toLowerCase().endsWith('.msd') || file.name.toLowerCase().endsWith('.hmd');
  if (label) {
    label.innerHTML = `
      <span class="font-bold text-slate-900">${file.name}</span> 
      <span class="text-slate-400 font-normal">(${(file.size / 1024).toFixed(1)} KB)</span>
      ${isMs ? '<span class="ml-1.5 px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 text-[8.5px] font-bold uppercase">MAXSURF Model</span>' : ''}
    `;
  }
  const hint = document.getElementById('upload-maxsurf-hint');
  const btn = document.getElementById('btn-submit-upload-hull');
  if (hint) {
    if (isMs) hint.classList.remove('hidden');
    else hint.classList.add('hidden');
  }
  if (btn) {
    btn.textContent = isMs ? 'Detect MAXSURF Settings & Import' : 'Parse & Import';
  }
}

async function submitUploadHull() {
  if (!selectedHullFile) {
    alert('Please choose a file to upload first.');
    return;
  }
  const btn = document.getElementById('btn-submit-upload-hull');
  const isMs = selectedHullFile.name.toLowerCase().endsWith('.msd') || selectedHullFile.name.toLowerCase().endsWith('.hmd');
  if (btn) {
    btn.disabled = true;
    btn.textContent = isMs ? 'Connecting to MAXSURF & Detecting Settings...' : 'Parsing...';
  }

  const origin = document.getElementById('upload-origin-select')?.value || 'ap';
  const scale = document.getElementById('upload-scale-select')?.value || '1.0';

  const formData = new FormData();
  formData.append('file', selectedHullFile);
  formData.append('origin', origin);
  formData.append('scale_factor', scale);

  try {
    const res = await fetch('/api/v1/lines-plan/upload', {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || res.statusText);
    }
    const data = await res.json();
    activeLinesData = data;
    closeUploadHullModal();
    renderLinesPlan();

    if (data.maxsurf_settings) {
      const ms = data.maxsurf_settings;
      console.log('Detected MAXSURF settings:', ms);
    }
  } catch (err) {
    alert(`File upload failed: ${err.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = isMs ? 'Detect MAXSURF Settings & Import' : 'Parse & Import';
    }
  }
}

window.renderLinesPlan = renderLinesPlan;
window.setLinesViewMode = setLinesViewMode;
window.handleLinesPresetChange = handleLinesPresetChange;
window.handleCellOffsetChange = handleCellOffsetChange;
window.handleDeckOffsetChange = handleDeckOffsetChange;
window.recalculateHydrostaticsFromTable = recalculateHydrostaticsFromTable;
window.toggleLinesExportMenu = toggleLinesExportMenu;
window.exportLinesDxf = exportLinesDxf;
window.exportLinesExcel = exportLinesExcel;
window.exportLinesCsv = exportLinesCsv;
window.openUploadHullModal = openUploadHullModal;
window.closeUploadHullModal = closeUploadHullModal;
window.openReferenceFrameModal = openReferenceFrameModal;
window.closeReferenceFrameModal = closeReferenceFrameModal;
window.openDesignGridModal = openDesignGridModal;
window.closeDesignGridModal = closeDesignGridModal;
window.saveReferenceFrameModal = saveReferenceFrameModal;
window.saveDesignGridModal = saveDesignGridModal;
window.handleHullFileSelected = handleHullFileSelected;
window.submitUploadHull = submitUploadHull;
window.resetCamera3D = resetCamera3D;
window.syncMaxsurfToDashboard = syncMaxsurfToDashboard;
