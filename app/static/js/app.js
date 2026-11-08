/**

 * Bangladesh Naval Architecture Scantling System

 * Modular Application Coordinator & State Controller

 */



let appState = null;

let currentTab = 'dashboard';

let currentSheet2Index = 0;

let currentAppFormPage = 1;

let empiricalFilterPart = 'all';

let empiricalSearchQuery = '';



// Autosave & Persistence State

let isAutosaveEnabled = localStorage.getItem('bangla_scantling_autosave') !== 'false';

let autosaveDebounceTimer = null;



document.addEventListener('DOMContentLoaded', async () => {

  await loadInitialState();

  setupEventListeners();

  renderApp();

});



async function loadInitialState() {

  try {

    const res = await fetch('/api/initial-state');

    if (!res.ok) throw new Error('Failed to fetch initial state');

    appState = await res.json();



    // Check browser localStorage for saved calculation session

    const localSaved = localStorage.getItem('bangla_scantling_saved_state');

    if (localSaved) {

      try {

        const parsed = JSON.parse(localSaved);

        if (parsed && parsed.dashboard_inputs) {

          appState.dashboard_inputs = Object.assign({}, appState.dashboard_inputs, parsed.dashboard_inputs);

          if (parsed.stiffener_profiles) appState.stiffener_profiles = parsed.stiffener_profiles;

          if (parsed.scantling_checklist) appState.scantling_checklist = parsed.scantling_checklist;

          if (parsed.lightship_plates) appState.lightship_plates = parsed.lightship_plates;

          if (parsed.lightship_angles) appState.lightship_angles = parsed.lightship_angles;

          if (parsed.calculation_brain && parsed.calculation_brain[0]?.derivation) appState.calculation_brain = parsed.calculation_brain;

          if (parsed.designer_seal_png !== undefined) appState.designer_seal_png = parsed.designer_seal_png;

          if (parsed.checker_seal_png !== undefined) appState.checker_seal_png = parsed.checker_seal_png;

          appState.has_restored_save = true;

          appState.last_saved_time = parsed.last_saved_time || 'Restored session';

        }

      } catch (e) {

        console.warn('Could not parse localStorage state:', e);

      }

    }



    // Restore seals from localStorage if available

    const savedDes = localStorage.getItem('bs_designer_seal');

    if (savedDes) {

      appState.designer_seal_png = savedDes;

    } else if (appState.designer_seal_png === undefined || appState.designer_seal_png === null) {

      appState.designer_seal_png = '/static/designer_seal_default.png';

    }



    const savedChk = localStorage.getItem('bs_checker_seal');

    if (savedChk) {

      appState.checker_seal_png = savedChk;

    } else if (appState.checker_seal_png === undefined || appState.checker_seal_png === null) {

      appState.checker_seal_png = '/static/checker_seal_default.png';

    }



    window.appState = appState;



    if (!appState.dashboard_inputs.hull_type) {

      appState.dashboard_inputs.hull_type = 'Double Bottom';

    }

    if (!appState._default_plate_qtys && appState.lightship_plates) {

      appState._default_plate_qtys = appState.lightship_plates.map(p => ({ sn: p.sn, qty: p.qty }));

    }

    if (!appState._default_angle_qtys && appState.lightship_angles) {

      appState._default_angle_qtys = appState.lightship_angles.map(a => ({ sn: a.sn, qty: a.qty }));

    }



    if (typeof recalculateAll === 'function') {

      recalculateAll(appState);

    }

    if (typeof updateSealUI === 'function') {

      updateSealUI();

    }



    // Sync Autosave UI toggle state

    const toggle = document.getElementById('toggle-autosave');

    if (toggle) toggle.checked = isAutosaveEnabled;



    const statusText = document.getElementById('save-status-text');

    if (statusText && appState.has_restored_save) {

      statusText.textContent = appState.last_saved_time ? `Restored (${appState.last_saved_time})` : 'Restored saved calculation';

    }

  } catch (err) {

    console.error('Error loading state:', err);

    alert('Failed to load vessel data: ' + err.message);

  }

}



