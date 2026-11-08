with open('app/static/js/views/StrengthView.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Normalize CRLF to LF
content = content.replace('\r\n', '\n')

# 1. Remove the static modal from renderStrengthView
old_modal_marker = '''    <!-- Strength PDF Modal -->
    <div id="strength-pdf-modal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 hidden flex items-center justify-center p-4">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-5xl h-[90vh] flex flex-col overflow-hidden">
        <div class="p-3 bg-slate-900 text-white flex justify-between items-center">
          <div class="flex items-center gap-2">
            <span class="font-bold text-sm">HULL STRENGTH &amp; MIDSHIP MODULUS BOOKLET (RULES 209 &amp; 223)</span>
            <span class="text-[11px] bg-blue-600 px-2 py-0.5 rounded text-white font-semibold">4 Pages Official Booklet</span>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="downloadStrengthPdf()" class="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-xs font-semibold rounded text-white flex items-center gap-1 cursor-pointer">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              Download
            </button>
            <button onclick="closeStrengthPdfModal()" class="text-slate-400 hover:text-white text-lg px-2 cursor-pointer">&times;</button>
          </div>
        </div>
        <div class="flex-1 bg-slate-100 p-1 relative">
          <div id="strength-pdf-loading" class="absolute inset-0 flex items-center justify-center bg-white/80 z-10">
            <div class="flex items-center gap-2 text-sm text-slate-700">
              <svg class="animate-spin h-5 w-5 text-blue-600" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
              <span>Generating official 4-page Hull Strength PDF deliverable...</span>
            </div>
          </div>
          <iframe id="strength-pdf-iframe" class="w-full h-full border-0 rounded bg-white"></iframe>
        </div>
      </div>
    </div>'''

if old_modal_marker in content:
    content = content.replace(old_modal_marker, '')
    print('Successfully removed static modal marker')
else:
    print('Warning: static modal marker not found')

# 2. Replace openStrengthPdfModal implementation
old_fn_start = 'async function openStrengthPdfModal() {'
idx = content.find(old_fn_start)
if idx != -1:
    content = content[:idx] + '''async function openStrengthPdfModal() {
  let modal = document.getElementById('strength-pdf-modal');

  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'strength-pdf-modal';
    modal.className = 'fixed inset-0 z-50 bg-slate-900/75 backdrop-blur-xs flex items-center justify-center p-3 md:p-6';
    modal.innerHTML = `
      <div class="bg-white rounded-lg shadow-2xl flex flex-col w-full h-full max-w-6xl max-h-[94vh] overflow-hidden border border-slate-300">
        <!-- Modal Header -->
        <div class="bg-slate-900 text-white px-4 py-2.5 flex items-center justify-between shrink-0 border-b border-slate-800">
          <div class="flex items-center gap-2.5">
            <div class="w-6 h-6 rounded bg-indigo-600 flex items-center justify-center text-white font-black text-xs">
              PDF
            </div>
            <div>
              <div class="text-xs font-bold tracking-tight text-white flex items-center gap-2">
                <span>HULL STRENGTH &amp; MIDSHIP MODULUS BOOKLET (RULES 209 &amp; 223)</span>
                <span class="px-1.5 py-0.2 bg-indigo-700/80 text-[10px] font-mono rounded">4 Pages Official Booklet</span>
              </div>
              <div class="text-[10px] text-slate-400">Rules 209 &amp; 223 • Longitudinal Bending Moments • Midship Section Modulus • Schedule Tables 66 &amp; 67 Compliance</div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <!-- Open in New Tab -->
            <button 
              id="btn-strength-pdf-new-tab" 
              onclick="openStrengthPdfInNewTab()" 
              class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-medium transition flex items-center gap-1 cursor-pointer"
              title="Open full PDF in separate browser tab"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
              <span>New Tab</span>
            </button>

            <!-- Download PDF Button -->
            <button 
              id="btn-strength-pdf-download" 
              onclick="downloadStrengthPdf()" 
              class="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-bold transition flex items-center gap-1 shadow-xs cursor-pointer"
              title="Download Hull Strength PDF booklet to computer"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              <span>Download PDF</span>
            </button>

            <!-- Close Modal Button -->
            <button 
              onclick="closeStrengthPdfModal()" 
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
          <div id="strength-pdf-loading" class="absolute inset-0 bg-white/90 backdrop-blur-2xs flex flex-col items-center justify-center z-10 space-y-3">
            <div class="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
            <div class="text-xs font-bold text-slate-800 tracking-wide">Generating Statutory Hull Strength PDF Booklet...</div>
            <div class="text-[11px] text-slate-500">Compiling Rules 209/223 Calculations, Midship Neutral Axis, and Tables 66/67 Matrix</div>
          </div>

          <!-- PDF IFrame -->
          <iframe id="strength-pdf-iframe" class="w-full h-full border-0" title="Hull Strength PDF Booklet"></iframe>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    // Escape key listener
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        closeStrengthPdfModal();
      }
    });
  } else {
    modal.classList.remove('hidden');
  }

  const loading = document.getElementById('strength-pdf-loading');
  const iframe = document.getElementById('strength-pdf-iframe');
  if (loading) loading.classList.remove('hidden');

  try {
    const payload = (typeof appState !== 'undefined') ? appState : {};
    const res = await fetch('/api/v1/strength/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const blob = await res.blob();
    if (activeStrengthPdfBlobUrl) {
      URL.revokeObjectURL(activeStrengthPdfBlobUrl);
    }
    activeStrengthPdfBlobUrl = URL.createObjectURL(blob);
    iframe.src = activeStrengthPdfBlobUrl;
    iframe.onload = () => {
      if (loading) loading.classList.add('hidden');
    };
  } catch (err) {
    console.error('Failed to generate strength PDF:', err);
    if (loading) loading.innerHTML = `<span class="text-red-600 font-bold p-4">Failed to generate PDF: ${err.message}</span>`;
  }
}

function closeStrengthPdfModal() {
  const modal = document.getElementById('strength-pdf-modal');
  if (modal) modal.classList.add('hidden');
}

function openStrengthPdfInNewTab() {
  if (activeStrengthPdfBlobUrl) {
    window.open(activeStrengthPdfBlobUrl, '_blank');
  } else {
    openStrengthPdfModal().then(() => {
      if (activeStrengthPdfBlobUrl) window.open(activeStrengthPdfBlobUrl, '_blank');
    });
  }
}

async function downloadStrengthPdf() {
  try {
    const payload = (typeof appState !== 'undefined') ? appState : {};
    const res = await fetch('/api/v1/strength/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const vName = (payload.dashboard_inputs && payload.dashboard_inputs.vessel_name) 
      ? payload.dashboard_inputs.vessel_name.replace(/\\s+/g, '_') 
      : 'Vessel';
    const a = document.createElement('a');
    a.href = url;
    a.download = `${vName}_Hull_Strength_Booklet.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  } catch (err) {
    console.error('Failed to download Strength PDF:', err);
    alert('Failed to download Strength PDF: ' + err.message);
  }
}

window.renderStrength = renderStrengthView;
window.toggleMidshipElement = toggleMidshipElement;
window.toggleAllMidshipElements = toggleAllMidshipElements;
window.resetMidshipElements = resetMidshipElements;
window.openStrengthPdfModal = openStrengthPdfModal;
window.closeStrengthPdfModal = closeStrengthPdfModal;
window.openStrengthPdfInNewTab = openStrengthPdfInNewTab;
window.downloadStrengthPdf = downloadStrengthPdf;
'''

with open('app/static/js/views/StrengthView.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated StrengthView.js successfully.')
