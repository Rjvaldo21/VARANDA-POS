# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

VARANDA-POS is a desktop Point of Sale application built with:

**Frontend Stack:**
- Vue.js 3 with Composition API and `<script setup>` syntax
- Vite for build tooling and development server
- Electron for desktop app packaging
- Pinia for state management
- Vue Router for navigation
- TailwindCSS for styling
- Vue-i18n for internationalization (supports English, Portuguese, Tetum)

**Backend Stack:**
- Django 5.2+ with Django REST Framework
- SQLite database (with PostgreSQL production support configured)
- JWT authentication via djangorestframework-simplejwt
- Jazzmin for Django admin interface customization
- Python barcode/QR code generation libraries

**Desktop Integration:**
- Electron main process (`electron/main.cjs`) handles window management and embeds Django backend
- Database is copied to user data directory on first run
- Production builds include backend files as extra resources

## Development Commands

**Start Development Environment:**
```bash
npm run dev
# Starts Vite dev server and Electron app with embedded Django backend
# This is the primary development command
```

**Backend Only (Manual):**
```bash
cd backend
python3 manage.py migrate
python3 manage.py runserver 127.0.0.1:8000
```

**Frontend Only:**
```bash
npm run vite  # Vite dev server only
```

**Build Commands:**
```bash
npm run build           # Build frontend
npm run electron:build  # Build desktop installer
npm run preview         # Preview production build
```

**Database Management:**
```bash
cd backend
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py dbshell
```

## Key Architecture Patterns

**API Configuration:**
- Base API URL configurable via `VITE_API_BASE_URL` environment variable
- JWT token refresh handled automatically in `src/axios.js`
- All API requests use Bearer token authentication
- CORS configured for development origins

**Vue.js Patterns:**
- Route-based pages in `src/pages/` directory
- Reusable components in `src/components/`
- Router guards enforce authentication (`src/router/index.js:79-90`)
- State management centralized in Pinia stores (`src/stores/`)

**Django Backend:**
- Single Django app `pos` contains all business logic
- Models follow POS domain (Product, Transaction, Customer, etc.)
- Custom user data path handling for Electron deployment
- Admin interface highly customized with Jazzmin theming

**Database Schema:**
- Core entities: Product, Category, Unit, Supplier, Customer, Warehouse
- Transaction system: Transaction, Purchase, Returns
- Stock management: Stock, StockMovement, StockAdjustment
- Multi-warehouse support with stock transfers
- Points/loyalty system integration

## Configuration Files

**Environment Variables:**
- `.env.development` - Development config
- `.env.production` - Production config  
- Key variables: `VITE_API_BASE_URL`, `VITE_API_TIMEOUT`

**Django Settings:**
- Environment-driven configuration in `backend/posbackend/settings.py`
- Database configurable via `DATABASE_URL`
- JWT token lifetimes configurable
- User data path handling for desktop deployment

## File Structure Notes

- Backup `.vue` files exist for many components (indicated by `.backup` suffix)
- Multiple documentation files exist for different aspects (running, deployment, etc.)
- Backend includes embedded Python distribution for standalone deployment
- Frontend uses alias `@` pointing to `src/` directory
- Electron packaging configured in `package.json` build section

## Testing & Linting

No specific testing framework is configured. When adding tests, check existing patterns first.

## Deployment Considerations

- Desktop app bundles Django backend as extra resources
- Database location handled differently in development vs production
- Multiple platform build targets supported (Windows, macOS, Linux)
- API timeout configured for slower networks (30s default)

## Application Modules & Save Functionality Checklist

This section provides a comprehensive list of all modules in VARANDA-POS for systematic testing of save functionality.

### 🏪 Core Business Modules

#### 1. Point of Sale (POS) - `src/pages/POS.vue`
- **Functionality**: Main cashier interface, cart management, payment processing
- **Save Operations**: Transaction creation, cart persistence
- **Status**: ✅ **FUNCTIONAL** - Cart saves to localStorage, transactions process via API
- **Test**: Add products to cart, process payment, verify transaction creation

