with open('app/static/js/app.js', 'r', encoding='utf-8') as f:
    js = f.read().replace('\r\n', '\n')

old_code = """  } else if (currentTab === 'calc-brain') {

    if (typeof renderCalcBrain === 'function') renderCalcBrain();"""

new_code = """  } else if (currentTab === 'vessel-db') {

    if (typeof renderVesselDb === 'function') renderVesselDb();

  } else if (currentTab === 'calc-brain') {

    if (typeof renderCalcBrain === 'function') renderCalcBrain();"""

assert old_code in js, "old_code not found in app.js"
js = js.replace(old_code, new_code)

with open('app/static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated renderApp in app.js for vessel-db")
