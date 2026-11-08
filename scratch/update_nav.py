with open('app/static/js/core/Navigation.js', 'r', encoding='utf-8') as f:
    js = f.read().replace('\r\n', '\n')

old_code = """    if (tabId === 'sheet2-calc' && typeof renderSheet2Calc === 'function') {
      renderSheet2Calc();
    } else if (tabId === 'dashboard' && typeof updateLiveDashboardDisplays === 'function') {"""

new_code = """    if (tabId === 'vessel-db' && typeof renderVesselDb === 'function') {
      renderVesselDb();
    } else if (tabId === 'sheet2-calc' && typeof renderSheet2Calc === 'function') {
      renderSheet2Calc();
    } else if (tabId === 'dashboard' && typeof updateLiveDashboardDisplays === 'function') {"""

assert old_code in js, "old_code not found in Navigation.js"
js = js.replace(old_code, new_code)

with open('app/static/js/core/Navigation.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated Navigation.js")
