/**
 * DetailCalcView - Renders Technical Section Modulus Calculation Booklet (Sheets 01 to N)
 * Includes interactive T, L, FB profile toolbar and vector cross-section diagram
 */

const STIFFENER_APP_FORM_MAP_JS = {
  'stiff_centre_keelson': { item_no: '31', rule: 'Rule 23', title: 'Kilsons & Webs (Centre girder)', page: 11, table_ref: 'Table 16' },
  'stiff_side_keelson': { item_no: '31', rule: 'Rule 23', title: 'Kilsons & Webs (Side girder)', page: 11, table_ref: 'Table 15' },
  'stiff_floor_single': { item_no: '28', rule: 'Rule 22', title: 'Bottom construction (Floor plate)', page: 11, table_ref: 'Table 13' },
  'stiff_bottom_transverse_barge': { item_no: '28', rule: 'Rule 22', title: 'Bottom construction (Floor plate)', page: 11, table_ref: 'Table 13' },
  'stiff_centre_girder': { item_no: '31', rule: 'Rule 23', title: 'Double bottom centre girder', page: 11, table_ref: 'Table 16' },
  'stiff_side_girder': { item_no: '31', rule: 'Rule 23', title: 'Double bottom side girder', page: 11, table_ref: 'Table 15' },
  'stiff_solid_floor': { item_no: '105', rule: 'Rule 22', title: 'Double bottom solid floor', page: 24, table_ref: 'Table 13' },
  'stiff_open_bracket_floor': { item_no: '105', rule: 'Rule 22', title: 'Double bottom bracket floor', page: 24, table_ref: 'Table 13' },
  'stiff_floor_girder_vertical': { item_no: '105', rule: 'Rule 22', title: 'Double bottom vertical stiffener', page: 24, table_ref: 'Table 52' },
  'stiff_bottom_longitudinal': { item_no: '105', rule: 'Rule 25', title: 'Double bottom longitudinals', page: 24, table_ref: 'Table 66' },
  'stiff_inner_bottom_longitudinal': { item_no: '105', rule: 'Rule 25', title: 'Inner bottom longitudinals', page: 24, table_ref: 'Table 66' },
  'stiff_hopper_longitudinal': { item_no: '105', rule: 'Rule 25', title: 'Hopper tank longitudinals', page: 24, table_ref: 'Table 66' },
  'stiff_main_frame': { item_no: '33', rule: 'Rule 25', title: 'Side frame (Section modulus)', page: 11, table_ref: 'Table 17' },
  'stiff_side_longitudinal': { item_no: '33', rule: 'Rule 25', title: 'Side shell longitudinal frame', page: 11, table_ref: 'Table 66' },
  'stiff_side_longitudinal_barge': { item_no: '33', rule: 'Rule 25', title: 'Side shell longitudinal frame', page: 11, table_ref: 'Table 66' },
  'stiff_inner_side_longitudinal': { item_no: '33', rule: 'Rule 25', title: 'Inner side longitudinal frame', page: 11, table_ref: 'Table 66' },
  'stiff_web_frame': { item_no: '35', rule: 'Rule 26', title: 'Web frame (Transverse framing)', page: 12, table_ref: 'Table 19' },
  'stiff_side_stringer': { item_no: '36', rule: 'Rule 27', title: 'Side stringer (between web framing)', page: 12, table_ref: 'Table 19' },
  'stiff_side_transverse': { item_no: '35', rule: 'Rule 26', title: 'Side transverse in wing tank', page: 12, table_ref: 'Table 19' },
  'stiff_horizontal_stringer': { item_no: '36', rule: 'Rule 27', title: 'Horizontal stringer in wing tank', page: 12, table_ref: 'Table 19' },
  'stiff_deck_beam': { item_no: '37', rule: 'Rule 28', title: 'Deck beam (Section modulus)', page: 12, table_ref: 'Table 20' },
  'stiff_deck_longitudinal': { item_no: '37', rule: 'Rule 28', title: 'Strength deck longitudinal beam', page: 12, table_ref: 'Table 36' },
  'stiff_deck_web_beam': { item_no: '38', rule: 'Rule 29', title: 'Deck web beam (Section modulus)', page: 12, table_ref: 'Table 29' },
  'stiff_deck_girder': { item_no: '39', rule: 'Rule 30', title: 'Deck girder (Section modulus)', page: 12, table_ref: 'Table 21' },
  'stiff_deck_transverse': { item_no: '38', rule: 'Rule 29', title: 'Deck transverse web beam', page: 12, table_ref: 'Table 21' },
  'stiff_cross_deck_beam': { item_no: '37', rule: 'Rule 28', title: 'Cross deck beam', page: 12, table_ref: 'Table 20' },
  'stiff_catamaran_cross_beam': { item_no: '37', rule: 'Rule 28', title: 'Cross beam joining hulls', page: 12, table_ref: 'Table 20' },
  'stiff_catamaran_cross_girder': { item_no: '39', rule: 'Rule 30', title: 'Cross deck girder', page: 12, table_ref: 'Table 21' },
  'stiff_catamaran_wet_deck': { item_no: '76', rule: 'Rule 65', title: 'Wet deck stiffener', page: 18, table_ref: 'Table 36' },
  'stiff_roof_beam': { item_no: '74', rule: 'Rule 63', title: 'Superstructure roof beam', page: 17, table_ref: 'Table 36' },
  'stiff_roof_girder_side': { item_no: '74', rule: 'Rule 63', title: 'Superstructure side roof girder', page: 17, table_ref: 'Table 37' },
  'stiff_roof_girder_centre': { item_no: '74', rule: 'Rule 63', title: 'Superstructure centre roof girder', page: 17, table_ref: 'Table 37' },
  'stiff_superstructure_wall': { item_no: '74', rule: 'Rule 63', title: 'Superstructure wall stiffener', page: 17, table_ref: 'Table 35' },
  'stiff_superstructure_frame': { item_no: '74', rule: 'Rule 63', title: 'Superstructure main frame', page: 17, table_ref: 'Table 35' },
  'stiff_bhd_transverse': { item_no: '44', rule: 'Rule 34', title: 'Watertight bulkhead stiffeners', page: 13, table_ref: 'Table 26' },
  'stiff_tank_bhd_stringer': { item_no: '48', rule: 'Rule 37', title: 'Tank bulkhead horizontal stringer', page: 13, table_ref: 'Table 28' },
  'stiff_tank_bhd_web': { item_no: '48', rule: 'Rule 37', title: 'Tank bulkhead vertical web', page: 13, table_ref: 'Table 28' },
  'stiff_hatch_end_beam': { item_no: '60', rule: 'Rule 50', title: 'Hatchway transverse beam', page: 15, table_ref: 'Table 33' },
  'stiff_hatch_side_girder': { item_no: '62', rule: 'Rule 51', title: 'Hatchway side girder beam', page: 15, table_ref: 'Table 21' },
  'stiff_portable_hatch_beam': { item_no: '60', rule: 'Rule 50', title: 'Portable removable hatch beam', page: 15, table_ref: 'Table 32' },
  'stiff_hatch_cover': { item_no: '64', rule: 'Rule 52', title: 'Steel hatch cover stiffeners', page: 16, table_ref: 'Table 34' }
};

