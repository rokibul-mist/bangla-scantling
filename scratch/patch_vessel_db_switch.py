with open('app/static/js/views/VesselDbView.js', 'r', encoding='utf-8') as f:
    js = f.read().replace('\r\n', '\n')

old_code = """    // Switch to Dashboard tab
    if (window.navigation) {
      window.navigation.switchTab('dashboard');
    }"""

new_code = """    // Switch to Dashboard tab
    if (typeof switchTab === 'function') {
      switchTab('dashboard');
    } else if (window.navigation) {
      window.navigation.switchTab('dashboard');
    }"""

assert old_code in js, "old_code not found in VesselDbView.js"
js = js.replace(old_code, new_code)

with open('app/static/js/views/VesselDbView.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated switchTab in VesselDbView.js")
