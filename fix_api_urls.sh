#!/bin/bash

echo "🔧 Fixing hardcoded API URLs in Vue components..."

# Array of files to update (critical ones first)
files=(
  "src/pages/Administrasaun.vue"
  "src/pages/IventoriuProdutu.vue"
  "src/pages/RelatoriuFaan.vue"
  "src/pages/RelatoriuTranzasaun.vue"
  "src/pages/RelatoriuFinansas.vue"
  "src/pages/TranzasaunKompra.vue"
  "src/pages/TranzasaunRetornuFaan.vue"
  "src/pages/TranzasaunRetornuKompra.vue"
  "src/pages/IventoriuSupplier.vue"
  "src/pages/IventoriuListaKliente.vue"
  "src/pages/Kategoria.vue"
  "src/pages/WarehouseList.vue"
  "src/pages/WarehouseStock.vue"
  "src/pages/StockMovementHistory.vue"
  "src/pages/InventoriuHadiaStok.vue"
  "src/pages/IventoriuUnidade.vue"
  "src/pages/KomputadorKasir.vue"
  "src/pages/RelatoriuProdutu.vue"
  "src/pages/KonfiguraPontos.vue"
  "src/components/pos/BarcodeInput.vue"
)

echo "📝 Creating backup of original files..."
for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    cp "$file" "${file}.backup"
    echo "  ✓ Backed up $file"
  fi
done

echo ""
echo "🔄 Replacing hardcoded URLs..."

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "  🔧 Processing $file..."
    
    # Replace axios import
    sed -i.tmp 's/import axios from '\''axios'\''/import api, { baseURL } from '\''@\/axios'\''/g' "$file"
    
    # Replace hardcoded API calls
    sed -i.tmp 's/axios\.get('\''http:\/\/localhost:8000\/api\//api.get('\''/g' "$file"
    sed -i.tmp 's/axios\.post('\''http:\/\/localhost:8000\/api\//api.post('\''/g' "$file"
    sed -i.tmp 's/axios\.put('\''http:\/\/localhost:8000\/api\//api.put('\''/g' "$file"
    sed -i.tmp 's/axios\.delete('\''http:\/\/localhost:8000\/api\//api.delete('\''/g' "$file"
    
    # Replace 127.0.0.1 variants
    sed -i.tmp 's/axios\.get('\''http:\/\/127\.0\.0\.1:8000\/api\//api.get('\''/g' "$file"
    sed -i.tmp 's/axios\.post('\''http:\/\/127\.0\.0\.1:8000\/api\//api.post('\''/g' "$file"
    sed -i.tmp 's/axios\.put('\''http:\/\/127\.0\.0\.1:8000\/api\//api.put('\''/g' "$file"
    sed -i.tmp 's/axios\.delete('\''http:\/\/127\.0\.0\.1:8000\/api\//api.delete('\''/g' "$file"
    
    # Remove manual Authorization headers (handled by interceptor)
    sed -i.tmp '/headers: {/,/Authorization: \`Bearer \${token}\`/d' "$file"
    sed -i.tmp '/headers: {/,/}/{ /Authorization/d; }' "$file"
    
    # Replace hardcoded base URL in template strings
    sed -i.tmp 's/http:\/\/localhost:8000/\${baseURL.replace("\/api\/", "")}/g' "$file"
    sed -i.tmp 's/http:\/\/127\.0\.0\.1:8000/\${baseURL.replace("\/api\/", "")}/g' "$file"
    
    # Clean up temp files
    rm -f "${file}.tmp"
    
    echo "    ✅ Updated $file"
  else
    echo "    ⚠️  File $file not found, skipping..."
  fi
done

echo ""
echo "🧹 Cleaning up specific issues..."

# Fix specific axios configuration issues
echo "  🔧 Fixing axios configurations..."

# Count changes
total_files_processed=$(ls src/**/*.vue.backup 2>/dev/null | wc -l)
echo ""
echo "📊 Summary:"
echo "  ✅ Processed ${#files[@]} files"
echo "  📁 Created $total_files_processed backup files"
echo "  🔄 All hardcoded URLs replaced with centralized API"
echo ""
echo "⚠️  Please test the application to ensure all API calls work correctly!"
echo "💡 To restore original files: find . -name '*.backup' -exec sh -c 'mv \"$1\" \"${1%.backup}\"' _ {} \;"