#### 2. Product Management - `src/pages/IventoriuProdutu.vue`
- **Functionality**: Product CRUD operations, pricing, stock management
- **Save Operations**: Create/Update products with validation
- **Required Fields**: `name`, `sku`, `price`, `cost_price`
- **API Endpoints**: `/api/products/`
- **Status**: ✅ **EXCELLENT** - Comprehensive validation, proper API integration
- **Code Quality**: A+ with robust error handling, loading states, and user feedback
- **Save Function**: `saveProduct` (lines 183-303) - Most comprehensive validation of all modules

#### 3. Category Management - `src/pages/Kategoria.vue`  
- **Functionality**: Product category management
- **Save Operations**: Create/Update categories
- **Required Fields**: `name`, `code`
- **API Endpoints**: `/api/categories/`
- **Status**: ✅ **EXCELLENT** - Enhanced validation with auto-uppercase conversion
- **Code Quality**: A+ with proper error handling and field-specific validation
- **Save Function**: `saveCategory` (lines 85-172) - Well-implemented with comprehensive error handling

#### 4. Supplier Management - `src/pages/IventoriuSupplier.vue`
- **Functionality**: Supplier information management
- **Save Operations**: Create/Update supplier details
- **Required Fields**: `name`
- **Optional Fields**: `phone`, `email`, `address`
- **API Endpoints**: `/api/suppliers/`
- **Status**: ✅ **EXCELLENT** - Email validation, proper optional field handling
- **Code Quality**: A+ with comprehensive error handling and input sanitization
- **Save Function**: `saveSupplier` (lines 102-188) - Includes regex email validation

#### 5. Unit Management - `src/pages/IventoriuUnidade.vue`
- **Functionality**: Measurement units (kg, pieces, liters, etc.)
- **Save Operations**: Create/Update units
- **Required Fields**: `name`
- **API Endpoints**: `/api/units/`
- **Status**: ✅ **EXCELLENT** - Clean implementation with proper validation
- **Code Quality**: A+ with comprehensive error handling covering all scenarios
- **Save Function**: `saveUnit` (lines 133-207) - Excellent error categorization

#### 6. Customer Management - `src/pages/IventoriuListaKliente.vue`
- **Functionality**: Customer profiles, loyalty points management
- **Save Operations**: Create/Update customer information
- **Required Fields**: `name`
- **Optional Fields**: `phone`, `email`, `address`, `points`
- **API Endpoints**: `/api/customers/`
- **Status**: ✅ **EXCELLENT** - Email validation, numeric points validation
- **Code Quality**: A+ with proper type conversion and comprehensive validation
- **Save Function**: `saveCustomer` (lines 127-220) - Includes points field integer conversion

### 🏢 System Configuration Modules

#### 7. User Administration - `src/pages/Administrasaun.vue`
- **Functionality**: System user management, roles, permissions
- **Save Operations**: Create/Update users with role assignment
- **Required Fields**: `username`, `first_name`, `last_name`, `email`, `role`, `password` (for new users)
- **API Endpoints**: `/api/users/`
- **Status**: ⚠️ **NEEDS TESTING**
- **Test Steps**:
  1. Create new user with all required fields
  2. Test password strength validation (min 8 characters)
  3. Test password confirmation matching
  4. Verify email format validation
  5. Test role assignment functionality
  6. Test user edit (password should be optional)

#### 8. Bank Management - `src/pages/Banku.vue`
- **Functionality**: Payment processing, bank accounts, fee configuration
- **Save Operations**: Create/Update bank details and fee structures
- **Required Fields**: `name`
- **Complex Fields**: Fee structure (percent_fee, fixed_fee, min_fee, max_fee)
- **API Endpoints**: `/api/banks/`
- **Status**: ⚠️ **NEEDS TESTING**
- **Test Steps**:
  1. Add bank with basic info
  2. Configure fee structure (percentage + fixed fees)
  3. Test payment method toggles (credit, transfer, QRIS)
  4. Verify numeric validation on fee fields

#### 9. Warehouse Management - `src/pages/WarehouseList.vue`
- **Functionality**: Multi-location inventory management
- **Save Operations**: Create/Update warehouse locations
- **Required Fields**: `name`, `location`
- **API Endpoints**: `/api/warehouses/`
- **Status**: ⚠️ **NEEDS TESTING**
- **Test Steps**:
  1. Add new warehouse with name and location
  2. Test edit functionality
  3. Verify required field validation

