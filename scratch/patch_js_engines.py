with open('app/static/js/calc.js', 'r', encoding='utf-8') as f:
    calc_js = f.read().replace('\r\n', '\n')

old_calc_fn = """function calcStiffenerSection(bp, tp, hw, tw, bf, tf) {
  bp = parseFloat(bp) || 0;
  tp = parseFloat(tp) || 0;
  hw = parseFloat(hw) || 0;
  tw = parseFloat(tw) || 0;
  bf = parseFloat(bf) || 0;
  tf = parseFloat(tf) || 0;

  const ap = bp * tp;
  const aw = hw * tw;
  const af = bf > 0 ? bf * tf : 0;
  const atot = ap + aw + af;

  if (atot <= 0) {
    return {
      ap: 0, aw: 0, af: 0, atot: 0,
      yna: 0, ip: 0, iw: 0, if: 0, ina: 0,
      ymax: 0, z_mm3: 0, z_cm3: 0
    };
  }

  // Centroid distance from outer face of plate (mm)
  const yna = (ap * (tp / 2.0) + aw * (tp + hw / 2.0) + af * (tp + hw + tf / 2.0)) / atot;

  // Parallel axis theorem moments of inertia (mm4)
  const ip = (bp * Math.pow(tp, 3)) / 12.0 + ap * Math.pow(yna - tp / 2.0, 2);
  const iw = (tw * Math.pow(hw, 3)) / 12.0 + aw * Math.pow(tp + hw / 2.0 - yna, 2);
  const iff = bf > 0 ? (bf * Math.pow(tf, 3)) / 12.0 + af * Math.pow(tp + hw + tf / 2.0 - yna, 2) : 0;

  const ina = ip + iw + iff;
  const total_depth = tp + hw + tf;
  const ymax = Math.max(yna, total_depth - yna);

  const z_mm3 = ymax > 0 ? ina / ymax : 0;
  const z_cm3 = z_mm3 / 1000.0;

  return {
    ap, aw, af, atot,
    yna, ip, iw, if: iff, ina,
    ymax, z_mm3, z_cm3
  };
}"""

new_calc_fn = """function calcStiffenerSection(bp, tp, hw, tw, bf, tf, profile_type) {
  bp = parseFloat(bp) || 0;
  tp = parseFloat(tp) || 0;
  hw = parseFloat(hw) || 0;
  tw = parseFloat(tw) || 0;
  bf = parseFloat(bf) || 0;
  tf = parseFloat(tf) || 0;
  const ptype = String(profile_type || (bf <= 0 ? 'FB' : 'L')).toUpperCase().trim();
  const is_fb = (ptype === 'FB' || bf <= 0);

  if (is_fb) {
    bf = 0;
    tf = 0;
  }

  const ap = bp * tp;
  const aw = hw * tw;
  const af = (!is_fb && bf > 0) ? bf * tf : 0;
  const atot = ap + aw + af;

  if (atot <= 0) {
    return {
      ap: 0, aw: 0, af: 0, atot: 0,
      yna: 0, ip: 0, iw: 0, if: 0, ina: 0,
      ymax: 0, z_mm3: 0, z_cm3: 0,
      profile_type: ptype
    };
  }

  // Centroid distance from outer face of plate (mm)
  const yna = is_fb
    ? (ap * (tp / 2.0) + aw * (tp + hw / 2.0)) / atot
    : (ap * (tp / 2.0) + aw * (tp + hw / 2.0) + af * (tp + hw + tf / 2.0)) / atot;

  // Parallel axis theorem moments of inertia (mm4)
  const ip = (bp * Math.pow(tp, 3)) / 12.0 + ap * Math.pow(yna - tp / 2.0, 2);
  const iw = (tw * Math.pow(hw, 3)) / 12.0 + aw * Math.pow(tp + hw / 2.0 - yna, 2);
  const iff = (!is_fb && bf > 0) ? (bf * Math.pow(tf, 3)) / 12.0 + af * Math.pow(tp + hw + tf / 2.0 - yna, 2) : 0;

  const ina = ip + iw + iff;
  const total_depth = tp + hw + (is_fb ? 0 : tf);
  const ymax = Math.max(yna, total_depth - yna);

  const z_mm3 = ymax > 0 ? ina / ymax : 0;
  const z_cm3 = z_mm3 / 1000.0;

  return {
    ap, aw, af, atot,
    yna, ip, iw, if: iff, ina,
    ymax, z_mm3, z_cm3,
    profile_type: ptype
  };
}"""

