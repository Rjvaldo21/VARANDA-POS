// Simple script to test backend connection
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

async function testBackendConnection() {
  console.log('🔍 Testing backend connection...')
  console.log('API Base URL:', API_BASE_URL)
  
  try {
    // Test basic connection
    console.log('\n1. Testing basic connection...')
    const healthResponse = await axios.get(`${API_BASE_URL}/`, {
      timeout: 5000
    })
    console.log('✅ Basic connection successful')
    console.log('Response status:', healthResponse.status)
    
    // Test authentication endpoint
    console.log('\n2. Testing auth endpoints...')
    try {
      const authResponse = await axios.post(`${API_BASE_URL}/token/`, {
        username: 'test',
        password: 'test'
      }, { timeout: 5000 })
      console.log('✅ Auth endpoint accessible')
    } catch (authError) {
      if (authError.response?.status === 401) {
        console.log('✅ Auth endpoint accessible (credentials invalid, which is expected)')
      } else {
        console.log('⚠️ Auth endpoint issue:', authError.message)
      }
    }
    
    // Test data endpoints
    console.log('\n3. Testing data endpoints...')
    const endpoints = ['products', 'categories', 'units', 'suppliers', 'customers']
    
    for (const endpoint of endpoints) {
      try {
        await axios.get(`${API_BASE_URL}/${endpoint}/`, {
          timeout: 5000,
          headers: {
            'Authorization': 'Bearer invalid-token-for-test'
          }
        })
        console.log(`✅ ${endpoint} endpoint accessible`)
      } catch (error) {
        if (error.response?.status === 401) {
          console.log(`✅ ${endpoint} endpoint accessible (auth required, which is expected)`)
        } else if (error.response?.status === 404) {
          console.log(`❌ ${endpoint} endpoint not found`)
        } else {
          console.log(`⚠️ ${endpoint} endpoint issue:`, error.message)
        }
      }
    }
    
  } catch (error) {
    console.error('❌ Backend connection failed:')
    console.error('Error:', error.message)
    
    if (error.code === 'ECONNREFUSED') {
      console.error('\n💡 Suggestion: Make sure the Django backend is running on port 8000')
      console.error('   Run: python manage.py runserver 8000')
    } else if (error.code === 'ETIMEDOUT') {
      console.error('\n💡 Suggestion: Backend is taking too long to respond')
      console.error('   Check if the backend is overloaded or having issues')
    }
  }
}

// Run the test
testBackendConnection().then(() => {
  console.log('\n🏁 Backend connection test completed')
}).catch(error => {
  console.error('🚨 Test script error:', error)
})