function getDetailCalcAppFormInfo(memberId, name, tableRef) {
  if (memberId && STIFFENER_APP_FORM_MAP_JS[memberId]) {
    return Object.assign({}, STIFFENER_APP_FORM_MAP_JS[memberId], tableRef ? { table_ref: tableRef } : {});
  }
  const n = (name || '').toLowerCase();
  if (n.includes('keelson') || n.includes('girder')) return { item_no: '31', rule: 'Rule 23', title: name || 'Kilsons & Girders', page: 11, table_ref: tableRef || 'Table 16' };
  if (n.includes('floor')) return { item_no: '28', rule: 'Rule 22', title: name || 'Bottom Floor Plate', page: 11, table_ref: tableRef || 'Table 13' };
  if (n.includes('frame') && !n.includes('web') && !n.includes('super')) return { item_no: '33', rule: 'Rule 25', title: name || 'Side Frame', page: 11, table_ref: tableRef || 'Table 17' };
  if (n.includes('web frame')) return { item_no: '35', rule: 'Rule 26', title: name || 'Web Frame', page: 12, table_ref: tableRef || 'Table 19' };
  if (n.includes('stringer')) return { item_no: '36', rule: 'Rule 27', title: name || 'Side Stringer', page: 12, table_ref: tableRef || 'Table 19' };
  if (n.includes('deck beam') || (n.includes('beam') && !n.includes('hatch') && !n.includes('roof'))) return { item_no: '37', rule: 'Rule 28', title: name || 'Deck Beam', page: 12, table_ref: tableRef || 'Table 20' };
  if (n.includes('deck girder')) return { item_no: '39', rule: 'Rule 30', title: name || 'Deck Girder', page: 12, table_ref: tableRef || 'Table 21' };
  if (n.includes('roof') || n.includes('superstructure')) return { item_no: '74', rule: 'Rule 63', title: name || 'Superstructure Stiffener', page: 17, table_ref: tableRef || 'Table 35' };
  if (n.includes('bulkhead') || n.includes('bhd')) return { item_no: '44', rule: 'Rule 34', title: name || 'Bulkhead Stiffener', page: 13, table_ref: tableRef || 'Table 26' };
  if (n.includes('hatch') && n.includes('cover')) return { item_no: '64', rule: 'Rule 52', title: name || 'Steel Hatch Cover', page: 16, table_ref: tableRef || 'Table 34' };
  if (n.includes('hatch')) return { item_no: '60', rule: 'Rule 50', title: name || 'Hatchway Beam', page: 15, table_ref: tableRef || 'Table 32' };
  return { item_no: '—', rule: 'Statutory Rule', title: name || 'Structural Member', page: '—', table_ref: tableRef || 'Statutory Table' };
}