assert old_calc_fn in calc_js, "old_calc_fn not found in calc.js"
calc_js = calc_js.replace(old_calc_fn, new_calc_fn)

old_call = "const s_res = calcStiffenerSection(spacing, tp, hw, tw, bf, tf);"
new_call = "const s_res = calcStiffenerSection(spacing, tp, hw, tw, bf, tf, ptype);"
assert old_call in calc_js, "old_call not found in calc.js"
calc_js = calc_js.replace(old_call, new_call)

# In sheet2_results.push({...s_res}):
old_push = """      sheet2_results.push({
        id: sheet_counter++,
        member_id: m_id,
        name: m.name,
        type: 'section_modulus',
        table_ref: m.table_ref || '',
        welded_on_plate: m.welded_on_plate || '',
        welded_plate_key: w_key,
        plate_width: spacing,
        plate_thk: tp,
        profile_type: ptype,
        web_height: hw,
        web_thk: tw,
        flange_width: bf,
        flange_thk: tf,
        rreq: req_sm,
        margin: margin,
        status: isComp ? 'COMPLIANT' : 'NON-COMPLIANT',
        derivation: m.derivation,
        ...s_res
      });"""

new_push = """      sheet2_results.push({
        id: sheet_counter++,
        member_id: m_id,
        name: m.name,
        type: 'section_modulus',
        table_ref: m.table_ref || '',
        welded_on_plate: m.welded_on_plate || '',
        welded_plate_key: w_key,
        plate_width: spacing,
        plate_thk: tp,
        web_height: hw,
        web_thk: tw,
        flange_width: bf,
        flange_thk: tf,
        rreq: req_sm,
        margin: margin,
        status: isComp ? 'COMPLIANT' : 'NON-COMPLIANT',
        derivation: m.derivation,
        ...s_res,
        profile_type: ptype
      });"""
assert old_push in calc_js, "old_push not found in calc.js"
calc_js = calc_js.replace(old_push, new_push)

with open('app/static/js/calc.js', 'w', encoding='utf-8') as f:
    f.write(calc_js)
print("Updated calc.js")

# Now NavalCalcEngine.js
with open('app/static/js/engine/NavalCalcEngine.js', 'r', encoding='utf-8') as f:
    engine_js = f.read().replace('\r\n', '\n')

