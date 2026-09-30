import codecs
with open('backend/core/views.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
if '\ufffd' in content:
    content = content.replace('\ufffd', 'í')
    with open('backend/core/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed views.py')
else:
    print('Clean views.py')