function handleAutosaveToggle(enabled) {

  isAutosaveEnabled = enabled;

  localStorage.setItem('bangla_scantling_autosave', enabled);

  const statusText = document.getElementById('save-status-text');

  const dot = document.getElementById('save-status-dot');

  if (enabled) {

    if (dot) dot.className = 'w-1.5 h-1.5 rounded-full bg-emerald-500';

    if (statusText) statusText.textContent = 'Autosave active';

    triggerAutosaveDebounced();

  } else {

    if (dot) dot.className = 'w-1.5 h-1.5 rounded-full bg-amber-500';

    if (statusText) statusText.textContent = 'Autosave paused (Manual save only)';

  }

}



function triggerAutosaveDebounced() {

  if (!isAutosaveEnabled) return;

  if (autosaveDebounceTimer) clearTimeout(autosaveDebounceTimer);



  const statusText = document.getElementById('save-status-text');

  const dot = document.getElementById('save-status-dot');

  if (dot) dot.className = 'w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse';

  if (statusText) statusText.textContent = 'Autosaving...';



  autosaveDebounceTimer = setTimeout(async () => {

    await saveProjectState(false);

  }, 1000);

}



async function saveProjectState(isManual = false) {

  if (!appState) return;

  if (autosaveDebounceTimer) {

    clearTimeout(autosaveDebounceTimer);

    autosaveDebounceTimer = null;

  }



  const timeStr = new Date().toLocaleTimeString();

  appState.last_saved_time = timeStr;



  const saveBtn = document.getElementById('btn-save-project');

  const saveIcon = document.getElementById('save-btn-icon');

  const saveText = document.getElementById('save-btn-text');

  const statusText = document.getElementById('save-status-text');

  const dot = document.getElementById('save-status-dot');



  if (isManual && saveBtn) {

    saveBtn.className = 'w-full px-3 py-2 bg-emerald-600 text-white rounded text-xs font-bold shadow-xs transition text-center';

    if (saveIcon) saveIcon.textContent = '';

    if (saveText) saveText.textContent = 'Saved!';

  }



  // 1. Save locally to browser

  try {

    localStorage.setItem('bangla_scantling_saved_state', JSON.stringify(appState));

  } catch (err) {

    console.warn('Could not save to localStorage:', err);

  }



  // 2. Persist to server backend

  try {

    await fetch('/api/save-state', {

      method: 'POST',

      headers: { 'Content-Type': 'application/json' },

      body: JSON.stringify(appState)

    });

  } catch (err) {

    console.warn('Could not save to server:', err);

  }



  if (dot) dot.className = 'w-1.5 h-1.5 rounded-full bg-emerald-500';

  if (statusText) statusText.textContent = `${isManual ? 'Saved' : 'Autosaved'} at ${timeStr}`;



  if (isManual && saveBtn) {

    setTimeout(() => {

      saveBtn.className = 'w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-bold shadow-xs transition text-center';

      if (saveIcon) saveIcon.textContent = '';

      if (saveText) saveText.textContent = 'Save Calculation';

    }, 1800);

  }

}



function setupEventListeners() {

  document.querySelectorAll('.nav-tab').forEach(tab => {

    tab.addEventListener('click', () => {

      const tabTarget = tab.getAttribute('data-tab');

      switchTab(tabTarget);

    });

  });



        document.getElementById('btn-print-view')?.addEventListener('click', () => window.print());

  document.getElementById('btn-reset-default')?.addEventListener('click', resetToDefaults);

}



