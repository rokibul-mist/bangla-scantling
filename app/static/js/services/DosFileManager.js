/**
 * DosFileManager - Department of Shipping (DOS) Project Serialization & File Manager.
 * Enables saving complete vessel scantling calculations to a .dos project file
 * and opening/restoring them dynamically across all application views.
 */
class DosFileManager {
  static init() {
    const saveBtn = document.getElementById('btn-save-dos');
    const openBtn = document.getElementById('btn-open-dos');
    const fileInput = document.getElementById('input-open-dos');

    if (saveBtn) {
      saveBtn.addEventListener('click', () => DosFileManager.exportDosFile());
    }

    if (openBtn && fileInput) {
      openBtn.addEventListener('click', () => fileInput.click());
      fileInput.addEventListener('change', (e) => DosFileManager.handleFileSelect(e));
    }
  }

  static exportDosFile() {
    const state = window.appState || {};
    const inputs = state.dashboard_inputs || {};
    const vesselName = inputs.vessel_name || 'Vessel';
    const hullType = inputs.hull_type || 'Double Bottom';
    const timestamp = new Date().toISOString();

    const dosPayload = {
      file_format: "BANGLA_DOS_PROJECT",
      format_version: "1.0",
      generator: "Department of Shipping (DOS) Inland Vessel Statutory Compliance System - SRO 308/2001",
      timestamp: timestamp,
      vessel_name: vesselName,
      vessel_type: inputs.vessel_type || 'Steel Body Cargo Vessel',
      hull_type: hullType,
      project_data: {
        dashboard_inputs: Object.assign({}, inputs),
        stiffener_custom_dims: Object.assign({}, state.stiffener_custom_dims || {}),
        stiffener_profiles: state.stiffener_profiles ? JSON.parse(JSON.stringify(state.stiffener_profiles)) : [],
        scantling_checklist: state.scantling_checklist ? JSON.parse(JSON.stringify(state.scantling_checklist)) : [],
        lightship_plates: state.lightship_plates ? JSON.parse(JSON.stringify(state.lightship_plates)) : [],
        lightship_angles: state.lightship_angles ? JSON.parse(JSON.stringify(state.lightship_angles)) : [],
        designer_seal_png: state.designer_seal_png || null,
        checker_seal_png: state.checker_seal_png || null,
        application_form_pages: state.application_form_pages || {},
        calculation_brain: state.calculation_brain || {},
        custom_brain_dact: state.custom_brain_dact || {}
      }
    };

    const jsonStr = JSON.stringify(dosPayload, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/octet-stream' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const safeName = vesselName.replace(/[^a-zA-Z0-9_\-]/g, '_');
    const safeHull = hullType.replace(/[^a-zA-Z0-9_\-]/g, '_');
    a.href = url;
    a.download = `${safeName}_${safeHull}.dos`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    // Button visual feedback
    const btn = document.getElementById('btn-save-dos');
    if (btn) {
      const origText = btn.innerHTML;
      btn.innerHTML = '<span>Saved .dos!</span>';
      setTimeout(() => { btn.innerHTML = origText; }, 2000);
    }
  }

  static handleFileSelect(event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const content = e.target.result;
        const parsed = JSON.parse(content);
        await DosFileManager.loadProjectData(parsed, file.name);
      } catch (err) {
        console.error('Failed to parse .dos file:', err);
        alert('Invalid or corrupted .dos file: ' + err.message);
      } finally {
        event.target.value = ''; // Reset input so same file can be reopened if desired
      }
    };
    reader.onerror = () => {
      alert('Error reading .dos file');
      event.target.value = '';
    };
    reader.readAsText(file);
  }

  static async loadProjectData(parsed, fileName) {
    let projectData = null;
    let vesselName = 'Vessel';
    let hullType = 'Double Bottom';

    if (parsed.file_format === 'BANGLA_DOS_PROJECT' && parsed.project_data) {
      projectData = parsed.project_data;
      vesselName = parsed.vessel_name || projectData.dashboard_inputs?.vessel_name || vesselName;
      hullType = parsed.hull_type || projectData.dashboard_inputs?.hull_type || hullType;
    } else if (parsed.dashboard_inputs) {
      projectData = parsed;
      vesselName = parsed.dashboard_inputs.vessel_name || vesselName;
      hullType = parsed.dashboard_inputs.hull_type || hullType;
    } else {
      throw new Error('Unrecognized DOS file format. Missing project data or dashboard inputs.');
    }

    if (!window.appState) window.appState = {};

    // 1. Merge dashboard inputs
    if (projectData.dashboard_inputs) {
      window.appState.dashboard_inputs = Object.assign({}, window.appState.dashboard_inputs || {}, projectData.dashboard_inputs);
    }

    // 2. Merge structural properties
    if (projectData.stiffener_custom_dims) {
      window.appState.stiffener_custom_dims = Object.assign({}, projectData.stiffener_custom_dims);
    }
    if (projectData.stiffener_profiles) {
      window.appState.stiffener_profiles = projectData.stiffener_profiles;
    }
    if (projectData.scantling_checklist) {
      window.appState.scantling_checklist = projectData.scantling_checklist;
    }
    if (projectData.lightship_plates) {
      window.appState.lightship_plates = projectData.lightship_plates;
    }
    if (projectData.lightship_angles) {
      window.appState.lightship_angles = projectData.lightship_angles;
    }
    if (projectData.calculation_brain) {
      window.appState.calculation_brain = projectData.calculation_brain;
    }
    if (projectData.custom_brain_dact) {
      window.appState.custom_brain_dact = projectData.custom_brain_dact;
    }
    if (projectData.application_form_pages) {
      window.appState.application_form_pages = projectData.application_form_pages;
    }

    // 3. Restore Seals
    if (projectData.designer_seal_png) {
      window.appState.designer_seal_png = projectData.designer_seal_png;
      localStorage.setItem('bs_designer_seal', projectData.designer_seal_png);
    }
    if (projectData.checker_seal_png) {
      window.appState.checker_seal_png = projectData.checker_seal_png;
      localStorage.setItem('bs_checker_seal', projectData.checker_seal_png);
    }

    // 4. Trigger statutory recalculations
    if (typeof recalculateAll === 'function') {
      recalculateAll(window.appState);
    }

    // 5. Update Seals UI
    if (typeof updateSealUI === 'function') {
      updateSealUI();
    }

    // 6. Persist to browser and backend server
    if (typeof saveProjectState === 'function') {
      await saveProjectState(true);
    }

    // 7. Update Top Header Stats
    if (typeof updateTopStats === 'function') {
      updateTopStats();
    }

    // 8. Re-render active view
    if (typeof renderApp === 'function') {
      renderApp();
    }

    // 9. Status feedback
    const statusText = document.getElementById('save-status-text');
    if (statusText) {
      statusText.textContent = `Opened: ${vesselName} (${hullType})`;
    }

    console.log(`Successfully opened DOS Project: ${vesselName} (${hullType}) from ${fileName}`);
  }
}

// Hook to DOM readiness
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => DosFileManager.init());
} else {
  DosFileManager.init();
}

window.DosFileManager = DosFileManager;
