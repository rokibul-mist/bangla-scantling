with open('app/static/js/views/StrengthView.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('\r\n', '\n')

# 1. Remove rina const
old_rina_line = "    const rina = report.rina_classification || {};\n"
if old_rina_line in content:
    content = content.replace(old_rina_line, "")
    print("Removed const rina line")

# 2. Replace RINA card with ISO 1976 / Rule 209 matrix card
old_card = '''        <!-- RINA Classification Rules Card (Section 103) -->
        <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div class="font-bold text-slate-900 text-sm mb-2 flex items-center justify-between border-b border-slate-100 pb-2">
            <span>RINA RULES CLASSIFICATION BENDING MOMENTS (PART B, CH 1 &amp; CH 8)</span>
            <span class="text-[11px] text-blue-700 font-semibold">Naval Arch Standard</span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs text-slate-700">
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Wave Parameter (C)</div>
              <div class="font-bold text-slate-900 mt-0.5">${(rina.wave_parameter_c || 6.486).toFixed(4)}</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Froude Number (F)</div>
              <div class="font-bold text-slate-900 mt-0.5">${(rina.froude_number_f || 0.275).toFixed(4)}</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Wave Hogging (M_wv,h)</div>
              <div class="font-bold text-slate-900 mt-0.5">${(rina.vertical_wave_hogging_knm || 0).toLocaleString('en-US', {maximumFractionDigits: 1})} kN·m</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Wave Sagging (M_wv,s)</div>
              <div class="font-bold text-slate-900 mt-0.5">${(rina.vertical_wave_sagging_knm || 0).toLocaleString('en-US', {maximumFractionDigits: 1})} kN·m</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Still Water Hog (M_swm,h)</div>
              <div class="font-bold text-slate-900 mt-0.5">${(rina.still_water_hogging_knm || 0).toLocaleString('en-US', {maximumFractionDigits: 1})} kN·m</div>
            </div>
            <div class="bg-emerald-50 p-2.5 rounded border border-emerald-200">
              <div class="text-emerald-700 text-[10px] font-bold">RINA Required Z_R</div>
              <div class="font-bold text-emerald-900 mt-0.5">${(rina.required_section_modulus_m3 || 0).toFixed(4)} m³ (${(rina.required_section_modulus_cm3 || 0).toLocaleString('en-US', {maximumFractionDigits: 0})} cm³)</div>
            </div>
          </div>
        </div>'''

new_card = '''        <!-- Statutory ISO 1976 & Rule 209 Longitudinal Criteria Card (Section 103) -->
        <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
          <div class="font-bold text-slate-900 text-sm mb-2 flex items-center justify-between border-b border-slate-100 pb-2">
            <span>STATUTORY SECTION MODULUS &amp; MOMENTS MATRIX (RULE 209 &amp; ISO 1976)</span>
            <span class="text-[11px] text-emerald-700 font-bold">ISO 1976 Standard</span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs text-slate-700">
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Wave Coeff (Cw)</div>
              <div class="font-bold text-slate-900 mt-0.5">${factorCw.toFixed(4)}</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Route Factor (kt)</div>
              <div class="font-bold text-slate-900 mt-0.5">${(report.factor_kt || 1.40).toFixed(2)}</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Shear Force (Q_design)</div>
              <div class="font-bold text-slate-900 mt-0.5">${(moms.shear_force_design_kn || 0).toLocaleString('en-US', {maximumFractionDigits: 1})} kN</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Stress Req Z1 (130 N/mm²)</div>
              <div class="font-bold text-slate-900 mt-0.5">${z1StressCm3.toLocaleString('en-US', {maximumFractionDigits: 0})} cm³</div>
            </div>
            <div class="bg-slate-50 p-2.5 rounded border border-slate-100">
              <div class="text-slate-500 text-[10px]">Empirical Req Z2 (kt·L²·B)</div>
              <div class="font-bold text-slate-900 mt-0.5">${z2EmpiricalCm3.toLocaleString('en-US', {maximumFractionDigits: 0})} cm³</div>
            </div>
            <div class="bg-emerald-50 p-2.5 rounded border border-emerald-200">
              <div class="text-emerald-700 text-[10px] font-bold">Rule Required Z_req</div>
              <div class="font-bold text-emerald-900 mt-0.5">${props.modulus_rule_required_cm3.toLocaleString('en-US', {maximumFractionDigits: 0})} cm³</div>
            </div>
          </div>
        </div>'''

if old_card in content:
    content = content.replace(old_card, new_card)
    print("Replaced RINA card with ISO 1976 card")
else:
    print("Warning: old_card not found")

# 3. Update Section 104 Header
content = content.replace(
    "<!-- CLASSICAL ASSUMED NEUTRAL AXIS INTEGRATION (SECTION 104 — RINA / SHIPDYN STYLE) -->",
    "<!-- CLASSICAL ASSUMED NEUTRAL AXIS INTEGRATION (SECTION 104 — RULE 209 / ISO 1976) -->"
)
content = content.replace(
    '<span class="px-2 py-0.5 bg-blue-100 text-blue-800 text-[10px] font-bold rounded">ShipDyn Standard</span>',
    '<span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded">ISO 1976 Standard</span>'
)

with open('app/static/js/views/StrengthView.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved StrengthView.js successfully")
