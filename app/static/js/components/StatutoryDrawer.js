/**
 * StatutoryDrawer.js
 * Persistent slide-over right drawer for Bangladesh Inland Laws, Construction Rules 2001,
 * and ISO 1976 Statutory Knowledge Base.
 * 
 * Features:
 * 1. Instant FTS5 full-text & rule-number search with snippet highlighting.
 * 2. 13-Book Table of Contents navigation tree.
 * 3. Dual-View Mode: Clean Digital Reader & Synchronized Original PDF Viewer.
 * 4. One-Click Department of Shipping (DOS) formal statutory citation copy.
 * 5. Expandable / Dockable responsive layout.
 */

class StatutoryDrawer {
  constructor() {
    this.isOpen = false;
    this.isExpanded = false;
    this.activeTab = 'reader'; // 'reader' | 'pdf'
    this.activeBookId = null; // null for All Books
    this.activeRuleId = null;
    this.activePageNo = 1;
    this.books = [];
    this.searchResults = [];
    this.debounceTimer = null;

    this.init();
  }

  init() {
    this.createDrawerDOM();
    this.attachEventListeners();
    this.loadBooks();
  }

  createDrawerDOM() {
    if (document.getElementById('statutory-drawer-root')) return;

    const root = document.createElement('div');
    root.id = 'statutory-drawer-root';
    root.innerHTML = `
      <!-- Backdrop -->
      <div 
        id="statutory-drawer-backdrop" 
        onclick="window.statutoryDrawer.close()"
        class="fixed inset-0 bg-slate-900/50 backdrop-blur-2xs z-50 transition-opacity opacity-0 pointer-events-none duration-200"
      ></div>

      <!-- Drawer Main Slide-Over Panel -->
      <aside 
        id="statutory-drawer-panel"
        class="fixed top-0 right-0 h-full w-[460px] md:w-[620px] lg:w-[720px] max-w-full bg-white shadow-2xl z-50 flex flex-col transform translate-x-full transition-transform duration-300 ease-in-out border-l border-slate-300"
      >
        <!-- Header -->
        <div class="bg-slate-900 text-white px-4 py-3 shrink-0 flex items-center justify-between border-b border-slate-800 select-none">
          <div class="flex items-center gap-2.5">
            <div class="w-7 h-7 rounded bg-amber-600 flex items-center justify-center text-white font-black text-xs shadow-xs">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
            </div>
            <div>
              <div class="text-xs font-bold tracking-tight text-white flex items-center gap-2">
                <span>STATUTORY CODE &amp; RULES OF BANGLADESH</span>
                <span class="px-1.5 py-0.2 bg-amber-500/80 text-[10px] font-mono rounded text-slate-950 font-bold">ISO 1976 &amp; SRO 308</span>
              </div>
              <div class="text-[10px] text-slate-400">13 Statutory Volumes · 887 Rules &amp; Tables · DOS Approved Reference Suite</div>
            </div>
          </div>

          <div class="flex items-center gap-1.5">
            <!-- Expand / Dock Width Button -->
            <button 
              onclick="window.statutoryDrawer.toggleExpand()" 
              class="w-7 h-7 flex items-center justify-center rounded text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer"
              title="Toggle Wide Screen"
            >
              <svg id="icon-expand" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/></svg>
            </button>

            <!-- Close Drawer Button -->
            <button 
              onclick="window.statutoryDrawer.close()" 
              class="w-7 h-7 flex items-center justify-center rounded text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer text-base"
              title="Close Drawer (Esc)"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Search Bar Toolbar -->
        <div class="p-2.5 bg-slate-50 border-b border-slate-200 shrink-0 space-y-2">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            </div>
            <input 
              type="text" 
              id="statutory-search-input"
              placeholder="Search Rule # (e.g. Rule 209, Table 66), keyword, member (bulkhead, freeboard, GM)..." 
              class="w-full pl-8 pr-8 py-1.5 bg-white border border-slate-300 rounded text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1.5 focus:ring-amber-500 focus:border-amber-500 shadow-2xs font-medium"
              oninput="window.statutoryDrawer.handleSearchInput(this.value)"
            />
            <button 
              id="btn-statutory-search-clear"
              onclick="window.statutoryDrawer.clearSearch()"
              class="absolute inset-y-0 right-0 pr-2.5 flex items-center text-slate-400 hover:text-slate-600 hidden cursor-pointer text-xs"
              title="Clear search"
            >
              ✕
            </button>
          </div>

          <!-- Book Filter Category Horizontal Pills -->
          <div class="flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px] no-scrollbar select-none" id="statutory-book-pills">
            <button 
              onclick="window.statutoryDrawer.setBookFilter(null)" 
              class="px-2 py-0.5 rounded-full font-semibold shrink-0 transition bg-slate-900 text-white pill-btn"
              data-book-id="all"
            >
              All Books (887)
            </button>
          </div>
        </div>

        <!-- Dual View Navigation Tabs -->
        <div class="bg-white border-b border-slate-200 px-3 flex items-center justify-between shrink-0">
          <div class="flex gap-4">
            <button 
              id="tab-btn-reader"
              onclick="window.statutoryDrawer.switchTab('reader')" 
              class="py-2 text-xs font-bold border-b-2 border-amber-600 text-amber-700 flex items-center gap-1.5 cursor-pointer"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
              <span>Digital Text &amp; Citations</span>
            </button>
            <button 
              id="tab-btn-pdf"
              onclick="window.statutoryDrawer.switchTab('pdf')" 
              class="py-2 text-xs font-semibold border-b-2 border-transparent text-slate-500 hover:text-slate-800 flex items-center gap-1.5 cursor-pointer"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
              <span>Synchronized Original PDF (Gazette)</span>
            </button>
          </div>

          <div id="statutory-page-indicator" class="text-[10px] text-slate-500 font-mono">
            Page <b id="statutory-active-page-label">1</b> of 201
          </div>
        </div>

        <!-- Main Content Body -->
        <div class="flex-1 overflow-hidden relative bg-slate-50 flex flex-col">
          <!-- Pane 1: Digital Reader / Search Results / TOC -->
          <div id="pane-statutory-reader" class="flex-1 overflow-y-auto p-3 md:p-4 space-y-3">
            <div id="statutory-dynamic-content">
              <!-- Dynamically rendered by renderContent() -->
            </div>
          </div>

          <!-- Pane 2: Synchronized PDF Viewer Iframe -->
          <div id="pane-statutory-pdf" class="flex-1 hidden bg-slate-200 relative">
            <iframe 
              id="statutory-pdf-iframe" 
              class="w-full h-full border-0" 
              src="/api/v1/library/pdf#page=1"
              title="Official Bangladesh Inland Vessel Rules PDF"
            ></iframe>
          </div>
        </div>

        <!-- Footer / Copy Citation Toast Bar -->
        <div id="statutory-citation-toast" class="bg-emerald-800 text-white text-[11px] font-medium px-3 py-1.5 flex items-center justify-between shrink-0 hidden animate-fade-in">
          <span class="flex items-center gap-1.5">
            <svg class="w-3.5 h-3.5 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            <span id="toast-citation-msg">Formal statutory citation copied to clipboard!</span>
          </span>
          <span class="text-[9px] text-emerald-200">Ready to paste into booklet or DOS submission</span>
        </div>
      </aside>
    `;

    document.body.appendChild(root);
  }

