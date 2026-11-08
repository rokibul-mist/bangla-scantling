/**
 * SaveVesselModal - Dialog to archive/save active calculated vessel into the Vessel Database
 */

function openSaveVesselModal(existingVesselId = null) {
  let modal = document.getElementById('save-vessel-modal');
  if (modal) {
    modal.remove();
  }

  const inputs = (window.appState && window.appState.dashboard_inputs) || {};
  const lsSummary = (window.appState && window.appState.lightship_summary) || {};
  const stats = (window.appState && window.appState.summary_stats) || {};

  const vesselName = inputs.vessel_name || 'M.V. CROWN MARINERS - 67';
  const vesselType = inputs.vessel_type || 'Steel Body Cargo Vessel';
  const hullType = inputs.hull_type || 'Single Hull';
  const route = inputs.route || inputs.proposed_route || 'Inland & bay crossing';
  const lbp = parseFloat(inputs.lbp || 69.85).toFixed(2);
  const breadth = parseFloat(inputs.breadth || 13.41).toFixed(2);
  const depth = parseFloat(inputs.depth || 5.18).toFixed(2);
  const draft = parseFloat(inputs.draft || 4.0).toFixed(2);

  const netSteelT = parseFloat(lsSummary.net_steel_t || 704.38).toFixed(2);
  const lightshipT = parseFloat(lsSummary.total_lightship_t || 1098.83).toFixed(2);
  const status = stats.status || 'COMPLIANT';
  const compCount = stats.compliant_count || 0;
  const totCount = stats.total_count || 0;

  modal = document.createElement('div');
  modal.id = 'save-vessel-modal';
  modal.className = 'fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-3 md:p-6';

  modal.innerHTML = `
    <div class="bg-white rounded-lg shadow-2xl flex flex-col w-full max-w-xl overflow-hidden border border-slate-300 animate-in fade-in zoom-in duration-150">
      
      <!-- Modal Header -->
      <div class="bg-slate-900 text-white px-4 py-3 flex items-center justify-between shrink-0 border-b border-slate-800">
        <div class="flex items-center gap-2.5">
          <div class="w-6 h-6 rounded bg-blue-600 flex items-center justify-center text-white font-black text-xs">
            DB
          </div>
          <div>
            <div class="text-xs font-bold tracking-tight text-white uppercase">
              Save Vessel Calculation to Database
            </div>
            <div class="text-[10px] text-slate-400">
              Persist complete vessel parameters, structural scantlings, and lightship booklet
            </div>
          </div>
        </div>
        <button onclick="closeSaveVesselModal()" class="text-slate-400 hover:text-white text-lg font-bold p-1 cursor-pointer">&times;</button>
      </div>

      <!-- Modal Body -->
      <div class="p-4 space-y-3.5 overflow-y-auto max-h-[75vh] text-xs">
        
        <!-- Live Snapshot Summary Banner -->
        <div class="bg-slate-50 border border-slate-200 rounded p-2.5 space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="font-bold text-slate-800 uppercase tracking-wide text-[11px]">Active Calculation Snapshot</span>
            <span class="px-2 py-0.5 rounded font-bold text-[10.5px] ${status === 'COMPLIANT' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-rose-100 text-rose-800 border border-rose-300'}">
              ${status} (${compCount}/${totCount} Rules)
            </span>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-2 pt-1 text-slate-600 font-mono text-[11px]">
            <div>Dimensions: <b class="text-slate-900">${lbp}×${breadth}×${depth}m</b></div>
            <div>Draft d: <b class="text-slate-900">${draft}m</b></div>
            <div>Net Steel: <b class="text-blue-900">${netSteelT} T</b></div>
            <div>Lightship: <b class="text-emerald-900">${lightshipT} T</b></div>
          </div>
        </div>

        <!-- Form Fields -->
        <div class="space-y-3">
          <div>
            <label class="block font-bold text-slate-700 mb-1">Vessel Name *</label>
            <input 
              type="text" 
              id="save-vessel-name" 
              class="compact-input w-full p-2 border rounded font-bold text-slate-900 bg-white border-slate-300 focus:border-blue-600" 
              value="${vesselName}"
              placeholder="e.g. M.V. CROWN MARINERS - 67"
              required
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label class="block font-medium text-slate-700 mb-1">Owner / Client</label>
              <input 
                type="text" 
                id="save-vessel-owner" 
                class="compact-input w-full p-2 border rounded text-slate-800 bg-white border-slate-300 focus:border-blue-600" 
                value="${inputs.owner || ''}"
                placeholder="e.g. Crown Navigation Ltd."
              />
            </div>
            <div>
              <label class="block font-medium text-slate-700 mb-1">Yard / Project Ref</label>
              <input 
                type="text" 
                id="save-vessel-yard-ref" 
                class="compact-input w-full p-2 border rounded text-slate-800 bg-white border-slate-300 focus:border-blue-600" 
                value="${inputs.yard_ref || ''}"
                placeholder="e.g. YD-2026/089"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-2 text-slate-700">
            <div>
              <span class="block text-[10.5px] font-medium text-slate-500 mb-0.5">Vessel Type</span>
              <div class="font-semibold text-slate-800 bg-slate-100 p-1.5 rounded border border-slate-200 text-[11px] truncate" title="${vesselType}">
                ${vesselType}
              </div>
            </div>
            <div>
              <span class="block text-[10.5px] font-medium text-slate-500 mb-0.5">Hull Construction</span>
              <div class="font-semibold text-slate-800 bg-slate-100 p-1.5 rounded border border-slate-200 text-[11px] truncate">
                ${hullType}
              </div>
            </div>
            <div>
              <span class="block text-[10.5px] font-medium text-slate-500 mb-0.5">Navigation Route</span>
              <div class="font-semibold text-slate-800 bg-slate-100 p-1.5 rounded border border-slate-200 text-[11px] truncate">
                ${route}
              </div>
            </div>
          </div>

          <div>
            <label class="block font-medium text-slate-700 mb-1">Engineering Notes & Remarks</label>
            <textarea 
              id="save-vessel-notes" 
              rows="3" 
              class="w-full p-2 border rounded text-xs text-slate-800 bg-white border-slate-300 focus:border-blue-600 font-sans"
              placeholder="Enter notes on structural scantlings, modifications, or classification requirements..."
            >${inputs.notes || ''}</textarea>
          </div>
        </div>

        <div id="save-vessel-alert" class="hidden text-xs p-2 rounded"></div>

      </div>

      <!-- Modal Footer -->
      <div class="bg-slate-50 border-t border-slate-200 px-4 py-2.5 flex items-center justify-between shrink-0">
        <span class="text-[10px] text-slate-500">Record will be saved permanently in vessel database</span>
        <div class="flex items-center gap-2">
          <button 
            type="button" 
            onclick="closeSaveVesselModal()" 
            class="px-3 py-1.5 border border-slate-300 hover:bg-slate-100 rounded text-xs font-semibold text-slate-700 transition cursor-pointer"
          >
            Cancel
          </button>
          <button 
            type="button" 
            id="btn-confirm-save-vessel"
            onclick="executeSaveVessel('${existingVesselId || ''}')" 
            class="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-bold transition flex items-center gap-1.5 shadow-xs cursor-pointer"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/></svg>
            <span id="btn-save-vessel-text">Save to Database</span>
          </button>
        </div>
      </div>

    </div>
  `;

  document.body.appendChild(modal);
  document.getElementById('save-vessel-name').focus();
}

