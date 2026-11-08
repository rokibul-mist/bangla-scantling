/**
 * VerificationModal - Interactive dialog to audit and verify cross-deliverable consistency
 * Ensures Application Form, Detail Calculation, and Lightship values are 100% inline.
 */

let lastVerificationReport = null;

async function runVerificationAudit(showModal = true) {
  try {
    const res = await fetch('/api/v1/verification/audit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(window.appState || {})
    });
    const report = await res.json();
    lastVerificationReport = report;

    // Update header badge if present
    updateHeaderVerificationBadge(report);

    if (showModal) {
      openVerificationModal(report);
    }
    return report;
  } catch (err) {
    console.error('Failed to run verification audit:', err);
    if (showModal) {
      alert('Verification audit failed: ' + err.message);
    }
    return null;
  }
}

function updateHeaderVerificationBadge(report) {
  const badge = document.getElementById('header-verification-badge');
  if (!badge) return;

  const isPass = report && report.overall_status === 'PASSED';
  const passCount = report?.summary?.passed_checks || 0;
  const totalCount = report?.summary?.total_checks || 0;

  badge.className = `flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-bold border transition-colors cursor-pointer ${
    isPass 
      ? 'bg-emerald-50 text-emerald-800 border-emerald-300 hover:bg-emerald-100' 
      : 'bg-rose-50 text-rose-800 border-rose-300 hover:bg-rose-100'
  }`;
  badge.innerHTML = `
    <span class="w-2 h-2 rounded-full ${isPass ? 'bg-emerald-600' : 'bg-rose-600'} animate-pulse"></span>
    <span>${isPass ? 'ALL DELIVERABLES INLINE' : 'DISCREPANCY DETECTED'} (${passCount}/${totalCount})</span>
  `;
}

