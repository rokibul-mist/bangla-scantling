/**
 * LightshipView - Renders Lightship Plates, Angles, and 56% Outfitting Weight Synthesis
 * Features live interactive quantity/dimension updates, clean element names,
 * and high-fidelity PDF booklet viewing and download.
 */

let activeLightshipPdfBlobUrl = null;

function renderLightship() {
  const container = document.getElementById('tab-content-lightship');
  if (!container) return;

  const inp = (typeof appState !== 'undefined' && appState.dashboard_inputs) ? appState.dashboard_inputs : {};
  const plates = (typeof appState !== 'undefined' && appState.lightship_plates) ? appState.lightship_plates : [];
  const angles = (typeof appState !== 'undefined' && appState.lightship_angles) ? appState.lightship_angles : [];
  const ls = (typeof appState !== 'undefined' && appState.lightship_summary) ? appState.lightship_summary : {};

  container.innerHTML = `
    <!-- Top Action & Info Bar -->
    <div class="bg-white p-3 rounded-lg border border-slate-200 mb-4 flex flex-wrap justify-between items-center gap-3 shadow-xs">
      <div>
        <div class="compact-title compact-title-primary mb-0 text-slate-900 font-bold flex items-center gap-2">
          <span>LIGHTSHIP WEIGHT ESTIMATION &amp; STEEL WEIGHT BREAKDOWN</span>
          <span class="px-2 py-0.5 bg-blue-100 text-blue-800 text-[10px] font-bold rounded">Statutory 56% Synthesis</span>
        </div>
        <div class="text-xs text-slate-500">Inland Shipping Rules 2001 &amp; SRO 308 Lightweight Verification</div>
      </div>
      <div class="flex items-center gap-2">
        <button 
          onclick="resetLightshipQuantities()" 
          class="px-2.5 py-1.5 border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 rounded text-xs font-semibold transition shadow-xs cursor-pointer flex items-center gap-1"
          title="Restore standard catalog quantities for all structural parts"
        >
          <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          <span>Reset Quantities</span>
        </button>

        <button 
          onclick="openLightshipPdfModal()" 
          class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-bold transition shadow-xs flex items-center gap-1.5 cursor-pointer"
          title="View official evaluated Lightship Weight PDF deliverable with cover page & seals"
        >
          <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
          <span>View Lightship PDF</span>
        </button>

        <button 
          onclick="downloadLightshipPdf()" 
          class="px-3 py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded text-xs font-semibold transition shadow-xs flex items-center gap-1.5 cursor-pointer"
          title="Download Lightship Booklet PDF"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
          <span>Download PDF</span>
        </button>
      </div>
    </div>

    <!-- Principal Particulars Table matching Excel header -->
    <div class="bg-white p-3 rounded-lg border border-slate-200 mb-4 shadow-xs">
      <div class="compact-title mb-2 font-bold text-slate-800">PRINCIPAL PARTICULARS (LINKED DYNAMICALLY TO DASHBOARD)</div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
        <div>Name of the Vessel: <b class="text-slate-900 ml-1">${inp.vessel_name || 'Vessel'}</b></div>
        <div>Length Overall (LOA): <b class="ml-1 text-slate-900 font-mono">${inp.loa || 76.21} m</b></div>
        <div>Length BP (LBP): <b class="ml-1 text-slate-900 font-mono">${inp.lbp || 69.85} m</b></div>
        <div>Length on Waterline (LWL): <b class="ml-1 text-slate-900 font-mono">${inp.lwl || 74.28} m</b></div>
        <div>Breadth Moulded (B): <b class="ml-1 text-slate-900 font-mono">${inp.breadth || 13.41} m</b></div>
        <div>Depth Moulded (D): <b class="ml-1 text-slate-900 font-mono">${inp.depth || 5.18} m</b></div>
        <div>Loaded Draft (d): <b class="ml-1 text-slate-900 font-mono">${inp.draft || 4.0} m</b></div>
        <div>Structural Steel Density: <b class="ml-1 text-slate-900 font-mono">7,850 kg/m³</b></div>
      </div>
    </div>

    <!-- 1. Steel Plating Table -->
    <div class="bg-white p-3 rounded-lg border border-slate-200 mb-4 shadow-xs">
      <div class="flex justify-between items-center mb-2">
        <div class="compact-title mb-0 font-bold text-slate-900">1. STEEL PLATING WEIGHT ESTIMATION</div>
        <span class="text-[11px] text-slate-500 italic">Plate dimensions (L &amp; B) dynamically linked to vessel dimensions; Quantity is live-editable</span>
      </div>
      <div class="overflow-x-auto">
        <table class="compact-table w-full">
          <thead>
            <tr class="bg-slate-50 text-slate-700 text-[11px]">
              <th style="width: 35px;" class="text-center">S/N</th>
              <th>ELEMENT (Clean Plate Name)</th>
              <th style="width: 95px;" class="text-center">L (mm)</th>
              <th style="width: 95px;" class="text-center">B (mm)</th>
              <th style="width: 75px;" class="text-right">t (mm)</th>
              <th style="width: 95px;" class="text-right">Volume (m³)</th>
              <th style="width: 85px;" class="text-right">Density</th>
              <th style="width: 80px;" class="text-center">Qty (Pcs)</th>
              <th style="width: 100px;" class="text-right">Weight (KG)</th>
              <th style="width: 100px;" class="text-right">Weight (Tonne)</th>
            </tr>
          </thead>
          <tbody>
            ${plates.map(p => {
              const clean_name = p.name ? (p.name.includes('(') && !p.name.startsWith('Superstructure') ? p.name.split('(')[0].trim() : p.name) : '';
              return `
                <tr class="hover:bg-slate-50/80 transition-colors">
                  <td class="text-center text-slate-500 font-semibold font-mono text-[11px]">${p.sn}</td>
                  <td class="font-medium text-slate-800">${clean_name}</td>
                  <td class="text-center p-1 bg-slate-50/40">
                    <input 
                      type="number" 
                      min="0" 
                      step="1"
                      id="ls-plate-l-${p.sn}"
                      value="${p.l !== undefined ? p.l : (p.l_dim || 0)}" 
                      oninput="handleLiveLightshipPlateDimChange(${p.sn}, 'l', this.value)"
                      class="w-20 text-right border border-slate-300 rounded px-1.5 py-0.5 font-mono text-xs font-semibold text-slate-800 bg-white hover:border-blue-400 focus:border-blue-600 focus:outline-none transition-colors"
                      title="Edit Plate Length L (mm)"
                    />
                  </td>
                  <td class="text-center p-1 bg-slate-50/40">
                    <input 
                      type="number" 
                      min="0" 
                      step="1"
                      id="ls-plate-b-${p.sn}"
                      value="${p.b !== undefined ? p.b : (p.b_dim || 0)}" 
                      oninput="handleLiveLightshipPlateDimChange(${p.sn}, 'b', this.value)"
                      class="w-20 text-right border border-slate-300 rounded px-1.5 py-0.5 font-mono text-xs font-semibold text-slate-800 bg-white hover:border-blue-400 focus:border-blue-600 focus:outline-none transition-colors"
                      title="Edit Plate Breadth B (mm)"
                    />
                  </td>
                  <td class="text-right font-mono font-bold text-blue-700 text-[11px]">${parseFloat(p.t || 0).toFixed(1)}</td>
                  <td id="ls-plate-vol-${p.sn}" class="text-right font-mono text-[11px] text-slate-600">${parseFloat(p.vol || 0).toFixed(4)}</td>
                  <td class="text-right font-mono text-[11px] text-slate-500">${p.density || 7850}</td>
                  <td class="text-center">
                    <input 
                      type="number" 
                      min="0" 
                      step="1"
                      value="${p.qty !== undefined ? p.qty : 1}" 
                      oninput="handleLiveLightshipPlateQtyChange(${p.sn}, this.value)"
                      class="w-16 text-center border border-slate-300 rounded px-1.5 py-0.5 font-mono text-xs font-bold text-slate-800 bg-white hover:border-blue-400 focus:border-blue-600 focus:bg-blue-50/20 focus:outline-none transition-colors"
                      title="Edit quantity of ${clean_name}"
                    />
                  </td>
                  <td id="ls-plate-kg-${p.sn}" class="text-right font-mono text-[11px] text-slate-800">${parseFloat(p.weight_kg || 0).toLocaleString(undefined, {maximumFractionDigits: 1})}</td>
                  <td id="ls-plate-tonne-${p.sn}" class="text-right font-bold font-mono text-slate-900 text-[11px]">${parseFloat(p.weight_tonne || 0).toFixed(3)}</td>
                </tr>
              `;
            }).join('')}
            <tr class="bg-slate-100 font-bold border-t-2 border-slate-300">
              <td colspan="8" class="text-right uppercase text-xs text-slate-800">Total Steel Plating Weight:</td>
              <td id="ls-total-plate-kg" class="text-right font-mono font-bold text-xs">${((ls.total_plate_tonne || 0) * 1000).toLocaleString(undefined, {maximumFractionDigits: 1})} kg</td>
              <td id="ls-total-plate-tonne" class="text-right font-mono font-bold text-blue-800 text-xs">${(ls.total_plate_tonne || 0).toFixed(3)} t</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 2. Stiffeners Angles Table -->
    <div class="bg-white p-3 rounded-lg border border-slate-200 mb-4 shadow-xs">
      <div class="flex justify-between items-center mb-2">
        <div class="compact-title mb-0 font-bold text-slate-900">2. STEEL STIFFENERS &amp; STRUCTURAL ANGLES WEIGHT ESTIMATION</div>
        <span class="text-[11px] text-slate-500 italic">Web (L), Flange (B) and thickness (t) linked from Dashboard; Span length dynamically bound to attached plate</span>
      </div>
      <div class="overflow-x-auto">
        <table class="compact-table w-full">
          <thead>
            <tr class="bg-slate-50 text-slate-700 text-[11px]">
              <th style="width: 32px;" class="text-center">S/N</th>
              <th>ELEMENT (Angle / Profile)</th>
              <th style="width: 75px;" class="text-right">L (mm)</th>
              <th style="width: 75px;" class="text-right">B (mm)</th>
              <th style="width: 65px;" class="text-right">t (mm)</th>
              <th style="width: 80px;" class="text-right">Area (mm²)</th>
              <th style="width: 90px;" class="text-right">Length (mm)</th>
              <th style="width: 85px;" class="text-right">Volume (m³)</th>
              <th style="width: 75px;" class="text-right">Density</th>
              <th style="width: 70px;" class="text-center">Qty (Pcs)</th>
              <th style="width: 95px;" class="text-right">Weight (KG)</th>
              <th style="width: 95px;" class="text-right">Weight (Tonne)</th>
            </tr>
          </thead>
          <tbody>
            ${angles.map(a => {
              const clean_name = a.name ? (a.name.includes('(') && !a.name.startsWith('Superstructure') && !a.name.startsWith('BHD') && !a.name.startsWith('Deck Beam') ? a.name.split('(')[0].trim() : a.name) : '';
              return `
                <tr class="hover:bg-slate-50/80 transition-colors">
                  <td class="text-center text-slate-500 font-semibold font-mono text-[11px]">${a.sn}</td>
                  <td class="font-medium text-slate-800">
                    <span>${clean_name}</span>
                    ${a.welded_on_plate ? `<span class="ml-1 px-1.5 py-0.2 text-[9.5px] font-medium text-emerald-700 bg-emerald-50 rounded border border-emerald-200" title="Attached to ${a.welded_on_plate}">on ${a.welded_on_plate}</span>` : ''}
                  </td>
                  <td class="text-right font-mono text-slate-700 text-[11px] font-semibold" title="Linked to Dashboard Profile Web Depth">${parseFloat(a.l_dim || 0).toLocaleString()}</td>
                  <td class="text-right font-mono text-slate-700 text-[11px] font-semibold" title="Linked to Dashboard Profile Flange Width">${parseFloat(a.b_dim || 0).toLocaleString()}</td>
                  <td class="text-right font-mono font-bold text-blue-700 text-[11px]" title="Linked to Dashboard Profile Web Thickness">${parseFloat(a.t || 0).toFixed(1)}</td>
                  <td id="ls-angle-area-${a.sn}" class="text-right font-mono font-bold text-blue-700 bg-blue-50/30 text-[11px]">${typeof a.area === 'number' ? a.area.toLocaleString() : a.area}</td>
                  <td id="ls-angle-len-${a.sn}" class="text-right font-mono text-slate-800 font-medium text-[11px]" title="${a.welded_on_plate ? `Dynamically linked to ${a.welded_on_plate}` : 'Span length (mm)'}">${parseFloat(a.length || 0).toLocaleString()}</td>
                  <td id="ls-angle-vol-${a.sn}" class="text-right font-mono text-[11px] text-slate-600">${parseFloat(a.vol || 0).toFixed(4)}</td>
                  <td class="text-right font-mono text-[11px] text-slate-500">${a.density || 7850}</td>
                  <td class="text-center">
                    <input 
                      type="number" 
                      min="0" 
                      step="1"
                      value="${a.qty !== undefined ? a.qty : 1}" 
                      oninput="handleLiveLightshipAngleQtyChange(${a.sn}, this.value)"
                      class="w-14 text-center border border-slate-300 rounded px-1 py-0.5 font-mono text-xs font-bold text-slate-800 bg-white hover:border-blue-400 focus:border-blue-600 focus:bg-blue-50/20 focus:outline-none transition-colors"
                      title="Edit quantity of ${clean_name}"
                    />
                  </td>
                  <td id="ls-angle-kg-${a.sn}" class="text-right font-mono text-[11px] text-slate-800">${parseFloat(a.weight_kg || 0).toLocaleString(undefined, {maximumFractionDigits: 1})}</td>
                  <td id="ls-angle-tonne-${a.sn}" class="text-right font-bold font-mono text-slate-900 text-[11px]">${parseFloat(a.weight_tonne || 0).toFixed(3)}</td>
                </tr>
              `;
            }).join('')}
            <tr class="bg-slate-100 font-bold border-t-2 border-slate-300">
              <td colspan="10" class="text-right uppercase text-xs text-slate-800">Total Steel Stiffeners Weight:</td>
              <td id="ls-total-angle-kg" class="text-right font-mono font-bold text-xs">${((ls.total_angle_tonne || 0) * 1000).toLocaleString(undefined, {maximumFractionDigits: 1})} kg</td>
              <td id="ls-total-angle-tonne" class="text-right font-mono font-bold text-blue-800 text-xs">${(ls.total_angle_tonne || 0).toFixed(3)} t</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 3. Statutory Lightship Synthesis Table matching Excel -->
    <div class="bg-white p-3 rounded-lg border border-slate-200 mb-4 max-w-xl shadow-xs">
      <div class="compact-title mb-2 font-bold text-slate-900 flex items-center justify-between">
        <span>3. STATUTORY LIGHTSHIP SYNTHESIS &amp; TOTAL ESTIMATION</span>
        <span class="text-[11px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-bold">56% Outfitting</span>
      </div>
      <table class="compact-table w-full">
        <tbody>
          <tr class="bg-slate-50/60 font-semibold">
            <td class="font-bold text-slate-900">Total Net Structural Steel (plate &amp; angle)</td>
            <td id="ls-synth-steel" class="text-right font-mono font-bold text-slate-900 text-sm">${(ls.total_steel_tonne || 0).toFixed(3)}</td>
            <td style="width: 60px;" class="text-slate-600">tonne</td>
          </tr>
          <tr>
            <td>Allowance / Rolling Margin (20%)</td>
            <td id="ls-synth-allowance" class="text-right font-mono text-slate-700">${(ls.allowance_tonne || 0).toFixed(3)}</td>
            <td class="text-slate-500">tonne</td>
          </tr>
          <tr>
            <td>Outfit &amp; Deck Equipment (15%)</td>
            <td id="ls-synth-outfit" class="text-right font-mono text-slate-700">${(ls.outfit_tonne || 0).toFixed(3)}</td>
            <td class="text-slate-500">tonne</td>
          </tr>
          <tr>
            <td>Piping, Valves &amp; Fittings (10%)</td>
            <td id="ls-synth-piping" class="text-right font-mono text-slate-700">${(ls.piping_tonne || 0).toFixed(3)}</td>
            <td class="text-slate-500">tonne</td>
          </tr>
          <tr>
            <td>Electrical &amp; Instrumentation (3% formula / 5% base)</td>
            <td id="ls-synth-electrical" class="text-right font-mono text-slate-700">${(ls.electrical_tonne || 0).toFixed(3)}</td>
            <td class="text-slate-500">tonne</td>
          </tr>
          <tr>
            <td>Accommodation Fittings &amp; Furniture (1%)</td>
            <td id="ls-synth-accom" class="text-right font-mono text-slate-700">${(ls.accom_tonne || 0).toFixed(3)}</td>
            <td class="text-slate-500">tonne</td>
          </tr>
          <tr>
            <td>Miscellaneous Statutory Items (7%)</td>
            <td id="ls-synth-misc" class="text-right font-mono text-slate-700">${(ls.misc_tonne || 0).toFixed(3)}</td>
            <td class="text-slate-500">tonne</td>
          </tr>
          <tr class="bg-blue-50/80 border-t-2 border-blue-600 font-black text-sm">
            <td class="text-blue-950 uppercase font-black">TOTAL LIGHT SHIP WEIGHT (DISPLACEMENT) :</td>
            <td id="ls-synth-total" class="text-right font-mono text-blue-900 font-black text-base">${(ls.total_lightship_tonne || 0).toFixed(3)}</td>
            <td class="text-blue-950 font-black">Tonne</td>
          </tr>
        </tbody>
      </table>
    </div>
  `;
}

