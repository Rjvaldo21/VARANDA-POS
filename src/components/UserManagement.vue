<template>
  <div class="card">
    <div class="card-header">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">User Management</h2>
        <button 
          v-if="canCreateUsers" 
          @click="openCreateModal" 
          class="btn btn-primary"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Add User
        </button>
      </div>
    </div>

    <div class="card-body">
      <!-- Filters -->
      <div class="mb-6 flex flex-wrap gap-4">
        <div class="form-group mb-0">
          <label class="form-label">Search Users</label>
          <input 
            v-model="searchQuery" 
            class="form-control" 
            placeholder="Search by name or username..."
          />
        </div>
        <div class="form-group mb-0">
          <label class="form-label">Filter by Role</label>
          <select v-model="roleFilter" class="form-control">
            <option value="">All Roles</option>
            <option value="super_admin">Super Admin</option>
            <option value="admin">Admin</option>
            <option value="manager">Manager</option>
            <option value="supervisor">Supervisor</option>
            <option value="cashier">Cashier</option>
            <option value="inventory_clerk">Inventory Clerk</option>
          </select>
        </div>
        <div class="form-group mb-0">
          <label class="form-label">Status</label>
          <select v-model="statusFilter" class="form-control">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      <!-- Users Table -->
      <div class="table-container">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Role</th>
                <th>Contact</th>
                <th>Status</th>
                <th>Last Login</th>
                <th v-if="canManageUsers">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>
                  <div class="flex items-center">
                    <div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center mr-3">
                      {{ getUserInitials(user) }}
                    </div>
                    <div>
                      <div class="font-medium">{{ user.full_name }}</div>
                      <div class="text-sm text-gray-500">@{{ user.username }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="flex items-center">
                    <span 
                      class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      :class="getRoleBadgeClass(user.profile?.role)"
                    >
                      {{ user.profile?.role_display || 'No Role' }}
                    </span>
                  </div>
                </td>
                <td>
                  <div>
                    <div>{{ user.email }}</div>
                    <div class="text-sm text-gray-500">{{ user.profile?.phone || 'No phone' }}</div>
                  </div>
                </td>
                <td>
                  <span 
                    class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  >
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <span v-if="user.last_login" class="text-sm">
                    {{ formatDate(user.last_login) }}
                  </span>
                  <span v-else class="text-sm text-gray-500">Never</span>
                </td>
                <td v-if="canManageUsers">
                  <div class="flex space-x-2">
                    <button 
                      @click="openEditModal(user)"
                      class="btn btn-sm btn-secondary"
                      title="Edit User"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                      </svg>
                    </button>
                    <button 
                      @click="openPermissionsModal(user)"
                      class="btn btn-sm btn-info text-white"
                      title="View Permissions"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v-2L4.257 10.257a6 6 0 017.743-7.743L15 5v2z"></path>
                      </svg>
                    </button>
                    <button 
                      v-if="user.id !== currentUser.id"
                      @click="toggleUserStatus(user)"
                      class="btn btn-sm"
                      :class="user.is_active ? 'btn-warning' : 'btn-success'"
                      :title="user.is_active ? 'Deactivate User' : 'Activate User'"
                    >
                      <svg v-if="user.is_active" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"></path>
                      </svg>
                      <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create/Edit User Modal -->
    <div v-if="showUserModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-gray-900">
                {{ editingUser ? 'Edit User' : 'Create New User' }}
              </h3>
              <p class="text-sm text-gray-500">
                {{ editingUser ? 'Update user information and permissions' : 'Add a new team member to your system' }}
              </p>
            </div>
          </div>
          <button @click="closeUserModal" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="saveUser" class="p-6">
          <!-- Error Display -->
          <div v-if="formErrors.length > 0" class="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex items-center mb-2">
              <svg class="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <h4 class="text-sm font-medium text-red-800">Please fix the following errors:</h4>
            </div>
            <ul class="list-disc list-inside text-sm text-red-700 space-y-1">
              <li v-for="error in formErrors" :key="error">{{ error }}</li>
            </ul>
          </div>

          <!-- Step 1: Basic Information -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">1</span>
              Basic Information
            </h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Username -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">
                  Username *
                  <span v-if="editingUser" class="text-gray-500">(cannot be changed)</span>
                </label>
                <div class="relative">
                  <input 
                    v-model="userForm.username" 
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    :class="{ 'bg-gray-100': editingUser, 'border-red-300': fieldErrors.username }"
                    :disabled="editingUser"
                    placeholder="Enter username"
                    @blur="validateField('username')"
                  />
                  <div v-if="!editingUser" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <svg v-if="fieldValidation.username === 'valid'" class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <svg v-else-if="fieldValidation.username === 'invalid'" class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </div>
                </div>
                <p v-if="fieldErrors.username" class="text-sm text-red-600">{{ fieldErrors.username }}</p>
                <p v-else class="text-sm text-gray-500">Unique identifier for login</p>
              </div>

              <!-- Email -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Email Address *</label>
                <div class="relative">
                  <input 
                    v-model="userForm.email" 
                    type="email"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    :class="{ 'border-red-300': fieldErrors.email }"
                    placeholder="user@example.com"
                    @blur="validateField('email')"
                  />
                  <div class="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <svg v-if="fieldValidation.email === 'valid'" class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <svg v-else-if="fieldValidation.email === 'invalid'" class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </div>
                </div>
                <p v-if="fieldErrors.email" class="text-sm text-red-600">{{ fieldErrors.email }}</p>
                <p v-else class="text-sm text-gray-500">Primary email for notifications</p>
              </div>

              <!-- First Name -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">First Name *</label>
                <input 
                  v-model="userForm.first_name" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  :class="{ 'border-red-300': fieldErrors.first_name }"
                  placeholder="John"
                  @blur="validateField('first_name')"
                />
                <p v-if="fieldErrors.first_name" class="text-sm text-red-600">{{ fieldErrors.first_name }}</p>
              </div>

              <!-- Last Name -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Last Name *</label>
                <input 
                  v-model="userForm.last_name" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  :class="{ 'border-red-300': fieldErrors.last_name }"
                  placeholder="Doe"
                  @blur="validateField('last_name')"
                />
                <p v-if="fieldErrors.last_name" class="text-sm text-red-600">{{ fieldErrors.last_name }}</p>
              </div>
            </div>
          </div>

          <!-- Step 2: Security & Access -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">2</span>
              Security & Access
            </h4>

            <!-- Passwords (only for new users) -->
            <div v-if="!editingUser" class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Password *</label>
                <div class="relative">
                  <input 
                    v-model="userForm.password" 
                    :type="showPassword ? 'text' : 'password'"
                    class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    :class="{ 'border-red-300': fieldErrors.password }"
                    placeholder="Create a strong password"
                    @input="validateField('password')"
                  />
                  <button 
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    <svg v-if="!showPassword" class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                    </svg>
                    <svg v-else class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
                    </svg>
                  </button>
                </div>
                <!-- Password strength indicator -->
                <div class="w-full bg-gray-200 rounded-full h-1.5">
                  <div 
                    class="h-1.5 rounded-full transition-all"
                    :class="getPasswordStrengthClass()"
                    :style="{ width: passwordStrength + '%' }"
                  ></div>
                </div>
                <p v-if="fieldErrors.password" class="text-sm text-red-600">{{ fieldErrors.password }}</p>
                <p v-else class="text-sm text-gray-500">{{ getPasswordStrengthText() }}</p>
              </div>

              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Confirm Password *</label>
                <div class="relative">
                  <input 
                    v-model="userForm.confirm_password" 
                    :type="showConfirmPassword ? 'text' : 'password'"
                    class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    :class="{ 'border-red-300': fieldErrors.confirm_password }"
                    placeholder="Confirm your password"
                    @blur="validateField('confirm_password')"
                  />
                  <button 
                    type="button"
                    @click="showConfirmPassword = !showConfirmPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    <svg v-if="!showConfirmPassword" class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                    </svg>
                    <svg v-else class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
                    </svg>
                  </button>
                  <div class="absolute inset-y-0 right-10 pr-3 flex items-center">
                    <svg v-if="passwordsMatch && userForm.confirm_password" class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                  </div>
                </div>
                <p v-if="fieldErrors.confirm_password" class="text-sm text-red-600">{{ fieldErrors.confirm_password }}</p>
                <p v-else-if="userForm.confirm_password && !passwordsMatch" class="text-sm text-red-600">Passwords do not match</p>
                <p v-else class="text-sm text-gray-500">Re-enter password to confirm</p>
              </div>
            </div>

            <!-- Role Selection -->
            <div class="space-y-1">
              <label class="block text-sm font-medium text-gray-700">Role & Permissions *</label>
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div 
                  v-for="role in roleOptions" 
                  :key="role.value"
                  class="relative"
                >
                  <label class="block">
                    <input 
                      v-model="userForm.profile.role" 
                      :value="role.value"
                      type="radio" 
                      class="sr-only"
                      @change="validateField('role')"
                    />
                    <div 
                      class="p-4 border-2 rounded-lg cursor-pointer transition-all hover:border-blue-300"
                      :class="userForm.profile.role === role.value ? 'border-blue-500 bg-blue-50' : 'border-gray-200'"
                    >
                      <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center space-x-2">
                          <div 
                            class="w-3 h-3 rounded-full"
                            :class="role.color"
                          ></div>
                          <span class="font-medium text-gray-900">{{ role.label }}</span>
                        </div>
                        <svg v-if="userForm.profile.role === role.value" class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                      </div>
                      <p class="text-sm text-gray-600">{{ role.description }}</p>
                    </div>
                  </label>
                </div>
              </div>
              <p v-if="fieldErrors.role" class="text-sm text-red-600">{{ fieldErrors.role }}</p>
            </div>
          </div>

          <!-- Step 3: Additional Information -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">3</span>
              Additional Information
            </h4>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Phone -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Phone Number</label>
                <input 
                  v-model="userForm.profile.phone" 
                  type="tel"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="+1 (555) 123-4567"
                />
                <p class="text-sm text-gray-500">For important notifications</p>
              </div>

              <!-- Date Hired -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Date Hired</label>
                <input 
                  v-model="userForm.profile.date_hired" 
                  type="date"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                />
                <p class="text-sm text-gray-500">Employee start date</p>
              </div>

              <!-- Preferred Shift -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Preferred Shift</label>
                <select 
                  v-model="userForm.profile.preferred_shift" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                >
                  <option value="flexible">🕒 Flexible</option>
                  <option value="morning">🌅 Morning (6AM - 2PM)</option>
                  <option value="afternoon">☀️ Afternoon (2PM - 10PM)</option>
                  <option value="night">🌙 Night (10PM - 6AM)</option>
                </select>
              </div>
            </div>

            <!-- Address -->
            <div class="space-y-1 mt-6">
              <label class="block text-sm font-medium text-gray-700">Address</label>
              <textarea 
                v-model="userForm.profile.address" 
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="Enter home address..."
              ></textarea>
              <p class="text-sm text-gray-500">Home or mailing address</p>
            </div>
          </div>

          <!-- Step 4: Status & Activation -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">4</span>
              Status & Activation
            </h4>

            <div class="space-y-4">
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h5 class="font-medium text-gray-900">System Access</h5>
                  <p class="text-sm text-gray-600">Allow user to login to the system</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input v-model="userForm.is_active" type="checkbox" class="sr-only">
                  <div class="w-11 h-6 bg-gray-200 rounded-full transition-colors" :class="userForm.is_active ? 'bg-blue-600' : ''">
                    <div class="w-4 h-4 bg-white rounded-full shadow transform transition-transform" :class="userForm.is_active ? 'translate-x-6' : 'translate-x-1'"></div>
                  </div>
                </label>
              </div>

              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h5 class="font-medium text-gray-900">Employee Status</h5>
                  <p class="text-sm text-gray-600">Mark as active employee in the system</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input v-model="userForm.profile.is_active_employee" type="checkbox" class="sr-only">
                  <div class="w-11 h-6 bg-gray-200 rounded-full transition-colors" :class="userForm.profile.is_active_employee ? 'bg-blue-600' : ''">
                    <div class="w-4 h-4 bg-white rounded-full shadow transform transition-transform" :class="userForm.profile.is_active_employee ? 'translate-x-6' : 'translate-x-1'"></div>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex items-center justify-between pt-6 border-t border-gray-200">
            <button 
              type="button" 
              @click="closeUserModal" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Cancel
            </button>
            <div class="flex space-x-3">
              <button 
                v-if="editingUser" 
                type="button" 
                @click="resetPassword" 
                class="px-4 py-2 text-sm font-medium text-white bg-yellow-600 border border-transparent rounded-lg hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 transition-colors"
              >
                Reset Password
              </button>
              <button 
                type="submit" 
                :disabled="!isFormValid || loading"
                class="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
              >
                <svg v-if="loading" class="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                {{ loading ? 'Saving...' : (editingUser ? 'Update User' : 'Create User') }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Permissions Modal -->
    <div v-if="showPermissionsModal" class="modal-overlay" @click.self="closePermissionsModal">
      <div class="modal-content max-w-2xl">
        <div class="card-header">
          <h3 class="text-lg font-semibold">
            User Permissions - {{ selectedUser?.full_name }}
          </h3>
          <button @click="closePermissionsModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <div class="card-body">
          <div class="mb-4">
            <div class="flex items-center">
              <span class="text-sm font-medium">Role:</span>
              <span 
                class="ml-2 px-2 py-1 text-xs font-semibold rounded-full"
                :class="getRoleBadgeClass(selectedUser?.profile?.role)"
              >
                {{ selectedUser?.profile?.role_display }}
              </span>
            </div>
            <p class="text-sm text-gray-600 mt-1">
              {{ getRoleDescription(selectedUser?.profile?.role) }}
            </p>
          </div>

          <div class="space-y-3">
            <h4 class="font-medium">Permissions:</h4>
            <div class="grid grid-cols-2 gap-2 max-h-64 overflow-y-auto">
              <div 
                v-for="permission in selectedUser?.profile?.permissions || []" 
                :key="permission"
                class="flex items-center p-2 bg-green-50 rounded-md"
              >
                <svg class="w-4 h-4 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <span class="text-sm">{{ formatPermission(permission) }}</span>
              </div>
            </div>
            <div v-if="!selectedUser?.profile?.permissions?.length" class="text-gray-500 text-center py-4">
              No permissions assigned
            </div>
          </div>
        </div>

        <div class="card-footer">
          <button @click="closePermissionsModal" class="btn btn-secondary">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import api from '../axios'

// Reactive state
const users = ref([])
const currentUser = ref({})
const loading = ref(false)
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')

// Modal states
const showUserModal = ref(false)
const showPermissionsModal = ref(false)
const editingUser = ref(null)
const selectedUser = ref(null)

// Form data
const userForm = ref({
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  confirm_password: '',
  is_active: true,
  profile: {
    role: '',
    phone: '',
    address: '',
    date_hired: '',
    preferred_shift: 'flexible',
    is_active_employee: true
  }
})

// Validation states
const fieldErrors = ref({})
const fieldValidation = ref({})
const formErrors = ref([])
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// Role options
const roleOptions = ref([
  {
    value: 'super_admin',
    label: 'Super Admin',
    description: 'Full system access with all permissions',
    color: 'bg-purple-500'
  },
  {
    value: 'admin',
    label: 'Admin', 
    description: 'Administrative access to most features',
    color: 'bg-red-500'
  },
  {
    value: 'manager',
    label: 'Manager',
    description: 'Store manager with operational permissions',
    color: 'bg-blue-500'
  },
  {
    value: 'supervisor',
    label: 'Supervisor',
    description: 'Shift supervisor with sales and customer focus',
    color: 'bg-green-500'
  },
  {
    value: 'cashier',
    label: 'Cashier',
    description: 'Basic cashier operations',
    color: 'bg-yellow-500'
  },
  {
    value: 'inventory_clerk',
    label: 'Inventory Clerk',
    description: 'Inventory and stock management specialist',
    color: 'bg-indigo-500'
  }
])

// Computed properties
const filteredUsers = computed(() => {
  let filtered = users.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.full_name.toLowerCase().includes(query) ||
      user.username.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query)
    )
  }

  if (roleFilter.value) {
    filtered = filtered.filter(user => user.profile?.role === roleFilter.value)
  }

  if (statusFilter.value) {
    const isActive = statusFilter.value === 'active'
    filtered = filtered.filter(user => user.is_active === isActive)
  }

  return filtered
})

