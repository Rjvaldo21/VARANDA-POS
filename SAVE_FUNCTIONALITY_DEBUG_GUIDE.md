# Save Functionality Debug Guide

## Issues Fixed

### 1. Authentication Token Handling
- **Problem**: Duplicate Authorization headers being sent
- **Solution**: Removed manual token headers since axios interceptor handles this automatically
- **Files affected**: All Vue components with save functions

### 2. Error Handling
- **Problem**: Generic error messages without proper debugging
- **Solution**: Enhanced error handling with specific error types and detailed logging
- **Features added**:
  - Validation error parsing
  - Network error detection
  - HTTP status code specific messages
  - Console logging for debugging

### 3. Form Validation
- **Problem**: Basic validation that didn't catch edge cases
- **Solution**: Enhanced validation for:
  - Required fields with proper trimming
  - Email format validation
  - Numeric field validation
  - Field-specific validation messages

### 4. API Configuration
- **Problem**: Missing environment configuration and timeouts
- **Solution**: 
  - Updated `.env` file with proper API URL (changed from port 8001 to 8000)
  - Added configurable timeout settings
  - Added debug mode configuration

### 5. Request/Response Logging
- **Problem**: No visibility into API calls
- **Solution**: Added comprehensive logging in axios interceptors
  - Request logging with method, URL, headers, and data
  - Response logging with status and data
  - Error logging with detailed error information

## How to Debug Save Issues

### 1. Check Browser Console
Open Developer Tools (F12) and look for:
- 🔄 API Request logs showing the request being made
- ✅ API Response logs for successful requests
- ❌ API Error logs for failed requests

### 2. Common Error Patterns

#### Authentication Errors (401)
```
❌ API Error: {
  method: 'POST',
  url: 'products/',
  status: 401,
  message: 'Unauthorized'
}
```
**Solution**: Check if user is logged in and token is valid

#### Validation Errors (400)
```
❌ API Error: {
  method: 'POST', 
  url: 'products/',
  status: 400,
  data: {
    name: ['This field is required'],
    price: ['Ensure this value is greater than 0']
  }
}
```
**Solution**: Check form validation and required fields

#### Network Errors
```
❌ API Error: {
  message: 'Network Error'
}
```
**Solution**: Check if backend is running and accessible

### 3. Test Backend Connection
Run the test script:
```bash
node test-backend.js
```

### 4. Check Environment Configuration
Verify `.env` file has correct API URL:
```
VITE_API_BASE_URL=http://localhost:8000/api
```

### 5. Backend Requirements
Make sure Django backend is running:
```bash
cd backend
python manage.py runserver 8000
```

## Save Function Flow

1. **Form Validation**: Enhanced client-side validation
2. **Data Preparation**: Clean and format data payload
3. **API Request**: Send request through axios with interceptors
4. **Token Handling**: Automatic token attachment and refresh
5. **Error Handling**: Comprehensive error parsing and user feedback
6. **Success Handling**: Update UI and refresh data

## Components Updated

- `src/pages/IventoriuProdutu.vue` - Product management
- `src/pages/Kategoria.vue` - Category management  
- `src/pages/IventoriuSupplier.vue` - Supplier management
- `src/pages/IventoriuUnidade.vue` - Unit management
- `src/pages/IventoriuListaKliente.vue` - Customer management
- `src/axios.js` - API configuration and interceptors

## Testing the Fixes

1. **Start the backend** (port 8000)
2. **Start the frontend** (`npm run dev`)
3. **Test each module**:
   - Add new product
   - Edit existing product
   - Delete product
   - Repeat for categories, suppliers, units, customers

4. **Check console logs** for detailed debugging information

## If Issues Persist

1. Check browser console for specific error messages
2. Verify backend is running and accessible
3. Check database connections in backend
4. Verify user authentication status
5. Test individual API endpoints manually

## Environment Variables

Key environment variables in `.env`:
- `VITE_API_BASE_URL`: Backend API URL
- `VITE_DEBUG`: Enable/disable debug logging
- `VITE_API_TIMEOUT`: Request timeout in milliseconds