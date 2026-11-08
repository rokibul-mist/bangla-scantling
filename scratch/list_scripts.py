import re

with open('app/static/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', text)
for s in scripts:
    print(s)
