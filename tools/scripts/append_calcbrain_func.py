with open('app/static/js/views/CalcBrainView.js', 'r', encoding='utf-8') as f:
    text = f.read()

helper_code = '''

function handleCalcBrainProvidedChange(memberId, rawVal) {
  if (!appState || !appState.calculation_brain) return;
  const s = String(rawVal).trim().replace(',', '.');
  const num = (s === '' || s === '-' || s === '.') ? '' : (parseFloat(s) || 0);

  const it = appState.calculation_brain.find(b => b.id === memberId || String(b.item) === String(memberId));
  if (!it) return;

  if (it.type === 'stiffener') {
    appState.stiffener_custom_dims = appState.stiffener_custom_dims || {};
    appState.stiffener_custom_dims[it.id] = appState.stiffener_custom_dims[it.id] || {};
    if (num === '') {
      delete appState.stiffener_custom_dims[it.id].custom_z;
    } else {
      appState.stiffener_custom_dims[it.id].custom_z = num;
    }
  } else if (it.type === 'plate') {
    const pKey = it.bound_plate_key || it.id;
    appState.dashboard_inputs = appState.dashboard_inputs || {};
    appState.dashboard_inputs[pKey] = num;
  } else {
    appState.dashboard_inputs = appState.dashboard_inputs || {};
    appState.dashboard_inputs[it.id] = num;
  }
  it.dact = num;

  recalculateAll(appState);
  updateTopStats();
  updateLiveCalcBrainDisplays();
  if (typeof updateLiveDashboardDisplays === 'function') {
    updateLiveDashboardDisplays();
  }
  triggerLivePdfUpdateDebounced();
  triggerAutosaveDebounced();
}

function updateLiveCalcBrainDisplays() {
  if (!appState || !appState.calculation_brain) return;
  const items = appState.calculation_brain;
  items.forEach(b => {
    const idKey = b.id || b.item;
    const reqEl = document.getElementById(`calcbrain-req-${idKey}`);
    if (reqEl) {
      reqEl.textContent = typeof b.rreq === 'number' ? b.rreq.toFixed(2) : (b.rreq || '-');
    }

    const provEl = document.getElementById(`calcbrain-input-${idKey}`);
    if (provEl && document.activeElement !== provEl) {
      const dVal = b.dact !== undefined ? b.dact : 0;
      const formatted = typeof dVal === 'number' ? (Number.isInteger(dVal) ? String(dVal) : dVal.toFixed(2)) : String(dVal);
      if (provEl.value !== formatted && parseFloat(provEl.value) !== dVal) {
        provEl.value = formatted;
      }
    }

    const marginEl = document.getElementById(`calcbrain-margin-${idKey}`);
    if (marginEl) {
      const isComp = b.status === 'COMPLIANT';
      marginEl.textContent = typeof b.margin === 'number' ? (b.margin >= 0 ? '+' : '') + b.margin.toFixed(2) : (b.margin || '');
      marginEl.className = `text-right font-mono text-[11.5px] font-semibold ${isComp ? 'text-emerald-700' : 'text-rose-700'}`;
    }

    const statusEl = document.getElementById(`calcbrain-status-${idKey}`);
    if (statusEl) {
      const isComp = b.status === 'COMPLIANT';
      statusEl.textContent = b.status || 'COMPLIANT';
      statusEl.className = isComp ? 'badge-comp' : 'badge-def';
    }
  });

  // Update summary badge
  const stats = appState.summary_stats || {};
  const brainBadge = document.getElementById('calcbrain-summary-badge');
  if (brainBadge) {
    brainBadge.textContent = `${stats.compliant_items || 0} / ${stats.total_items || 0} COMPLIANT (${stats.compliance_pct || '100.0'}%)`;
  }
}
'''

if 'function handleCalcBrainProvidedChange' not in text:
    text += helper_code

with open('app/static/js/views/CalcBrainView.js', 'w', encoding='utf-8') as f:
    f.write(text)

print('Appended handleCalcBrainProvidedChange successfully!')
