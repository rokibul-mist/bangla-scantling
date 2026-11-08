with open('app/static/js/views/VesselDbView.js', 'r', encoding='utf-8') as f:
    js = f.read().replace('\r\n', '\n')

old_code = """    // Update client appState with evaluated state
    window.appState = data.state;
    if (window.appStore) {
      window.appStore.setState(data.state);
    }"""

new_code = """    // Update client appState with evaluated state
    window.appState = data.state;
    if (window.appStore && typeof window.appStore.setData === 'function') {
      window.appStore.setData(data.state);
    }"""

assert old_code in js, "old_code not found in VesselDbView.js"
js = js.replace(old_code, new_code)

with open('app/static/js/views/VesselDbView.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("Fixed appStore.setData in VesselDbView.js")
