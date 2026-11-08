with open('app/templates/components/sidebar_right.html', 'r', encoding='utf-8') as f:
    html = f.read().replace('\r\n', '\n')

old_part = """      <!-- Status & Last Saved Timestamp Indicator -->
      <div id="save-status-container" class="text-[9.5px] text-slate-500 text-center mt-1 flex items-center justify-center gap-1">
        <span id="save-status-dot" class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
        <span id="save-status-text" class="truncate">Changes saved</span>
      </div>
    </div>"""

new_part = """      <!-- Status & Last Saved Timestamp Indicator -->
      <div id="save-status-container" class="text-[9.5px] text-slate-500 text-center mt-1 flex items-center justify-center gap-1">
        <span id="save-status-dot" class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
        <span id="save-status-text" class="truncate">Changes saved</span>
      </div>

      <!-- Save to Vessel Database -->
      <button onclick="openSaveVesselModal()" class="w-full mt-2 px-2 py-1 bg-slate-800 hover:bg-slate-900 text-white rounded text-[10.5px] font-semibold transition text-center cursor-pointer flex items-center justify-center gap-1 shadow-2xs" title="Save this vessel calculation into the permanent Vessel Database">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/></svg>
        <span>Save to Vessel DB</span>
      </button>

      <!-- Browse Vessel Database -->
      <button onclick="if (window.navigation) window.navigation.switchTab('vessel-db');" class="w-full mt-1 px-2 py-1 border border-slate-300 hover:bg-slate-100 text-slate-700 rounded text-[10.5px] font-semibold transition text-center cursor-pointer flex items-center justify-center gap-1" title="Browse and open stored vessels from the database">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
        <span>Browse Vessel DB</span>
      </button>
    </div>"""

assert old_part in html, "old_part not found"
html = html.replace(old_part, new_part)

with open('app/templates/components/sidebar_right.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated sidebar_right.html")