/**
 * Live Plate Dimension (L or B) Change Handler
 * Updates plate dimension and cascades immediately to all attached stiffeners' span lengths!
 */
function handleLiveLightshipPlateDimChange(sn, field, rawVal) {
  if (typeof appState === 'undefined' || !appState.lightship_plates) return;
  const plate = appState.lightship_plates.find(p => p.sn === sn);
  if (!plate) return;

  const val = Math.max(0, parseFloat(rawVal) || 0);
  plate[field] = val;

  const vol = (parseFloat(plate.l || 0) / 1000) * (parseFloat(plate.b || 0) / 1000) * (parseFloat(plate.t || 0) / 1000);
  plate.vol = vol;
  plate.weight_kg = vol * (parseFloat(plate.density) || 7850) * (plate.qty !== undefined ? plate.qty : 1);
  plate.weight_tonne = plate.weight_kg / 1000.0;

  // Direct DOM update for plate row
  const volEl = document.getElementById(`ls-plate-vol-${sn}`);
  const kgEl = document.getElementById(`ls-plate-kg-${sn}`);
  const tEl = document.getElementById(`ls-plate-tonne-${sn}`);
  if (volEl) volEl.textContent = vol.toFixed(4);
  if (kgEl) kgEl.textContent = plate.weight_kg.toLocaleString(undefined, {maximumFractionDigits: 1});
  if (tEl) tEl.textContent = plate.weight_tonne.toFixed(3);

  // Cascade to attached stiffeners in appState.lightship_angles
  if (appState.lightship_angles && appState.lightship_angles.length > 0) {
    const pName = (plate.name || '').toLowerCase();
    const pId = (plate.id || '').toLowerCase();

    appState.lightship_angles.forEach(a => {
      const aNameLower = (a.name || '').toLowerCase();
      const wName = (a.welded_on_plate || '').toLowerCase();
      const wKey = (a.welded_plate_key || '').toLowerCase();

      // Check if stiffener a is attached to this plate
      const isMatch = (wName && (pName.includes(wName) || wName.includes(pName))) ||
                      (wKey && (pId.includes(wKey) || wKey.includes(pId))) ||
                      (pName.includes('keel') && (aNameLower.includes('center keelson') || aNameLower.includes('keel'))) ||
                      (pName.includes('bottom') && (aNameLower.includes('keelson') || aNameLower.includes('floor') || aNameLower.includes('bottom'))) ||
                      ((pName.includes('side') || pName.includes('shell')) && (aNameLower.includes('frame') || aNameLower.includes('stringer') || aNameLower.includes('side'))) ||
                      (pName.includes('deck') && (aNameLower.includes('deck') || aNameLower.includes('beam'))) ||
                      ((pName.includes('bhd') || pName.includes('bulkhead')) && (aNameLower.includes('bhd') || aNameLower.includes('bulkhead')));

      if (isMatch) {
        const isTransverse = ['floor', 'deck_beam', 'deck beam', 'web_beam', 'roof_beam', 'end_beam', 'portable'].some(w => aNameLower.includes(w));
        const isVertical = ['frame', 'vertical', 'transverse', 'wall_stiffener'].some(w => aNameLower.includes(w)) && !isTransverse;

        if (isTransverse) {
          a.length = Math.round((parseFloat(plate.b || 0) / 2.0) * 10) / 10;
        } else if (isVertical) {
          a.length = parseFloat(plate.b || 0);
        } else {
          a.length = parseFloat(plate.l || 0);
        }

        // Recompute stiffener volume & weight
        const ld = parseFloat(a.l_dim) || 0;
        const bd = parseFloat(a.b_dim) || 0;
        const thk = parseFloat(a.t) || 0;
        a.area = Math.round((ld + bd) * thk * 100) / 100;
        a.vol = (a.area / 1e6) * (parseFloat(a.length) / 1000.0);
        a.weight_kg = a.vol * (parseFloat(a.density) || 7850) * (a.qty !== undefined ? a.qty : 1);
        a.weight_tonne = a.weight_kg / 1000.0;

        // Direct DOM update for stiffener row
        const aLenEl = document.getElementById(`ls-angle-len-${a.sn}`);
        const aVolEl = document.getElementById(`ls-angle-vol-${a.sn}`);
        const aKgEl = document.getElementById(`ls-angle-kg-${a.sn}`);
        const aTEl = document.getElementById(`ls-angle-tonne-${a.sn}`);
        if (aLenEl) aLenEl.textContent = parseFloat(a.length).toLocaleString();
        if (aVolEl) aVolEl.textContent = a.vol.toFixed(4);
        if (aKgEl) aKgEl.textContent = a.weight_kg.toLocaleString(undefined, {maximumFractionDigits: 1});
        if (aTEl) aTEl.textContent = a.weight_tonne.toFixed(3);
      }
    });
  }

  // Recalculate summary totals
  if (typeof recalculateAll === 'function') {
    recalculateAll(appState);
  }
  updateLightshipSummaryDOM();

  if (typeof triggerAutosaveDebounced === 'function') {
    triggerAutosaveDebounced();
  }
}

