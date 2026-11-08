/**
 * Navigation - Controls tab switching, UI active states, and header sync
 */
class Navigation {
  static init() {
    document.querySelectorAll('.nav-tab').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = e.currentTarget.getAttribute('data-tab');
        if (target) {
          Navigation.switchTab(target);
        }
      });
    });
  }

  static switchTab(tabId) {
    if (window.appStore) {
      window.appStore.setActiveTab(tabId);
    }

    // Update active tab buttons
    document.querySelectorAll('.nav-tab').forEach(btn => {
      if (btn.getAttribute('data-tab') === tabId) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Hide all tab panes
    document.querySelectorAll('.tab-content').forEach(pane => {
      pane.classList.add('hidden');
    });

    // Show active pane
    const targetPane = document.getElementById(`tab-content-${tabId}`);
    if (targetPane) {
      targetPane.classList.remove('hidden');
    }

    if (tabId === 'vessel-db' && typeof renderVesselDb === 'function') {
      renderVesselDb();
    } else if (tabId === 'sheet2-calc' && typeof renderSheet2Calc === 'function') {
      renderSheet2Calc();
    } else if (tabId === 'dashboard' && typeof updateLiveDashboardDisplays === 'function') {
      updateLiveDashboardDisplays();
    } else if (tabId === 'calc-brain') {
      if (typeof renderCalcBrain === 'function') {
        renderCalcBrain();
      } else if (typeof updateLiveCalcBrainDisplays === 'function') {
        updateLiveCalcBrainDisplays();
      }
    } else if (tabId === 'application-form' && typeof renderApplicationForm === 'function') {
      renderApplicationForm();
    } else if (tabId === 'lightship' && typeof renderLightship === 'function') {
      renderLightship();
    } else if (tabId === 'strength' && typeof renderStrength === 'function') {
      renderStrength();
    } else if (tabId === 'tonnage-calc' && typeof renderTonnage === 'function') {
      renderTonnage();
    }

    // Trigger tab-specific render if registered
    if (window.eventBus) {
      window.eventBus.emit('tab:switched', tabId);
    }
  }

  static syncTopHeader(data) {
    const vesselNameEl = document.getElementById('top-vessel-name');
    if (vesselNameEl && data && data.dashboard_inputs) {
      vesselNameEl.textContent = data.dashboard_inputs.vessel_name || 'M.V. CROWN MARINERS - 67';
    }
  }
}

window.navigation = Navigation;