function formatCalcDim(val) {
  if (val === undefined || val === null || val === '') return '0';
  const num = parseFloat(val);
  if (isNaN(num)) return '0';
  return (num % 1 === 0) ? num.toFixed(0) : num.toFixed(1);
}

function renderSheet2Calc() {
  const container = document.getElementById('tab-content-sheet2-calc');
  if (!container) return;

  const results = appState.sheet2_results || [];
  if (currentSheet2Index >= results.length) currentSheet2Index = 0;
  const activeItem = results[currentSheet2Index] || results[0];

  if (!activeItem) {
    container.innerHTML = '<div class="p-8 text-center text-xs text-slate-500 bg-white border border-slate-200">No active stiffener calculation sheets available for this hull type.</div>';
    return;
  }

  const ptype = (activeItem.profile_type || (activeItem.flange_width > 0 ? 'L' : 'FB')).toUpperCase();
  const isFB = (ptype === 'FB' || activeItem.flange_width <= 0);

  const profStr = isFB 
    ? `FB ${formatCalcDim(activeItem.web_height)}x${formatCalcDim(activeItem.web_thk)} mm` 
    : `${ptype} ${formatCalcDim(activeItem.web_height)}x${formatCalcDim(activeItem.flange_width)}x${formatCalcDim(activeItem.flange_thk || activeItem.web_thk)} mm`;

  const deriv = activeItem.derivation || {};
  const hasComponents = deriv.components && Array.isArray(deriv.components) && deriv.components.length > 0;
  const appInfo = getDetailCalcAppFormInfo(activeItem.member_id, activeItem.name, activeItem.table_ref);

  container.innerHTML = `
    <!-- Selector Bar -->
    <div class="bg-white p-3 rounded border border-slate-200 mb-4 flex flex-wrap items-center justify-between gap-3 shadow-xs">
      <div class="flex items-center gap-2">
        <div class="compact-title compact-title-primary mb-0">DETAIL CALCULATIONS: STATUTORY SCANTLINGS BOOKLET</div>
        <span class="text-xs text-slate-500">Sheet <b>${activeItem.id}</b> of ${results.length}</span>
      </div>
      <div class="flex items-center gap-2">
        <select class="compact-select text-xs max-w-md font-medium" onchange="currentSheet2Index = parseInt(this.value); renderSheet2Calc();">
          ${results.map((r, idx) => `
            <option value="${idx}" ${idx === currentSheet2Index ? 'selected' : ''}>Sheet ${r.id < 10 ? '0' + r.id : r.id} : ${r.name}</option>
          `).join('')}
        </select>
      </div>
    </div>

    <!-- Interactive Profile Configuration Toolbar for Active Stiffener -->
    ${activeItem.type === 'section_modulus' ? `
      <div class="bg-blue-50/80 border border-blue-200 p-3 rounded mb-4 flex flex-wrap items-center justify-between gap-3 text-xs shadow-xs">
        <div class="flex items-center gap-2">
          <span class="font-bold text-blue-900 uppercase tracking-wide">Cross-Section Profile:</span>
          <div class="inline-flex rounded border border-blue-300 p-0.5 bg-white shadow-2xs" role="group">
            <button 
              type="button" 
              onclick="handleDetailCalcProfileTypeChange('${activeItem.member_id}', 'L')" 
              class="px-3 py-1 font-bold rounded ${ptype === 'L' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-700 hover:bg-slate-100'} transition cursor-pointer"
            >
              L (Angle)
            </button>
            <button 
              type="button" 
              onclick="handleDetailCalcProfileTypeChange('${activeItem.member_id}', 'T')" 
              class="px-3 py-1 font-bold rounded ${ptype === 'T' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-700 hover:bg-slate-100'} transition cursor-pointer"
            >
              T (T-Bar)
            </button>
            <button 
              type="button" 
              onclick="handleDetailCalcProfileTypeChange('${activeItem.member_id}', 'FB')" 
              class="px-3 py-1 font-bold rounded ${ptype === 'FB' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-700 hover:bg-slate-100'} transition cursor-pointer"
            >
              FB (Flat Bar)
            </button>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5">
            <span class="text-slate-700 font-medium">Web (hw×tw):</span>
            <input 
              type="text" 
              inputmode="decimal" 
              class="compact-input w-16 text-center font-mono font-bold p-1 border rounded bg-white text-xs border-slate-300 focus:border-blue-600" 
              value="${formatCalcDim(activeItem.web_height)}" 
              onfocus="this.select()" 
              oninput="handleDetailCalcDimChange('${activeItem.member_id}', 'web_depth', this.value)" 
              title="Web Depth hw (mm)"
            />
            <span class="text-slate-400 font-bold">×</span>
            <input 
              type="text" 
              inputmode="decimal" 
              class="compact-input w-14 text-center font-mono font-bold p-1 border rounded bg-white text-xs border-slate-300 focus:border-blue-600" 
              value="${parseFloat(activeItem.web_thk).toFixed(1)}" 
              onfocus="this.select()" 
              oninput="handleDetailCalcDimChange('${activeItem.member_id}', 'web_thk', this.value)" 
              title="Web Thickness tw (mm)"
            />
          </div>

          ${!isFB ? `
            <div class="flex items-center gap-1.5">
              <span class="text-slate-700 font-medium">Flange (bf×tf):</span>
              <input 
                type="text" 
                inputmode="decimal" 
                class="compact-input w-16 text-center font-mono font-bold p-1 border rounded bg-white text-xs border-slate-300 focus:border-blue-600" 
                value="${formatCalcDim(activeItem.flange_width)}" 
                onfocus="this.select()" 
                oninput="handleDetailCalcDimChange('${activeItem.member_id}', 'flange_width', this.value)" 
                title="Flange Width bf (mm)"
              />
              <span class="text-slate-400 font-bold">×</span>
              <input 
                type="text" 
                inputmode="decimal" 
                class="compact-input w-14 text-center font-mono font-bold p-1 border rounded bg-white text-xs border-slate-300 focus:border-blue-600" 
                value="${parseFloat(activeItem.flange_thk).toFixed(1)}" 
                onfocus="this.select()" 
                oninput="handleDetailCalcDimChange('${activeItem.member_id}', 'flange_thk', this.value)" 
                title="Flange Thickness tf (mm)"
              />
            </div>
          ` : `
            <span class="text-slate-500 font-mono italic px-2 py-0.5 bg-white border border-slate-200 rounded">No Flange (Flat Bar)</span>
          `}
        </div>
      </div>
    ` : ''}

    <!-- Active Stiffener Detailed Calculation Card -->
    <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
      
      <!-- Left Box: Exact tabular card matching statutory calculation booklet -->
      <div class="md:col-span-7 bg-white p-6 border border-slate-300 font-sans text-[13px] leading-relaxed text-slate-900 shadow-xs">
        
        <!-- Header Box: Light gray background with border -->
        <div class="bg-slate-100 border border-slate-900 px-3.5 py-2 text-[13px] font-normal text-slate-900 mb-3 tracking-wide flex items-center justify-between">
          <span>Sheet ${activeItem.id < 10 ? '0' + activeItem.id : activeItem.id} : ${activeItem.name} : &nbsp;<b>${profStr}</b></span>
          <span class="text-xs px-2.5 py-0.5 rounded font-mono font-bold bg-slate-200 text-slate-800 border border-slate-400">
            APPLICATION FORM: ITEM ${appInfo.item_no} (${appInfo.rule})
          </span>
        </div>

        <!-- Attached Plating & Welded Joint Banner -->
        <div class="text-xs text-blue-900 bg-blue-50 border border-blue-200 px-3 py-1.5 rounded mb-4 font-medium flex items-center justify-between">
          <span>Attached Strake: <b>${activeItem.welded_on_plate || 'Shell Plating'}</b></span>
          <span>Welded Plate Thickness tp = <b>${activeItem.plate_thk} mm</b></span>
          <span>Effective Flange bp = <b>${activeItem.plate_width} mm</b></span>
        </div>

        ${activeItem.type === 'section_modulus' ? `
          <!-- Section 1: Dimensions and Areas -->
          <div class="space-y-1.5 mb-4 text-[13px]">
            <!-- Plate Dimensions & Area -->
            <div class="grid grid-cols-12 gap-1 items-center">
              <div class="col-span-3 text-slate-900">Plate Width:</div>
              <div class="col-span-2 text-right font-mono">${parseFloat(activeItem.plate_width).toFixed(2)}</div>
              <div class="col-span-1 pl-1 text-slate-900">mm</div>
              <div class="col-span-3 pl-3 text-slate-900">Plate Area:</div>
              <div class="col-span-2 text-right font-mono">${parseFloat(activeItem.ap).toFixed(2)}</div>
              <div class="col-span-1 pl-1 text-slate-900">mm<sup>2</sup></div>
            </div>
            <div class="grid grid-cols-12 gap-1 items-center">
              <div class="col-span-3 text-slate-900">Plate Thickness:</div>
              <div class="col-span-2 text-right font-mono">${parseFloat(activeItem.plate_thk).toFixed(2)}</div>
              <div class="col-span-1 pl-1 text-slate-900">mm</div>
              <div class="col-span-6"></div>
            </div>

            <!-- Web Dimensions & Area -->
            <div class="grid grid-cols-12 gap-1 items-center pt-2">
              <div class="col-span-3 text-slate-900">Web Height:</div>
              <div class="col-span-2 text-right font-mono">${formatCalcDim(activeItem.web_height)}</div>
              <div class="col-span-1 pl-1 text-slate-900">mm</div>
              <div class="col-span-3 pl-3 text-slate-900">Web Plate Area:</div>
              <div class="col-span-2 text-right font-mono">${parseFloat(activeItem.aw).toFixed(2)}</div>
              <div class="col-span-1 pl-1 text-slate-900">mm<sup>2</sup></div>
            </div>
            <div class="grid grid-cols-12 gap-1 items-center">
              <div class="col-span-3 text-slate-900">Web Thickness:</div>
              <div class="col-span-2 text-right font-mono">${parseFloat(activeItem.web_thk).toFixed(1)}</div>
              <div class="col-span-1 pl-1 text-slate-900">mm</div>
              <div class="col-span-6"></div>
            </div>

            <!-- Flange Dimensions & Area -->
            <div class="grid grid-cols-12 gap-1 items-center pt-2 ${isFB ? 'text-slate-400' : ''}">
              <div class="col-span-3 text-slate-900">Flange Width:</div>
              <div class="col-span-2 text-right font-mono">${isFB ? '—' : formatCalcDim(activeItem.flange_width)}</div>
              <div class="col-span-1 pl-1 text-slate-900">mm</div>
              <div class="col-span-3 pl-3 text-slate-900">Flange Plate Area :</div>
              <div class="col-span-2 text-right font-mono">${isFB ? '0.00' : parseFloat(activeItem.af).toFixed(2)}</div>
              <div class="col-span-1 pl-1 text-slate-900">mm<sup>2</sup></div>
            </div>
            <div class="grid grid-cols-12 gap-1 items-center ${isFB ? 'text-slate-400' : ''}">
              <div class="col-span-3 text-slate-900">Flange Thickness:</div>
              <div class="col-span-2 text-right font-mono">${isFB ? '—' : parseFloat(activeItem.flange_thk).toFixed(1)}</div>
              <div class="col-span-1 pl-1 text-slate-900">mm</div>
              <div class="col-span-6 pl-3 italic text-xs text-slate-500">${isFB ? '(Flat Bar — No Flange)' : ''}</div>
            </div>
          </div>

          <!-- Section 2: Distance of Neutral Axis -->
          <div class="my-4 text-[13px] leading-snug">
            <div class="text-slate-900">Distance of Neutral Axis from outer surface of plate : Moment / Area</div>
            <div class="font-mono text-slate-900 mt-1">= &nbsp;<b>${parseFloat(activeItem.yna).toFixed(3)}</b> &nbsp;mm</div>
          </div>

          <!-- Section 3: Moments of Inertia -->
          <div class="my-4 text-[13px] space-y-1 font-mono">
            <div class="flex items-center">
              <span class="w-16 font-sans text-slate-900">So, &nbsp;Ip:</span>
              <span class="w-32 text-right font-mono">${parseFloat(activeItem.ip).toFixed(3)}</span>
              <span class="pl-2 font-sans text-slate-900">mm<sup>4</sup></span>
            </div>
            <div class="flex items-center">
              <span class="w-16 font-sans text-slate-900">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Iw:</span>
              <span class="w-32 text-right font-mono">${parseFloat(activeItem.iw).toFixed(3)}</span>
              <span class="pl-2 font-sans text-slate-900">mm<sup>4</sup></span>
            </div>
            <div class="flex items-center ${isFB ? 'text-slate-400' : ''}">
              <span class="w-16 font-sans text-slate-900">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;If:</span>
              <span class="w-32 text-right font-mono">${parseFloat(activeItem.if || 0).toFixed(3)}</span>
              <span class="pl-2 font-sans text-slate-900">mm<sup>4</sup></span>
              ${isFB ? '<span class="pl-3 italic text-xs text-slate-400 font-sans">(Flat Bar: If = 0)</span>' : ''}
            </div>
            <div class="flex items-center font-bold text-slate-900">
              <span class="w-16 font-sans text-slate-900">&nbsp;&nbsp;&nbsp;&nbsp;INA:</span>
              <span class="w-32 text-right font-mono">${parseFloat(activeItem.ina).toFixed(3)}</span>
              <span class="pl-2 font-sans text-slate-900">mm<sup>4</sup></span>
            </div>
          </div>

          <!-- Section 4: Section Modulus -->
          <div class="mt-4 pt-3 text-[13px] border-t border-slate-200">
            <div class="flex items-center">
              <span class="w-48 text-slate-900 font-semibold">Section Modulus, Z :</span>
              <span class="w-32 text-right font-mono">${parseFloat(activeItem.z_mm3).toFixed(3)}</span>
              <span class="pl-2 text-slate-900">mm<sup>3</sup></span>
            </div>
            <div class="flex items-center mt-1">
              <span class="w-48 text-right pr-2 font-mono">=</span>
              <span class="w-32 text-right font-mono font-bold text-blue-900 text-sm">${parseFloat(activeItem.z_cm3).toFixed(4)}</span>
              <span class="pl-2 text-slate-900 font-bold">cm<sup>3</sup></span>
            </div>
            <div class="flex items-center mt-2 text-xs text-slate-600">
              <span class="w-48">Rule Required Z:</span>
              <span class="w-32 text-right font-mono">${parseFloat(activeItem.rreq || 0).toFixed(2)}</span>
              <span class="pl-2">cm<sup>3</sup> &nbsp;(Margin: <b class="${activeItem.margin >= 0 ? 'text-emerald-700' : 'text-rose-700'}">${activeItem.margin >= 0 ? '+' : ''}${parseFloat(activeItem.margin || 0).toFixed(2)} cm<sup>3</sup></b>)</span>
            </div>
          </div>

          <!-- Section 5: Statutory Rule Derivation & Criteria Breakdown -->
          <div class="mt-4 pt-3 border-t border-slate-200 text-xs">
            <div class="flex items-center justify-between mb-1.5">
              <span class="font-bold text-slate-900 uppercase tracking-wide">Application Form Reference:</span>
              <span class="font-mono text-xs text-blue-900 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 font-semibold">
                Item ${appInfo.item_no}: ${appInfo.title} (Page ${appInfo.page} of 24)
              </span>
            </div>
            <div class="flex items-center justify-between mb-1.5">
              <span class="font-bold text-slate-900 uppercase tracking-wide">Statutory Rule Reference:</span>
              <span class="font-mono text-xs text-slate-700 bg-slate-100 px-2 py-0.5 rounded border border-slate-300 font-semibold">${appInfo.rule} (${activeItem.table_ref || deriv.table_no || 'Statutory Schedule'})</span>
            </div>
            ${deriv.formula_desc ? `<div class="text-slate-700 mb-1.5 font-medium">${deriv.formula_desc}</div>` : ''}
            ${deriv.derivation_text ? `<div class="font-mono bg-slate-50 border border-slate-200 p-2 rounded text-slate-800 leading-relaxed mb-2">${deriv.derivation_text}</div>` : ''}
            ${hasComponents ? `
              <div class="mt-2 space-y-1">
                <div class="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Statutory Member Components:</div>
                ${deriv.components.map(c => `
                  <div class="flex items-center justify-between text-xs py-0.5 border-b border-slate-100 last:border-b-0">
                    <span class="text-slate-800 font-medium">${c.name} (${c.param}):</span>
                    <span class="font-mono text-slate-700">Req: <b>${c.rreq} ${c.unit}</b> | Prov: <b>${c.prov} ${c.unit}</b> 
                      <span class="${c.status === 'COMPLIANT' ? 'text-emerald-700' : 'text-rose-700'} font-bold">(${c.status === 'COMPLIANT' ? '+' : ''}${c.margin} ${c.unit})</span>
                    </span>
                  </div>
                `).join('')}
              </div>
            ` : ''}
          </div>
        ` : `
          <div class="space-y-2 py-3 text-[13px]">
            <div>Formula: <b>${activeItem.rule_formula || activeItem.rule}</b></div>
            <div>Limit: <b>${activeItem.limit || activeItem.min_limit}</b></div>
            <div>Provided: <b>${activeItem.actual_spacing || activeItem.actual_pos || activeItem.area_cm2}</b></div>
            <div class="font-bold text-emerald-700">Status: ${activeItem.status}</div>
          </div>
        `}
      </div>

      <!-- Right Box: Technical Vector Schematic Box matching Image 2 -->
      <div class="md:col-span-5 flex flex-col justify-between">
        ${activeItem.type === 'section_modulus' 
          ? renderStiffenerSvg(activeItem.plate_width, activeItem.plate_thk, activeItem.web_height, activeItem.web_thk, activeItem.flange_width, activeItem.flange_thk, activeItem.yna, activeItem.name, activeItem.z_cm3, ptype, 360, 280)
          : '<div class="p-8 text-center text-xs text-slate-500 bg-white border border-slate-800 h-full flex items-center justify-center">Rule Check Schematic Not Required</div>'
        }
      </div>

    </div>
  `;
}

