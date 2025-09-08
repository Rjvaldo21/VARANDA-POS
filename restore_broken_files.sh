#!/bin/bash

echo "🔧 Restoring broken Vue files from backups..."

# Files that are incomplete
broken_files=(
  "src/pages/KonfiguraPontos.vue"
  "src/pages/TranzasaunRetornuKompra.vue"
  "src/pages/RelatoriuProdutu.vue"
  "src/pages/RelatoriuFaan.vue"
  "src/pages/IventoriuUnidade.vue"
  "src/pages/RelatoriuFinansas.vue"
  "src/pages/IventoriuProdutu.vue"
  "src/pages/WarehouseList.vue"
  "src/pages/TranzasaunRetornuFaan.vue"
)

for file in "${broken_files[@]}"; do
  backup_file="${file}.backup"
  if [ -f "$backup_file" ]; then
    echo "  🔄 Restoring $file from backup..."
    cp "$backup_file" "$file"
    
    # Apply the centralized API fixes to restored file
    echo "  🔧 Applying API centralization fixes..."
    sed -i.tmp 's/import axios from '\''axios'\''/import api, { baseURL } from '\''@\/axios'\''/g' "$file"
    sed -i.tmp 's/axios\.get('\''http:\/\/localhost:8000\/api\//api.get('\''/g' "$file"
    sed -i.tmp 's/axios\.post('\''http:\/\/localhost:8000\/api\//api.post('\''/g' "$file"
    sed -i.tmp 's/axios\.put('\''http:\/\/localhost:8000\/api\//api.put('\''/g' "$file"
    sed -i.tmp 's/axios\.delete('\''http:\/\/localhost:8000\/api\//api.delete('\''/g' "$file"
    sed -i.tmp 's/axios\.get('\''http:\/\/127\.0\.0\.1:8000\/api\//api.get('\''/g' "$file"
    sed -i.tmp 's/axios\.post('\''http:\/\/127\.0\.0\.1:8000\/api\//api.post('\''/g' "$file"
    
    # Fix image URLs
    sed -i.tmp 's/http:\/\/localhost:8000/baseURL.replace("\/api\/", "")/g' "$file"
    sed -i.tmp 's/http:\/\/127\.0\.0\.1:8000/baseURL.replace("\/api\/", "")/g' "$file"
    
    # Fix @error handlers
    sed -i.tmp 's/@error="e => e.target.src = '\''http:\/\/[^'\'']*media\/logos\/default.jpg'\''"/&error="e => e.target.src = baseURL.replace('\''\\/api\\/'\''','\'\'\'') + '\''\\/media\\/logos\\/default.jpg'\''"/g' "$file"
    
    # Clean up
    rm -f "${file}.tmp"
    
    echo "  ✅ Restored and fixed $file"
  else
    echo "  ❌ No backup found for $file"
  fi
done

echo ""
echo "✅ File restoration completed!"
echo "🧪 Please test the application now."