/**
 * Live Plate Quantity Change Handler
 */
function handleLiveLightshipPlateQtyChange(sn, rawVal) {
  if (typeof appState === 'undefined' || !appState.lightship_plates) return;
  const plate = appState.lightship_plates.find(p => p.sn === sn);
  if (!plate) return;

  const qty = Math.max(0, parseInt(rawVal, 10) || 0);
  plate.qty = qty;

  const vol = (parseFloat(plate.l || plate.l_dim || 0) / 1000) * (parseFloat(plate.b || plate.b_dim || 0) / 1000) * (parseFloat(plate.t || 0) / 1000);
  plate.vol = vol;
  plate.weight_kg = vol * (parseFloat(plate.density) || 7850) * qty;
  plate.weight_tonne = plate.weight_kg / 1000.0;

  // Direct DOM update for speed
  const volEl = document.getElementById(`ls-plate-vol-${sn}`);
  const kgEl = document.getElementById(`ls-plate-kg-${sn}`);
  const tEl = document.getElementById(`ls-plate-tonne-${sn}`);
  if (volEl) volEl.textContent = vol.toFixed(4);
  if (kgEl) kgEl.textContent = plate.weight_kg.toLocaleString(undefined, {maximumFractionDigits: 1});
  if (tEl) tEl.textContent = plate.weight_tonne.toFixed(3);

  // Recalculate full state
  if (typeof recalculateAll === 'function') {
    recalculateAll(appState);
  }
  updateLightshipSummaryDOM();

  if (typeof triggerAutosaveDebounced === 'function') {
    triggerAutosaveDebounced();
  }
}