function openVerificationModal(reportData = null) {
  const report = reportData || lastVerificationReport;
  if (!report) {
    runVerificationAudit(true);
    return;
  }

  let modal = document.getElementById('verification-audit-modal');
  if (modal) modal.remove();

  const isPass = report.overall_status === 'PASSED';
  const summary = report.summary || {};
  const cats = report.categories || {};

  modal = document.createElement('div');
  modal.id = 'verification-audit-modal';
  modal.className = 'fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-3 md:p-6';

  modal.innerHTML = `
    <div class="bg-white rounded-lg shadow-2xl flex flex-col w-full max-w-4xl max-h-[90vh] overflow-hidden border border-slate-300 animate-in fade-in zoom-in duration-150">
      
      <!-- Modal Header -->
      <div class="bg-slate-900 text-white px-5 py-3.5 flex items-center justify-between shrink-0 border-b border-slate-800">
        <div class="flex items-center gap-3">
          <div class="w-7 h-7 rounded ${isPass ? 'bg-emerald-600' : 'bg-rose-600'} flex items-center justify-center text-white font-black text-xs shadow-xs">
            VA
          </div>
          <div>
            <div class="text-sm font-bold tracking-tight text-white uppercase flex items-center gap-2">
              Deliverables Verification &amp; Harmonization Audit
              <span class="text-[10px] px-2 py-0.5 rounded font-mono font-bold ${isPass ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'}">
                ${report.overall_status}
              </span>
            </div>
            <div class="text-[10.5px] text-slate-400">
              Cross-validating Application Form, Detail Calculations (20 sheets), and Lightship Synthesis
            </div>
          </div>
        </div>
        <button onclick="document.getElementById('verification-audit-modal').remove()" class="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 text-sm font-bold">
          ✕
        </button>
      </div>

      <!-- Scorecard Banner -->
      <div class="bg-slate-50 border-b border-slate-200 px-5 py-3 shrink-0 flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-6">
          <div>
            <div class="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Total Checks</div>
            <div class="text-lg font-mono font-black text-slate-900">${summary.total_checks || 0}</div>
          </div>
          <div>
            <div class="text-[10px] uppercase font-bold text-emerald-700 tracking-wider">Passed</div>
            <div class="text-lg font-mono font-black text-emerald-700">${summary.passed_checks || 0}</div>
          </div>
          <div>
            <div class="text-[10px] uppercase font-bold text-rose-700 tracking-wider">Failed</div>
            <div class="text-lg font-mono font-black text-rose-700">${summary.failed_checks || 0}</div>
          </div>
          <div>
            <div class="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Pass Rate</div>
            <div class="text-lg font-mono font-black text-blue-700">${summary.pass_rate_pct || 100}%</div>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button onclick="runVerificationAudit(true)" class="px-3 py-1.5 text-xs font-semibold bg-white border border-slate-300 text-slate-700 rounded hover:bg-slate-100 flex items-center gap-1.5 shadow-xs">
            <span>Re-run Audit</span>
          </button>
        </div>
      </div>

      <!-- Verdict Note -->
      <div class="px-5 py-2.5 ${isPass ? 'bg-emerald-50/50 text-emerald-900 border-b border-emerald-100' : 'bg-rose-50/50 text-rose-900 border-b border-rose-100'} text-xs font-medium">
        ${report.verdict}
      </div>

      <!-- Modal Body (Scrollable Category Tabs) -->
      <div class="p-5 flex-1 overflow-y-auto space-y-6">

        <!-- 1. Physical Deliverables Integrity -->
        <div>
          <div class="flex items-center justify-between mb-2 pb-1 border-b border-slate-200">
            <span class="text-xs font-bold text-slate-800 uppercase tracking-wide">1. Generated Physical Deliverables on Disk</span>
            <span class="text-[10.5px] text-slate-500 font-mono">PDF page counts &amp; live Excel formulas</span>
          </div>
          <div class="space-y-1.5">
            ${(cats.deliverables || []).map(c => `
              <div class="p-2 rounded border text-xs flex items-center justify-between gap-3 ${c.status === 'PASS' ? 'bg-white border-slate-200' : 'bg-rose-50 border-rose-300'}">
                <div class="flex items-center gap-2">
                  <span class="w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold ${c.status === 'PASS' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
                    ${c.status === 'PASS' ? '✓' : '✗'}
                  </span>
                  <div>
                    <div class="font-bold text-slate-800">${c.name}</div>
                    <div class="text-[11px] text-slate-500">${c.message}</div>
                  </div>
                </div>
                <div class="text-right font-mono text-[11px] shrink-0">
                  <div class="text-slate-600">Expected: <b>${c.expected}</b></div>
                  <div class="${c.status === 'PASS' ? 'text-emerald-700 font-bold' : 'text-rose-700 font-bold'}">Observed: ${c.actual}</div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- 2. Lightship Synthesis -->
        <div>
          <div class="flex items-center justify-between mb-2 pb-1 border-b border-slate-200">
            <span class="text-xs font-bold text-slate-800 uppercase tracking-wide">2. Lightship Weight Synthesis &amp; Outfitting Ratio</span>
            <span class="text-[10.5px] text-slate-500 font-mono">Net Steel × 1.56 = Total Lightship</span>
          </div>
          <div class="space-y-1.5">
            ${(cats.lightship || []).map(c => `
              <div class="p-2 rounded border text-xs flex items-center justify-between gap-3 ${c.status === 'PASS' ? 'bg-white border-slate-200' : 'bg-rose-50 border-rose-300'}">
                <div class="flex items-center gap-2">
                  <span class="w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold ${c.status === 'PASS' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
                    ${c.status === 'PASS' ? '✓' : '✗'}
                  </span>
                  <div>
                    <div class="font-bold text-slate-800">${c.name}</div>
                    <div class="text-[11px] text-slate-500">${c.message}</div>
                  </div>
                </div>
                <div class="text-right font-mono text-[11px] shrink-0">
                  <span class="text-slate-600">${c.expected}</span> &rarr; 
                  <span class="${c.status === 'PASS' ? 'text-emerald-700 font-bold' : 'text-rose-700 font-bold'}">${c.actual}</span>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- 3. Stiffener Section Moduli Alignment -->
        <div>
          <div class="flex items-center justify-between mb-2 pb-1 border-b border-slate-200">
            <span class="text-xs font-bold text-slate-800 uppercase tracking-wide">3. Stiffeners Section Moduli Alignment (20 Sheets)</span>
            <span class="text-[10.5px] text-slate-500 font-mono">Detail Calc vs Calculation Brain vs Application Form</span>
          </div>
          <div class="max-h-60 overflow-y-auto space-y-1 pr-1 border border-slate-200 rounded p-2 bg-slate-50/50">
            ${(cats.stiffeners || []).map(c => `
              <div class="p-1.5 rounded bg-white border border-slate-200 text-xs flex items-center justify-between gap-2">
                <div class="flex items-center gap-2">
                  <span class="text-[10px] font-bold ${c.status === 'PASS' ? 'text-emerald-700' : 'text-rose-700'}">
                    ${c.status === 'PASS' ? '✓' : '✗'}
                  </span>
                  <span class="font-medium text-slate-800">${c.name}:</span>
                  <span class="text-slate-500 text-[11px]">${c.message}</span>
                </div>
                <div class="font-mono text-[11px] font-semibold text-slate-700 shrink-0">
                  ${c.actual}
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- 5. Hull Longitudinal Strength & Tables 66/67 Matrix -->
        <div>
          <div class="flex items-center justify-between mb-2 pb-1 border-b border-slate-200">
            <span class="text-xs font-bold text-slate-800 uppercase tracking-wide">5. Global Longitudinal Strength &amp; Tables 66 &amp; 67 Compliance</span>
            <span class="text-[10.5px] text-slate-500 font-mono">Rules 209 &amp; 223 (Bending, Shear, Local Members)</span>
          </div>
          <div class="space-y-1.5">
            ${(cats.strength || []).map(c => `
              <div class="p-2 rounded border text-xs flex items-center justify-between gap-3 ${c.status === 'PASS' ? 'bg-white border-slate-200' : 'bg-rose-50 border-rose-300'}">
                <div class="flex items-center gap-2">
                  <span class="w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold ${c.status === 'PASS' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
                    ${c.status === 'PASS' ? '✓' : '✗'}
                  </span>
                  <div>
                    <div class="font-bold text-slate-800">${c.name}</div>
                    <div class="text-[11px] text-slate-500">${c.message}</div>
                  </div>
                </div>
                <div class="text-right font-mono text-[11px] shrink-0 font-bold ${c.status === 'PASS' ? 'text-emerald-700' : 'text-rose-700'}">
                  ${c.actual}
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- 4. Plate Scantling Thicknesses -->
        <div>
          <div class="flex items-center justify-between mb-2 pb-1 border-b border-slate-200">
            <span class="text-xs font-bold text-slate-800 uppercase tracking-wide">4. Plate Scantlings Alignment</span>
            <span class="text-[10.5px] text-slate-500 font-mono">Dashboard Inputs vs Brain vs Lightship Plates</span>
          </div>
          <div class="space-y-1.5">
            ${(cats.plates || []).map(c => `
              <div class="p-2 rounded border text-xs flex items-center justify-between gap-3 ${c.status === 'PASS' ? 'bg-white border-slate-200' : 'bg-rose-50 border-rose-300'}">
                <div class="flex items-center gap-2">
                  <span class="w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold ${c.status === 'PASS' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
                    ${c.status === 'PASS' ? '✓' : '✗'}
                  </span>
                  <div>
                    <div class="font-bold text-slate-800">${c.name}</div>
                    <div class="text-[11px] text-slate-500">${c.message}</div>
                  </div>
                </div>
                <div class="text-right font-mono text-[11px] shrink-0 font-bold ${c.status === 'PASS' ? 'text-emerald-700' : 'text-rose-700'}">
                  ${c.actual} mm
                </div>
              </div>
            `).join('')}
          </div>
        </div>

      </div>

      <!-- Modal Footer -->
      <div class="bg-slate-50 px-5 py-3 border-t border-slate-200 flex items-center justify-between shrink-0">
        <span class="text-[11px] text-slate-500 font-mono">
          Audit Timestamp: ${report.timestamp.replace('T', ' ').slice(0, 19)}
        </span>
        <button onclick="document.getElementById('verification-audit-modal').remove()" class="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded shadow-xs">
          Close Audit
        </button>
      </div>

    </div>
  `;

  document.body.appendChild(modal);
}

// Auto-run lightweight check on load to update header badge
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    runVerificationAudit(false);
  }, 1000);
});
