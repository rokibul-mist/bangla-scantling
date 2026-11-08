/**
 * Client-Side Statutory Scantlings & Section Modulus Calculation Engine
 * Replicates the exact naval architectural derivations from the Excel workbook
 */

function calcStiffenerSection(bp, tp, hw, tw, bf, tf, profile_type) {
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
}

function recalculateAll(state) {
  state = state || window.appState || {};
  const inputs = state.dashboard_inputs || {};
  const custom_dims = state.stiffener_custom_dims || {};
  state.stiffener_custom_dims = custom_dims;

  const factorRule = String(inputs.factor_rule || 'auto').toLowerCase();
  const route = String(inputs.proposed_route || inputs.route || 'Inland & bay crossing');
  const rLower = route.toLowerCase();
  
  const mat = String(inputs.hull_material || '').toLowerCase();
  const isOldSteel = mat.includes('old');

  let kt = 1.00;
  let kz = 1.00;
  let ruleDesc = "Rule Baseline - Inland Calm Water (kt=1.00, kz=1.00)";
  
  if (inputs.factor_mode === 'manual' || factorRule === 'custom' || (inputs.custom_kt !== undefined && inputs.custom_kz !== undefined)) {
    kt = parseFloat(inputs.custom_kt !== undefined ? inputs.custom_kt : (inputs.effective_kt || 1.20)) || 1.20;
    kz = parseFloat(inputs.custom_kz !== undefined ? inputs.custom_kz : (inputs.effective_kz || 1.25)) || 1.25;
    ruleDesc = `Custom Factor (${kt.toFixed(2)} / ${kz.toFixed(2)})`;
  } else if (isOldSteel) {
    kt = 1.40;
    kz = 1.40;
    ruleDesc = "Statutory Rule for Steel (Old): kt=1.40, kz=1.40";
  } else if (rLower.includes('bay') || rLower.includes('coastal') || factorRule.includes('sro 308')) {
    kt = 1.20;
    kz = 1.25;
    ruleDesc = "Rule 4(3) SRO 308 (Bay Crossing: kt=1.20, kz=1.25)";
  } else if (rLower.includes('rough')) {
    kt = 1.10;
    kz = 1.15;
    ruleDesc = "Inland Rough Water Regulation (kt=1.10, kz=1.15)";
  } else if (rLower.includes('seasonal crossing')) {
    kt = 1.15;
    kz = 1.20;
    ruleDesc = "Seasonal Coastal Crossing (kt=1.15, kz=1.20)";
  } else if (rLower.includes('round seasonal')) {
    kt = 1.05;
    kz = 1.10;
    ruleDesc = "Round Seasonal Regulation (kt=1.05, kz=1.10)";
  }
  
  let hullType = String(inputs.hull_type || 'Double Bottom');
  if (hullType === 'Single Bottom') {
    hullType = 'Single Hull';
  }
  const isSingleHull = hullType.toLowerCase().includes('single');
  const isDoubleHull = hullType.toLowerCase().includes('double hull');
  const vesselType = String(inputs.vessel_type || 'Steel Body Cargo Vessel');

  const isBay = kt > 1.0 || rLower.includes('bay');

  inputs.effective_kt = kt;
  inputs.effective_kz = kz;
  inputs.factor_rule_desc = ruleDesc;
  inputs.hull_type = hullType;

  const lbp = parseFloat(inputs.lbp) || 69.85;
  const spacing = parseFloat(inputs.frame_spacing) || 550;

  // Plate thickness mapping from inputs
  const plate_thk_map = {
    't_keel': parseFloat(inputs.t_keel !== undefined ? inputs.t_keel : 13.0),
    'w_keel': parseFloat(inputs.w_keel !== undefined ? inputs.w_keel : 1100.0),
    't_bottom': parseFloat(inputs.t_bottom !== undefined ? inputs.t_bottom : 12.0),
    't_bilge': parseFloat(inputs.t_bilge !== undefined ? inputs.t_bilge : 14.0),
    't_side': parseFloat(inputs.t_side !== undefined ? inputs.t_side : 12.0),
    't_sheer': parseFloat(inputs.t_sheer !== undefined ? inputs.t_sheer : (inputs.t_side !== undefined ? inputs.t_side : 12.0)),
    't_deck_all': parseFloat(inputs.t_deck_all !== undefined ? inputs.t_deck_all : 12.0),
    't_deck_hatch': parseFloat(inputs.t_deck_hatch !== undefined ? inputs.t_deck_hatch : 12.0),
    't_inner_bottom': isSingleHull ? 0.0 : parseFloat(inputs.t_inner_bottom !== undefined ? inputs.t_inner_bottom : 14.0),
    't_margin': isSingleHull ? 0.0 : parseFloat(inputs.t_margin !== undefined ? inputs.t_margin : 14.0),
    't_inner_side': parseFloat(inputs.t_inner_side !== undefined ? inputs.t_inner_side : 12.0),
    't_hopper': parseFloat(inputs.t_hopper !== undefined ? inputs.t_hopper : 12.0),
    't_bhd': parseFloat(inputs.t_bhd !== undefined ? inputs.t_bhd : 10.0),
    't_bhd_collision': parseFloat(inputs.t_bhd_collision !== undefined ? inputs.t_bhd_collision : 11.0),
    't_coaming': parseFloat(inputs.t_coaming !== undefined ? inputs.t_coaming : 12.0),
    't_hatch_long': parseFloat(inputs.t_hatch_long !== undefined ? inputs.t_hatch_long : 13.0),
    't_hatch_trans': parseFloat(inputs.t_hatch_trans !== undefined ? inputs.t_hatch_trans : 12.0),
    't_hatch_cover': parseFloat(inputs.t_hatch_cover !== undefined ? inputs.t_hatch_cover : 8.0),
    't_stem': parseFloat(inputs.t_stem !== undefined ? inputs.t_stem : 14.0),
    't_transom': parseFloat(inputs.t_transom !== undefined ? inputs.t_transom : 12.0),
    't_bulwark': parseFloat(inputs.t_bulwark !== undefined ? inputs.t_bulwark : 6.0),
    't_poop_deck': parseFloat(inputs.t_poop_deck !== undefined ? inputs.t_poop_deck : 7.0),
    't_forecastle_deck': parseFloat(inputs.t_forecastle_deck !== undefined ? inputs.t_forecastle_deck : 7.0),
    't_nav_deck': parseFloat(inputs.t_nav_deck !== undefined ? inputs.t_nav_deck : 6.0),
    't_second_deck': parseFloat(inputs.t_second_deck !== undefined ? inputs.t_second_deck : 6.5),
    't_passenger_deck': parseFloat(inputs.t_passenger_deck !== undefined ? inputs.t_passenger_deck : 6.0),
    't_wet_deck': parseFloat(inputs.t_wet_deck !== undefined ? inputs.t_wet_deck : 8.0),
    't_tunnel_side': parseFloat(inputs.t_tunnel_side !== undefined ? inputs.t_tunnel_side : 8.5),
    't_chine': parseFloat(inputs.t_chine !== undefined ? inputs.t_chine : 14.0),
    't_rake': parseFloat(inputs.t_rake !== undefined ? inputs.t_rake : 12.0),
    't_long_bhd': parseFloat(inputs.t_long_bhd !== undefined ? inputs.t_long_bhd : 10.0),
    't_tank_bhd': parseFloat(inputs.t_tank_bhd !== undefined ? inputs.t_tank_bhd : 10.0),
    't_cofferdam': parseFloat(inputs.t_cofferdam !== undefined ? inputs.t_cofferdam : 9.0),
    't_wash_bhd': parseFloat(inputs.t_wash_bhd !== undefined ? inputs.t_wash_bhd : 9.0),
    't_pump_room_bhd': parseFloat(inputs.t_pump_room_bhd !== undefined ? inputs.t_pump_room_bhd : 9.0),
    't_deck_strip': parseFloat(inputs.t_deck_strip !== undefined ? inputs.t_deck_strip : 12.0),
    't_floor_web': parseFloat(inputs.t_floor_web !== undefined ? inputs.t_floor_web : 10.0),
    't_chain_locker': parseFloat(inputs.t_chain_locker !== undefined ? inputs.t_chain_locker : 8.0),
    't_rudder': parseFloat(inputs.t_rudder !== undefined ? inputs.t_rudder : 10.0),
    't_tank_boundary': parseFloat(inputs.t_tank_boundary !== undefined ? inputs.t_tank_boundary : 11.0),
  };

  // Get dynamic structural members for this hull type and vessel type
  const existingBrainMap = new Map((state.calculation_brain || []).map(x => [x.id, x]));
  let activeMembers = [];
  if (typeof STRUCTURAL_CATALOG !== 'undefined' && STRUCTURAL_CATALOG.getActiveMembers) {
    activeMembers = STRUCTURAL_CATALOG.getActiveMembers(hullType, vesselType);
  } else if (state.calculation_brain && state.calculation_brain.length > 0) {
    activeMembers = JSON.parse(JSON.stringify(state.calculation_brain));
  }

  const sheet2_results = [];
  let sheet_counter = 1;
  let compliantCount = 0;

  activeMembers.forEach(m => {
    const m_id = m.id;
    const m_type = m.type;
    const prev = existingBrainMap.get(m_id);
    if (prev) {
      if (prev.derivation) m.derivation = prev.derivation;
      if (prev.baseline !== undefined) m.baseline = prev.baseline;
      if (prev.rreq !== undefined) m.rreq = prev.rreq;
      if (prev.table_ref) m.table_ref = prev.table_ref;
    }
    const raw_base = parseFloat(m.baseline) || 0;

    if (m_type === 'plate') {
      const b_key = m.bound_plate_key;
      let prov_val = raw_base;
      if (state.custom_brain_dact && state.custom_brain_dact[m_id] !== undefined) {
        prov_val = parseFloat(state.custom_brain_dact[m_id]);
      } else if (b_key && inputs[b_key] !== undefined) {
        prov_val = parseFloat(inputs[b_key]);
      } else if (inputs[m_id] !== undefined) {
        prov_val = parseFloat(inputs[m_id]);
      } else if (b_key && plate_thk_map[b_key] !== undefined) {
        prov_val = plate_thk_map[b_key];
      }
      
      let effFactor = kt;
      if (m_id.includes('width') || m_id === 'plate_keel_width' || m_id === 'w_keel' || m_id === 'plate_bulwark' || m_id === 'plate_chain_locker_wall') {
        effFactor = 1.00;
      } else if (m.derivation && m.derivation.inputs_used && m.derivation.inputs_used.factor !== undefined) {
        effFactor = m.derivation.inputs_used.factor;
      }
      m.factor = effFactor;
      const baseToUse = (m.derivation && typeof m.derivation.baseline === 'number') ? m.derivation.baseline : raw_base;
      const req_val = +(baseToUse * effFactor).toFixed(2);
      m.baseline = baseToUse;
      m.rreq = req_val;
      m.dact = prov_val;
      if (m.derivation) {
        m.derivation.baseline = baseToUse;
        m.derivation.rreq = req_val;
        m.derivation.factor = effFactor;
        if (m.id === 'mat_min_hull' || !m.derivation.table_view) {
          m.derivation.derivation_text = `Rule 8(1) Minimum Hull Plating: Baseline = ${baseToUse.toFixed(1)} mm × kt (${effFactor.toFixed(2)}) = ${req_val.toFixed(2)} mm.`;
        }
      }

      const margin = +(prov_val - req_val).toFixed(2);
      const isComp = margin >= 0;
      m.margin = margin;
      m.status = isComp ? 'COMPLIANT' : 'NON-COMPLIANT';
      if (isComp) compliantCount++;

    } else if (m_type === 'stiffener') {
      // Attached plate thickness dynamically bound to the plate it is welded to
      const w_key = m.welded_plate_key || 't_side';
      const tp = plate_thk_map[w_key] !== undefined ? plate_thk_map[w_key] : 12.0;

      // Custom or default profile dimensions
      const c_dim = custom_dims[m_id] || {};
      const d_prof = m.default_profile || {};

      const ptype = c_dim.profile_type || d_prof.profile_type || 'L';
      const hw = parseFloat(c_dim.web_depth !== undefined ? c_dim.web_depth : d_prof.web_depth) || 150;
      const tw = parseFloat(c_dim.web_thk !== undefined ? c_dim.web_thk : d_prof.web_thk) || 10;
      const bf = ptype === 'FB' ? 0 : (parseFloat(c_dim.flange_width !== undefined ? c_dim.flange_width : d_prof.flange_width) || 100);
      const tf = ptype === 'FB' ? 0 : (parseFloat(c_dim.flange_thk !== undefined ? c_dim.flange_thk : d_prof.flange_thk) || 10);

      // Section Modulus calculation with attached plate
      const s_res = calcStiffenerSection(spacing, tp, hw, tw, bf, tf, ptype);
      const prov_sm = s_res.z_cm3;

      m.factor = kz;
      const baseSmToUse = (m.derivation && typeof m.derivation.baseline === 'number') ? m.derivation.baseline : raw_base;
      const req_sm = +(baseSmToUse * kz).toFixed(2);
      m.baseline = baseSmToUse;
      m.rreq = req_sm;
      m.dact = +prov_sm.toFixed(2);
      if (m.derivation) {
        m.derivation.baseline = baseSmToUse;
        m.derivation.rreq = req_sm;
        m.derivation.factor = kz;
      }

      const margin = +(prov_sm - req_sm).toFixed(2);
      let isComp = margin >= 0;

      // Multi-criterion components evaluation if table prescribes multiple physical parts
      const rawComps = (m.derivation && m.derivation.components) ? m.derivation.components : (m.components || []);
      if (rawComps && rawComps.length > 0) {
        let allPass = true;
        const provFaceArea = +((bf * tf) / 100.0).toFixed(2); // cm2
        m.components = rawComps.map(c => {
          const cCopy = Object.assign({}, c);
          const rreq = parseFloat(cCopy.rreq) || 0;
          let prov = +prov_sm.toFixed(2);
          if (cCopy.param === 'web_thk') prov = tw;
          else if (cCopy.param === 'face_area' || cCopy.param === 'flange_area') prov = provFaceArea;
          else if (cCopy.param === 'face_width' || cCopy.param === 'flange_width') prov = bf;
          else if (cCopy.param === 'web_depth') prov = hw;
          else if (cCopy.param === 'sm') prov = +prov_sm.toFixed(2);

          const cMargin = +(prov - rreq).toFixed(2);
          const cStatus = cMargin >= 0 ? 'COMPLIANT' : 'NON-COMPLIANT';
          if (cStatus !== 'COMPLIANT') allPass = false;

          cCopy.prov = prov;
          cCopy.margin = cMargin;
          cCopy.status = cStatus;
          return cCopy;
        });
        if (m.derivation) m.derivation.components = m.components;
        isComp = isComp && allPass;
      }

      m.margin = margin;
      m.status = isComp ? 'COMPLIANT' : 'NON-COMPLIANT';
      if (isComp) compliantCount++;

      m.welded_plate_thickness = tp;
      m.profile_type = ptype;
      m.web_depth = hw;
      m.web_thk = tw;
      m.flange_width = bf;
      m.flange_thk = tf;

      // Add to Sheet-2 detail calculation booklet
      sheet2_results.push({
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
      });

    } else {
      // Dimension / Limit / Check
      m.factor = 1.00;
      let req_val = raw_base;
      m.rreq = req_val;

      let dact = raw_base;
      if (inputs[m_id] !== undefined) {
        dact = parseFloat(inputs[m_id]);
      } else if (state.custom_brain_dact && state.custom_brain_dact[m_id] !== undefined) {
        dact = parseFloat(state.custom_brain_dact[m_id]);
      } else if (m.dact !== undefined) {
        dact = parseFloat(m.dact);
      }
      m.dact = dact;

      let isComp = false;
      if (m_id === 'frame_spacing_limit') {
        const max_s = 450.0 + 2.0 * lbp;
        m.rreq = +max_s.toFixed(2);
        m.dact = spacing;
        isComp = spacing <= max_s;
        m.margin = +(max_s - spacing).toFixed(2);
      } else if (m_id === 'bhd_collision_pos') {
        const min_pos = 0.05 * lbp;
        const max_pos = 0.08 * lbp;
        const actual_pos = parseFloat(inputs.actual_collision_bhd_pos || 4.8);
        m.rreq = +min_pos.toFixed(2);
        m.dact = actual_pos;
        isComp = (actual_pos >= min_pos) && (actual_pos <= max_pos);
        m.margin = +(actual_pos - min_pos).toFixed(2);
      } else {
        isComp = dact >= req_val;
        m.margin = +(dact - req_val).toFixed(2);
      }

      m.status = isComp ? 'COMPLIANT' : 'NON-COMPLIANT';
      if (isComp) compliantCount++;
    }
  });

  state.calculation_brain = activeMembers;
  state.sheet2_results = sheet2_results;

  // Update Checklist (if existing)
  const chk = state.scantling_checklist || [];
  chk.forEach(row => {
    const no = row.no;
    if (no === 1) row.provided = plate_thk_map.t_keel;
    else if (no === 2) row.provided = plate_thk_map.t_bottom;
    else if (no === 3) row.provided = plate_thk_map.t_bilge;
    else if (no === 4) row.provided = plate_thk_map.t_side;
    else if (no === 5) row.provided = plate_thk_map.t_deck_hatch;
    else if (no === 6) row.provided = plate_thk_map.t_deck_all;
    else if (no === 15) row.provided = plate_thk_map.t_bhd;
    else if (no === 17) row.provided = plate_thk_map.t_hatch_long;
    else if (no === 18) row.provided = plate_thk_map.t_hatch_trans;
    else if (no === 19) row.provided = plate_thk_map.t_hatch_cover;
    else if (no === 21) row.provided = plate_thk_map.t_inner_bottom;

    const bVal = parseFloat(row.baseline) || 0;
    if ([1, 2, 3, 4, 5, 6, 15, 17, 18, 19, 21].includes(no)) {
      row.factor = kt;
      row.required = +(bVal * kt).toFixed(2);
    } else {
      row.factor = kz;
      row.required = +(bVal * kz).toFixed(2);
    }

    const rreq = parseFloat(row.required) || 0;
    const dact = parseFloat(row.provided) || 0;
    row.margin = +(dact - rreq).toFixed(2);
    row.margin_pct = rreq > 0 ? +((dact - rreq) / rreq).toFixed(4) : 0;
    row.status = dact >= rreq ? 'COMPLIED' : 'DEFICIENT';
  });

  // Dynamically update Stiffener Profiles (Table 4) derived Section Modulus
  const profPlateMap = {
    1: 't_side', 2: 't_bottom', 3: 't_side', 4: 't_deck_all',
    5: 't_deck_all', 6: 't_deck_all', 7: 't_bhd', 8: 't_bhd',
    9: 't_side', 10: 't_deck_hatch'
  };

  (state.stiffener_profiles || []).forEach(p => {
    const wKey = profPlateMap[p.id] || 't_side';
    const tp = plate_thk_map[wKey] !== undefined ? plate_thk_map[wKey] : 12.0;
    const s_res = calcStiffenerSection(spacing, tp, p.web_depth, p.web_thk, p.flange_width, p.flange_thk);
    p.derived_sm = +(s_res.z_cm3.toFixed(2));
    p.yna = +(s_res.yna.toFixed(2));
    p.tp = tp;
  });

  // Update Lightship Plates & Dimensions linked dynamically to Dashboard & Vessel Particulars
  const loa_m = parseFloat(inputs.loa) || 76.21;
  const loa_mm = +(loa_m * 1000.0).toFixed(1);
  const bm_m = parseFloat(inputs.breadth) || 13.41;
  const bm_mm = +(bm_m * 1000.0).toFixed(1);
  const dm_m = parseFloat(inputs.depth) || 5.18;
  const dm_mm = +(dm_m * 1000.0).toFixed(1);
  const hdb_mm = 500.0;

  const profiles_by_id = {};
  (state.stiffener_profiles || []).forEach(prof => {
    if (prof && prof.id) profiles_by_id[prof.id] = prof;
  });

  const cleanElementName = (raw) => {
    if (!raw) return '';
    let s = String(raw).trim();
    if (s.includes('(') && !s.startsWith('Superstructure') && !s.startsWith('BHD') && !s.startsWith('Deck Beam')) {
      s = s.split('(')[0].trim();
    }
    return s.replace(/\s+\d+(\.\d+)?\s*mm$/i, '').trim();
  };

  const scale_l_ratio = loa_mm > 0 ? loa_mm / 76210.0 : 1.0;
  const scale_b_ratio = bm_mm > 0 ? bm_mm / 13410.0 : 1.0;
  const scale_d_ratio = dm_mm > 0 ? dm_mm / 5180.0 : 1.0;

  // Master baseline structural plate assemblies (19 standard shipbuilding assemblies)
  const MASTER_BOM_PLATES = [
    { sn: 1, id: "plate_keel", name: "Keel Plate", bound_key: "t_keel", l0: 76210, b0: 600, t_def: 13.0, qty_def: 1, scale_l: "loa", scale_b: "fixed" },
    { sn: 2, id: "plate_bottom", name: "Bottom Shell Plating", bound_key: "t_bottom", l0: 76210, b0: 4605, t_def: 12.0, qty_def: 2, scale_l: "loa", scale_b: "bm" },
    { sn: 3, id: "plate_bilge", name: "Bilge Plating", bound_key: "t_bilge", l0: 76210, b0: 3000, t_def: 14.0, qty_def: 2, scale_l: "loa", scale_b: "fixed" },
    { sn: 4, id: "plate_side", name: "Side Shell Plating", bound_key: "t_side", l0: 76210, b0: 3680, t_def: 12.0, qty_def: 2, scale_l: "loa", scale_b: "dm" },
    { sn: 5, id: "plate_sheer_strake", name: "Sheer Strake Plating", bound_key: "t_side", l0: 76210, b0: 900, t_def: 12.0, qty_def: 2, scale_l: "loa", scale_b: "fixed" },
    { sn: 6, id: "plate_bulwark", name: "Bulwark Plating", bound_key: "t_bulwark", l0: 50600, b0: 1000, t_def: 10.0, qty_def: 2, scale_l: "loa", scale_b: "fixed" },
    { sn: 7, id: "plate_deck_hatch", name: "Hatchway Deck Plating", bound_key: "t_deck_hatch", l0: 47740, b0: 2100, t_def: 12.0, qty_def: 2, scale_l: "loa", scale_b: "fixed" },
    { sn: 8, id: "plate_main_deck", name: "Main Deck Plating", bound_key: "t_deck_all", l0: 17350, b0: 11928, t_def: 12.0, qty_def: 1, scale_l: "loa", scale_b: "bm" },
    { sn: 9, id: "plate_main_deck_wall", name: "Main Deck Wall (Superstructure)", bound_key: "t_side", l0: 15753, b0: 2300, t_def: 10.0, qty_def: 1, scale_l: "loa", scale_b: "fixed" },
    { sn: 10, id: "plate_poop_wall", name: "Poop Deck Wall", bound_key: "t_side", l0: 8803, b0: 2100, t_def: 8.0, qty_def: 1, scale_l: "loa", scale_b: "fixed" },
    { sn: 11, id: "plate_poop_deck", name: "Poop Deck Plating", bound_key: "t_poop_deck", l0: 15499, b0: 9781, t_def: 7.0, qty_def: 1, scale_l: "loa", scale_b: "bm" },
    { sn: 12, id: "plate_bridge_wall", name: "Bridge Deck Wall", bound_key: "t_side", l0: 3100, b0: 2000, t_def: 8.0, qty_def: 1, scale_l: "fixed", scale_b: "fixed" },
    { sn: 13, id: "plate_bridge_deck", name: "Bridge Deck Plating", bound_key: "t_nav_deck", l0: 7840, b0: 8803, t_def: 6.0, qty_def: 1, scale_l: "fixed", scale_b: "bm" },
    { sn: 14, id: "plate_bhd", name: "Transverse Watertight Bulkheads", bound_key: "t_bhd", l0: 6705, b0: 5180, t_def: 10.0, qty_def: 5, scale_l: "bm", scale_b: "dm" },
    { sn: 15, id: "plate_hatch_covers", name: "Cargo Hatch Covers Plating", bound_key: "t_deck_hatch", l0: 14630, b0: 8993, t_def: 10.0, qty_def: 3, scale_l: "loa", scale_b: "bm" },
    { sn: 16, id: "plate_forecastle_deck", name: "Forecastle Deck Plating", bound_key: "t_forecastle_deck", l0: 10111, b0: 8516, t_def: 12.0, qty_def: 1, scale_l: "loa", scale_b: "bm" },
    { sn: 17, id: "plate_inner_bottom", name: "Double Bottom Tank Top Plate", bound_key: "t_inner_bottom", l0: 76210, b0: 13410, t_def: 12.0, qty_def: 0, scale_l: "loa", scale_b: "bm" },
    { sn: 18, id: "plate_stem_transom", name: "Stem, Stern & Rudder Assembly", bound_key: "t_stem", l0: 8000, b0: 3500, t_def: 14.0, qty_def: 2, scale_l: "fixed", scale_b: "fixed" },
    { sn: 19, id: "plate_partitions", name: "Superstructure Partition Bulkheads", bound_key: "t_side", l0: 11928, b0: 2300, t_def: 6.0, qty_def: 2, scale_l: "bm", scale_b: "fixed" }
  ];

  // Master baseline structural stiffener assemblies (21 standard shipbuilding assemblies)
  const MASTER_BOM_ANGLES = [
    { sn: 1, id: "stiff_centre_keelson", name: "Center Keelson", weld_plate: "Keel Plate", hw: 500, bf: 400, tw: 12.0, len0: 76210, qty_def: 1, scale_len: "loa" },
    { sn: 2, id: "stiff_side_keelson", name: "Side Keelson", weld_plate: "Bottom Shell Plating", hw: 500, bf: 150, tw: 11.0, len0: 76210, qty_def: 8, scale_len: "loa" },
    { sn: 3, id: "stiff_side_stringer", name: "Side Stringer", weld_plate: "Side Shell Plating", hw: 324, bf: 90, tw: 11.0, len0: 76210, qty_def: 6, scale_len: "loa" },
    { sn: 4, id: "stiff_deck_girder", name: "Deck Girder", weld_plate: "Main Deck Plating", hw: 300, bf: 90, tw: 11.0, len0: 76210, qty_def: 7, scale_len: "loa" },
    { sn: 5, id: "stiff_floor_single", name: "Floor", weld_plate: "Bottom Shell Plating", hw: 500, bf: 150, tw: 14.0, len0: 6705, qty_def: 126, scale_len: "bm_half" },
    { sn: 6, id: "stiff_web_frame", name: "Web Frame", weld_plate: "Side Shell Plating", hw: 324, bf: 90, tw: 11.0, len0: 4380, qty_def: 27, scale_len: "dm" },
    { sn: 7, id: "stiff_main_frame", name: "Main Frame", weld_plate: "Side Shell Plating", hw: 190, bf: 90, tw: 9.0, len0: 4380, qty_def: 100, scale_len: "dm" },
    { sn: 8, id: "stiff_deck_beam", name: "Deck Beam", weld_plate: "Main Deck Plating", hw: 140, bf: 90, tw: 9.0, len0: 6705, qty_def: 52, scale_len: "bm_half" },
    { sn: 9, id: "stiff_deck_web_beam", name: "Deck Web", weld_plate: "Main Deck Plating", hw: 300, bf: 90, tw: 11.0, len0: 6705, qty_def: 27, scale_len: "bm_half" },
    { sn: 10, id: "stiff_deck_beam_main", name: "Deck Beam (Main Deck)", weld_plate: "Main Deck Plating", hw: 75, bf: 75, tw: 6.0, len0: 6705, qty_def: 30, scale_len: "bm_half" },
    { sn: 11, id: "stiff_deck_beam_poop", name: "Deck Beam (Poop Deck)", weld_plate: "Poop Deck Plating", hw: 65, bf: 65, tw: 6.0, len0: 3813, qty_def: 18, scale_len: "fixed" },
    { sn: 12, id: "stiff_deck_beam_bridge", name: "Deck Beam (Bridge Deck)", weld_plate: "Bridge Deck Plating", hw: 50, bf: 50, tw: 5.0, len0: 2897, qty_def: 7, scale_len: "fixed" },
    { sn: 13, id: "stiff_bhd_vertical", name: "BHD Angle (Vertical)", weld_plate: "Transverse Watertight Bulkheads", hw: 120, bf: 120, tw: 10.0, len0: 5180, qty_def: 45, scale_len: "dm" },
    { sn: 14, id: "stiff_bhd_horizontal", name: "BHD Angle (Horizontal)", weld_plate: "Transverse Watertight Bulkheads", hw: 120, bf: 120, tw: 10.0, len0: 13410, qty_def: 25, scale_len: "bm" },
    { sn: 15, id: "stiff_hatch_girder", name: "Hatch Girder", weld_plate: "Hatchway Deck Plating", hw: 65, bf: 65, tw: 6.0, len0: 4605, qty_def: 15, scale_len: "fixed" },
    { sn: 16, id: "stiff_super_girder_main", name: "Superstructure Girder (Main Deck)", weld_plate: "Main Deck Wall (Superstructure)", hw: 75, bf: 75, tw: 6.0, len0: 2300, qty_def: 31, scale_len: "fixed" },
    { sn: 17, id: "stiff_super_girder_poop", name: "Superstructure Girder (Poop Deck)", weld_plate: "Poop Deck Wall", hw: 65, bf: 65, tw: 6.0, len0: 2100, qty_def: 17, scale_len: "fixed" },
    { sn: 18, id: "stiff_super_girder_bridge", name: "Superstructure Girder (Bridge Deck)", weld_plate: "Bridge Deck Wall", hw: 50, bf: 50, tw: 5.0, len0: 2000, qty_def: 6, scale_len: "fixed" },
    { sn: 19, id: "stiff_super_long_main", name: "Superstructure Long. Girder (Main Deck)", weld_plate: "Main Deck Wall (Superstructure)", hw: 200, bf: 90, tw: 7.0, len0: 15753, qty_def: 1, scale_len: "fixed" },
    { sn: 20, id: "stiff_super_long_poop", name: "Superstructure Long. Girder (Poop Deck)", weld_plate: "Poop Deck Wall", hw: 200, bf: 90, tw: 7.0, len0: 8803, qty_def: 1, scale_len: "fixed" },
    { sn: 21, id: "stiff_super_long_bridge", name: "Superstructure Long. Girder (Bridge Deck)", weld_plate: "Bridge Deck Wall", hw: 200, bf: 90, tw: 7.0, len0: 3100, qty_def: 1, scale_len: "fixed" },
  ];

  const existing_plates_by_id = {};
  (state.lightship_plates || []).forEach(p => {
    if (p.id) existing_plates_by_id[p.id] = p;
    if (p.sn) existing_plates_by_id[`sn_${p.sn}`] = p;
  });

  const existing_angles_by_id = {};
  (state.lightship_angles || []).forEach(a => {
    if (a.id) existing_angles_by_id[a.id] = a;
    if (a.sn) existing_angles_by_id[`sn_${a.sn}`] = a;
  });

  const custom_brain_dact = state.custom_brain_dact || {};
  const brain_by_id = {};
  (state.calculation_brain || []).forEach(m => {
    if (m && m.id) brain_by_id[m.id] = m;
  });

  // Synthesize Plates
  let total_plate_kg = 0;
  const plates = MASTER_BOM_PLATES.map(tmpl => {
    const sn = tmpl.sn;
    const m_id = tmpl.id;
    const name = cleanElementName(tmpl.name);
    let saved = existing_plates_by_id[m_id] || existing_plates_by_id[`sn_${sn}`] || {};
    if (saved && saved.id && saved.id !== m_id && saved.name !== name) saved = {};

    let t_val = tmpl.t_def;
    if (custom_brain_dact[m_id] !== undefined) {
      t_val = parseFloat(custom_brain_dact[m_id]);
    } else if (inputs[tmpl.bound_key] !== undefined) {
      t_val = parseFloat(inputs[tmpl.bound_key]);
    } else if (brain_by_id[m_id] && brain_by_id[m_id].dact !== undefined) {
      t_val = parseFloat(brain_by_id[m_id].dact);
    } else if (plate_thk_map[tmpl.bound_key] !== undefined) {
      t_val = parseFloat(plate_thk_map[tmpl.bound_key]);
    } else if (saved.t !== undefined) {
      t_val = parseFloat(saved.t);
    }

    let def_l = tmpl.l0;
    if (tmpl.scale_l === "loa") def_l = Math.round(tmpl.l0 * scale_l_ratio * 10) / 10;
    else if (tmpl.scale_l === "bm") def_l = bm_mm;

    let def_b = tmpl.b0;
    if (tmpl.scale_b === "bm") def_b = Math.round(tmpl.b0 * scale_b_ratio * 10) / 10;
    else if (tmpl.scale_b === "dm") def_b = Math.round(tmpl.b0 * scale_d_ratio * 10) / 10;

    let def_qty = tmpl.qty_def;
    if (m_id === "plate_inner_bottom") {
      def_qty = isSingleHull ? 0 : 1;
    }

    let saved_l = saved.l !== undefined ? parseFloat(saved.l) : def_l;
    let saved_b = saved.b !== undefined ? parseFloat(saved.b) : def_b;
    let saved_qty = saved.qty !== undefined ? parseInt(saved.qty, 10) : def_qty;

    if (tmpl.scale_l === "fixed" && saved_l > 25000.0) saved_l = def_l;
    if (tmpl.scale_b === "fixed" && saved_b > 6000.0) saved_b = def_b;
    if (m_id === "plate_inner_bottom" && isSingleHull) saved_qty = 0;

    const vol = (saved_l / 1000.0) * (saved_b / 1000.0) * (t_val / 1000.0);
    const weight_kg = vol * 7850.0 * saved_qty;
    const weight_tonne = weight_kg / 1000.0;
    total_plate_kg += weight_kg;

    return {
      sn: sn,
      id: m_id,
      name: name,
      element: name,
      l: saved_l,
      b: saved_b,
      t: t_val,
      density: 7850,
      qty: saved_qty,
      vol: vol,
      weight_kg: weight_kg,
      weight_tonne: weight_tonne
    };
  });
  state.lightship_plates = plates;

  // Synthesize Angles
  let total_angle_kg = 0;
  const angles = MASTER_BOM_ANGLES.map(tmpl => {
    const sn = tmpl.sn;
    const s_id = tmpl.id;
    const name = cleanElementName(tmpl.name);
    let saved = existing_angles_by_id[s_id] || existing_angles_by_id[`sn_${sn}`] || {};
    if (saved && saved.id && saved.id !== s_id && saved.name !== name) saved = {};

    const c_dim = custom_dims[s_id] || {};
    const brain_m = brain_by_id[s_id] || {};
    const d_prof = brain_m.default_profile || {};

    const hw = parseFloat(c_dim.web_depth || brain_m.web_depth || d_prof.web_depth || saved.l_dim || tmpl.hw);
    const tw = parseFloat(c_dim.web_thk || brain_m.web_thk || d_prof.web_thk || saved.t || tmpl.tw);
    const bf = parseFloat(c_dim.flange_width || brain_m.flange_width || d_prof.flange_width || saved.b_dim || tmpl.bf);

    let def_len = tmpl.len0;
    if (tmpl.scale_len === "loa") def_len = Math.round(tmpl.len0 * scale_l_ratio * 10) / 10;
    else if (tmpl.scale_len === "bm") def_len = bm_mm;
    else if (tmpl.scale_len === "bm_half") def_len = Math.round((bm_mm / 2.0) * 10) / 10;
    else if (tmpl.scale_len === "dm") def_len = Math.round((dm_mm > 500 ? dm_mm - 500 : dm_mm) * 10) / 10;

    let def_qty = tmpl.qty_def;
    let saved_len = saved.length !== undefined ? parseFloat(saved.length) : def_len;
    let saved_qty = saved.qty !== undefined ? parseInt(saved.qty, 10) : def_qty;

    if (saved_qty > def_qty * 3) saved_qty = def_qty;

    const area = Math.round((hw + bf) * tw * 100) / 100;
    const vol = (area / 1e6) * (saved_len / 1000.0);
    const weight_kg = vol * 7850.0 * saved_qty;
    const weight_tonne = weight_kg / 1000.0;
    total_angle_kg += weight_kg;

    return {
      sn: sn,
      id: s_id,
      name: name,
      element: name,
      welded_on_plate: tmpl.weld_plate,
      l_dim: hw,
      b_dim: bf,
      t: tw,
      length: saved_len,
      density: 7850,
      qty: saved_qty,
      area: area,
      vol: vol,
      weight_kg: weight_kg,
      weight_tonne: weight_tonne
    };
  });
  state.lightship_angles = angles;

  const total_steel_t = (total_plate_kg + total_angle_kg) / 1000.0;
  const allowance_t = total_steel_t * 0.20;
  const outfit_t = total_steel_t * 0.15;
  const piping_t = total_steel_t * 0.10;
  const electrical_t = total_steel_t * 0.03;
  const accom_t = total_steel_t * 0.01;
  const misc_t = total_steel_t * 0.07;
  const total_lightship_t = total_steel_t + allowance_t + outfit_t + piping_t + electrical_t + accom_t + misc_t;

  state.lightship_summary = {
    total_plate_tonne: +(total_plate_kg / 1000.0).toFixed(3),
    total_angle_tonne: +(total_angle_kg / 1000.0).toFixed(3),
    total_steel_tonne: +total_steel_t.toFixed(3),
    allowance_tonne: +allowance_t.toFixed(3),
    outfit_tonne: +outfit_t.toFixed(3),
    piping_tonne: +piping_t.toFixed(3),
    electrical_tonne: +electrical_t.toFixed(3),
    accom_tonne: +accom_t.toFixed(3),
    misc_tonne: +misc_t.toFixed(3),
    total_lightship_tonne: +total_lightship_t.toFixed(3)
  };

  const totalAudited = activeMembers.length;
  state.summary_stats = {
    compliant_items: compliantCount,
    total_items: totalAudited,
    compliance_pct: totalAudited > 0 ? +((compliantCount / totalAudited) * 100.0).toFixed(1) : 100.0,
    checklist_complied: chk.filter(c => c.status === 'COMPLIED').length,
    checklist_total: chk.length,
    active_status: isBay ? 'BAY CROSSING' : 'INLAND BASELINE',
    overall_status: compliantCount >= totalAudited - 2 ? 'COMPLIANT' : 'ACTION REQUIRED'
  };

  return state;
}