  attachEventListeners() {
    // Keyboard shortcut Alt + R to toggle drawer
    document.addEventListener('keydown', (e) => {
      if (e.altKey && (e.key === 'r' || e.key === 'R')) {
        e.preventDefault();
        this.toggle();
      } else if (e.key === 'Escape' && this.isOpen) {
        this.close();
      }
    });
  }

  open() {
    const backdrop = document.getElementById('statutory-drawer-backdrop');
    const panel = document.getElementById('statutory-drawer-panel');

    if (backdrop && panel) {
      backdrop.classList.remove('pointer-events-none', 'opacity-0');
      backdrop.classList.add('opacity-100');
      panel.classList.remove('translate-x-full');
      this.isOpen = true;

      // Focus search input
      setTimeout(() => {
        const input = document.getElementById('statutory-search-input');
        if (input && !this.activeRuleId) input.focus();
      }, 250);
    }
  }

  close() {
    const backdrop = document.getElementById('statutory-drawer-backdrop');
    const panel = document.getElementById('statutory-drawer-panel');

    if (backdrop && panel) {
      backdrop.classList.remove('opacity-100');
      backdrop.classList.add('opacity-0', 'pointer-events-none');
      panel.classList.add('translate-x-full');
      this.isOpen = false;
    }
  }

  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  toggleExpand() {
    const panel = document.getElementById('statutory-drawer-panel');
    if (!panel) return;

    this.isExpanded = !this.isExpanded;
    if (this.isExpanded) {
      panel.classList.remove('w-[460px]', 'md:w-[620px]', 'lg:w-[720px]');
      panel.classList.add('w-full', 'md:w-[940px]', 'lg:w-[1100px]');
    } else {
      panel.classList.remove('w-full', 'md:w-[940px]', 'lg:w-[1100px]');
      panel.classList.add('w-[460px]', 'md:w-[620px]', 'lg:w-[720px]');
    }
  }