/**
 * Live Angle Dimension Change Handler
 */
function handleLiveLightshipAngleDimChange(sn, field, rawVal) {
  if (typeof appState === 'undefined' || !appState.lightship_angles) return;
  const angle = appState.lightship_angles.find(a => a.sn === sn);
  if (!angle) return;

  const val = Math.max(0, parseFloat(rawVal) || 0);
  angle[field] = val;
  angle._auto_linked_prof = false; // User custom dimension

  const ld = parseFloat(angle.l_dim) || 0;
  const bd = parseFloat(angle.b_dim) || 0;
  const thk = parseFloat(angle.t) || 0;
  angle.area = Math.round((ld + bd) * thk * 100) / 100;

  const vol = (angle.area / 1e6) * (parseFloat(angle.length) / 1000.0);
  angle.vol = vol;
  angle.weight_kg = vol * (parseFloat(angle.density) || 7850) * (angle.qty || 1);
  angle.weight_tonne = angle.weight_kg / 1000.0;

  // Direct DOM update
  const areaEl = document.getElementById(`ls-angle-area-${sn}`);
  const volEl = document.getElementById(`ls-angle-vol-${sn}`);
  const kgEl = document.getElementById(`ls-angle-kg-${sn}`);
  const tEl = document.getElementById(`ls-angle-tonne-${sn}`);
  if (areaEl) areaEl.textContent = angle.area.toLocaleString();
  if (volEl) volEl.textContent = vol.toFixed(4);
  if (kgEl) kgEl.textContent = angle.weight_kg.toLocaleString(undefined, {maximumFractionDigits: 1});
  if (tEl) tEl.textContent = angle.weight_tonne.toFixed(3);

  if (typeof recalculateAll === 'function') {
    recalculateAll(appState);
  }
  updateLightshipSummaryDOM();

  if (typeof triggerAutosaveDebounced === 'function') {
    triggerAutosaveDebounced();
  }
}

