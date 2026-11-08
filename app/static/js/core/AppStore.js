/**
 * AppStore - Centralized Reactive State Store
 */
class AppStore {
  constructor() {
    this.state = {
      data: null,
      activeTab: 'dashboard',
      autosaveEnabled: true,
      activeDetailSheetId: 1,
      saveTimeout: null,
      lastSavedStateString: null
    };
    this.listeners = [];
  }

  getState() {
    return this.state;
  }

  getData() {
    return this.state.data;
  }

  setData(data) {
    this.state.data = data;
    this.notify('data', this.state.data);
  }

  getActiveTab() {
    return this.state.activeTab;
  }

  setActiveTab(tabId) {
    this.state.activeTab = tabId;
    this.notify('tab', tabId);
  }

  getAutosaveEnabled() {
    return this.state.autosaveEnabled;
  }

  setAutosaveEnabled(enabled) {
    this.state.autosaveEnabled = enabled;
    this.notify('autosave', enabled);
  }

  getActiveDetailSheetId() {
    return this.state.activeDetailSheetId;
  }

  setActiveDetailSheetId(id) {
    this.state.activeDetailSheetId = id;
    this.notify('detailSheet', id);
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notify(changeType, payload) {
    this.listeners.forEach(fn => {
      try {
        fn(this.state, changeType, payload);
      } catch (e) {
        console.error('Error in store listener:', e);
      }
    });
    if (window.eventBus) {
      window.eventBus.emit(`store:${changeType}`, payload);
      window.eventBus.emit('store:changed', this.state);
    }
  }
}

window.appStore = new AppStore();
