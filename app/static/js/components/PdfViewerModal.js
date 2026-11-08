/**
 * PdfViewerModal - High-Fidelity Engineering Booklet PDF Preview & Export Modal
 * Renders Cover Page, Executive Dashboard, and All Detail Calculation Sheets with Vector Figures
 */

let activePdfBlobUrl = null;

async function openDetailCalcPdfModal() {
  let modal = document.getElementById('pdf-viewer-modal');
  
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'pdf-viewer-modal';
    modal.className = 'fixed inset-0 z-50 bg-slate-900/75 backdrop-blur-xs flex items-center justify-center p-3 md:p-6';
    modal.innerHTML = `
      <div class="bg-white rounded-lg shadow-2xl flex flex-col w-full h-full max-w-6xl max-h-[94vh] overflow-hidden border border-slate-300">
        <!-- Modal Header -->
        <div class="bg-slate-900 text-white px-4 py-2.5 flex items-center justify-between shrink-0 border-b border-slate-800">
          <div class="flex items-center gap-2.5">
            <div class="w-6 h-6 rounded bg-rose-600 flex items-center justify-center text-white font-black text-xs">
              PDF
            </div>
            <div>
              <div class="text-xs font-bold tracking-tight text-white flex items-center gap-2">
                <span>STATUTORY DETAIL CALCULATION BOOKLET</span>
                <span class="px-1.5 py-0.2 bg-blue-600/80 text-[10px] font-mono rounded">ReportLab Vector Engine</span>
              </div>
              <div class="text-[10px] text-slate-400">Cover Page • Executive Dashboard • All Stiffener Sheets with Vector Figures</div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <!-- Open in New Tab -->
            <button 
              id="btn-pdf-new-tab" 
              onclick="openPdfInNewTab()" 
              class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-medium transition flex items-center gap-1 cursor-pointer"
              title="Open full PDF in separate browser tab"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
              <span>New Tab</span>
            </button>

            <!-- Download PDF Button -->
            <button 
              id="btn-pdf-download" 
              onclick="downloadDetailCalcPdf()" 
              class="px-2.5 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-bold transition flex items-center gap-1 shadow-xs cursor-pointer"
              title="Download PDF booklet to computer"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              <span>Download PDF</span>
            </button>

            <!-- Close Modal Button -->
            <button 
              onclick="closeDetailCalcPdfModal()" 
              class="ml-2 w-7 h-7 flex items-center justify-center rounded text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer text-base"
              title="Close Preview (Esc)"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Modal Body: IFrame and Loading Screen -->
        <div class="relative flex-1 bg-slate-100 overflow-hidden flex flex-col">
          <!-- Loading Overlay -->
          <div id="pdf-loading-overlay" class="absolute inset-0 bg-white/90 backdrop-blur-2xs flex flex-col items-center justify-center z-10 space-y-3">
            <div class="w-10 h-10 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            <div class="text-xs font-bold text-slate-800 tracking-wide">Generating Live PDF Engineering Booklet...</div>
            <div class="text-[11px] text-slate-500">Compiling Cover Page, Executive Dashboard, and All Vector Cross-Sections</div>
          </div>

          <!-- PDF IFrame -->
          <iframe id="pdf-preview-iframe" class="w-full h-full border-0" title="Detail Calculation PDF Booklet"></iframe>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    // Escape key listener
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        closeDetailCalcPdfModal();
      }
    });
  } else {
    modal.classList.remove('hidden');
  }

  const loader = document.getElementById('pdf-loading-overlay');
  const iframe = document.getElementById('pdf-preview-iframe');
  if (loader) loader.classList.remove('hidden');

  try {
    // Send live appState snapshot so that unsaved user edits are 100% evaluated
    const payload = (typeof appState !== 'undefined') ? appState : {};
    const res = await fetch('/api/pdf/detail-calculation/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`PDF generation failed: ${res.statusText}`);

    const blob = await res.blob();
    if (activePdfBlobUrl) {
      URL.revokeObjectURL(activePdfBlobUrl);
    }
    activePdfBlobUrl = URL.createObjectURL(blob);

    if (iframe) {
      iframe.src = activePdfBlobUrl;
      iframe.onload = () => {
        if (loader) loader.classList.add('hidden');
      };
    }
  } catch (err) {
    console.error('Failed to preview Detail Calculation PDF:', err);
    if (loader) {
      loader.innerHTML = `
        <div class="text-rose-600 font-bold text-sm mb-1">Failed to generate PDF</div>
        <div class="text-xs text-slate-600 mb-3">${err.message || 'Error communicating with PDF engine.'}</div>
        <button onclick="closeDetailCalcPdfModal()" class="px-3 py-1 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded text-xs font-semibold">
          Close
        </button>
      `;
    }
  }
}

function closeDetailCalcPdfModal() {
  const modal = document.getElementById('pdf-viewer-modal');
  if (modal) {
    modal.classList.add('hidden');
  }
}

function openPdfInNewTab() {
  if (activePdfBlobUrl) {
    window.open(activePdfBlobUrl, '_blank');
  } else {
    window.open('/api/pdf/detail-calculation/preview', '_blank');
  }
}

function downloadDetailCalcPdf() {
  if (activePdfBlobUrl) {
    const vName = (appState && appState.dashboard_inputs && appState.dashboard_inputs.vessel_name) 
      ? appState.dashboard_inputs.vessel_name.replace(/\s+/g, '_') 
      : 'Vessel';
    const a = document.createElement('a');
    a.href = activePdfBlobUrl;
    a.download = `${vName}_Detail_Calculation_Booklet.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } else {
    window.location.href = '/api/pdf/detail-calculation/export';
  }
}

window.openDetailCalcPdfModal = openDetailCalcPdfModal;
window.closeDetailCalcPdfModal = closeDetailCalcPdfModal;
window.openPdfInNewTab = openPdfInNewTab;
window.downloadDetailCalcPdf = downloadDetailCalcPdf;