function handleDetailCalcProfileTypeChange(memberId, newType) {
  if (!appState || !memberId) return;
  appState.stiffener_custom_dims = appState.stiffener_custom_dims || {};
  appState.stiffener_custom_dims[memberId] = appState.stiffener_custom_dims[memberId] || {};
  
  appState.stiffener_custom_dims[memberId].profile_type = newType;
  delete appState.stiffener_custom_dims[memberId].custom_z;

  if (newType === 'FB') {
    appState.stiffener_custom_dims[memberId].flange_width = 0;
    appState.stiffener_custom_dims[memberId].flange_thk = 0;
  } else {
    // If switching from FB to L or T, restore flange if 0
    const curBf = appState.stiffener_custom_dims[memberId].flange_width;
    const curTf = appState.stiffener_custom_dims[memberId].flange_thk;
    if (!curBf || curBf <= 0) {
      appState.stiffener_custom_dims[memberId].flange_width = 100;
    }
    if (!curTf || curTf <= 0) {
      appState.stiffener_custom_dims[memberId].flange_thk = 10;
    }
  }

  recalculateAll(appState);
  updateTopStats();
  renderSheet2Calc();
  if (typeof updateLiveDashboardDisplays === 'function') {
    updateLiveDashboardDisplays();
  }
  triggerAutosaveDebounced();
}

function handleDetailCalcDimChange(memberId, field, rawVal) {
  if (!appState || !memberId) return;
  appState.stiffener_custom_dims = appState.stiffener_custom_dims || {};
  appState.stiffener_custom_dims[memberId] = appState.stiffener_custom_dims[memberId] || {};
  
  const s = String(rawVal).trim().replace(',', '.');
  const num = (s === '' || s === '-' || s === '.') ? '' : (parseFloat(s) || 0);

  appState.stiffener_custom_dims[memberId][field] = num;
  delete appState.stiffener_custom_dims[memberId].custom_z;

  recalculateAll(appState);
  updateTopStats();
  renderSheet2Calc();
  if (typeof updateLiveDashboardDisplays === 'function') {
    updateLiveDashboardDisplays();
  }
  triggerAutosaveDebounced();
}

window.detailCalcView = { render: renderSheet2Calc };