### 📦 Inventory Operations

#### 10. Stock Adjustment - `src/pages/InventoriuHadiaStok.vue`
- **Functionality**: Manual inventory adjustments, stock corrections
- **Save Operations**: Create stock adjustment records
- **Required Fields**: `product`, `new_stock`, `reason`
- **API Endpoints**: `/api/stock-adjustments/`
- **Status**: ⚠️ **NEEDS TESTING**
- **Test Steps**:
  1. Select product and adjust stock quantity
  2. Enter adjustment reason
  3. Verify all fields are required
  4. Check stock history tracking

### 🔍 Save Functionality Testing Protocol

For each module, follow these standard tests:

#### **Pre-Test Setup:**
1. Ensure backend is running (`cd backend && python manage.py runserver`)
2. Start frontend (`npm run dev`)
3. Login with valid credentials
4. Open browser developer tools (F12)

#### **Standard Test Cases:**
1. **Create New Record**:
   - Fill all required fields ✅
   - Submit form and check console for API calls
   - Verify success message and list refresh
   - Check database/admin panel for record creation

2. **Validation Testing**:
   - Submit empty required fields ❌
   - Verify client-side validation messages
   - Check server-side validation responses

3. **Edit Existing Record**:
   - Load existing record in form ✅
   - Modify values and save
   - Verify changes persisted correctly

4. **Error Handling**:
   - Test with invalid data types
   - Test with duplicate values where applicable
   - Verify graceful error handling

#### **Debug Information to Monitor:**
- Browser console logs (🔄 API Request, ✅ API Response, ❌ API Error)
- Network tab for HTTP status codes
- Local storage for authentication tokens
- Vue DevTools for component state

#### **Common Issues to Check:**
- Authentication token presence and validity
- CORS configuration between frontend and backend
- API endpoint URL consistency (port 8000 vs 8001)
- Form validation rules matching backend requirements
- Network connectivity between frontend and backend

Use this checklist to systematically verify save functionality across all modules. Update status indicators as testing progresses.

## Logo Upload Fix (Store Configuration)

### 🐛 **Issue Fixed**: Store Logo Upload Failing

**Problem**: Logo upload in system configuration (`src/pages/Konfigura.vue`) was failing silently.

**Root Causes Identified**:
1. Backend missing multipart/form-data parser configuration
2. Frontend lacking comprehensive file validation
3. No proper error handling for file upload scenarios
4. Missing loading states during upload process

**✅ Solutions Implemented**:

#### Backend Fixes (`backend/pos/views.py`):
```python
class StoreProfileViewSet(viewsets.ModelViewSet):
    queryset = StoreProfile.objects.all()
    serializer_class = StoreProfileSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
```

#### Frontend Enhancements (`src/pages/Konfigura.vue`):
1. **File Validation**: Added comprehensive validation for:
   - File size (max 5MB)
   - File types (JPEG, JPG, PNG, GIF, WebP)
   - Image validity check using Image() loader
   
2. **Enhanced Error Handling**: Added specific error messages for:
   - HTTP 413 (file too large)
   - HTTP 415 (unsupported file type)
   - Validation errors with field-specific feedback
   - Network errors and authentication issues

3. **Loading States**: Added visual feedback:
   - Spinning loader during save operation
   - Disabled button state while saving
   - Clear success/error messaging

4. **Improved FormData Handling**:
   - Proper multipart/form-data upload
   - Automatic Content-Type header handling by axios
   - Form field validation and trimming

#### File Structure:
- Logo uploads stored in `backend/media/logos/` with timestamp naming
- Default logo fallback system maintained
- Automatic old logo cleanup on update

### **Status**: ✅ **FIXED**

**Test Steps**:
1. Navigate to System Configuration (⚙️ Konfigura)
2. Click "Edit" button next to logo
3. Select image file (JPG/PNG/GIF/WebP, max 5MB)
4. Fill required store name field
5. Click "Save Changes" button
6. Verify success message and logo update

**Debug Information**: Console logs show detailed upload progress:
- `🔄 Saving store profile...`
- `📸 Adding logo file to upload: [filename] ([size] bytes)`
- `📦 FormData contents: [field details]`
- `✅ Store profile saved successfully`