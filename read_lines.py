with open('frontend/src/App.tsx', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'value={current?.code' in line:
        print(f"Line {i+1}: {repr(line)}")
        break
