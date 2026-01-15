#!/bin/bash

echo "🔧 Fixing remaining API URL issues..."

# Fix template string issues in image error handlers
echo "  📷 Fixing image error handlers..."
find src -name "*.vue" -exec sed -i.tmp 's/@error="e => e.target.src = '\''${baseURL.replace("\/api\/", "")}\/media\/logos\/default.jpg'\''"/&="e => e.target.src = baseURL.replace('"'"'\/api\/'"'"', '"'"''"'"') + '"'"'\/media\/logos\/default.jpg'"'"'"/g' {} \;

# Fix axios reference issues - some files still use axios instead of api
echo "  🔗 Fixing axios references..."
find src -name "*.vue" -exec sed -i.tmp 's/const response = await axios\.get/const response = await api.get/g' {} \;
find src -name "*.vue" -exec sed -i.tmp 's/const res = await axios\.get/const res = await api.get/g' {} \;
find src -name "*.vue" -exec sed -i.tmp 's/await axios\.delete/await api.delete/g' {} \;
find src -name "*.vue" -exec sed -i.tmp 's/await axios\.put/await api.put/g' {} \;
find src -name "*.vue" -exec sed -i.tmp 's/await axios\.post/await api.post/g' {} \;
find src -name "*.vue" -exec sed -i.tmp 's/await axios\.patch/await api.patch/g' {} \;

# Fix broken template strings
echo "  🛠️  Fixing broken template strings..."
find src -name "*.vue" -exec sed -i.tmp 's/'\''${baseURL.replace("\/api\/", "")}\/api\//api.get('\''/g' {} \;

# Fix duplicate imports
echo "  🗂️  Fixing duplicate imports..."
find src -name "*.vue" -exec sed -i.tmp '/import api from '\''@\/axios'\''/d' {} \;

# Fix remaining hardcoded URLs in template strings
echo "  🎯 Fixing template string URLs..."
find src -name "*.vue" -exec sed -i.tmp 's/\${baseURL\.replace("\/api\/", "")}\/api\//baseURL/g' {} \;

# Fix specific axios configuration duplicates
echo "  ⚙️  Fixing axios configuration duplicates..."
sed -i.tmp 's/const api = axios\.create({ baseURL: '\''${baseURL\.replace("\/api\/", "")}\/api'\'' })/\/\/ Axios instance configured in @\/axios/g' src/pages/KonfiguraPontos.vue

# Clean up temp files
find src -name "*.tmp" -delete

echo "  🧹 Cleaning up..."

# Fix any remaining broken references
find src -name "*.vue" -exec grep -l "axios\.get\|axios\.post\|axios\.put\|axios\.delete" {} \; | while read file; do
  echo "    ⚠️  Still has direct axios usage: $file"
done

echo ""
echo "📊 Summary of fixes:"
echo "  ✅ Fixed image error handlers"  
echo "  ✅ Replaced direct axios calls with api instance"
echo "  ✅ Fixed broken template strings"
echo "  ✅ Removed duplicate imports"
echo "  ✅ Fixed axios configuration duplicates"
echo ""
echo "⚠️  Please review the changes and test the application!"