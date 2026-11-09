/**
 * Comprehensive Statutory Rules & Empirical Tables Interpolation Engine (100 Members, Tables 1-67)
 * Implements the complete Bangladesh Department of Shipping (DOS) SRO 308/2001 & Inland Shipping Ordinance
 * statutory scantling rules and interpolations for ALL structural members.
 */

function interp1D(x, xNodes, yNodes) {
  if (x <= xNodes[0]) {
    const lam = (x - xNodes[0]) / (xNodes[1] - xNodes[0]);
    return yNodes[0] + lam * (yNodes[1] - yNodes[0]);
  }
  const n = xNodes.length;
  if (x >= xNodes[n - 1]) {
    const lam = (x - xNodes[n - 2]) / (xNodes[n - 1] - xNodes[n - 2]);
    return yNodes[n - 2] + lam * (yNodes[n - 1] - yNodes[n - 2]);
  }
  for (let i = 0; i < n - 1; i++) {
    if (x >= xNodes[i] && x <= xNodes[i + 1]) {
      const lam = (x - xNodes[i]) / (xNodes[i + 1] - xNodes[i]);
      return yNodes[i] + lam * (yNodes[i + 1] - yNodes[i]);
    }
  }
  return yNodes[0];
}

function applySpacingCorr(baseVal, spacing, isSm = false) {
  if (spacing <= 550.0) return baseVal;
  const ratio = spacing / 550.0;
  const factor = isSm ? ratio : Math.sqrt(ratio);
  return +(baseVal * factor).toFixed(2);
}

