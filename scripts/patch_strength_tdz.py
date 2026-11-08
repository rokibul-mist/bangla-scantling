with open('app/static/js/views/StrengthView.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('\r\n', '\n')

old_block = """  const moms = report.bending_moments;
  const props = report.midship_properties;
  const t66 = report.table_66_stresses;
  const t67 = report.table_67_local_stresses || [];
  const part = report.particulars;
  const work = report.practical_working || {};
  const assumed = report.assumed_axis_integration || {};
  const rina = report.rina_classification || {};

  const isCompliant = report.is_compliant;
  const statusBadge = isCompliant 
    ? '<span class="px-2.5 py-1 bg-emerald-100 text-emerald-800 text-xs font-bold rounded-full border border-emerald-300">STATUTORY COMPLIANT</span>'
    : '<span class="px-2.5 py-1 bg-red-100 text-red-800 text-xs font-bold rounded-full border border-red-300">NON-COMPLIANT</span>';

  const selectedCount = props.elements_selected_count || props.elements.filter(e => e.is_included).length;
  const totalCount = props.elements_count || props.elements.length;

  const yDeckM = props.distance_to_deck_m || yDeckM || (parseFloat(part.depth || 5.18) - props.neutral_axis_above_keel_m);
  const yBottomM = props.neutral_axis_above_keel_m || yBottomM || (parseFloat(part.depth || 5.18) * 0.45);
  const z1StressCm3 = z1StressCm3 || (((moms.m_design_knm || 0) * 1000.0) / 130.0);
  const z2EmpiricalCm3 = props.modulus_empirical_cm3 || (1.75 * (report.factor_kt || 1.40) * Math.pow(part.lbp || 66.8, 2) * (part.breadth || 11.2) * ((part.cb || 0.75) + 0.70));
  const firstMomentCm3 = props.first_moment_cm3 || (props.total_area_cm2 * yBottomM * 100.0);
  const factorCw = moms.wave_coefficient_cw || report.factor_cw || 0.936;

  try {"""

new_block = """  try {
    const moms = report.bending_moments || {};
    const props = report.midship_properties || {};
    const t66 = report.table_66_stresses || {};
    const t67 = report.table_67_local_stresses || [];
    const part = report.particulars || {};
    const work = report.practical_working || {};
    const assumed = report.assumed_axis_integration || {};
    const rina = report.rina_classification || {};

    const isCompliant = !!report.is_compliant;
    const statusBadge = isCompliant 
      ? '<span class="px-2.5 py-1 bg-emerald-100 text-emerald-800 text-xs font-bold rounded-full border border-emerald-300">STATUTORY COMPLIANT</span>'
      : '<span class="px-2.5 py-1 bg-red-100 text-red-800 text-xs font-bold rounded-full border border-red-300">NON-COMPLIANT</span>';

    const elementsList = props.elements || [];
    const selectedCount = props.elements_selected_count ?? elementsList.filter(e => e.is_included).length;
    const totalCount = props.elements_count ?? elementsList.length;

    const depthM = parseFloat(part.depth || 5.18);
    const yBottomM = props.neutral_axis_above_keel_m ?? (depthM * 0.45);
    const yDeckM = props.distance_to_deck_m ?? (depthM - yBottomM);
    const z1StressCm3 = (((moms.m_design_knm || 0) * 1000.0) / 130.0);
    const z2EmpiricalCm3 = props.modulus_empirical_cm3 || (1.75 * (report.factor_kt || 1.40) * Math.pow(part.lbp || 66.8, 2) * (part.breadth || 11.2) * ((part.cb || 0.75) + 0.70));
    const firstMomentCm3 = props.first_moment_cm3 || ((props.total_area_cm2 || 0) * yBottomM * 100.0);
    const factorCw = moms.wave_coefficient_cw || report.factor_cw || 0.936;"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('app/static/js/views/StrengthView.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: Patched StrengthView.js')
else:
    print('ERROR: old_block not found in StrengthView.js')