old_engine_fn = """  static calcStiffenerSection(bp, tp, hw, tw, bf, tf) {
    if (typeof window.calcStiffenerSection === 'function') {
      return window.calcStiffenerSection(bp, tp, hw, tw, bf, tf);
    }
    // Fallback direct math
    bp = parseFloat(bp) || 0;
    tp = parseFloat(tp) || 0;
    hw = parseFloat(hw) || 0;
    tw = parseFloat(tw) || 0;
    bf = parseFloat(bf) || 0;
    tf = parseFloat(tf) || 0;

    const ap = bp * tp;
    const aw = hw * tw;
    const af = bf > 0 ? bf * tf : 0;
    const atot = ap + aw + af;

    if (atot <= 0) {
      return {
        ap: 0, aw: 0, af: 0, atot: 0,
        yna: 0, ip: 0, iw: 0, if: 0, ina: 0,
        ymax: 0, z_mm3: 0, z_cm3: 0
      };
    }

    const yna = (ap * (tp / 2.0) + aw * (tp + hw / 2.0) + af * (tp + hw + tf / 2.0)) / atot;
    const ip = (bp * Math.pow(tp, 3)) / 12.0 + ap * Math.pow(yna - tp / 2.0, 2);
    const iw = (tw * Math.pow(hw, 3)) / 12.0 + aw * Math.pow(tp + hw / 2.0 - yna, 2);
    const iff = bf > 0 ? (bf * Math.pow(tf, 3)) / 12.0 + af * Math.pow(tp + hw + tf / 2.0 - yna, 2) : 0;
    const ina = ip + iw + iff;
    const total_depth = tp + hw + tf;
    const ymax = Math.max(yna, total_depth - yna);
    const z_mm3 = ymax > 0 ? ina / ymax : 0;
    const z_cm3 = z_mm3 / 1000.0;

    return {
      ap, aw, af, atot,
      yna, ip, iw, if: iff, ina,
      ymax, z_mm3, z_cm3
    };
  }"""

new_engine_fn = """  static calcStiffenerSection(bp, tp, hw, tw, bf, tf, profile_type) {
    if (typeof window.calcStiffenerSection === 'function') {
      return window.calcStiffenerSection(bp, tp, hw, tw, bf, tf, profile_type);
    }
    // Fallback direct math
    bp = parseFloat(bp) || 0;
    tp = parseFloat(tp) || 0;
    hw = parseFloat(hw) || 0;
    tw = parseFloat(tw) || 0;
    bf = parseFloat(bf) || 0;
    tf = parseFloat(tf) || 0;
    const ptype = String(profile_type || (bf <= 0 ? 'FB' : 'L')).toUpperCase().trim();
    const is_fb = (ptype === 'FB' || bf <= 0);

    if (is_fb) {
      bf = 0;
      tf = 0;
    }

    const ap = bp * tp;
    const aw = hw * tw;
    const af = (!is_fb && bf > 0) ? bf * tf : 0;
    const atot = ap + aw + af;

    if (atot <= 0) {
      return {
        ap: 0, aw: 0, af: 0, atot: 0,
        yna: 0, ip: 0, iw: 0, if: 0, ina: 0,
        ymax: 0, z_mm3: 0, z_cm3: 0,
        profile_type: ptype
      };
    }

    const yna = is_fb
      ? (ap * (tp / 2.0) + aw * (tp + hw / 2.0)) / atot
      : (ap * (tp / 2.0) + aw * (tp + hw / 2.0) + af * (tp + hw + tf / 2.0)) / atot;
    const ip = (bp * Math.pow(tp, 3)) / 12.0 + ap * Math.pow(yna - tp / 2.0, 2);
    const iw = (tw * Math.pow(hw, 3)) / 12.0 + aw * Math.pow(tp + hw / 2.0 - yna, 2);
    const iff = (!is_fb && bf > 0) ? (bf * Math.pow(tf, 3)) / 12.0 + af * Math.pow(tp + hw + tf / 2.0 - yna, 2) : 0;
    const ina = ip + iw + iff;
    const total_depth = tp + hw + (is_fb ? 0 : tf);
    const ymax = Math.max(yna, total_depth - yna);
    const z_mm3 = ymax > 0 ? ina / ymax : 0;
    const z_cm3 = z_mm3 / 1000.0;

    return {
      ap, aw, af, atot,
      yna, ip, iw, if: iff, ina,
      ymax, z_mm3, z_cm3,
      profile_type: ptype
    };
  }"""

assert old_engine_fn in engine_js, "old_engine_fn not found in NavalCalcEngine.js"
engine_js = engine_js.replace(old_engine_fn, new_engine_fn)

with open('app/static/js/engine/NavalCalcEngine.js', 'w', encoding='utf-8') as f:
    f.write(engine_js)
print("Updated NavalCalcEngine.js")