/**
 * Live Angle Quantity Change Handler
 */
function handleLiveLightshipAngleQtyChange(sn, rawVal) {
  if (typeof appState === 'undefined' || !appState.lightship_angles) return;
  const angle = appState.lightship_angles.find(a => a.sn === sn);
  if (!angle) return;

  const qty = Math.max(0, parseInt(rawVal, 10) || 0);
  angle.qty = qty;

  const vol = ((parseFloat(angle.area) || 0) / 1e6) * (parseFloat(angle.length || 0) / 1000.0);
  angle.vol = vol;
  angle.weight_kg = vol * (parseFloat(angle.density) || 7850) * qty;
  angle.weight_tonne = angle.weight_kg / 1000.0;

  const volEl = document.getElementById(`ls-angle-vol-${sn}`);
  const kgEl = document.getElementById(`ls-angle-kg-${sn}`);
  const tEl = document.getElementById(`ls-angle-tonne-${sn}`);
  if (volEl) volEl.textContent = vol.toFixed(4);
  if (kgEl) kgEl.textContent = angle.weight_kg.toLocaleString(undefined, {maximumFractionDigits: 1});
  if (tEl) tEl.textContent = angle.weight_tonne.toFixed(3);

  if (typeof recalculateAll === 'function') {
    recalculateAll(appState);
  }
  updateLightshipSummaryDOM();

  if (typeof triggerAutosaveDebounced === 'function') {
    triggerAutosaveDebounced();
  }
}

