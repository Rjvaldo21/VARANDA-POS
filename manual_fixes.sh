#!/bin/bash

echo "🔧 Manual fixes for remaining issues..."

# Fix baseURL concatenation issues
echo "  🔗 Fixing baseURL concatenation issues..."
find src -name "*.vue" -exec sed -i.tmp 's/`baseURLusers/`users/g' {} \;
find src -name "*.vue" -exec sed -i.tmp 's/`baseURLsuppliers/`suppliers/g' {} \;
find src -name "*.vue" -exec sed -i.tmp 's/`baseURLwarehouses/`warehouses/g' {} \;
find src -name "*.vue" -exec sed -i.tmp 's/`baseURLstock-movements/`stock-movements/g' {} \;
find src -name "*.vue" -exec sed -i.tmp 's/`baseURLcustomers/`customers/g' {} \;
find src -name "*.vue" -exec sed -i.tmp 's/`baseURLunits/`units/g' {} \;

# Fix broken URLs in specific files
echo "  🛠️  Fixing specific broken URLs..."
find src -name "*.vue" -exec sed -i.tmp 's/baseURLproducts/products/g' {} \;

# Fix broken image error handlers
echo "  🖼️  Fixing image error handlers..."
find src -name "*.vue" -exec sed -i.tmp "s/@error=\"e => e.target.src = '\${baseURL.replace(\"\/api\/\", \"\")}\/media\/logos\/default.jpg'\"=\"e => e.target.src = baseURL.replace('\/api\/', '') + '\/media\/logos\/default.jpg'\"/&error=\"e => e.target.src = baseURL.replace('\/api\/', '') + '\/media\/logos\/default.jpg'\"/g" {} \;

# Fix broken API calls
echo "  ⚙️  Fixing broken API calls..."
sed -i.tmp 's/api.get('\''sales\/total\/'\'',$/{
  const res = await api.get('\''sales\/total\/'\',/g' src/pages/RelatoriuFaan.vue

sed -i.tmp 's/const { data } = await axios.get($/{
  const { data } = await api.get(\/'\/finance\/summary\/'\/,/g' src/pages/RelatoriuFinansas.vue

# Fix BarcodeInput.vue
sed -i.tmp 's/baseURLproducts/products/g' src/components/pos/BarcodeInput.vue

# Fix broken api calls with template strings
find src -name "*.vue" -exec sed -i.tmp 's/api\.get(\([^)]*\)$/api.get(\1)/g' {} \;

# Clean up temp files
find src -name "*.tmp" -delete

echo ""
echo "✅ Manual fixes completed!"
echo "  ✅ Fixed baseURL concatenation"
echo "  ✅ Fixed broken URLs"  
echo "  ✅ Fixed image error handlers"
echo "  ✅ Fixed broken API calls"
echo ""
echo "⚠️  Please test the application!"