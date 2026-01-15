#!/bin/bash

echo "🔧 Simple fix for malformed @error attributes..."

# List of files to fix
files=(
  "src/pages/StockMovementHistory.vue"
  "src/pages/IventoriuSupplier.vue" 
  "src/pages/TranzasaunKompra.vue"
  "src/pages/IventoriuListaKliente.vue"
  "src/pages/Kategoria.vue"
  "src/pages/InventoriuHadiaStok.vue"
  "src/pages/RelatoriuTranzasaun.vue"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "  🔧 Fixing $file"
    # Use a simpler approach - find the line and replace it entirely
    sed -i.bak 's/.*@error.*baseURL.*jpg.*error.*/          @error="e => e.target.src = baseURL.replace('"'"'\/api\/'"'"', '"'"''"'"') + '"'"'\/media\/logos\/default.jpg'"'"'"/' "$file"
    rm -f "$file.bak"
  fi
done

echo ""
echo "✅ Fixed all remaining malformed @error attributes!"
echo "🧪 Please test the application now."