/**
 * Updates Lightship Subtotals and Synthesis Table in the DOM
 */
function updateLightshipSummaryDOM() {
  if (typeof appState === 'undefined' || !appState.lightship_summary) return;
  const ls = appState.lightship_summary;

  const totPlateKgEl = document.getElementById('ls-total-plate-kg');
  const totPlateTEl = document.getElementById('ls-total-plate-tonne');
  if (totPlateKgEl) totPlateKgEl.textContent = `${((ls.total_plate_tonne || 0) * 1000).toLocaleString(undefined, {maximumFractionDigits: 1})} kg`;
  if (totPlateTEl) totPlateTEl.textContent = `${(ls.total_plate_tonne || 0).toFixed(3)} t`;

  const totAngleKgEl = document.getElementById('ls-total-angle-kg');
  const totAngleTEl = document.getElementById('ls-total-angle-tonne');
  if (totAngleKgEl) totAngleKgEl.textContent = `${((ls.total_angle_tonne || 0) * 1000).toLocaleString(undefined, {maximumFractionDigits: 1})} kg`;
  if (totAngleTEl) totAngleTEl.textContent = `${(ls.total_angle_tonne || 0).toFixed(3)} t`;

  const setSynth = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = (val || 0).toFixed(3);
  };

  setSynth('ls-synth-steel', ls.total_steel_tonne);
  setSynth('ls-synth-allowance', ls.allowance_tonne);
  setSynth('ls-synth-outfit', ls.outfit_tonne);
  setSynth('ls-synth-piping', ls.piping_tonne);
  setSynth('ls-synth-electrical', ls.electrical_tonne);
  setSynth('ls-synth-accom', ls.accom_tonne);
  setSynth('ls-synth-misc', ls.misc_tonne);
  setSynth('ls-synth-total', ls.total_lightship_tonne);
}

