/**
 * NavalCalcEngine - Client-side Naval Scantling Calculations Engine
 */
class NavalCalcEngine {
  static calcStiffenerSection(bp, tp, hw, tw, bf, tf, profile_type) {
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
  }

  static recalculateAll(state) {
    if (typeof window.recalculateAll === 'function') {
      return window.recalculateAll(state);
    }
    return state;
  }
}

window.navalCalcEngine = NavalCalcEngine;
