with open('app/static/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('vessel-db nav button:', 'data-tab="vessel-db"' in text)
print('tab-content-vessel-db:', 'tab-content-vessel-db' in text)
print('VesselDbView.js:', 'VesselDbView.js' in text)
print('SaveVesselModal.js:', 'SaveVesselModal.js' in text)
print('Save to Vessel DB button:', 'Save to Vessel DB' in text)