/**
 * Resets Lightship Quantities to standard master defaults
 */
function resetLightshipQuantities() {
  if (!confirm('Reset all Lightship plate and stiffener quantities to catalog defaults?')) return;
  if (typeof appState === 'undefined') return;

  if (appState._default_plate_qtys && appState.lightship_plates) {
    const defaultMap = {};
    appState._default_plate_qtys.forEach(d => { defaultMap[d.sn] = d.qty; });
    appState.lightship_plates.forEach(p => {
      if (defaultMap[p.sn] !== undefined) p.qty = defaultMap[p.sn];
    });
  }

  if (appState._default_angle_qtys && appState.lightship_angles) {
    const defaultMap = {};
    appState._default_angle_qtys.forEach(d => { defaultMap[d.sn] = d.qty; });
    appState.lightship_angles.forEach(a => {
      if (defaultMap[a.sn] !== undefined) a.qty = defaultMap[a.sn];
      a._auto_linked_prof = true; // Re-enable automatic profile binding
    });
  }

  if (typeof recalculateAll === 'function') {
    recalculateAll(appState);
  }
  renderLightship();

  if (typeof triggerAutosaveDebounced === 'function') {
    triggerAutosaveDebounced();
  }
}

/**
 * Opens Lightship PDF Booklet Modal
 */
