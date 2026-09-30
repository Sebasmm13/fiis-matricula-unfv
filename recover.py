with open('frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Original chars should be at odd indices.
# Let's check if even indices are all 'í'
evens = content[::2]
all_i = all(c == 'í' for c in evens)
print(f"Total length: {len(content)}")
print(f"All evens are í: {all_i}")

if all_i:
    original = content[1::2]
    with open('frontend/src/App_recovered.tsx', 'w', encoding='utf-8') as f:
        f.write(original)
    print("Recovered!")
else:
    print("Not all evens are í, finding where it breaks...")
    for i in range(0, len(content), 2):
        if content[i] != 'í':
            print(f"Breaks at {i}: {repr(content[i:i+10])}")
            break
