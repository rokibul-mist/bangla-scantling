/**
 * Main Application Bootstrap - Orchestrates Store, Views, Navigation, and Lifecycle
 */
class MainApp {
  static async init() {
    console.log('Initializing Bangladesh Naval Scantlings Application...');
    
    // 1. Initialize Navigation
    if (window.navigation) {
      window.navigation.init();
    }

    // 2. Load Initial State from API
    try {
      const data = await window.apiClient.getInitialState();
      window.appState = data;
      if (window.appStore) {
        window.appStore.setData(data);
      }
      
      // Sync Seal UI
      if (window.sealManager) {
        window.sealManager.updateSealUI();
      }

      // Render Active View
      if (typeof window.renderApp === 'function') {
        window.renderApp();
      }

      console.log('Application initialized successfully with state:', data);
    } catch (err) {
      console.error('Initialization error:', err);
    }
  }
}

window.mainApp = MainApp;
