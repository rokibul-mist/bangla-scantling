with open('app/static/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = '<div id="tab-content-dashboard" class="tab-content"></div>'
replacement = '<div id="tab-content-dashboard" class="tab-content"></div>\n\n  <!-- 2. Vessel Database -->\n  <div id="tab-content-vessel-db" class="tab-content hidden"></div>'

assert target in text, "target not found"
text = text.replace(target, replacement, 1)

with open('app/static/index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated tab-content in static index.html")
