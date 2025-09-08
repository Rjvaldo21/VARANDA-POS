#!/usr/bin/env python3
import re
import glob

# Files that need fixing
files = [
    'src/pages/StockMovementHistory.vue',
    'src/pages/IventoriuSupplier.vue', 
    'src/pages/TranzasaunKompra.vue',
    'src/pages/IventoriuListaKliente.vue',
    'src/pages/Kategoria.vue',
    'src/pages/InventoriuHadiaStok.vue',
    'src/pages/RelatoriuTranzasaun.vue',
    'src/pages/KomputadorKasir.vue'
]

# Pattern to match malformed @error attributes
bad_pattern = re.compile(r'@error="[^"]*\${baseURL\.replace\([^}]*\)}[^"]*jpg[^"]*"[^"]*"[^"]*error="[^"]*"')
good_replacement = '@error="e => e.target.src = baseURL.replace(\'/api/\', \'\') + \'/media/logos/default.jpg\'"'

print("🔧 Fixing malformed @error attributes...")

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find and replace the malformed patterns
        original_content = content
        content = bad_pattern.sub(good_replacement, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed {file_path}")
        else:
            print(f"  ⚠️  No issues found in {file_path}")
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")

print("\n✅ All files processed!")
print("🔍 You may want to manually check the files to ensure they're correct.")