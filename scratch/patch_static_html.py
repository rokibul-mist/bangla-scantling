import re

with open('app/static/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Navigation item
nav_target = re.compile(
    r'(<button class="nav-tab active[^>]+data-tab="dashboard">.*?<\/button>)(\s*)(<button class="nav-tab[^>]+data-tab="sheet2-calc">)',
    re.DOTALL
)
nav_replacement = r'''\1\2<button class="nav-tab w-full !text-[11.5px] !py-1.5 !px-2 flex items-center justify-between" data-tab="vessel-db">
  <span class="truncate">Vessel Database</span>
  <span id="nav-vessel-count" class="text-[9px] px-1.5 py-0.2 rounded font-mono font-bold bg-blue-100 text-blue-800">DB</span>
</button>\2\3'''
content, n1 = nav_target.subn(nav_replacement, content, count=1)
print(f"Patched navigation: {n1}")

# 2. Tab content container
tab_target = re.compile(
    r'(<div id="tab-content-dashboard"[^>]*></div>)(\s*)(<div id="tab-content-sheet2-calc")',
    re.DOTALL
)
tab_replacement = r'''\1\2<div id="tab-content-vessel-db" class="tab-content hidden"></div>\2\3'''
content, n2 = tab_target.subn(tab_replacement, content, count=1)
print(f"Patched tab content: {n2}")

# 3. Scripts
script_target = re.compile(
    r'(<script src="/static/js/components/PdfViewerModal\.js[^>]*></script>)',
    re.DOTALL
)
script_replacement = r'''\1
<script src="/static/js/components/SaveVesselModal.js?v=20261103"></script>
<script src="/static/js/views/VesselDbView.js?v=20261103"></script>'''
content, n3 = script_target.subn(script_replacement, content, count=1)
print(f"Patched scripts: {n3}")

# 4. Right sidebar buttons
sb_target = re.compile(
    r'(<div id="save-status-container".*?<\/div>)(\s*)(<\/div>\s*<!-- ADVANCED DETAIL CALCULATION PDF)',
    re.DOTALL
)
sb_replacement = r'''\1
      <button onclick="openSaveVesselModal()" class="w-full mt-2 px-2 py-1 bg-slate-800 hover:bg-slate-900 text-white rounded text-[10.5px] font-semibold transition text-center cursor-pointer flex items-center justify-center gap-1 shadow-2xs" title="Save this vessel calculation into the permanent Vessel Database">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/></svg>
        <span>Save to Vessel DB</span>
      </button>

      <button onclick="if (window.navigation) window.navigation.switchTab('vessel-db');" class="w-full mt-1 px-2 py-1 border border-slate-300 hover:bg-slate-100 text-slate-700 rounded text-[10.5px] font-semibold transition text-center cursor-pointer flex items-center justify-center gap-1" title="Browse and open stored vessels from the database">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
        <span>Browse Vessel DB</span>
      </button>\2\3'''
content, n4 = sb_target.subn(sb_replacement, content, count=1)
print(f"Patched sidebar: {n4}")

with open('app/static/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved app/static/index.html successfully")