  switchTab(tab) {
    this.activeTab = tab;
    const btnReader = document.getElementById('tab-btn-reader');
    const btnPdf = document.getElementById('tab-btn-pdf');
    const paneReader = document.getElementById('pane-statutory-reader');
    const panePdf = document.getElementById('pane-statutory-pdf');
    const iframe = document.getElementById('statutory-pdf-iframe');

    if (tab === 'reader') {
      btnReader.className = "py-2 text-xs font-bold border-b-2 border-amber-600 text-amber-700 flex items-center gap-1.5 cursor-pointer";
      btnPdf.className = "py-2 text-xs font-semibold border-b-2 border-transparent text-slate-500 hover:text-slate-800 flex items-center gap-1.5 cursor-pointer";
      paneReader.classList.remove('hidden');
      panePdf.classList.add('hidden');
    } else {
      btnReader.className = "py-2 text-xs font-semibold border-b-2 border-transparent text-slate-500 hover:text-slate-800 flex items-center gap-1.5 cursor-pointer";
      btnPdf.className = "py-2 text-xs font-bold border-b-2 border-amber-600 text-amber-700 flex items-center gap-1.5 cursor-pointer";
      paneReader.classList.add('hidden');
      panePdf.classList.remove('hidden');

      // Sync iframe page
      if (iframe && this.activePageNo) {
        iframe.src = `/api/v1/library/pdf#page=${this.activePageNo}`;
      }
    }
  }

  async loadBooks() {
    try {
      const res = await fetch('/api/v1/library/books');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      this.books = data.books || [];
      this.renderBookPills();
      this.renderContent();
    } catch (err) {
      console.error('[StatutoryDrawer] Failed to load books:', err);
    }
  }

  renderBookPills() {
    const container = document.getElementById('statutory-book-pills');
    if (!container) return;

    let html = `
      <button 
        onclick="window.statutoryDrawer.setBookFilter(null)" 
        class="px-2 py-0.5 rounded-full font-semibold shrink-0 transition ${this.activeBookId === null ? 'bg-slate-900 text-white' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'}"
      >
        All Books (887)
      </button>
    `;

    this.books.forEach(b => {
      const isSelected = this.activeBookId === b.id;
      html += `
        <button 
          onclick="window.statutoryDrawer.setBookFilter(${b.id})" 
          class="px-2 py-0.5 rounded-full font-semibold shrink-0 transition text-nowrap ${isSelected ? 'bg-amber-600 text-white' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'}"
          title="${b.title} (${b.rules_count} items)"
        >
          ${b.id}. ${b.short_title} (${b.rules_count})
        </button>
      `;
    });

    container.innerHTML = html;
  }

  setBookFilter(bookId) {
    this.activeBookId = bookId;
    this.renderBookPills();
    const query = document.getElementById('statutory-search-input')?.value || '';
    if (query.trim()) {
      this.performSearch(query);
    } else {
      this.activeRuleId = null;
      this.renderContent();
    }
  }