function switchTab(tabId) {

  currentTab = tabId;

  document.querySelectorAll('.nav-tab').forEach(t => {

    if (t.getAttribute('data-tab') === tabId) {

      t.classList.add('active');

    } else {

      t.classList.remove('active');

    }

  });



  document.querySelectorAll('.tab-content').forEach(c => {

    c.classList.add('hidden');

  });



  const activeContent = document.getElementById(`tab-content-${tabId}`);

  if (activeContent) {

    activeContent.classList.remove('hidden');

  }



  renderApp();

}



function renderApp() {

  if (!appState) return;



  updateTopStats();



  if (currentTab === 'dashboard' || currentTab === 'cover-page') {

    if (typeof renderDashboard === 'function') renderDashboard();

  } else if (currentTab === 'application-form') {

    if (typeof renderApplicationForm === 'function') renderApplicationForm();

  } else if (currentTab === 'sheet2-calc') {

    if (typeof renderSheet2Calc === 'function') renderSheet2Calc();

  } else if (currentTab === 'lightship') {

    if (typeof renderLightship === 'function') renderLightship();

  } else if (currentTab === 'strength') {

    if (typeof renderStrength === 'function') renderStrength();

  } else if (currentTab === 'empirical-tables') {

    if (typeof renderEmpiricalTables === 'function') renderEmpiricalTables();

  } else if (currentTab === 'vessel-db') {

    if (typeof renderVesselDb === 'function') renderVesselDb();

  } else if (currentTab === 'calc-brain') {

    if (typeof renderCalcBrain === 'function') renderCalcBrain();
  } else if (currentTab === 'stability') {
    if (window.statutoryViews && typeof window.statutoryViews.renderStability === 'function') window.statutoryViews.renderStability();
  } else if (currentTab === 'freeboard') {
    if (window.statutoryViews && typeof window.statutoryViews.renderFreeboard === 'function') window.statutoryViews.renderFreeboard();
  } else if (currentTab === 'subdivision') {
    if (window.statutoryViews && typeof window.statutoryViews.renderSubdivision === 'function') window.statutoryViews.renderSubdivision();
  } else if (currentTab === 'steering') {
    if (window.statutoryViews && typeof window.statutoryViews.renderSteering === 'function') window.statutoryViews.renderSteering();
  } else if (currentTab === 'machinery') {
    if (window.statutoryViews && typeof window.statutoryViews.renderMachinery === 'function') window.statutoryViews.renderMachinery();
  } else if (currentTab === 'equipment') {
    if (window.statutoryViews && typeof window.statutoryViews.renderEquipment === 'function') window.statutoryViews.renderEquipment();
  } else if (currentTab === 'tonnage-calc') {
    if (typeof renderTonnage === 'function') renderTonnage();
  } else if (currentTab === 'passenger-tonnage') {
    if (window.statutoryViews && typeof window.statutoryViews.renderPassengerTonnage === 'function') window.statutoryViews.renderPassengerTonnage();

  }

}



function updateTopStats() {

  const inputs = appState.dashboard_inputs || {};

  const vNameEl = document.getElementById('top-vessel-name');

  if (vNameEl) vNameEl.textContent = inputs.vessel_name || 'Vessel';

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

    if (typeof updateSealUI === 'function') {

      updateSealUI();

    }

    const statusText = document.getElementById('save-status-text');

    const dot = document.getElementById('save-status-dot');

    if (dot) dot.className = 'w-1.5 h-1.5 rounded-full bg-emerald-500';

    if (statusText) statusText.textContent = 'Reset to master defaults';

  }

}



// Global window bindings

window.resetToDefaults = resetToDefaults;

window.switchTab = switchTab;

window.renderApp = renderApp;

window.loadInitialState = loadInitialState;

window.handleAutosaveToggle = handleAutosaveToggle;

window.triggerAutosaveDebounced = triggerAutosaveDebounced;

window.saveProjectState = saveProjectState;



function toggleAppFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(err => console.log(err));
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen().catch(err => console.log(err));
    }
  }
}

window.toggleAppFullscreen = toggleAppFullscreen;