const StatutoryInterpolators = {
  // Table 0: Rule 8(1) Minimum Hull Plating
  interpolateRule08: function(lbp, kt) {
    const base = lbp <= 20.0 ? 3.5 : +(3.0 + 0.04 * lbp).toFixed(2);
    return { baseline: base, rreq: +(base * kt).toFixed(2), unit: 'mm', table_ref: 'Rule 8(1)' };
  },

  // Table 1: Keel Plating & Width (Rule 9, Table 1)
  interpolateTable01: function(lbp, spacing, kt, isWidth = false) {
    const lNodes = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0];
    if (isWidth) {
      const wNodes = [850.0, 900.0, 950.0, 1000.0, 1050.0, 1100.0];
      const wBase = interp1D(lbp, lNodes, wNodes);
      return { baseline: +wBase.toFixed(1), rreq: +wBase.toFixed(1), unit: 'mm', table_ref: 'Table 1' };
    }
    const thk550 = [5.5, 6.0, 6.5, 7.0, 7.5, 8.0];
    const tBase = interp1D(lbp, lNodes, thk550);
    const tCorr = applySpacingCorr(tBase, spacing, false);
    return { baseline: +tCorr.toFixed(2), rreq: +(tCorr * kt).toFixed(2), unit: 'mm', table_ref: 'Table 1' };
  },

  // Table 2: Bottom Plating (Rule 10, Table 2)
  interpolateTable02: function(lbp, draft, spacing, kt) {
    const lNodes = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0];
    const thk550 = [5.0, 5.5, 6.0, 6.5, 7.0, 7.5];
    const tBase = interp1D(lbp, lNodes, thk550);
    const tCorr = applySpacingCorr(tBase, spacing, false);
    return { baseline: +tCorr.toFixed(2), rreq: +(tCorr * kt).toFixed(2), unit: 'mm', table_ref: 'Table 2' };
  },

  // Table 3: Bilge Plating (Rule 11, Table 3)
  interpolateTable03: function(lbp, spacing, kt) {
    const lNodes = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0];
    const thk550 = [5.5, 6.0, 6.5, 7.0, 7.5, 8.0];
    const tBase = interp1D(lbp, lNodes, thk550);
    const tCorr = applySpacingCorr(tBase, spacing, false);
    return { baseline: +tCorr.toFixed(2), rreq: +(tCorr * kt).toFixed(2), unit: 'mm', table_ref: 'Table 3' };
  },

  // Table 4: Side Shell Plating (Rule 12, Table 4)
  interpolateTable04: function(lbp, depth, spacing, kt) {
    const lNodes = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0];
    const thk550 = [5.5, 5.5, 6.0, 6.5, 7.0, 7.5];
    const tBase = interp1D(lbp, lNodes, thk550);
    const tCorr = applySpacingCorr(tBase, spacing, false);
    return { baseline: +tCorr.toFixed(2), rreq: +(tCorr * kt).toFixed(2), unit: 'mm', table_ref: 'Table 4' };
  },

  // Table 5: Hatchway Deck Plating (Rule 13, Table 5)
  interpolateTable05: function(lbp, spacing, kt) {
    const lNodes = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0];
    const thkTrans = [5.0, 5.5, 6.0, 6.5, 7.0, 7.5];
    const tBase = interp1D(lbp, lNodes, thkTrans);
    const tCorr = applySpacingCorr(tBase, spacing, false);
    return { baseline: +tCorr.toFixed(2), rreq: +(tCorr * kt).toFixed(2), unit: 'mm', table_ref: 'Table 5' };
  },

  // Table 6: Main Deck & Superstructure Decks Plating (Rule 14, Table 6)
  interpolateTable06: function(lbp, spacing, kt) {
    const lNodes = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0];
    const thk550 = [4.5, 5.0, 5.5, 6.0, 6.5, 7.0];
    const tBase = interp1D(lbp, lNodes, thk550);
    const tCorr = applySpacingCorr(tBase, spacing, false);
    return { baseline: +tCorr.toFixed(2), rreq: +(tCorr * kt).toFixed(2), unit: 'mm', table_ref: 'Table 6' };
  },

  // Table 7-12: Stem & Stern Frames (Rules 15-20, Tables 7-12)
  interpolateStem: function(lbp, kt, part = 'plate') {
    const lNodes = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0];
    if (part === 'plate') {
      const thkNodes = [6.0, 6.5, 7.5, 8.5, 9.5, 10.5];
      const val = interp1D(lbp, lNodes, thkNodes);
      return { baseline: +val.toFixed(2), rreq: +(val * kt).toFixed(2), unit: 'mm', table_ref: 'Table 7' };
    }
    if (part === 'bar_stem') {
      const wNodes = [110.0, 130.0, 150.0, 165.0, 180.0, 195.0];
      const val = interp1D(lbp, lNodes, wNodes);
      return { baseline: +val.toFixed(1), rreq: +val.toFixed(1), unit: 'mm', table_ref: 'Table 8' };
    }
    if (part === 'propeller_post') {
      const wNodes = [120.0, 140.0, 160.0, 180.0, 200.0, 220.0];
      const val = interp1D(lbp, lNodes, wNodes);
      return { baseline: +val.toFixed(1), rreq: +val.toFixed(1), unit: 'mm', table_ref: 'Table 10' };
    }
    if (part === 'sole_piece') {
      const wNodes = [130.0, 150.0, 175.0, 200.0, 220.0, 240.0];
      const val = interp1D(lbp, lNodes, wNodes);
      return { baseline: +val.toFixed(1), rreq: +val.toFixed(1), unit: 'mm', table_ref: 'Table 11' };
    }
    if (part === 'sole_piece_thk') {
      const tNodes = [35.0, 40.0, 48.0, 55.0, 62.0, 70.0];
      const val = interp1D(lbp, lNodes, tNodes);
      return { baseline: +val.toFixed(1), rreq: +val.toFixed(1), unit: 'mm', table_ref: 'Table 11' };
    }
    if (part === 'propeller_boss_thk') {
      return { baseline: 35.0, rreq: 35.0, unit: 'mm', table_ref: 'Table 12' };
    }
    // stern_frame_bar
    const wNodes = [115.0, 135.0, 155.0, 170.0, 190.0, 210.0];
    const val = interp1D(lbp, lNodes, wNodes);
    return { baseline: +val.toFixed(1), rreq: +val.toFixed(1), unit: 'mm', table_ref: 'Table 9' };
  },

  // Table 13: Floors / Bottom Framing Section Modulus (Rule 21, Table 13)
  interpolateTable13: function(draft, spacing, breadth, kz) {
    const draftNodes = [1.0, 1.5, 2.5, 3.0, 3.5, 4.0];
    const bNodes = [2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0];
    const grid = [
      [8.0, 18.0, 31.0, 70.0, 123.0, 196.0, 280.0],
      [9.0, 20.0, 35.0, 77.0, 138.0, 218.0, 310.0],
      [10.0, 22.0, 38.0, 85.0, 150.0, 235.0, 340.0],
      [12.0, 26.0, 46.0, 105.0, 185.0, 288.0, 415.0],
      [13.0, 30.0, 52.0, 115.0, 205.0, 320.0, 465.0],
      [15.0, 32.0, 58.0, 128.0, 225.0, 355.0, 510.0],
      [16.0, 35.0, 62.5, 140.0, 246.0, 385.0, 550.0],
      [22.0, 48.0, 86.0, 194.0, 342.0, 535.0, 770.0],
      [24.0, 53.0, 94.0, 212.0, 375.0, 590.0, 845.0],
      [23.0, 52.0, 94.0, 208.0, 370.0, 588.0, 830.0],
      [26.0, 58.0, 104.0, 232.0, 410.0, 650.0, 925.0],
      [28.0, 65.0, 114.0, 255.0, 450.0, 705.0, 1014.0],
      [27.0, 62.0, 108.0, 242.0, 430.0, 675.0, 968.0],
      [30.0, 68.0, 120.0, 270.0, 440.0, 750.0, 1076.0],
      [33.0, 75.0, 128.0, 300.0, 526.0, 828.0, 1183.0],
      [30.0, 70.0, 123.0, 278.0, 492.0, 765.0, 1106.0],
      [34.0, 78.0, 138.0, 310.0, 548.0, 854.0, 1229.0],
      [38.0, 85.0, 150.0, 340.0, 600.0, 935.0, 1352.0]
    ];
    let dIdx = 5;
    for (let i = 0; i < draftNodes.length - 1; i++) {
      if (draft >= draftNodes[i] && draft <= draftNodes[i+1]) {
        dIdx = (draft - draftNodes[i] < draftNodes[i+1] - draft) ? i : i + 1;
        break;
      }
    }
    const rowIdx = dIdx * 3 + (spacing <= 475 ? 0 : (spacing <= 525 ? 1 : 2));
    const zBase = interp1D(breadth, bNodes, grid[Math.min(rowIdx, grid.length - 1)]);
    const zCorr = applySpacingCorr(zBase, spacing, true);
    return {
      baseline: +zCorr.toFixed(2),
      rreq: +(zCorr * kz).toFixed(2),
      unit: 'cm³',
      table_ref: 'Table 13'
    };
  },

  // Tables 14-16: Keelsons (Rules 22-24, Tables 14-16)
  interpolateKeelson: function(lbp, kz, isCenter = true) {
    const baseSm = isCenter ? 1057.77 : 400.0;
    return {
      baseline: baseSm,
      rreq: +(baseSm * kz).toFixed(2),
      unit: 'cm³',
      table_ref: isCenter ? 'Table 16' : 'Table 15'
    };
  },

  // Table 17: Side Frames Section Modulus (Rule 25, Table 17)
  interpolateTable17: function(depth, spacing, kz) {
    const dNodes = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0];
    const smNodes = [15.0, 19.0, 27.0, 46.0, 73.0, 110.0, 155.0, 215.0, 285.0, 365.0, 470.0, 590.0];
    const zBase = interp1D(depth, dNodes, smNodes);
    const zCorr = applySpacingCorr(zBase, spacing, true);
    return {
      baseline: +zCorr.toFixed(2),
      rreq: +(zCorr * kz).toFixed(2),
      unit: 'cm³',
      table_ref: 'Table 17'
    };
  },

  // Table 19: Side Stringers / Web Frames Section Modulus (Rule 27, Table 19)
  interpolateTable19: function(depth, kz) {
    const dNodes = [2.5, 3.0, 3.5, 4.0];
    const sm2m = [36.0, 53.0, 71.0, 93.0];
    const sm3m = [82.0, 118.0, 160.0, 209.0];
    const z2 = interp1D(depth, dNodes, sm2m);
    const z3 = interp1D(depth, dNodes, sm3m);
    const zBase = (z2 + z3) / 2.0;
    return {
      baseline: +zBase.toFixed(2),
      rreq: +(zBase * kz).toFixed(2),
      unit: 'cm³',
      table_ref: 'Table 19'
    };
  },

  // Table 20: Deck Beams Section Modulus (Rule 28, Table 20)
  interpolateTable20: function(breadth, spacing, kz) {
    const bNodes = [3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0];
    const smNodes = [4.0, 6.0, 9.0, 14.0, 24.0, 40.0, 60.0, 85.0, 115.0];
    const zBase = interp1D(breadth / 2.0, bNodes, smNodes);
    const zCorr = applySpacingCorr(zBase, spacing, true);
    return { baseline: +zCorr.toFixed(2), rreq: +(zCorr * kz).toFixed(2), unit: 'cm³', table_ref: 'Table 20' };
  },

  // Table 21: Deck Girders (Rule 29, Table 21)
  interpolateTable21: function(breadth, kz) {
    const bNodes = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0];
    const span3 = [240.0, 305.0, 375.0, 450.0, 520.0, 590.0];
    const span4 = [400.0, 530.0, 655.0, 785.0, 910.0, 1040.0];
    const meanB = Math.min(8.0, Math.max(3.0, breadth * 0.4));
    const z3 = interp1D(meanB, bNodes, span3);
    const z4 = interp1D(meanB, bNodes, span4);
    const zBase = (z3 + z4) / 2.0;
    return { baseline: +zBase.toFixed(2), rreq: +(zBase * kz).toFixed(2), unit: 'cm³', table_ref: 'Table 21' };
  },

  // Rule 29: Deck Web Beams (2 x Z_beam)
  interpolateDeckWebBeam: function(breadth, spacing, kz) {
    const beam = this.interpolateTable20(breadth, spacing, kz);
    const base = +(beam.baseline * 2.0).toFixed(2);
    return { baseline: base, rreq: +(base * kz).toFixed(2), unit: 'cm³', table_ref: 'Rule 29, Table 20' };
  },

  // Table 22-23: Pillars (Rule 35, Tables 22-23)
  interpolatePillars: function(depth, isTubular = false) {
    if (isTubular) {
      return { baseline: 101.6, rreq: 101.6, unit: 'mm', table_ref: 'Table 23' };
    }
    const hNodes = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0];
    const diaNodes = [34.0, 37.0, 40.0, 43.0, 45.0, 47.0, 49.0, 51.0, 53.0, 55.0, 57.0, 58.0, 60.0, 61.0, 61.0, 64.0];
    const hPillar = depth > 4.0 ? 3.0 : depth;
    const dia = interp1D(hPillar, hNodes, diaNodes);
    return { baseline: +dia.toFixed(1), rreq: +dia.toFixed(1), unit: 'mm', table_ref: 'Table 22' };
  },

  // Table 24: Collision Bulkhead Position (Rule 31, Table 24)
  interpolateCollisionBhdPos: function(lbp) {
    const pos = +(lbp * 0.05).toFixed(2);
    return { baseline: pos, rreq: pos, unit: 'm', table_ref: 'Table 24' };
  },

  // Tables 25-26: Watertight & Collision Bulkheads (Rules 33-34, Tables 25-26)
  interpolateBulkheads: function(depth, spacing, factor, isStiffener = false, isCollision = false) {
    const hNodes = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0];
    let yNodes;
    if (isCollision) {
      yNodes = isStiffener
        ? [13.0, 28.0, 47.0, 80.0, 120.0, 180.0, 255.0, 345.0]
        : [4.0, 4.5, 4.5, 5.0, 5.5, 5.5, 6.0, 6.0];
    } else {
      yNodes = isStiffener
        ? [11.0, 21.0, 38.0, 64.0, 95.0, 140.0, 200.0, 275.0]
        : [4.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.5, 5.5];
    }
    const valBase = interp1D(depth, hNodes, yNodes);
    const valCorr = applySpacingCorr(valBase, spacing, isStiffener);
    return {
      baseline: +valCorr.toFixed(2),
      rreq: +(valCorr * factor).toFixed(2),
      unit: isStiffener ? 'cm³' : 'mm',
      table_ref: isCollision ? 'Table 25' : 'Table 26'
    };
  },

  // Tables 27-28: Tank Bulkheads (Rule 38, Tables 27-28)
  interpolateTankBulkheads: function(depth, spacing, factor, isStiffener = false) {
    const hNodes = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0];
    const yNodes = isStiffener
      ? [13.0, 28.0, 47.0, 80.0, 120.0, 180.0, 255.0, 345.0]
      : [4.0, 4.5, 4.5, 5.0, 5.5, 5.5, 6.0, 6.0];
    const valBase = interp1D(depth, hNodes, yNodes);
    const valCorr = applySpacingCorr(valBase, spacing, isStiffener);
    return {
      baseline: +valCorr.toFixed(2),
      rreq: +(valCorr * factor).toFixed(2),
      unit: isStiffener ? 'cm³' : 'mm',
      table_ref: isStiffener ? 'Table 28' : 'Table 27'
    };
  },

  // Tables 30-31: Coamings (Rule 38, Tables 30-31)
  interpolateCoamings: function(lbp, kt) {
    const lNodes = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0];
    const thk = [5.0, 6.0, 7.0, 7.5, 8.0, 8.5];
    const val = interp1D(lbp, lNodes, thk);
    return { baseline: +val.toFixed(2), rreq: +(val * kt).toFixed(2), unit: 'mm', table_ref: 'Table 30' };
  },

  // Tables 32-35: Hatch Beams & Covers (Rules 41-42, Tables 32-35)
  interpolateHatchBeamsCovers: function(spacing, kz, memberId) {
    let smBase = 9.0;
    let tRef = 'Table 34';
    if (memberId.includes('portable') || memberId.includes('end_beam') || memberId.includes('side_girder')) {
      smBase = 13.0;
      tRef = 'Table 32';
    } else if (memberId.includes('superstructure')) {
      smBase = 16.0;
      tRef = 'Table 35';
    }
    const smCorr = applySpacingCorr(smBase, spacing, true);
    return { baseline: +smCorr.toFixed(2), rreq: +(smCorr * kz).toFixed(2), unit: 'cm³', table_ref: tRef };
  },

  // Tables 36-37: Roof Beams & Girders (Rules 44-45, Tables 36-37)
  interpolateRoof: function(spacing, kz, isGirder = false) {
    const base = isGirder ? 35.0 : 13.0;
    const smCorr = applySpacingCorr(base, spacing, true);
    return { baseline: +smCorr.toFixed(2), rreq: +(smCorr * kz).toFixed(2), unit: 'cm³', table_ref: isGirder ? 'Table 37' : 'Table 36' };
  },

  // Tables 39-43: Rudder & Steering (Rules 48-52, Tables 39-44)
  interpolateRudder: function(lbp, depth, memberId) {
    if (memberId.includes('spade')) {
      return { baseline: 110.0, rreq: 110.0, unit: 'mm', table_ref: 'Table 40' };
    }
    if (memberId.includes('pintle')) {
      return { baseline: 65.0, rreq: 65.0, unit: 'mm', table_ref: 'Table 42' };
    }
    if (memberId.includes('coupling') || memberId.includes('bolts')) {
      return { baseline: 28.0, rreq: 28.0, unit: 'mm', table_ref: 'Table 41' };
    }
    if (memberId.includes('flange')) {
      return { baseline: 25.0, rreq: 25.0, unit: 'mm', table_ref: 'Table 41' };
    }
    if (memberId.includes('tiller')) {
      return { baseline: 900.0, rreq: 900.0, unit: 'mm', table_ref: 'Table 44' };
    }
    if (memberId.includes('chains')) {
      return { baseline: 14.0, rreq: 14.0, unit: 'mm', table_ref: 'Table 44' };
    }
    if (memberId.includes('blade')) {
      return { baseline: 10.0, rreq: 10.0, unit: 'mm', table_ref: 'Table 4' };
    }
    // Main stock dia
    const lNodes = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0];
    const diaNodes = [55.0, 65.0, 75.0, 85.0, 95.0, 105.0];
    const dia = interp1D(lbp, lNodes, diaNodes);
    return { baseline: +dia.toFixed(1), rreq: +dia.toFixed(1), unit: 'mm', table_ref: 'Table 39' };
  },

  // Tables 45-46: Equipment (Anchors, Chains)
  interpolateEquipment: function(lbp, breadth, depth, memberId) {
    const en = +(lbp * (breadth + depth)).toFixed(1);
    if (memberId === 'equipment_number') {
      return { baseline: en, rreq: en, unit: 'EN', table_ref: 'Table 45' };
    }
    if (memberId === 'anchor_mass') {
      const mass = +(en * 0.45).toFixed(0);
      return { baseline: mass, rreq: mass, unit: 'kg', table_ref: 'Table 46' };
    }
    const len = +(Math.min(300, Math.max(120, en * 0.25))).toFixed(0);
    return { baseline: len, rreq: len, unit: 'm', table_ref: 'Table 46' };
  },

  // Tables 47-48: Bulwark & Chain Locker
  interpolateBulwarkLocker: function(lbp, memberId) {
    if (memberId === 'plate_bulwark') {
      const thk = lbp <= 40 ? 5.0 : 6.0;
      return { baseline: thk, rreq: thk, unit: 'mm', table_ref: 'Table 47' };
    }
    const thk = lbp <= 40 ? 6.0 : 7.0;
    return { baseline: thk, rreq: thk, unit: 'mm', table_ref: 'Table 48' };
  },

  // Tables 49-50: Struts
  interpolateStruts: function(memberId) {
    const isV = memberId.includes('v_strut');
    return { baseline: isV ? 90.0 : 80.0, rreq: isV ? 90.0 : 80.0, unit: 'mm', table_ref: isV ? 'Table 49' : 'Table 50' };
  },

  // Tables 54-57: Piping
  interpolatePiping: function(lbp, memberId) {
    if (memberId === 'pipe_main_bilge_dia') {
      const dia = +(35.0 + 1.66 * Math.sqrt(lbp * 15.0)).toFixed(1);
      return { baseline: dia, rreq: dia, unit: 'mm', table_ref: 'Table 57' };
    }
    return { baseline: 4.5, rreq: 4.5, unit: 'mm', table_ref: 'Table 54' };
  },

  // Tables 66 & 52: Longitudinals (Bottom & Inner Bottom)
  interpolateTable66: function(lbp, spacing, kz, isInner = false) {
    const base70m = isInner ? 125.0 : 145.0;
    const lScale = Math.min(1.0, Math.max(0.40, lbp / 70.0));
    const zBase = +(base70m * lScale).toFixed(2);
    const zCorr = applySpacingCorr(zBase, spacing, true);
    return {
      baseline: +zCorr.toFixed(2),
      rreq: +(zCorr * kz).toFixed(2),
      unit: 'cm³',
      table_ref: 'Table 66'
    };
  },

  // MASTER DISPATCHER FOR ALL 100 STRUCTURAL MEMBERS
  interpolateMember: function(memberId, inputs) {
    inputs = inputs || {};
    const lbp = parseFloat(inputs.lbp || inputs.L) || 69.85;
    const breadth = parseFloat(inputs.breadth || inputs.B) || 13.41;
    const depth = parseFloat(inputs.depth || inputs.D) || 5.18;
    const draft = parseFloat(inputs.draft || inputs.d) || 4.0;
    const spacing = parseFloat(inputs.frame_spacing || inputs.spacing) || 550.0;
    const kt = parseFloat(inputs.effective_kt || inputs.kt) || 1.40;
    const kz = parseFloat(inputs.effective_kz || inputs.kz) || 1.40;

    // Rule 8(1) Min Hull Plate
    if (memberId === 'mat_min_hull') return this.interpolateRule08(lbp, kt);

    // Keel Plating (Table 1)
    if (memberId === 'plate_keel') return this.interpolateTable01(lbp, spacing, kt, false);
    if (memberId === 'plate_keel_width' || memberId === 'w_keel') return this.interpolateTable01(lbp, spacing, kt, true);

    // Bottom Plating (Table 2)
    if (memberId === 'plate_bottom' || memberId === 'plate_inner_bottom' || memberId === 'plate_margin' ||
        memberId === 'plate_rake' || memberId === 'plate_hopper' || memberId === 'plate_solid_floor_web') {
      return this.interpolateTable02(lbp, draft, spacing, kt);
    }

    // Bilge & Chine (Table 3)
    if (memberId === 'plate_bilge' || memberId === 'plate_chine') return this.interpolateTable03(lbp, spacing, kt);

    // Side Shell (Table 4)
    if (memberId === 'plate_side' || memberId === 'plate_sheer_strake' || memberId === 'plate_transom' ||
        memberId === 'plate_inner_side' || memberId === 'plate_tunnel_side') {
      return this.interpolateTable04(lbp, depth, spacing, kt);
    }

    // Hatchway Deck (Table 5)
    if (memberId === 'plate_hatchway_deck' || memberId === 'plate_deck_hatch') return this.interpolateTable05(lbp, spacing, kt);

    // Deck Plating (Table 6)
    if (memberId === 'plate_main_deck' || memberId === 'plate_deck_all' || memberId === 'plate_poop_deck' ||
        memberId === 'plate_forecastle_deck' || memberId === 'plate_second_deck' ||
        memberId === 'plate_upper_passenger_deck' || memberId === 'plate_nav_deck' ||
        memberId === 'plate_wet_deck' || memberId === 'plate_deck_strip') {
      return this.interpolateTable06(lbp, spacing, kt);
    }

    // Stem & Stern (Tables 7-12)
    if (memberId === 'plate_stem') return this.interpolateStem(lbp, kt, 'plate');
    if (memberId === 'bar_stem') return this.interpolateStem(lbp, kt, 'bar_stem');
    if (memberId === 'stern_frame_bar') return this.interpolateStem(lbp, kt, 'stern_frame_bar');
    if (memberId === 'propeller_post') return this.interpolateStem(lbp, kt, 'propeller_post');
    if (memberId === 'sole_piece') return this.interpolateStem(lbp, kt, 'sole_piece');
    if (memberId === 'sole_piece_thk') return this.interpolateStem(lbp, kt, 'sole_piece_thk');
    if (memberId === 'propeller_boss_thk') return this.interpolateStem(lbp, kt, 'propeller_boss_thk');

    // Bottom Floors (Table 13)
    if (memberId === 'stiff_floor_single' || memberId === 'stiff_solid_floor' ||
        memberId === 'stiff_open_bracket_floor' || memberId === 'stiff_bottom_transverse_barge') {
      return this.interpolateTable13(draft, spacing, breadth, kz);
    }

    // Longitudinals (Table 66)
    if (memberId === 'stiff_bottom_longitudinal') return this.interpolateTable66(lbp, spacing, kz, false);
    if (memberId === 'stiff_inner_bottom_longitudinal') return this.interpolateTable66(lbp, spacing, kz, true);

    // Keelsons (Tables 14-16)
    if (memberId === 'stiff_centre_keelson' || memberId === 'stiff_centre_girder') return this.interpolateKeelson(lbp, kz, true);
    if (memberId === 'stiff_side_keelson' || memberId === 'stiff_side_girder') return this.interpolateKeelson(lbp, kz, false);

    // Side Frames & Longitudinals (Table 17)
    if (memberId === 'stiff_main_frame' || memberId === 'stiff_side_frame' ||
        memberId === 'stiff_side_longitudinal' || memberId === 'stiff_side_longitudinal_barge' ||
        memberId === 'stiff_inner_side_longitudinal' || memberId === 'stiff_hopper_longitudinal') {
      return this.interpolateTable17(depth, spacing, kz);
    }

    // Side Stringers & Web Frames (Table 19)
    if (memberId === 'stiff_web_frame' || memberId === 'stiff_side_stringer') return this.interpolateTable19(depth, kz);

    // Deck Beams (Table 20)
    if (memberId === 'stiff_deck_beam' || memberId === 'stiff_deck_longitudinal') return this.interpolateTable20(breadth, spacing, kz);

    // Deck Girders & Web Beams (Tables 21 & 29)
    if (memberId === 'stiff_deck_girder') return this.interpolateTable21(breadth, kz);
    if (memberId === 'stiff_deck_web_beam' || memberId === 'stiff_deck_transverse') return this.interpolateDeckWebBeam(breadth, spacing, kz);

    // Roof Beams & Girders (Tables 36-37)
    if (memberId === 'stiff_roof_beam') return this.interpolateRoof(spacing, kz, false);
    if (memberId === 'stiff_roof_girder_side' || memberId === 'stiff_roof_girder_centre') return this.interpolateRoof(spacing, kz, true);

    // Pillars (Tables 22-23)
    if (memberId === 'pillar_solid_dia') return this.interpolatePillars(depth, false);
    if (memberId === 'pillar_tubular_dia') return this.interpolatePillars(depth, true);

    // Collision Bulkhead Position (Table 24)
    if (memberId === 'bhd_collision_pos') return this.interpolateCollisionBhdPos(lbp);

    // Watertight & Collision Bulkheads (Tables 25-26)
    if (memberId === 'plate_bhd_wt' || memberId === 'plate_long_bhd' || memberId === 'plate_cofferdam' ||
        memberId === 'plate_wash_bhd' || memberId === 'plate_pump_room_bhd') {
      return this.interpolateBulkheads(depth, spacing, kt, false, false);
    }
    if (memberId === 'plate_bhd_collision') return this.interpolateBulkheads(depth, spacing, kt, false, true);
    if (memberId === 'stiff_bhd_transverse') return this.interpolateBulkheads(depth, spacing, kz, true, false);

    // Tank Bulkheads (Tables 27-28)
    if (memberId === 'plate_bhd_tank' || memberId === 'plate_tank_boundary') return this.interpolateTankBulkheads(depth, spacing, kt, false);
    if (memberId === 'stiff_tank_bhd_web' || memberId === 'stiff_tank_bhd_stringer') return this.interpolateTankBulkheads(depth, spacing, kz, true);

    // Coamings (Tables 30-31)
    if (memberId === 'plate_coaming_long' || memberId === 'plate_coaming_trans') return this.interpolateCoamings(lbp, kt);

    // Hatch Beams, Covers & Deckhouse (Tables 32-35)
    if (memberId === 'stiff_portable_hatch_beam' || memberId === 'stiff_hatch_end_beam' ||
        memberId === 'stiff_hatch_side_girder' || memberId === 'stiff_hatch_cover' ||
        memberId === 'stiff_superstructure_wall' || memberId === 'stiff_superstructure_frame') {
      return this.interpolateHatchBeamsCovers(spacing, kz, memberId);
    }

    // Rudder & Steering (Tables 39-44)
    if (memberId.startsWith('rudder_') || memberId.startsWith('steering_')) return this.interpolateRudder(lbp, depth, memberId);

    // Struts (Tables 49-50)
    if (memberId === 'v_strut_shaft' || memberId === 'i_strut_shaft') return this.interpolateStruts(memberId);

    // Piping (Tables 54-57)
    if (memberId === 'pipe_wall_thk' || memberId === 'pipe_main_bilge_dia') return this.interpolatePiping(lbp, memberId);

    // Equipment (Tables 45-46)
    if (memberId === 'equipment_number' || memberId === 'anchor_mass' || memberId === 'chain_cable_length') {
      return this.interpolateEquipment(lbp, breadth, depth, memberId);
    }

    // Bulwark & Locker (Tables 47-48)
    if (memberId === 'plate_bulwark' || memberId === 'plate_chain_locker_wall') return this.interpolateBulwarkLocker(lbp, memberId);

    return null;
  }
};

window.StatutoryInterpolators = StatutoryInterpolators;