/**
 * Technical Black & White Stiffener Cross-Section Geometry SVG matching Image 2
 */
function renderStiffenerSvg(bp, tp, hw, tw, bf, tf, yna, memberName = 'SIDE FRAME', z_cm3 = 221.5, ptype = 'L', width = 360, height = 280) {
  // Defensive parameter check: if width/height passed in place of ptype
  if (typeof ptype === 'number') {
    height = width;
    width = ptype;
    ptype = 'L';
  }
  width = (typeof width === 'number' && !isNaN(width) && width > 0) ? width : 360;
  height = (typeof height === 'number' && !isNaN(height) && height > 0) ? height : 280;

  bp = parseFloat(bp) || 550;
  tp = parseFloat(tp) || 12;
  hw = parseFloat(hw) || 150;
  tw = parseFloat(tw) || 10;
  bf = parseFloat(bf) || 0;
  tf = parseFloat(tf) || 0;
  yna = parseFloat(yna) || 37;

  const profType = String(ptype || 'L').toUpperCase().trim();
  const isFB = profType === 'FB' || bf <= 0 || tf <= 0;
  const isT = profType === 'T' && !isFB;
  const isL = !isFB && !isT;

  const effectiveBf = isFB ? 0 : bf;
  const effectiveTf = isFB ? 0 : tf;

  const totalHeightMm = tp + hw + effectiveTf;
  const maxW = Math.max(bp * 0.45, effectiveBf, 120);
  const scaleY = (height - 95) / (totalHeightMm || 1);
  const scaleX = (width - 60) / (maxW || 1);
  const scale = Math.min(scaleX, scaleY, 0.95);

  const cx = width / 2;
  const baseY = height - 38;

  // Attached Plate (centered horizontally)
  const pW = Math.min(bp * 0.35 * scale, width - 50);
  const pH = Math.max(tp * scale, 5);
  const plateX = cx - pW / 2;
  const plateY = baseY - pH;

  // Web (centered horizontally)
  const wH = hw * scale;
  const wW = Math.max(tw * scale, 4);
  const webX = cx - wW / 2;
  const webY = plateY - wH;

  // Flange (T-bar or L-angle)
  const fW = effectiveBf * scale;
  const fH = Math.max(effectiveTf * scale, 4);
  // For T-bar: flange is centered over web
  // For L-angle: flange extends to the right from web
  const flangeX = isT ? (cx - fW / 2) : webX;
  const flangeY = webY - fH;

  // Neutral Axis Line
  const naY = baseY - (yna * scale);

  let profStr = '';
  if (isFB) {
    profStr = `FB ${Math.round(hw)}x${Math.round(tw)} mm`;
  } else if (isT) {
    profStr = `T ${Math.round(hw)}x${Math.round(effectiveBf)}x${Math.round(tw)} mm`;
  } else {
    profStr = `L ${Math.round(hw)}x${Math.round(effectiveBf)}x${Math.round(tw)} mm`;
  }

  return `
    <svg viewBox="0 0 ${width} ${height}" class="w-full h-auto bg-white border border-black rounded-none shadow-none font-sans">
      <!-- Header text as in image 2 -->
      <text x="16" y="22" font-size="11" font-weight="700" fill="#000000" font-family="'Helvetica Neue', Arial, sans-serif" letter-spacing="0.5">${memberName.toUpperCase()}</text>
      <text x="16" y="38" font-size="9.5" font-weight="500" fill="#111827" font-family="'Helvetica Neue', Arial, sans-serif">Section: ${profStr}</text>
      <text x="16" y="52" font-size="9.5" font-weight="500" fill="#111827" font-family="'Helvetica Neue', Arial, sans-serif">Section Modulus: Z = ${parseFloat(z_cm3).toFixed(2)} cm3</text>

      <!-- Attached Plate -->
      <rect x="${plateX}" y="${plateY}" width="${pW}" height="${pH}" fill="#f3f4f6" stroke="#000000" stroke-width="1.2"/>
      <text x="${cx}" y="${plateY + pH + 12}" font-size="8.5" font-family="'Courier New', monospace" fill="#000000" font-weight="600" text-anchor="middle">Pl. ${Math.round(bp)}x${Math.round(tp)}</text>

      <!-- Web -->
      <rect x="${webX}" y="${webY}" width="${wW}" height="${wH}" fill="#e5e7eb" stroke="#000000" stroke-width="1.2"/>
      <text x="${webX - 8}" y="${webY + wH/2 + 3}" font-size="8.5" font-family="'Courier New', monospace" fill="#000000" font-weight="600" text-anchor="end">${Math.round(hw)}x${Math.round(tw)}</text>

      <!-- Flange -->
      ${!isFB && effectiveBf > 0 ? `
        <rect x="${flangeX}" y="${flangeY}" width="${fW}" height="${fH}" fill="#e5e7eb" stroke="#000000" stroke-width="1.2"/>
        <text x="${flangeX + fW/2}" y="${flangeY - 4}" font-size="8.5" font-family="'Courier New', monospace" fill="#000000" font-weight="600" text-anchor="middle">${Math.round(effectiveBf)}x${Math.round(effectiveTf)}</text>
      ` : ''}

      <!-- Neutral Axis Line -->
      <line x1="25" y1="${naY}" x2="${width - 25}" y2="${naY}" stroke="#000000" stroke-dasharray="4,2" stroke-width="0.8"/>
      <text x="${width - 20}" y="${naY - 3}" font-size="8.5" font-family="'Helvetica Neue', Arial, sans-serif" fill="#000000" font-weight="700" text-anchor="end">N.A.</text>

      <!-- Bottom border line and title as in image 2 -->
      <line x1="0" y1="${height - 22}" x2="${width}" y2="${height - 22}" stroke="#000000" stroke-width="0.8"/>
      <text x="${cx}" y="${height - 8}" font-size="8.5" font-family="'Helvetica Neue', Arial, sans-serif" font-weight="700" fill="#000000" text-anchor="middle" letter-spacing="0.5">STRUCTURAL CROSS-SECTION GEOMETRY</text>
    </svg>
  `;
}
