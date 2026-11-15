/**
 * ShipLab-BD Hull Lines & Offset Geometry Engine
 * High-performance mathematical hull generation, cubic spline fairing,
 * multi-view 2D naval architectural projection, and 3D wireframe orbit rendering.
 *
 * Prepared for Bangladesh Inland & Coastal Naval Architecture Suite.
 */

class HullLinesEngine {
  constructor() {
    this.defaultUnits = 'm';
  }

  /**
   * Catmull-Rom to Cubic Bezier curve conversion for canvas path smoothing.
   */
  static drawSpline(ctx, points) {
    if (!points || points.length < 2) return;
    if (points.length === 2) {
      ctx.moveTo(points[0].x, points[0].y);
      ctx.lineTo(points[1].x, points[1].y);
      return;
    }

    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 0; i < points.length - 1; i++) {
      const p0 = i > 0 ? points[i - 1] : points[i];
      const p1 = points[i];
      const p2 = points[i + 1];
      const p3 = i < points.length - 2 ? points[i + 2] : p2;

      const cp1x = p1.x + (p2.x - p0.x) / 6;
      const cp1y = p1.y + (p2.y - p0.y) / 6;
      const cp2x = p2.x - (p3.x - p1.x) / 6;
      const cp2y = p2.y - (p3.y - p1.y) / 6;

      ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, p2.x, p2.y);
    }
  }

  /**
   * Generate default parametric design grid and hull offsets.
   */
  static generateParametricHull(lbp, beam, depth, draft, cb = 0.75, cm = 0.98, preset = 'general_cargo') {
    const halfB = beam / 2.0;
    const numStations = 11; // 0 to 10
    const stations = [];
    for (let i = 0; i < numStations; i++) {
      const x = (i / 10.0) * lbp;
      const frac = i / 10.0;
      let label = `St ${i}`;
      if (i === 0) label = 'AP (St 0)';
      else if (i === 5) label = 'Mid (St 5)';
      else if (i === 10) label = 'FP (St 10)';
      stations.push({
        id: `st_${i}`,
        station_num: i,
        x_pos: x,
        fraction_lbp: frac,
        label: label
      });
    }

    // Waterlines
    const numWls = 8;
    const waterlines = [];
    const maxZ = depth * 1.15;
    for (let j = 0; j <= numWls; j++) {
      const z = (j / numWls) * maxZ;
      const isDwl = Math.abs(z - draft) < (maxZ / (numWls * 2));
      waterlines.push({
        id: `wl_${j}`,
        z_height: z,
        label: isDwl ? `DWL (${z.toFixed(2)}m)` : `WL ${z.toFixed(2)}m`,
        is_dwl: isDwl
      });
    }

    // Buttocks
    const numButts = 4;
    const buttocks = [];
    for (let k = 1; k <= numButts; k++) {
      const y = (k / (numButts + 1)) * halfB;
      buttocks.push({
        id: `butt_${k}`,
        y_offset: y,
        label: `Buttock ${y.toFixed(2)}m`
      });
    }

    // Generate Half-breadths
    const halfBreadths = {};
    for (const st of stations) {
      halfBreadths[st.id] = {};
      const xi = st.fraction_lbp; // 0.0 at AP to 1.0 at FP

      // Longitudinal section area coefficient / waterline fullness
      let longFactor;
      if (preset === 'sand_barge') {
        if (xi < 0.15) longFactor = 0.2 + 0.8 * (xi / 0.15);
        else if (xi > 0.85) longFactor = 0.2 + 0.8 * ((1.0 - xi) / 0.15);
        else longFactor = 1.0;
      } else if (preset === 'passenger_launch') {
        longFactor = Math.sin(xi * Math.PI) ** 0.85;
      } else if (preset === 'oil_tanker') {
        if (xi < 0.20) longFactor = (xi / 0.20) ** 0.55;
        else if (xi > 0.80) longFactor = ((1.0 - xi) / 0.20) ** 0.60;
        else longFactor = 1.0;
      } else {
        // General Cargo
        if (xi < 0.25) longFactor = (xi / 0.25) ** 0.65;
        else if (xi > 0.75) longFactor = ((1.0 - xi) / 0.25) ** 0.70;
        else longFactor = 1.0;
      }

      for (const wl of waterlines) {
        const zi = wl.z_height;
        const zNorm = Math.min(1.0, zi / draft);

        let vertFactor;
        if (preset === 'sand_barge') {
          vertFactor = zNorm > 0.15 ? 1.0 : (zNorm / 0.15);
        } else if (preset === 'passenger_launch') {
          vertFactor = Math.sqrt(Math.max(0, zNorm));
        } else {
          // Rounded bilge
          vertFactor = Math.min(1.0, (zNorm ** (1.0 / 4.0)));
        }

        // Taper above draft towards main deck
        let flare = 1.0;
        if (zi > draft) {
          const excess = (zi - draft) / (depth - draft || 1.0);
          flare = 1.0 + (xi > 0.6 ? 0.08 * excess : -0.02 * excess);
        }

        let hb = halfB * longFactor * vertFactor * flare;
        if (zi <= 0.01) hb = 0.0; // Baseline centerline
        if (st.fraction_lbp < 0.02 && zi < draft * 0.3) hb = Math.min(hb, 0.15);
        halfBreadths[st.id][wl.id] = Math.max(0.0, Math.min(halfB * 1.05, hb));
      }
    }

    // Deck & Sheer Profile
    const deckProfile = stations.map(st => {
      const xi = st.fraction_lbp;
      // Parabolic sheer: forward sheer = 1.5% LBP, aft sheer = 0.75% LBP
      const aftSheer = 0.0075 * lbp * ((0.5 - Math.min(0.5, xi)) / 0.5) ** 2;
      const fwdSheer = 0.0150 * lbp * ((Math.max(0.5, xi) - 0.5) / 0.5) ** 2;
      const totalSheer = depth + (xi < 0.5 ? aftSheer : fwdSheer);
      return {
        station_id: st.id,
        x_pos: st.x_pos,
        deck_height: totalSheer,
        deck_half_breadth: halfB * (1.0 - (xi > 0.7 ? 0.15 * ((xi - 0.7) / 0.3) ** 2 : 0)),
        sheer_height: totalSheer
      };
    });

    const data = {
      vessel_name: 'Parametric Hull',
      preset_type: preset,
      reference_frame: {
        origin: 'ap',
        baseline: 'molded',
        symmetry: 'symmetric',
        units: 'm',
        scale_factor: 1.0
      },
      design_grid: {
        stations,
        waterlines,
        buttocks,
        lbp,
        beam,
        depth,
        draft
      },
      half_breadths: halfBreadths,
      deck_profile: deckProfile
    };

    data.hydrostatics = this.calculateHydrostatics(data);
    return data;
  }

  /**
   * Simpson's & Trapezoidal integration for hydrostatics.
   */
  static calculateHydrostatics(data) {
    const grid = data.design_grid;
    const draft = grid.draft;
    const stations = [...grid.stations].sort((a, b) => a.x_pos - b.x_pos);
    const waterlines = grid.waterlines.filter(w => w.z_height <= draft + 0.01).sort((a, b) => a.z_height - b.z_height);

    if (stations.length < 3 || waterlines.length < 2) {
      return { draft_m: draft };
    }

    // Integrate each waterline along stations
    const xVals = stations.map(s => s.x_pos);
    const awpList = [];

    for (const wl of waterlines) {
      const yVals = stations.map(s => data.half_breadths[s.id]?.[wl.id] || 0.0);
      let awp = 0.0;
      let momX = 0.0;
      for (let i = 0; i < xVals.length - 1; i++) {
        const dx = xVals[i + 1] - xVals[i];
        const yAvg = (yVals[i] + yVals[i + 1]) * 0.5;
        const xAvg = (xVals[i] + xVals[i + 1]) * 0.5;
        awp += 2.0 * yAvg * dx;
        momX += 2.0 * yAvg * xAvg * dx;
      }
      const lcf = awp > 0.01 ? (momX / awp) : (grid.lbp / 2.0);
      awpList.push({ z: wl.z_height, awp, lcf });
    }

    // Integrate Awp vertically along Z
    let volume = 0.0;
    let momZ = 0.0;
    let momVolX = 0.0;
    for (let j = 0; j < awpList.length - 1; j++) {
      const dz = awpList[j + 1].z - awpList[j].z;
      const aAvg = (awpList[j].awp + awpList[j + 1].awp) * 0.5;
      const zAvg = (awpList[j].z + awpList[j + 1].z) * 0.5;
      const lcfAvg = (awpList[j].lcf + awpList[j + 1].lcf) * 0.5;
      volume += aAvg * dz;
      momZ += aAvg * zAvg * dz;
      momVolX += aAvg * lcfAvg * dz;
    }
    volume = Math.max(0.1, volume);

    const displacement = volume * 1.000; // Fresh/inland water
    const lcb = momVolX / volume;
    const kb = momZ / volume;

    // Transverse inertia IT at draft
    const desWl = waterlines[waterlines.length - 1];
    const desYVals = stations.map(s => data.half_breadths[s.id]?.[desWl.id] || 0.0);
    let itTrans = 0.0;
    for (let i = 0; i < xVals.length - 1; i++) {
      const dx = xVals[i + 1] - xVals[i];
      const yCubAvg = ((desYVals[i] ** 3) + (desYVals[i + 1] ** 3)) * 0.5;
      itTrans += (2.0 / 3.0) * yCubAvg * dx;
    }
    const bmt = itTrans / volume;
    const kmt = kb + bmt;

    const designAwp = awpList[awpList.length - 1]?.awp || 0.0;
    const lcf = awpList[awpList.length - 1]?.lcf || (grid.lbp / 2.0);

    const cb = volume / (grid.lbp * grid.beam * draft);
    const cwp = designAwp / (grid.lbp * grid.beam);
    const midIdx = Math.floor(stations.length / 2);
    const midSt = stations[midIdx];
    const midWls = waterlines.map(w => data.half_breadths[midSt.id]?.[w.id] || 0.0);
    let midArea = 0.0;
    for (let j = 0; j < waterlines.length - 1; j++) {
      const dz = waterlines[j + 1].z_height - waterlines[j].z_height;
      const yAvg = (midWls[j] + midWls[j + 1]) * 0.5;
      midArea += 2.0 * yAvg * dz;
    }
    const cm = Math.max(0.70, Math.min(0.995, midArea / (grid.beam * draft)));
    const cp = cb / cm;
    const wettedSurface = grid.lbp * (1.7 * draft + cb * grid.beam);

    return {
      draft_m: Math.round(draft * 1000) / 1000,
      volume_m3: Math.round(volume * 100) / 100,
      displacement_tonnes: Math.round(displacement * 100) / 100,
      waterplane_area_m2: Math.round(designAwp * 100) / 100,
      wetted_surface_m2: Math.round(wettedSurface * 100) / 100,
      block_coefficient_cb: Math.round(cb * 10000) / 10000,
      prismatic_coefficient_cp: Math.round(cp * 10000) / 10000,
      midship_coefficient_cm: Math.round(cm * 10000) / 10000,
      waterplane_coefficient_cwp: Math.round(cwp * 10000) / 10000,
      lcb_from_ap_m: Math.round(lcb * 1000) / 1000,
      lcb_percent_lbp: Math.round((lcb / grid.lbp) * 10000) / 100,
      lcf_from_ap_m: Math.round(lcf * 1000) / 1000,
      kmt_m: Math.round(kmt * 1000) / 1000
    };
  }

  /**
   * Render Body Plan (Transverse sections).
   * Left: Afterbody (AP to Midship). Right: Forebody (Midship to FP).
   */
  static renderBodyPlan(canvas, data, options = {}) {
    if (!canvas || !data) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const grid = data.design_grid;
    const halfB = grid.beam / 2.0;
    const maxZ = Math.max(...grid.waterlines.map(wl => wl.z_height), grid.depth * 1.15);

    // Padding & View Bounds
    const pad = 40;
    const cx = w / 2.0;
    const scaleX = (w - pad * 2) / (grid.beam * 1.2);
    const scaleY = (h - pad * 2) / (maxZ * 1.1);
    const scale = Math.min(scaleX, scaleY);
    const baseLineY = h - pad;

    // Background & Border
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, w, h);

    // Grid Construction Lines
    ctx.lineWidth = 0.5;
    ctx.strokeStyle = '#E2E8F0';
    ctx.font = '9px system-ui, sans-serif';
    ctx.fillStyle = '#64748B';

    // Waterlines
    for (const wl of grid.waterlines) {
      const y = baseLineY - wl.z_height * scale;
      ctx.beginPath();
      ctx.moveTo(cx - halfB * scale * 1.05, y);
      ctx.lineTo(cx + halfB * scale * 1.05, y);
      ctx.stroke();

      if (wl.is_dwl) {
        ctx.fillStyle = '#2563EB';
        ctx.fillText(`DWL ${wl.z_height.toFixed(2)}m`, cx + halfB * scale * 1.07, y + 3);
        ctx.fillStyle = '#64748B';
      } else {
        ctx.fillText(`${wl.z_height.toFixed(1)}m`, cx + halfB * scale * 1.07, y + 3);
      }
    }

    // Buttocks (Vertical)
    for (const butt of grid.buttocks) {
      const xRight = cx + butt.y_offset * scale;
      const xLeft = cx - butt.y_offset * scale;
      ctx.beginPath();
      ctx.moveTo(xRight, baseLineY);
      ctx.lineTo(xRight, baseLineY - maxZ * scale);
      ctx.moveTo(xLeft, baseLineY);
      ctx.lineTo(xLeft, baseLineY - maxZ * scale);
      ctx.stroke();

      ctx.fillText(`${butt.y_offset.toFixed(1)}m`, xRight - 10, baseLineY + 12);
      ctx.fillText(`${butt.y_offset.toFixed(1)}m`, xLeft - 10, baseLineY + 12);
    }

    // Centerline & Baseline
    ctx.lineWidth = 1.2;
    ctx.strokeStyle = '#334155';
    // Centerline (dashed)
    ctx.setLineDash([4, 3]);
    ctx.beginPath();
    ctx.moveTo(cx, baseLineY + 10);
    ctx.lineTo(cx, baseLineY - maxZ * scale - 10);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillText('CL', cx - 6, baseLineY - maxZ * scale - 14);

    // Baseline (solid)
    ctx.beginPath();
    ctx.moveTo(cx - halfB * scale * 1.1, baseLineY);
    ctx.lineTo(cx + halfB * scale * 1.1, baseLineY);
    ctx.stroke();
    ctx.fillText('BL (BASELINE)', cx - halfB * scale * 1.1, baseLineY + 12);

    // Section Labels: Forebody (Starboard) & Afterbody (Port)
    ctx.font = 'bold 10px system-ui, sans-serif';
    ctx.fillStyle = '#1E293B';
    ctx.fillText('PORT / AFTERBODY (AFT OF MIDSHIP)', pad, pad - 12);
    ctx.fillText('STARBOARD / FOREBODY (FWD OF MIDSHIP)', cx + 20, pad - 12);

    // Draw Stations Curves
    const stations = [...grid.stations].sort((a, b) => a.x_pos - b.x_pos);
    const midIdx = Math.floor(stations.length / 2);

    stations.forEach((st, idx) => {
      const isForebody = idx >= midIdx;
      const pts = [];

      for (const wl of grid.waterlines) {
        const hb = data.half_breadths[st.id]?.[wl.id] || 0.0;
        const xCanvas = isForebody ? (cx + hb * scale) : (cx - hb * scale);
        const yCanvas = baseLineY - wl.z_height * scale;
        pts.push({ x: xCanvas, y: yCanvas });
      }

      ctx.beginPath();
      if (idx === midIdx) {
        // Midship section on BOTH sides
        ctx.strokeStyle = '#0284C7';
        ctx.lineWidth = 2.0;
        this.drawSpline(ctx, pts);
        ctx.stroke();

        // Draw mirrored midship on afterbody
        const mirrorPts = pts.map(p => ({ x: cx - (p.x - cx), y: p.y }));
        ctx.beginPath();
        this.drawSpline(ctx, mirrorPts);
        ctx.stroke();
      } else {
        ctx.strokeStyle = isForebody ? '#0F766E' : '#7C3AED';
        ctx.lineWidth = 1.2;
        this.drawSpline(ctx, pts);
        ctx.stroke();
      }

      // Label at deck/top
      const topPt = pts[pts.length - 1];
      if (topPt) {
        ctx.fillStyle = isForebody ? '#0F766E' : '#7C3AED';
        ctx.font = '9px system-ui, sans-serif';
        ctx.fillText(st.station_num.toString(), topPt.x - 3, topPt.y - 4);
      }
    });
  }

  /**
   * Render Sheer Plan (Profile View).
   * Stations along X, Waterlines along Z, Keel at bottom, Sheer at top.
   */
  static renderSheerPlan(canvas, data, options = {}) {
    if (!canvas || !data) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const grid = data.design_grid;
    const lbp = grid.lbp;
    const maxZ = Math.max(...grid.waterlines.map(wl => wl.z_height), grid.depth * 1.25);

    const pad = 45;
    const scaleX = (w - pad * 2) / (lbp * 1.05);
    const scaleZ = (h - pad * 2) / (maxZ * 1.15);
    const scale = Math.min(scaleX, scaleZ * 2.0); // Allow aspect ratio fit
    const baseLineY = h - pad;
    const originX = pad;

    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, w, h);

    // Title & View
    ctx.font = 'bold 10px system-ui, sans-serif';
    ctx.fillStyle = '#1E293B';
    ctx.fillText('SHEER PLAN (PROFILE VIEW - ELEVATION)', pad, pad - 12);

    // Waterlines (Horizontal Grid)
    ctx.lineWidth = 0.5;
    ctx.strokeStyle = '#E2E8F0';
    ctx.font = '9px system-ui, sans-serif';
    ctx.fillStyle = '#64748B';

    for (const wl of grid.waterlines) {
      const y = baseLineY - wl.z_height * scaleZ;
      ctx.beginPath();
      ctx.moveTo(originX, y);
      ctx.lineTo(originX + lbp * scaleX, y);
      ctx.stroke();

      if (wl.is_dwl) {
        ctx.fillStyle = '#2563EB';
        ctx.fillText(`DWL ${wl.z_height.toFixed(2)}m`, originX + lbp * scaleX + 6, y + 3);
        ctx.fillStyle = '#64748B';
      } else {
        ctx.fillText(`${wl.z_height.toFixed(1)}m`, originX + lbp * scaleX + 6, y + 3);
      }
    }

    // Stations (Vertical Grid)
    for (const st of grid.stations) {
      const x = originX + st.x_pos * scaleX;
      ctx.beginPath();
      ctx.moveTo(x, baseLineY);
      ctx.lineTo(x, baseLineY - maxZ * scaleZ);
      ctx.stroke();
      ctx.fillText(st.label || `St ${st.station_num}`, x - 10, baseLineY + 14);
    }

    // Baseline & Keel
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = '#1E293B';
    ctx.beginPath();
    ctx.moveTo(originX, baseLineY);
    ctx.lineTo(originX + lbp * scaleX, baseLineY);
    ctx.stroke();
    ctx.fillText('BL (BASELINE / KEEL)', originX, baseLineY + 28);

    // Deck Sheer Line
    if (data.deck_profile && data.deck_profile.length > 0) {
      const deckPts = data.deck_profile.map(dp => ({
        x: originX + dp.x_pos * scaleX,
        y: baseLineY - dp.deck_height * scaleZ
      }));
      ctx.lineWidth = 1.8;
      ctx.strokeStyle = '#059669';
      ctx.beginPath();
      this.drawSpline(ctx, deckPts);
      ctx.stroke();
      ctx.fillStyle = '#059669';
      ctx.fillText('DECK AT SIDE (SHEER LINE)', deckPts[Math.floor(deckPts.length / 2)].x - 40, deckPts[Math.floor(deckPts.length / 2)].y - 8);
    }

    // Buttock Profile Curves
    grid.buttocks.forEach((butt, bIdx) => {
      const buttPts = [];
      const yTarget = butt.y_offset;

      for (const st of grid.stations) {
        // Interpolate Z height where half-breadth equals buttock Y
        const wls = grid.waterlines;
        let matchZ = null;
        for (let j = 0; j < wls.length - 1; j++) {
          const hb1 = data.half_breadths[st.id]?.[wls[j].id] || 0.0;
          const hb2 = data.half_breadths[st.id]?.[wls[j + 1].id] || 0.0;
          if ((hb1 <= yTarget && hb2 >= yTarget) || (hb1 >= yTarget && hb2 <= yTarget)) {
            const frac = Math.abs(hb2 - hb1) > 0.001 ? (yTarget - hb1) / (hb2 - hb1) : 0;
            matchZ = wls[j].z_height + frac * (wls[j + 1].z_height - wls[j].z_height);
            break;
          }
        }
        if (matchZ !== null) {
          buttPts.push({
            x: originX + st.x_pos * scaleX,
            y: baseLineY - matchZ * scaleZ
          });
        }
      }

      if (buttPts.length >= 2) {
        ctx.lineWidth = 1.0;
        ctx.strokeStyle = bIdx % 2 === 0 ? '#D97706' : '#DC2626';
        ctx.beginPath();
        this.drawSpline(ctx, buttPts);
        ctx.stroke();
        ctx.fillStyle = ctx.strokeStyle;
        ctx.fillText(butt.label, buttPts[buttPts.length - 1].x - 30, buttPts[buttPts.length - 1].y - 4);
      }
    });
  }

  /**
   * Render Half-Breadth Plan (Waterlines Plan).
   * Stations along X, Half-Breadths along Y from Centerline.
   */
  static renderHalfBreadthPlan(canvas, data, options = {}) {
    if (!canvas || !data) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const grid = data.design_grid;
    const lbp = grid.lbp;
    const halfB = grid.beam / 2.0;

    const pad = 45;
    const scaleX = (w - pad * 2) / (lbp * 1.05);
    const scaleY = (h - pad * 2) / (halfB * 1.25);
    const clY = h - pad;
    const originX = pad;

    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, w, h);

    // Title & View
    ctx.font = 'bold 10px system-ui, sans-serif';
    ctx.fillStyle = '#1E293B';
    ctx.fillText('HALF-BREADTH PLAN (WATERLINES - PLAN VIEW)', pad, pad - 12);

    // Station Transverse Grid Lines
    ctx.lineWidth = 0.5;
    ctx.strokeStyle = '#E2E8F0';
    ctx.font = '9px system-ui, sans-serif';
    ctx.fillStyle = '#64748B';

    for (const st of grid.stations) {
      const x = originX + st.x_pos * scaleX;
      ctx.beginPath();
      ctx.moveTo(x, clY);
      ctx.lineTo(x, clY - halfB * scaleY * 1.15);
      ctx.stroke();
      ctx.fillText(st.label || `St ${st.station_num}`, x - 8, clY + 14);
    }

    // Buttock Longitudinal Guide Lines
    for (const butt of grid.buttocks) {
      const y = clY - butt.y_offset * scaleY;
      ctx.beginPath();
      ctx.moveTo(originX, y);
      ctx.lineTo(originX + lbp * scaleX, y);
      ctx.stroke();
      ctx.fillText(`${butt.y_offset.toFixed(1)}m Butt`, originX + lbp * scaleX + 6, y + 3);
    }

    // Centerline (CL)
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = '#1E293B';
    ctx.beginPath();
    ctx.moveTo(originX, clY);
    ctx.lineTo(originX + lbp * scaleX, clY);
    ctx.stroke();
    ctx.fillText('CL (CENTERLINE)', originX, clY + 28);

    // Draw Waterlines Curves
    grid.waterlines.forEach((wl, idx) => {
      const pts = grid.stations.map(st => {
        const hb = data.half_breadths[st.id]?.[wl.id] || 0.0;
        return {
          x: originX + st.x_pos * scaleX,
          y: clY - hb * scaleY
        };
      });

      ctx.beginPath();
      if (wl.is_dwl) {
        ctx.strokeStyle = '#2563EB';
        ctx.lineWidth = 2.0;
        this.drawSpline(ctx, pts);
        ctx.stroke();
        ctx.fillStyle = '#2563EB';
        ctx.font = 'bold 9px system-ui, sans-serif';
        ctx.fillText(`DWL (${wl.z_height.toFixed(2)}m)`, pts[Math.floor(pts.length / 2)].x, pts[Math.floor(pts.length / 2)].y - 4);
      } else {
        ctx.strokeStyle = idx % 2 === 0 ? '#475569' : '#0284C7';
        ctx.lineWidth = 1.0;
        this.drawSpline(ctx, pts);
        ctx.stroke();
        ctx.fillStyle = '#64748B';
        ctx.font = '9px system-ui, sans-serif';
        ctx.fillText(`${wl.z_height.toFixed(1)}m`, pts[pts.length - 1].x - 12, pts[pts.length - 1].y - 3);
      }
    });

    // Deck at Side Contour
    if (data.deck_profile && data.deck_profile.length > 0) {
      const deckPts = data.deck_profile.map(dp => ({
        x: originX + dp.x_pos * scaleX,
        y: clY - dp.deck_half_breadth * scaleY
      }));
      ctx.lineWidth = 1.6;
      ctx.strokeStyle = '#059669';
      ctx.beginPath();
      this.drawSpline(ctx, deckPts);
      ctx.stroke();
      ctx.fillStyle = '#059669';
      ctx.fillText('DECK LINE', deckPts[Math.floor(deckPts.length / 2)].x, deckPts[Math.floor(deckPts.length / 2)].y - 6);
    }
  }

  /**
   * 3D Wireframe Orbit Perspective Projection on HTML5 Canvas.
   */
  static render3DOrbit(canvas, data, camera = { yaw: 0.65, pitch: 0.35, zoom: 1.0, panX: 0, panY: 0 }) {
    if (!canvas || !data) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const grid = data.design_grid;
    const lbp = grid.lbp;
    const beam = grid.beam;
    const depth = grid.depth;

    ctx.fillStyle = '#F8FAFC';
    ctx.fillRect(0, 0, w, h);

    // 3D Rotation Matrix
    const cy = Math.cos(camera.yaw);
    const sy = Math.sin(camera.yaw);
    const cp = Math.cos(camera.pitch);
    const sp = Math.sin(camera.pitch);

    // Origin centered at midship, baseline
    const cx = w / 2.0 + camera.panX;
    const cyScreen = h / 2.0 + camera.panY;
    const baseScale = (Math.min(w, h) * 0.75 / lbp) * camera.zoom;

    const project = (x, y, z) => {
      // Center at midship
      const xc = x - lbp / 2.0;
      const yc = y;
      const zc = z - depth * 0.4;

      // Rotate Yaw around Z
      const x1 = xc * cy - yc * sy;
      const y1 = xc * sy + yc * cy;
      const z1 = zc;

      // Rotate Pitch around X
      const x2 = x1;
      const y2 = y1 * cp - z1 * sp;
      const z2 = y1 * sp + z1 * cp;

      // Isometric / Slight perspective
      const dist = 3.0 * lbp;
      const factor = dist / (dist + y2);
      const px = cx + x2 * baseScale * factor;
      const py = cyScreen - z2 * baseScale * factor;
      return { x: px, y: py, depth: y2 };
    };

    // Draw Reference Axes
    const o3d = project(0, 0, 0);
    const x3d = project(lbp * 0.2, 0, 0);
    const y3d = project(0, beam * 0.4, 0);
    const z3d = project(0, 0, depth * 0.8);

    ctx.lineWidth = 1.5;
    // X Axis (Longitudinal)
    ctx.strokeStyle = '#DC2626';
    ctx.beginPath(); ctx.moveTo(o3d.x, o3d.y); ctx.lineTo(x3d.x, x3d.y); ctx.stroke();
    // Y Axis (Transverse)
    ctx.strokeStyle = '#16A34A';
    ctx.beginPath(); ctx.moveTo(o3d.x, o3d.y); ctx.lineTo(y3d.x, y3d.y); ctx.stroke();
    // Z Axis (Vertical)
    ctx.strokeStyle = '#2563EB';
    ctx.beginPath(); ctx.moveTo(o3d.x, o3d.y); ctx.lineTo(z3d.x, z3d.y); ctx.stroke();

    ctx.font = '9px system-ui, sans-serif';
    ctx.fillStyle = '#64748B';
    ctx.fillText('X (LBP)', x3d.x + 4, x3d.y);
    ctx.fillText('Y (Beam)', y3d.x + 4, y3d.y);
    ctx.fillText('Z (Depth)', z3d.x + 4, z3d.y);

    // Draw Transverse Stations (Both Port & Starboard)
    ctx.lineWidth = 0.8;
    for (const st of grid.stations) {
      const isMid = Math.abs(st.x_pos - lbp / 2.0) < 0.1;
      ctx.strokeStyle = isMid ? '#0284C7' : '#94A3B8';
      ctx.lineWidth = isMid ? 1.5 : 0.8;

      // Starboard half
      const stbPts = grid.waterlines.map(wl => {
        const hb = data.half_breadths[st.id]?.[wl.id] || 0.0;
        return project(st.x_pos, hb, wl.z_height);
      });
      // Port half
      const portPts = grid.waterlines.map(wl => {
        const hb = data.half_breadths[st.id]?.[wl.id] || 0.0;
        return project(st.x_pos, -hb, wl.z_height);
      });

      ctx.beginPath();
      for (let i = 0; i < stbPts.length; i++) {
        if (i === 0) ctx.moveTo(stbPts[i].x, stbPts[i].y);
        else ctx.lineTo(stbPts[i].x, stbPts[i].y);
      }
      ctx.stroke();

      ctx.beginPath();
      for (let i = 0; i < portPts.length; i++) {
        if (i === 0) ctx.moveTo(portPts[i].x, portPts[i].y);
        else ctx.lineTo(portPts[i].x, portPts[i].y);
      }
      ctx.stroke();
    }

    // Draw Longitudinal Waterlines Rings
    for (const wl of grid.waterlines) {
      const isDwl = wl.is_dwl;
      ctx.lineWidth = isDwl ? 1.8 : 0.6;
      ctx.strokeStyle = isDwl ? '#2563EB' : '#CBD5E1';

      const ringPts = [];
      // Starboard side AP -> FP
      for (let i = 0; i < grid.stations.length; i++) {
        const st = grid.stations[i];
        const hb = data.half_breadths[st.id]?.[wl.id] || 0.0;
        ringPts.push(project(st.x_pos, hb, wl.z_height));
      }
      // Port side FP -> AP
      for (let i = grid.stations.length - 1; i >= 0; i--) {
        const st = grid.stations[i];
        const hb = data.half_breadths[st.id]?.[wl.id] || 0.0;
        ringPts.push(project(st.x_pos, -hb, wl.z_height));
      }

      ctx.beginPath();
      for (let k = 0; k < ringPts.length; k++) {
        if (k === 0) ctx.moveTo(ringPts[k].x, ringPts[k].y);
        else ctx.lineTo(ringPts[k].x, ringPts[k].y);
      }
      ctx.closePath();
      ctx.stroke();
    }

    // Draw Keel Line along X
    ctx.lineWidth = 1.8;
    ctx.strokeStyle = '#1E293B';
    ctx.beginPath();
    const keelStart = project(0, 0, 0);
    const keelEnd = project(lbp, 0, 0);
    ctx.moveTo(keelStart.x, keelStart.y);
    ctx.lineTo(keelEnd.x, keelEnd.y);
    ctx.stroke();

    // 3D View Overlay Info
    ctx.fillStyle = '#475569';
    ctx.font = '9px system-ui, sans-serif';
    ctx.fillText('3D Hull Wireframe (Drag to Rotate, Scroll to Zoom, Right-Drag to Pan)', 10, h - 10);
  }
}

window.HullLinesEngine = HullLinesEngine;