  handleSearchInput(value) {
    const clearBtn = document.getElementById('btn-statutory-search-clear');
    if (clearBtn) {
      clearBtn.classList.toggle('hidden', !value.trim());
    }

    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      this.performSearch(value);
    }, 200);
  }

  clearSearch() {
    const input = document.getElementById('statutory-search-input');
    if (input) input.value = '';
    const clearBtn = document.getElementById('btn-statutory-search-clear');
    if (clearBtn) clearBtn.classList.add('hidden');
    this.searchResults = [];
    this.activeRuleId = null;
    this.renderContent();
  }

  async performSearch(query) {
    const cleanQ = query.trim();
    if (!cleanQ) {
      this.searchResults = [];
      this.renderContent();
      return;
    }

    try {
      let url = `/api/v1/library/search?q=${encodeURIComponent(cleanQ)}`;
      if (this.activeBookId) {
        url += `&book_id=${this.activeBookId}`;
      }

      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      this.searchResults = data.results || [];
      this.renderSearchResults(cleanQ);
    } catch (err) {
      console.error('[StatutoryDrawer] Search error:', err);
    }
  }

  renderSearchResults(query) {
    const container = document.getElementById('statutory-dynamic-content');
    if (!container) return;

    if (!this.searchResults.length) {
      container.innerHTML = `
        <div class="text-center py-12 px-4 bg-white rounded-lg border border-slate-200">
          <div class="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400 mb-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </div>
          <div class="text-xs font-bold text-slate-800">No matching statutory clauses found</div>
          <div class="text-[11px] text-slate-500 mt-1">Try searching by Rule number (e.g. <b>Rule 209</b>, <b>Table 66</b>), keywords (<b>keel</b>, <b>bulkhead</b>, <b>stability</b>), or reset book filters.</div>
        </div>
      `;
      return;
    }

    let html = `
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs font-bold text-slate-800">Search Results for "${htmlEscape(query)}"</span>
        <span class="text-[10px] font-mono bg-amber-100 text-amber-900 px-1.5 py-0.5 rounded font-bold">${this.searchResults.length} Clauses</span>
      </div>
      <div class="space-y-2.5">
    `;

    this.searchResults.forEach(r => {
      html += `
        <div class="bg-white p-3 rounded-lg border border-slate-200 hover:border-amber-400 transition shadow-2xs hover:shadow-xs group">
          <div class="flex items-start justify-between gap-2">
            <div>
              <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono">${r.rule_no}</span>
              <span class="text-xs font-bold text-slate-900 ml-1 group-hover:text-amber-700 transition cursor-pointer" onclick="window.statutoryDrawer.openRule(${r.id})">
                ${r.rule_title}
              </span>
            </div>
            <span class="text-[9.5px] text-slate-400 shrink-0 font-mono">Page ${r.page_no}</span>
          </div>

          <div class="text-[11.5px] text-slate-600 mt-1.5 leading-relaxed line-clamp-3">
            ${r.snippet}
          </div>

          <div class="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <span class="text-[10px] text-amber-800 font-medium">${r.book_short_title}</span>
            <div class="flex items-center gap-1.5">
              <button 
                onclick="window.statutoryDrawer.copyCitation(${r.id})" 
                class="px-2 py-0.8 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[10px] font-semibold transition flex items-center gap-1 cursor-pointer"
                title="Copy formal Department of Shipping Citation"
              >
                <svg class="w-3 h-3 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
                <span>Copy Citation</span>
              </button>
              <button 
                onclick="window.statutoryDrawer.openRule(${r.id})" 
                class="px-2 py-0.8 bg-amber-600 hover:bg-amber-700 text-white rounded text-[10px] font-bold transition flex items-center gap-1 cursor-pointer"
              >
                <span>Read Full Rule</span>
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
              </button>
            </div>
          </div>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;
  }

  renderContent() {
    if (this.searchResults.length) {
      this.renderSearchResults(document.getElementById('statutory-search-input')?.value || '');
      return;
    }

    if (this.activeRuleId) {
      this.loadAndRenderActiveRule(this.activeRuleId);
      return;
    }

    // Default: Render Table of Contents Browser
    this.renderTocBrowser();
  }

  async renderTocBrowser() {
    const container = document.getElementById('statutory-dynamic-content');
    if (!container) return;

    let targetBooks = this.books;
    if (this.activeBookId) {
      targetBooks = this.books.filter(b => b.id === this.activeBookId);
    }

    let html = `
      <div class="mb-3">
        <div class="text-xs font-bold text-slate-900">STATUTORY VOLUMES &amp; TABLE OF CONTENTS</div>
        <div class="text-[11px] text-slate-500">Select any volume to expand chapters, read scantlings clauses, or view official gazette pages.</div>
      </div>
      <div class="space-y-2.5">
    `;

    targetBooks.forEach(b => {
      html += `
        <div class="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-2xs">
          <div class="p-3 bg-slate-50/80 border-b border-slate-200 flex items-start justify-between gap-2">
            <div>
              <div class="flex items-center gap-1.5">
                <span class="w-4 h-4 rounded-full bg-slate-900 text-white flex items-center justify-center font-mono text-[9px] font-bold">${b.id}</span>
                <span class="text-xs font-bold text-slate-900">${b.title}</span>
              </div>
              <div class="text-[11px] text-slate-600 mt-1 leading-relaxed">${b.description}</div>
            </div>
            <span class="text-[10px] bg-amber-100 text-amber-900 font-mono font-bold px-1.5 py-0.5 rounded shrink-0">
              ${b.rules_count} Clauses
            </span>
          </div>

          <div class="p-2 flex items-center justify-between text-[11px] bg-white">
            <span class="text-[10px] text-slate-400 font-mono">Gazette Pages ${b.start_page} – ${b.end_page}</span>
            <div class="flex items-center gap-2">
              <button 
                onclick="window.statutoryDrawer.jumpToPdfPage(${b.start_page})" 
                class="px-2 py-0.8 border border-slate-300 hover:bg-slate-100 text-slate-700 rounded text-[10px] font-semibold transition flex items-center gap-1 cursor-pointer"
                title="View original scanned PDF starting at page ${b.start_page}"
              >
                <svg class="w-3 h-3 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                <span>View PDF (p.${b.start_page})</span>
              </button>
              <button 
                onclick="window.statutoryDrawer.expandBookRules(${b.id})" 
                class="px-2.5 py-0.8 bg-slate-900 hover:bg-slate-800 text-white rounded text-[10px] font-bold transition flex items-center gap-1 cursor-pointer"
              >
                <span>Browse Rules</span>
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
            </div>
          </div>
          <div id="book-rules-list-${b.id}" class="hidden border-t border-slate-200 bg-slate-50 p-2 space-y-1"></div>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;
  }

  async expandBookRules(bookId) {
    const listContainer = document.getElementById(`book-rules-list-${bookId}`);
    if (!listContainer) return;

    if (!listContainer.classList.contains('hidden')) {
      listContainer.classList.add('hidden');
      return;
    }

    listContainer.classList.remove('hidden');
    listContainer.innerHTML = `<div class="p-2 text-xs text-slate-500 flex items-center gap-2"><div class="w-3.5 h-3.5 border-2 border-amber-600 border-t-transparent rounded-full animate-spin"></div> Loading clauses...</div>`;

    try {
      const res = await fetch(`/api/v1/library/book/${bookId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const rules = data.rules || [];

      if (!rules.length) {
        listContainer.innerHTML = `<div class="p-2 text-xs text-slate-400">No individual clauses indexed for this volume.</div>`;
        return;
      }

      let rHtml = `<div class="grid grid-cols-1 gap-1 max-h-72 overflow-y-auto pr-1">`;
      rules.forEach(r => {
        rHtml += `
          <div 
            onclick="window.statutoryDrawer.openRule(${r.id})"
            class="p-1.5 rounded hover:bg-white hover:border-slate-300 border border-transparent transition cursor-pointer flex items-center justify-between text-xs"
          >
            <div class="truncate mr-2">
              <span class="font-mono font-bold text-slate-800 text-[10px]">${r.rule_no}:</span>
              <span class="text-slate-700 ml-1">${r.rule_title}</span>
            </div>
            <span class="text-[9px] text-slate-400 font-mono shrink-0">p.${r.page_no}</span>
          </div>
        `;
      });
      rHtml += `</div>`;
      listContainer.innerHTML = rHtml;
    } catch (err) {
      listContainer.innerHTML = `<div class="p-2 text-xs text-red-500">Failed to load rules: ${err.message}</div>`;
    }
  }

  async openRule(ruleId) {
    this.activeRuleId = ruleId;
    this.switchTab('reader');
    await this.loadAndRenderActiveRule(ruleId);
  }

  async loadAndRenderActiveRule(ruleId) {
    const container = document.getElementById('statutory-dynamic-content');
    if (!container) return;

    container.innerHTML = `<div class="p-8 text-center text-xs text-slate-500 flex flex-col items-center gap-2"><div class="w-6 h-6 border-2 border-amber-600 border-t-transparent rounded-full animate-spin"></div> Fetching statutory clause...</div>`;

    try {
      const res = await fetch(`/api/v1/library/rule/${ruleId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const r = await res.json();

      this.activePageNo = r.page_no;
      const pageLabel = document.getElementById('statutory-active-page-label');
      if (pageLabel) pageLabel.innerText = r.page_no;

      let html = `
        <div class="bg-white rounded-lg border border-slate-200 p-4 shadow-xs space-y-3">
          <!-- Back navigation & actions -->
          <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
            <button 
              onclick="window.statutoryDrawer.backToList()" 
              class="px-2 py-1 rounded text-slate-600 hover:text-slate-900 hover:bg-slate-100 text-xs font-semibold transition flex items-center gap-1 cursor-pointer"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
              <span>Back</span>
            </button>

            <div class="flex items-center gap-1.5">
              <button 
                onclick="window.statutoryDrawer.copyCitation(${r.id})" 
                class="px-2.5 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded text-xs font-bold transition flex items-center gap-1 cursor-pointer shadow-xs"
                title="Copy formal statutory citation to clipboard"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
                <span>Copy DOS Citation</span>
              </button>

              <button 
                onclick="window.statutoryDrawer.jumpToPdfPage(${r.page_no})" 
                class="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded text-xs font-semibold transition flex items-center gap-1 cursor-pointer"
                title="View original gazette scanned page in split viewer"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                <span>View in PDF (p.${r.page_no})</span>
              </button>
            </div>
          </div>

          <!-- Rule Header Meta -->
          <div>
            <div class="flex items-center gap-2">
              <span class="px-2 py-0.5 rounded bg-amber-100 text-amber-900 font-mono font-bold text-xs">${r.rule_no}</span>
              <span class="text-[10px] text-slate-500 font-medium">${r.book_title}</span>
            </div>
            <h2 class="text-base font-bold text-slate-900 mt-1">${r.rule_title}</h2>
            ${r.chapter_title ? `<div class="text-[10.5px] text-slate-400 mt-0.5">${r.chapter_title}</div>` : ''}
          </div>

          <!-- Rule Formatted HTML Content -->
          <div class="statutory-clause-body bg-slate-50 p-3.5 rounded-lg border border-slate-200 text-slate-800">
            ${r.content_html || `<p class="text-xs text-slate-700 leading-relaxed">${htmlEscape(r.content_text)}</p>`}
          </div>

          <!-- Tags & Statutory Meta -->
          ${r.tags ? `
            <div class="pt-2 border-t border-slate-100 flex flex-wrap items-center gap-1">
              <span class="text-[10px] text-slate-400 font-semibold mr-1">Tags:</span>
              ${r.tags.split(', ').map(t => `<span class="px-1.5 py-0.3 bg-slate-100 text-slate-600 rounded text-[9.5px] font-mono">${t}</span>`).join('')}
            </div>
          ` : ''}

          <!-- Formal Citation Box -->
          <div class="bg-amber-50/70 p-2.5 rounded border border-amber-200/80 flex items-center justify-between text-xs">
            <div class="truncate mr-2">
              <span class="text-[10px] font-bold text-amber-900 uppercase">Citation:</span>
              <span class="text-slate-800 font-medium ml-1">${r.citation_text}</span>
            </div>
            <button 
              onclick="window.statutoryDrawer.copyCitation(${r.id})" 
              class="text-amber-700 hover:text-amber-900 font-bold shrink-0 text-[11px] underline cursor-pointer"
            >
              Copy
            </button>
          </div>
        </div>
      `;

      container.innerHTML = html;
    } catch (err) {
      container.innerHTML = `<div class="p-4 text-xs text-red-600 bg-red-50 rounded border border-red-200">Failed to render rule: ${err.message}</div>`;
    }
  }

  backToList() {
    this.activeRuleId = null;
    this.renderContent();
  }

  jumpToPdfPage(pageNo) {
    this.activePageNo = pageNo;
    const pageLabel = document.getElementById('statutory-active-page-label');
    if (pageLabel) pageLabel.innerText = pageNo;

    this.switchTab('pdf');
  }

  async copyCitation(ruleId) {
    try {
      const res = await fetch(`/api/v1/library/rule/${ruleId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const r = await res.json();
      const citation = `${r.citation_text} (Page ${r.page_no}), Statutory Inland Vessel Rules & Laws of Bangladesh (S.R.O. 308/Law-2001 & ISO 1976).`;

      if (navigator.clipboard) {
        await navigator.clipboard.writeText(citation);
      } else {
        const temp = document.createElement('textarea');
        temp.value = citation;
        document.body.appendChild(temp);
        temp.select();
        document.execCommand('copy');
        document.body.removeChild(temp);
      }

      this.showToast(`Copied: "${citation.substring(0, 60)}..."`);
    } catch (err) {
      console.error('[StatutoryDrawer] Copy citation failed:', err);
    }
  }

  showToast(message) {
    const toast = document.getElementById('statutory-citation-toast');
    const msgEl = document.getElementById('toast-citation-msg');
    if (toast && msgEl) {
      msgEl.innerText = message;
      toast.classList.remove('hidden');
      setTimeout(() => {
        toast.classList.add('hidden');
      }, 3500);
    }
  }
}

function htmlEscape(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Auto-instantiate when DOM is ready
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      window.statutoryDrawer = new StatutoryDrawer();
    });
  } else {
    window.statutoryDrawer = new StatutoryDrawer();
  }
}