async function openLightshipPdfModal() {
  let modal = document.getElementById('lightship-pdf-modal');
  
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'lightship-pdf-modal';
    modal.className = 'fixed inset-0 z-50 bg-slate-900/75 backdrop-blur-xs flex items-center justify-center p-3 md:p-6';
    modal.innerHTML = `
      <div class="bg-white rounded-lg shadow-2xl flex flex-col w-full h-full max-w-6xl max-h-[94vh] overflow-hidden border border-slate-300">
        <!-- Modal Header -->
        <div class="bg-slate-900 text-white px-4 py-2.5 flex items-center justify-between shrink-0 border-b border-slate-800">
          <div class="flex items-center gap-2.5">
            <div class="w-6 h-6 rounded bg-emerald-600 flex items-center justify-center text-white font-black text-xs">
              PDF
            </div>
            <div>
              <div class="text-xs font-bold tracking-tight text-white flex items-center gap-2">
                <span>STATUTORY LIGHTSHIP WEIGHT ESTIMATION BOOKLET</span>
                <span class="px-1.5 py-0.2 bg-emerald-700/80 text-[10px] font-mono rounded">ReportLab Vector Engine</span>
              </div>
              <div class="text-[10px] text-slate-400">Formal Cover Page with Dual Seals • Plating Table • Stiffeners Table • 56% Synthesis</div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <!-- Open in New Tab -->
            <button 
              id="btn-ls-pdf-new-tab" 
              onclick="openLightshipPdfInNewTab()" 
              class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-medium transition flex items-center gap-1 cursor-pointer"
              title="Open full PDF in separate browser tab"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
              <span>New Tab</span>
            </button>

            <!-- Download PDF Button -->
            <button 
              id="btn-ls-pdf-download" 
              onclick="downloadLightshipPdf()" 
              class="px-2.5 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-bold transition flex items-center gap-1 shadow-xs cursor-pointer"
              title="Download Lightship PDF booklet to computer"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              <span>Download PDF</span>
            </button>

            <!-- Close Modal Button -->
            <button 
              onclick="closeLightshipPdfModal()" 
              class="ml-2 w-7 h-7 flex items-center justify-center rounded text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer text-base"
              title="Close Preview (Esc)"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Modal Body: IFrame and Loading Screen -->
        <div class="relative flex-1 bg-slate-100 overflow-hidden flex flex-col">
          <!-- Loading Overlay -->
          <div id="ls-pdf-loading-overlay" class="absolute inset-0 bg-white/90 backdrop-blur-2xs flex flex-col items-center justify-center z-10 space-y-3">
            <div class="w-10 h-10 border-3 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
            <div class="text-xs font-bold text-slate-800 tracking-wide">Generating Live Lightship PDF Booklet...</div>
            <div class="text-[11px] text-slate-500">Compiling Cover Page, Plating Scantlings, Stiffeners &amp; 56% Outfitting Synthesis</div>
          </div>

          <!-- PDF IFrame -->
          <iframe id="ls-pdf-preview-iframe" class="w-full h-full border-0" title="Lightship Calculation PDF Booklet"></iframe>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        closeLightshipPdfModal();
      }
    });
  } else {
    modal.classList.remove('hidden');
  }

  const loader = document.getElementById('ls-pdf-loading-overlay');
  const iframe = document.getElementById('ls-pdf-preview-iframe');
  if (loader) loader.classList.remove('hidden');

  try {
    const payload = (typeof appState !== 'undefined') ? appState : {};
    const res = await fetch('/api/lightship/pdf/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);

    const blob = await res.blob();
    if (activeLightshipPdfBlobUrl) {
      URL.revokeObjectURL(activeLightshipPdfBlobUrl);
    }
    activeLightshipPdfBlobUrl = URL.createObjectURL(blob);
    if (iframe) iframe.src = activeLightshipPdfBlobUrl;
  } catch (err) {
    console.error('Error generating Lightship PDF:', err);
    alert('Failed to generate Lightship PDF: ' + err.message);
    if (modal) modal.classList.add('hidden');
  } finally {
    if (loader) loader.classList.add('hidden');
  }
}

function closeLightshipPdfModal() {
  const modal = document.getElementById('lightship-pdf-modal');
  if (modal) modal.classList.add('hidden');
  if (activeLightshipPdfBlobUrl) {
    URL.revokeObjectURL(activeLightshipPdfBlobUrl);
    activeLightshipPdfBlobUrl = null;
  }
}

function openLightshipPdfInNewTab() {
  if (activeLightshipPdfBlobUrl) {
    window.open(activeLightshipPdfBlobUrl, '_blank');
  } else {
    window.open('/api/lightship/pdf/preview', '_blank');
  }
}

function downloadLightshipPdf() {
  const vName = (typeof appState !== 'undefined' && appState.dashboard_inputs && appState.dashboard_inputs.vessel_name) 
    ? appState.dashboard_inputs.vessel_name.replace(/\s+/g, '_') 
    : 'Vessel';
  const filename = `${vName}_Lightship_Booklet.pdf`;

  if (activeLightshipPdfBlobUrl) {
    const a = document.createElement('a');
    a.href = activeLightshipPdfBlobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } else {
    window.location.href = '/api/lightship/pdf/export';
  }
}

// Global window bindings
window.lightshipView = { render: renderLightship };
window.handleLiveLightshipPlateQtyChange = handleLiveLightshipPlateQtyChange;
window.handleLiveLightshipPlateDimChange = handleLiveLightshipPlateDimChange;
window.handleLiveLightshipAngleDimChange = handleLiveLightshipAngleDimChange;
window.handleLiveLightshipAngleQtyChange = handleLiveLightshipAngleQtyChange;
window.resetLightshipQuantities = resetLightshipQuantities;
window.openLightshipPdfModal = openLightshipPdfModal;
window.closeLightshipPdfModal = closeLightshipPdfModal;
window.openLightshipPdfInNewTab = openLightshipPdfInNewTab;
window.downloadLightshipPdf = downloadLightshipPdf;
