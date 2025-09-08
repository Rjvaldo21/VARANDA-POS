#!/bin/bash

echo "🔧 Fixing JavaScript parsing errors..."

# Fix malformed @error attributes that got corrupted during previous fixes
echo "  🖼️  Fixing malformed image error handlers..."

# Find and fix the specific malformed @error patterns
find src -name "*.vue" -exec sed -i.tmp 's/@error="e => e.target.src = '\''\${baseURL.replace("\/api\/", "")}\/media\/logos\/default.jpg'\''\"="e => e.target.src = baseURL.replace('\''\/api\/'\''.*jpg'\''"/&error="e => e.target.src = baseURL.replace('\''\\/api\\/'\''','\'\'\'') + '\''\\/media\\/logos\\/default.jpg'\''"/g' {} \;

# More direct approach - fix all broken @error attributes
find src -name "*.vue" -exec sed -i.tmp 's/@error="[^"]*"="e => e.target.src = baseURL.replace[^"]*"error="e => e.target.src = baseURL.replace[^"]*/&error="e => e.target.src = baseURL.replace('\''\\/api\\/'\''','\'\'\'') + '\''\\/media\\/logos\\/default.jpg'\''"/g' {} \;

# Clean approach - remove all broken @error and add clean one
echo "  🧹 Cleaning up malformed attributes..."
find src -name "*.vue" -exec sed -i.tmp 's/@error="[^"]*baseURL[^"]*jpg[^"]*"[^>]*/&error="e => e.target.src = baseURL.replace('\''\\/api\\/'\''','\'\'\'') + '\''\\/media\\/logos\\/default.jpg'\''"/g' {} \;

# More specific fix for the exact pattern we see
find src -name "*.vue" -exec sed -i.tmp 's/@error="e => e.target.src = '\''${baseURL.replace("\/api\/", "")}\/media\/logos\/default.jpg'\''\"="e => e.target.src = baseURL.replace(.*)jpg(.*)"/&error="e => e.target.src = baseURL.replace('\''\\/api\\/'\''','\'\'\'') + '\''\\/media\\/logos\\/default.jpg'\''"/g' {} \;

# Final cleanup - remove any remaining broken patterns
find src -name "*.vue" -exec sed -i.tmp 's/\${baseURL\.replace("[^"]*")}[^"]*jpg[^"]*"error="[^"]*"/baseURL.replace('\''\\/api\\/'\''','\'\'\'') + '\''\\/media\\/logos\\/default.jpg'\''"/g' {} \;

echo ""
echo "  🔧 Manual fix for specific files..."

# Fix each problematic file individually
files=(
  "src/pages/Administrasaun.vue"
  "src/pages/KomputadorKasir.vue"
  "src/pages/RelatoriuTranzasaun.vue"
  "src/pages/InventoriuHadiaStok.vue"
  "src/pages/Kategoria.vue"
  "src/pages/IventoriuListaKliente.vue"
  "src/pages/TranzasaunKompra.vue"
  "src/pages/IventoriuSupplier.vue"
  "src/pages/StockMovementHistory.vue"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "    🔧 Fixing $file"
    # Remove the entire malformed @error line and add clean one
    sed -i.tmp '/@error.*baseURL.*jpg.*error/c\          @error="e => e.target.src = baseURL.replace('\''/api/'\'', '\''\'''') + '\''/media/logos/default.jpg'\''"' "$file"
  fi
done

# Clean up temp files
find src -name "*.tmp" -delete

echo ""
echo "✅ Fixed JavaScript parsing errors!"
echo "  ✅ Fixed malformed @error attributes"
echo "  ✅ Cleaned up broken template expressions"
echo ""
echo "⚠️  Please test the application to ensure images load correctly!"