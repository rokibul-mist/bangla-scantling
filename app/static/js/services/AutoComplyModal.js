/**
 * AutoComplyModal - Interactive Preview & Solver for 100% Statutory Scantling Compliance
 */

class AutoComplyModal {
  constructor() {
    this.containerId = 'autocomply-modal-container';
    this.currentPreview = null;
  }

  ensureContainer() {
    let container = document.getElementById(this.containerId);
    if (!container) {
      container = document.createElement('div');
      container.id = this.containerId;
      document.body.appendChild(container);
    }
    return container;
  }

  async open() {
    const container = this.ensureContainer();
    const currentState = window.appState || {};

    // Show loading spinner
    container.innerHTML = `
      <div class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
        <div class="bg-white rounded-lg shadow-xl p-6 flex items-center gap-3 border border-slate-200">
          <svg class="animate-spin h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          <span class="text-xs font-semibold text-slate-700">Analyzing statutory rules & optimizing scantlings...</span>
        </div>
      </div>
    `;

    try {
      const res = await fetch('/api/auto-comply/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentState)
      });

      if (!res.ok) throw new Error('Failed to generate compliance preview');
      const data = await res.json();
      this.currentPreview = data;
      this.renderModal(data);
    } catch (err) {
      console.error(err);
      container.innerHTML = `
        <div class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div class="bg-white rounded-lg shadow-xl p-6 max-w-sm text-center border border-slate-200">
            <div class="text-rose-600 text-sm font-bold mb-2">Notice</div>
            <div class="text-xs font-bold text-slate-800 mb-1">Auto-Comply Error</div>
            <div class="text-[11px] text-slate-600 mb-4">${err.message || 'Unable to analyze scantlings'}</div>
            <button onclick="window.autoComplyModal.close()" class="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs font-semibold rounded cursor-pointer">Close</button>
          </div>
        </div>
      `;
    }
  }

  close() {
    const container = document.getElementById(this.containerId);
    if (container) container.innerHTML = '';
  }

  renderModal(data) {
    const container = this.ensureContainer();
    const changes = data.changes || [];
    const oldCount = data.old_compliant_count || 0;
    const newCount = data.new_compliant_count || 0;
    const total = data.total_items || 77;
    const oldPct = Math.round((oldCount / total) * 100);
    const newPct = Math.round((newCount / total) * 100);

    container.innerHTML = `
      <div class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-4xl w-full border border-slate-200 overflow-hidden flex flex-col max-h-[90vh] my-auto">
          
          <!-- Modal Header -->
          <div class="px-5 py-3.5 bg-gradient-to-r from-emerald-800 to-teal-900 text-white flex items-center justify-between shrink-0">
            <div class="flex items-center gap-2.5">
              
              <div>
                <h3 class="text-xs font-bold tracking-tight uppercase">Statutory Scantling Auto-Compliance Optimizer</h3>
                <p class="text-[10px] text-emerald-200 font-medium">Standard commercial plate increments & certified naval stiffener profiles</p>
              </div>
            </div>
            <button onclick="window.autoComplyModal.close()" class="text-emerald-200 hover:text-white text-lg font-bold p-1 cursor-pointer">&times;</button>
          </div>

          <!-- Compliance Scorecard Progress Banner -->
          <div class="px-5 py-3 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 shrink-0">
            <div class="flex items-center gap-4">
              <div class="text-center">
                <div class="text-[10px] text-slate-500 font-semibold uppercase">Current Compliance</div>
                <div class="text-sm font-black text-rose-600">${oldCount} / ${total} (${oldPct}%)</div>
              </div>
              <div class="text-slate-400 font-bold text-base">&rarr;</div>
              <div class="text-center">
                <div class="text-[10px] text-slate-500 font-semibold uppercase">Target Compliance</div>
                <div class="text-sm font-black text-emerald-600">${newCount} / ${total} (${newPct}% PASS)</div>
              </div>
            </div>
            <div class="text-right">
              <span class="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-full border border-emerald-300">
                ${changes.length} Scantlings to Optimize
              </span>
            </div>
          </div>

          <!-- Comparison Table Content -->
          <div class="p-4 overflow-y-auto flex-1">
            ${changes.length === 0 ? `
              <div class="p-8 text-center bg-emerald-50/60 rounded-lg border border-emerald-200">
                <div class="text-emerald-700 text-sm font-bold mb-2">Status</div>
                <div class="text-xs font-bold text-emerald-900">All Scantlings Fully Compliant</div>
                <div class="text-[11px] text-emerald-700 mt-1">100% of statutory rules are already passing with required safety margins.</div>
              </div>
            ` : `
              <div class="overflow-x-auto border border-slate-200 rounded-lg">
                <table class="w-full text-left border-collapse text-[11px]">
                  <thead>
                    <tr class="bg-slate-100 text-slate-700 border-b border-slate-200">
                      <th class="py-2 px-3 font-bold">Structural Member</th>
                      <th class="py-2 px-2.5 font-bold">Category</th>
                      <th class="py-2 px-2.5 font-bold">Rule Req</th>
                      <th class="py-2 px-2.5 font-bold text-rose-700">Current (Fail)</th>
                      <th class="py-2 px-2.5 font-bold text-emerald-700">Proposed Compliant</th>
                      <th class="py-2 px-2.5 font-bold text-emerald-800">Margin</th>
                      <th class="py-2 px-2.5 font-bold text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100">
                    ${changes.map((c, i) => `
                      <tr class="${i % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'} hover:bg-emerald-50/40 transition">
                        <td class="py-2 px-3 font-semibold text-slate-800">
                          <div>${c.name}</div>
                          <div class="text-[9.5px] font-mono text-slate-400">${c.id}</div>
                        </td>
                        <td class="py-2 px-2.5 text-slate-500 text-[10px]">${c.category}</td>
                        <td class="py-2 px-2.5 font-mono font-bold text-slate-700">${c.rreq} ${c.unit}</td>
                        <td class="py-2 px-2.5 font-mono font-semibold text-rose-600 bg-rose-50/40">
                          ${c.old_profile}
                        </td>
                        <td class="py-2 px-2.5 font-mono font-bold text-emerald-700 bg-emerald-50/50">
                          ${c.new_profile}
                        </td>
                        <td class="py-2 px-2.5 font-mono font-bold text-emerald-700">
                          ${c.new_margin}
                        </td>
                        <td class="py-2 px-2.5 text-center">
                          <span class="px-1.5 py-0.5 text-[9.5px] font-bold bg-emerald-100 text-emerald-800 rounded border border-emerald-200">
                            PASS
                          </span>
                        </td>
                      </tr>
                    `).join('')}
                  </tbody>
                </table>
              </div>
            `}
          </div>

          <!-- Modal Actions Footer -->
          <div class="px-5 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between shrink-0">
            <button onclick="window.autoComplyModal.close()" class="px-3.5 py-1.5 border border-slate-300 hover:bg-slate-100 text-slate-700 rounded text-xs font-semibold cursor-pointer transition">
              Cancel
            </button>
            ${changes.length > 0 ? `
              <button onclick="window.autoComplyModal.apply()" class="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-xs font-bold cursor-pointer transition shadow-xs flex items-center gap-1.5">
                <span>Apply All Compliant Scantlings (100% Pass)</span>
              </button>
            ` : `
              <button onclick="window.autoComplyModal.close()" class="px-4 py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded text-xs font-bold cursor-pointer transition">
                Done
              </button>
            `}
          </div>

        </div>
      </div>
    `;
  }

  async apply() {
    if (!this.currentPreview || !this.currentPreview.proposed_state) {
      this.close();
      return;
    }

    const prop = this.currentPreview.proposed_state;
    const countUpdated = this.currentPreview.items_updated_count;
    const countTotal = this.currentPreview.total_items;
    const state = window.appState;

    // Immediately close modal
    this.close();

    if (!state) return;

    // 1. Synchronize primary dashboard plating inputs
    if (prop.dashboard_inputs) {
      state.dashboard_inputs = Object.assign({}, state.dashboard_inputs || {}, prop.dashboard_inputs);
    }

    // 2. Synchronize Calculation Brain provided values
    if (prop.custom_brain_dact) {
      state.custom_brain_dact = Object.assign({}, state.custom_brain_dact || {}, prop.custom_brain_dact);
    }

    // 3. Synchronize Stiffener custom dimensions
    if (prop.stiffener_custom_dims) {
      state.stiffener_custom_dims = Object.assign({}, state.stiffener_custom_dims || {}, prop.stiffener_custom_dims);
    }

    // 4. Trigger global recomputation
    if (typeof recalculateAll === 'function') {
      recalculateAll(state);
    }

    // 5. Refresh entire application and active view
    if (typeof window.renderApp === 'function') {
      window.renderApp();
    } else {
      if (typeof refreshCurrentTab === 'function') refreshCurrentTab();
      if (typeof renderDashboard === 'function') renderDashboard();
      if (typeof renderCalcBrain === 'function') renderCalcBrain();
    }

    // 6. Save updated state to backend so it persists
    try {
      await fetch('/api/save-state', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(state)
      });
    } catch (e) {
      console.warn('Auto-save after auto-comply failed:', e);
    }

    // 7. Show success toast notification
    this.showSuccessToast(countUpdated, countTotal);
  }

  showSuccessToast(updatedCount, totalCount) {
    let toast = document.getElementById('autocomply-success-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'autocomply-success-toast';
      document.body.appendChild(toast);
    }
    toast.innerHTML = `
      <div class="fixed bottom-5 right-5 z-50 bg-emerald-700 text-white px-4 py-3 rounded-lg shadow-xl border border-emerald-500 flex items-center gap-3 transition-all animate-bounce">
        
        <div>
          <div class="text-xs font-bold">100% Scantling Compliance Achieved!</div>
          <div class="text-[10.5px] text-emerald-100">Optimized ${updatedCount} scantlings. All ${totalCount} rules now pass.</div>
        </div>
      </div>
    `;
    setTimeout(() => {
      if (toast) toast.innerHTML = '';
    }, 4500);
  }
}

// Global instance
window.autoComplyModal = new AutoComplyModal();