function closeSaveVesselModal() {
  const modal = document.getElementById('save-vessel-modal');
  if (modal) {
    modal.remove();
  }
}

async function executeSaveVessel(existingVesselId) {
  const nameInput = document.getElementById('save-vessel-name');
  const ownerInput = document.getElementById('save-vessel-owner');
  const yardInput = document.getElementById('save-vessel-yard-ref');
  const notesInput = document.getElementById('save-vessel-notes');
  const btn = document.getElementById('btn-confirm-save-vessel');
  const btnText = document.getElementById('btn-save-vessel-text');
  const alertEl = document.getElementById('save-vessel-alert');

  const vName = (nameInput && nameInput.value.trim()) || '';
  if (!vName) {
    if (alertEl) {
      alertEl.className = 'text-xs p-2 rounded bg-rose-50 text-rose-800 border border-rose-200 block';
      alertEl.textContent = 'Please provide a valid vessel name.';
    }
    return;
  }

  if (btn) btn.disabled = true;
  if (btnText) btnText.textContent = 'Saving...';

  // Synchronize inputs in appState
  if (window.appState && window.appState.dashboard_inputs) {
    window.appState.dashboard_inputs.vessel_name = vName;
    window.appState.dashboard_inputs.owner = ownerInput ? ownerInput.value.trim() : '';
    window.appState.dashboard_inputs.yard_ref = yardInput ? yardInput.value.trim() : '';
    window.appState.dashboard_inputs.notes = notesInput ? notesInput.value.trim() : '';
  }

  const customMeta = {
    id: existingVesselId || undefined,
    vessel_name: vName,
    owner: ownerInput ? ownerInput.value.trim() : '',
    yard_ref: yardInput ? yardInput.value.trim() : '',
    notes: notesInput ? notesInput.value.trim() : ''
  };

  try {
    const res = await fetch('/api/vessels', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        state: window.appState,
        custom_meta: customMeta
      })
    });

    const data = await res.json();
    if (!res.ok || data.status !== 'ok') {
      throw new Error(data.detail || data.message || 'Failed to save vessel');
    }

    closeSaveVesselModal();
    showToastNotification(`Vessel '${vName}' saved to database successfully!`, 'success');

    // Update top header name
    const topNameEl = document.getElementById('top-vessel-name');
    if (topNameEl) topNameEl.textContent = vName;

    // If currently on vessel-db view, refresh it
    if (typeof renderVesselDb === 'function') {
      renderVesselDb();
    }

  } catch (err) {
    console.error('Save vessel error:', err);
    if (alertEl) {
      alertEl.className = 'text-xs p-2 rounded bg-rose-50 text-rose-800 border border-rose-200 block';
      alertEl.textContent = `Error: ${err.message}`;
    }
    if (btn) btn.disabled = false;
    if (btnText) btnText.textContent = 'Save to Database';
  }
}

function showToastNotification(message, type = 'info') {
  let toast = document.getElementById('app-toast-notification');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'app-toast-notification';
    toast.className = 'fixed bottom-4 right-4 z-50 flex items-center gap-2 px-4 py-2.5 rounded-lg shadow-lg text-xs font-bold text-white transition-all transform duration-300';
    document.body.appendChild(toast);
  }

  toast.className = `fixed bottom-4 right-4 z-50 flex items-center gap-2 px-4 py-2.5 rounded-lg shadow-lg text-xs font-bold text-white transition-all transform duration-300 ${
    type === 'success' ? 'bg-emerald-600' : (type === 'error' ? 'bg-rose-600' : 'bg-blue-600')
  }`;
  toast.textContent = message;
  toast.style.opacity = '1';
  toast.style.transform = 'translateY(0)';

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
  }, 3500);
}

window.openSaveVesselModal = openSaveVesselModal;
window.closeSaveVesselModal = closeSaveVesselModal;
window.executeSaveVessel = executeSaveVessel;
window.showToastNotification = showToastNotification;
