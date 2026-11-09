/**
 * Client-Side Statutory Rules & Empirical Tables Interpolation Engine
 * Mirrors the statutory table algorithms from Bangladesh Inland Shipping Rules 2001 & SRO 308
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
    // Find draft index
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

  // Table 1: Keel Plating (Rule 9, Table 1)
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

  // Table 6: Main Deck Plating (Rule 14, Table 6)
  interpolateTable06: function(lbp, spacing, kt) {
    const lNodes = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0];
    const thk550 = [4.5, 5.0, 5.5, 6.0, 6.5, 7.0];
    const tBase = interp1D(lbp, lNodes, thk550);
    const tCorr = applySpacingCorr(tBase, spacing, false);
    return { baseline: +tCorr.toFixed(2), rreq: +(tCorr * kt).toFixed(2), unit: 'mm', table_ref: 'Table 6' };
  },

  // Table 20: Deck Beams Section Modulus (Rule 28, Table 20)
  interpolateTable20: function(breadth, spacing, kz) {
    const bNodes = [3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0];
    const smNodes = [4.0, 6.0, 9.0, 14.0, 24.0, 40.0, 60.0, 85.0, 115.0];
    const zBase = interp1D(breadth / 2.0, bNodes, smNodes); // half-breadth span for supported beams
    const zCorr = applySpacingCorr(zBase, spacing, true);
    return { baseline: +zCorr.toFixed(2), rreq: +(zCorr * kz).toFixed(2), unit: 'cm³', table_ref: 'Table 20' };
  },

  // Master Member Dispatcher
  interpolateMember: function(memberId, inputs) {
    const lbp = parseFloat(inputs.lbp) || 69.85;
    const breadth = parseFloat(inputs.breadth) || 13.41;
    const depth = parseFloat(inputs.depth) || 5.18;
    const draft = parseFloat(inputs.draft) || 4.0;
    const spacing = parseFloat(inputs.frame_spacing) || 550.0;
    const kt = parseFloat(inputs.effective_kt) || 1.40;
    const kz = parseFloat(inputs.effective_kz) || 1.40;

    if (memberId === 'stiff_main_frame' || memberId === 'stiff_side_frame') {
      return this.interpolateTable17(depth, spacing, kz);
    }
    if (memberId === 'stiff_web_frame' || memberId === 'stiff_side_stringer') {
      return this.interpolateTable19(depth, kz);
    }
    if (memberId === 'stiff_floor_single' || memberId === 'stiff_solid_floor') {
      return this.interpolateTable13(draft, spacing, breadth, kz);
    }
    if (memberId === 'plate_keel') {
      return this.interpolateTable01(lbp, spacing, kt, false);
    }
    if (memberId === 'plate_keel_width' || memberId === 'w_keel') {
      return this.interpolateTable01(lbp, spacing, kt, true);
    }
    if (memberId === 'plate_bottom' || memberId === 'plate_inner_bottom' || memberId === 'plate_margin' || memberId === 'plate_rake') {
      return this.interpolateTable02(lbp, draft, spacing, kt);
    }
    if (memberId === 'plate_bilge' || memberId === 'plate_chine') {
      return this.interpolateTable03(lbp, spacing, kt);
    }
    if (memberId === 'plate_side' || memberId === 'plate_sheer_strake' || memberId === 'plate_transom' || memberId === 'plate_inner_side') {
      return this.interpolateTable04(lbp, depth, spacing, kt);
    }
    if (memberId === 'plate_deck_all' || memberId === 'plate_main_deck' || memberId === 'plate_poop_deck' || memberId === 'plate_forecastle_deck') {
      return this.interpolateTable06(lbp, spacing, kt);
    }
    if (memberId === 'stiff_deck_beam' || memberId === 'stiff_deck_longitudinal') {
      return this.interpolateTable20(breadth, spacing, kz);
    }
    return null;
  }
};

window.StatutoryInterpolators = StatutoryInterpolators;
