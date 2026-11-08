/**
 * SealManager - Controls Designer & Checker seal uploads, removals, and DOM preview synchronization
 * Persists custom seals in localStorage and syncs with live appState for PDF booklet generation.
 */

function getActiveState() {
  if (typeof appState !== 'undefined' && appState) {
    window.appState = appState;
    return appState;
  }
  if (window.appState) return window.appState;
  if (window.appStore && window.appStore.getData()) {
    window.appState = window.appStore.getData();
    return window.appState;
  }
  window.appState = {};
  return window.appState;
}

class SealManager {
  static init() {
    const savedDesigner = localStorage.getItem('bs_designer_seal');
    const savedChecker = localStorage.getItem('bs_checker_seal');

    const state = getActiveState();
    if (savedDesigner) {
      state.designer_seal_png = savedDesigner;
    } else if (!state.designer_seal_png) {
      state.designer_seal_png = '/static/designer_seal_default.png';
    }

    if (savedChecker) {
      state.checker_seal_png = savedChecker;
    } else if (!state.checker_seal_png) {
      state.checker_seal_png = '/static/checker_seal_default.png';
    }

    if (typeof appState !== 'undefined' && appState) {
      appState.designer_seal_png = state.designer_seal_png;
      appState.checker_seal_png = state.checker_seal_png;
    }
    window.appState = state;

    SealManager.updateSealUI();
  }

  static handleSealUpload(role, event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target.result;
      const state = getActiveState();
      
      if (role === 'designer') {
        state.designer_seal_png = dataUrl;
        try { localStorage.setItem('bs_designer_seal', dataUrl); } catch(err) { console.warn(err); }
      } else {
        state.checker_seal_png = dataUrl;
        try { localStorage.setItem('bs_checker_seal', dataUrl); } catch(err) { console.warn(err); }
      }

      if (typeof appState !== 'undefined' && appState) {
        if (role === 'designer') appState.designer_seal_png = dataUrl;
        else appState.checker_seal_png = dataUrl;
      }
      window.appState = state;
      
      SealManager.updateSealUI();
      
      if (typeof window.triggerAutosaveDebounced === 'function') {
        window.triggerAutosaveDebounced();
      } else if (typeof triggerAutosaveDebounced === 'function') {
        triggerAutosaveDebounced();
      }
    };
    reader.readAsDataURL(file);
  }

  static clearSeal(role) {
    const state = getActiveState();
    if (role === 'designer') {
      state.designer_seal_png = '/static/designer_seal_default.png';
      try { localStorage.removeItem('bs_designer_seal'); } catch(err) {}
      const inp = document.getElementById('upload-designer-seal');
      if (inp) inp.value = '';
    } else {
      state.checker_seal_png = '/static/checker_seal_default.png';
      try { localStorage.removeItem('bs_checker_seal'); } catch(err) {}
      const inp = document.getElementById('upload-checker-seal');
      if (inp) inp.value = '';
    }

    if (typeof appState !== 'undefined' && appState) {
      if (role === 'designer') appState.designer_seal_png = state.designer_seal_png;
      else appState.checker_seal_png = state.checker_seal_png;
    }
    window.appState = state;

    SealManager.updateSealUI();
    
    if (typeof window.triggerAutosaveDebounced === 'function') {
      window.triggerAutosaveDebounced();
    } else if (typeof triggerAutosaveDebounced === 'function') {
      triggerAutosaveDebounced();
    }
  }

  static updateSealUI() {
    const state = getActiveState();
    const desSeal = state.designer_seal_png || '/static/designer_seal_default.png';
    const chkSeal = state.checker_seal_png || '/static/checker_seal_default.png';
    const isCustomDes = desSeal.startsWith('data:image');
    const isCustomChk = chkSeal.startsWith('data:image');

    // Designer Seal UI
    const desPreview = document.getElementById('preview-designer-seal');
    const desImg = document.getElementById('img-designer-seal');
    const desClearBtn = document.getElementById('btn-clear-designer-seal');

    if (desImg) desImg.src = desSeal;
    if (desPreview) desPreview.classList.remove('hidden');
    if (desClearBtn) {
      if (isCustomDes) desClearBtn.classList.remove('hidden');
      else desClearBtn.classList.add('hidden');
    }

    // Checker Seal UI
    const chkPreview = document.getElementById('preview-checker-seal');
    const chkImg = document.getElementById('img-checker-seal');
    const chkClearBtn = document.getElementById('btn-clear-checker-seal');

    if (chkImg) chkImg.src = chkSeal;
    if (chkPreview) chkPreview.classList.remove('hidden');
    if (chkClearBtn) {
      if (isCustomChk) chkClearBtn.classList.remove('hidden');
      else chkClearBtn.classList.add('hidden');
    }
  }
}

// Auto-initialize when script loads or DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => SealManager.init());
} else {
  SealManager.init();
}

window.sealManager = SealManager;
window.handleSealUpload = (role, event) => SealManager.handleSealUpload(role, event);
window.clearSeal = (role) => SealManager.clearSeal(role);
window.updateSealUI = () => SealManager.updateSealUI();