const canCreateUsers = computed(() => {
  return currentUser.value.profile?.can_manage_users || false
})

const canManageUsers = computed(() => {
  return currentUser.value.profile?.can_manage_users || false
})

// Password validation computed properties
const passwordStrength = computed(() => {
  const password = userForm.value.password
  if (!password) return 0
  
  let strength = 0
  if (password.length >= 8) strength += 25
  if (password.match(/[a-z]/)) strength += 25
  if (password.match(/[A-Z]/)) strength += 25
  if (password.match(/[0-9!@#$%^&*]/)) strength += 25
  
  return strength
})

const passwordsMatch = computed(() => {
  return userForm.value.password === userForm.value.confirm_password
})

const isFormValid = computed(() => {
  if (editingUser.value) {
    // For editing, check required fields except password
    return userForm.value.username && 
           userForm.value.first_name && 
           userForm.value.last_name && 
           userForm.value.email && 
           userForm.value.profile.role &&
           Object.keys(fieldErrors.value).length === 0
  } else {
    // For creating, check all required fields including password
    return userForm.value.username && 
           userForm.value.first_name && 
           userForm.value.last_name && 
           userForm.value.email && 
           userForm.value.password && 
           userForm.value.confirm_password &&
           userForm.value.profile.role &&
           passwordsMatch.value &&
           Object.keys(fieldErrors.value).length === 0
  }
})

// Methods
const loadUsers = async () => {
  try {
    loading.value = true 
    await nextTick()
    const response = await api.get('/api/users/')
    users.value = response.data
  } catch (error) {
    console.error('Error loading users:', error)
    alert('Error loading users')
  } finally { 
    await nextTick();
    loading.value = false
  }
}

const loadCurrentUser = async () => {
  try {
    const response = await api.get('/api/users/me/')
    currentUser.value = response.data
  } catch (error) {
    console.error('Error loading current user:', error)
  }
}

const openCreateModal = () => {
  editingUser.value = null
  resetForm()
  showUserModal.value = true
}

const openEditModal = (user) => {
  editingUser.value = user
  populateForm(user)
  showUserModal.value = true
}

const closeUserModal = () => {
  showUserModal.value = false
  editingUser.value = null
  resetForm()
}

const openPermissionsModal = (user) => {
  selectedUser.value = user
  showPermissionsModal.value = true
}

const closePermissionsModal = () => {
  showPermissionsModal.value = false
  selectedUser.value = null
}

const resetForm = () => {
  userForm.value = {
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirm_password: '',
    is_active: true,
    profile: {
      role: '',
      phone: '',
      address: '',
      date_hired: '',
      preferred_shift: 'flexible',
      is_active_employee: true
    }
  }
  fieldErrors.value = {}
  fieldValidation.value = {}
  formErrors.value = []
}

// Validation methods
const validateField = (fieldName) => {
  const value = fieldName === 'role' ? userForm.value.profile.role : userForm.value[fieldName]
  
  switch (fieldName) {
    case 'username':
      if (!value) {
        fieldErrors.value.username = 'Username is required'
        fieldValidation.value.username = 'invalid'
      } else if (value.length < 3) {
        fieldErrors.value.username = 'Username must be at least 3 characters'
        fieldValidation.value.username = 'invalid'
      } else {
        delete fieldErrors.value.username
        fieldValidation.value.username = 'valid'
      }
      break
      
    case 'email':
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!value) {
        fieldErrors.value.email = 'Email is required'
        fieldValidation.value.email = 'invalid'
      } else if (!emailRegex.test(value)) {
        fieldErrors.value.email = 'Please enter a valid email address'
        fieldValidation.value.email = 'invalid'
      } else {
        delete fieldErrors.value.email
        fieldValidation.value.email = 'valid'
      }
      break
      
    case 'first_name':
      if (!value) {
        fieldErrors.value.first_name = 'First name is required'
      } else {
        delete fieldErrors.value.first_name
      }
      break
      
    case 'last_name':
      if (!value) {
        fieldErrors.value.last_name = 'Last name is required'
      } else {
        delete fieldErrors.value.last_name
      }
      break
      
    case 'password':
      if (!editingUser.value) {
        if (!value) {
          fieldErrors.value.password = 'Password is required'
        } else if (value.length < 8) {
          fieldErrors.value.password = 'Password must be at least 8 characters'
        } else {
          delete fieldErrors.value.password
        }
      }
      break
      
    case 'confirm_password':
      if (!editingUser.value) {
        if (!value) {
          fieldErrors.value.confirm_password = 'Please confirm your password'
        } else if (value !== userForm.value.password) {
          fieldErrors.value.confirm_password = 'Passwords do not match'
        } else {
          delete fieldErrors.value.confirm_password
        }
      }
      break
      
    case 'role':
      if (!value) {
        fieldErrors.value.role = 'Please select a role'
      } else {
        delete fieldErrors.value.role
      }
      break
  }
}

const getPasswordStrengthClass = () => {
  const strength = passwordStrength.value
  if (strength < 25) return 'bg-red-500'
  if (strength < 50) return 'bg-yellow-500'  
  if (strength < 75) return 'bg-blue-500'
  return 'bg-green-500'
}

const getPasswordStrengthText = () => {
  const strength = passwordStrength.value
  if (strength === 0) return 'Enter a password'
  if (strength < 25) return 'Very weak password'
  if (strength < 50) return 'Weak password'
  if (strength < 75) return 'Good password'
  return 'Strong password'
}

const resetPassword = async () => {
  if (!editingUser.value) return
  
  const confirmed = confirm('Are you sure you want to reset this user\'s password? They will need to set a new password on their next login.')
  if (!confirmed) return
  
  try {
    loading.value = true 
    await nextTick()
    await api.post(`/api/users/${editingUser.value.id}/reset-password/`)
    alert('Password reset email sent to user successfully')
  } catch (error) {
    console.error('Error resetting password:', error)
    alert('Error resetting password: ' + (error.response?.data?.detail || 'Unknown error'))
  } finally { 
    await nextTick();
    loading.value = false
  }
}

const populateForm = (user) => {
  userForm.value = {
    username: user.username,
    first_name: user.first_name,
    last_name: user.last_name,
    email: user.email,
    password: '',
    confirm_password: '',
    is_active: user.is_active,
    profile: {
      role: user.profile?.role || '',
      phone: user.profile?.phone || '',
      address: user.profile?.address || '',
      date_hired: user.profile?.date_hired || '',
      preferred_shift: user.profile?.preferred_shift || 'flexible',
      is_active_employee: user.profile?.is_active_employee || true
    }
  }
}

const saveUser = async () => {
  try {
    loading.value = true 
    await nextTick()
    
    if (editingUser.value) {
      // Update user
      const response = await api.put(`/api/users/${editingUser.value.id}/`, userForm.value)
      const index = users.value.findIndex(u => u.id === editingUser.value.id)
      users.value[index] = response.data
    } else {
      // Create user
      const response = await api.post('/api/users/', userForm.value)
      users.value.push(response.data)
    }
    
    closeUserModal()
    alert(editingUser.value ? 'User updated successfully' : 'User created successfully')
  } catch (error) {
    console.error('Error saving user:', error)
    alert('Error saving user: ' + (error.response?.data?.detail || 'Unknown error'))
  } finally { 
    await nextTick();
    loading.value = false
  }
}

const toggleUserStatus = async (user) => {
  try {
    const newStatus = !user.is_active
    const response = await api.put(`/api/users/${user.id}/`, {
      ...user,
      is_active: newStatus
    })
    
    const index = users.value.findIndex(u => u.id === user.id)
    users.value[index] = response.data
    
    alert(`User ${newStatus ? 'activated' : 'deactivated'} successfully`)
  } catch (error) {
    console.error('Error updating user status:', error)
    alert('Error updating user status')
  }
}

// Utility methods
const getUserInitials = (user) => {
  if (user.first_name && user.last_name) {
    return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
  }
  return user.username[0].toUpperCase()
}

const getRoleBadgeClass = (role) => {
  const classes = {
    'super_admin': 'bg-purple-100 text-purple-800',
    'admin': 'bg-red-100 text-red-800',
    'manager': 'bg-blue-100 text-blue-800',
    'supervisor': 'bg-green-100 text-green-800',
    'cashier': 'bg-yellow-100 text-yellow-800',
    'inventory_clerk': 'bg-indigo-100 text-indigo-800'
  }
  return classes[role] || 'bg-gray-100 text-gray-800'
}

const getRoleDescription = (role) => {
  const descriptions = {
    'super_admin': 'Full system access with all permissions',
    'admin': 'Administrative access to most features',
    'manager': 'Store manager with operational permissions',
    'supervisor': 'Shift supervisor with sales and customer focus',
    'cashier': 'Basic cashier operations',
    'inventory_clerk': 'Inventory and stock management specialist'
  }
  return descriptions[role] || 'No description available'
}

const formatPermission = (permission) => {
  return permission.split('.').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

// Lifecycle
onMounted(() => {
  loadCurrentUser()
  loadUsers()
})
</script>