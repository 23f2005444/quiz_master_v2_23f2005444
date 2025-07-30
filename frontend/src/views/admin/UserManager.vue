<template>
  <div class="admin-layout">
    <AdminNavbar />
    <div class="d-flex">
      <div class="d-none d-lg-block">
        <AdminSidebar />
      </div>
      
      <div class="content p-4 w-100">
        <div class="container-fluid">
          <h1 class="h3 mb-4">Users Management</h1>
          
          <!-- Search & Filter -->
          <div class="card mb-4 border-0 shadow-sm">
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-8">
                  <div class="input-group">
                    <span class="input-group-text bg-white">
                      <i class="bi bi-search"></i>
                    </span>
                    <input 
                      v-model="searchQuery" 
                      type="text" 
                      class="form-control" 
                      placeholder="Search by name or email..." 
                    />
                  </div>
                </div>
                <div class="col-md-4 d-flex justify-content-md-end">
                  <button 
                    @click="loadUsers" 
                    class="btn btn-outline-secondary d-flex align-items-center"
                  >
                    <i class="bi bi-arrow-repeat me-2"></i> Refresh
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Users Table -->
          <div class="card border-0 shadow-sm">
            <div class="card-body p-0">
              <div v-if="loading" class="text-center p-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              
              <div v-else class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                  <thead class="table-light">
                    <tr>
                      <th scope="col">Full Name</th>
                      <th scope="col">Email</th>
                      <th scope="col">Qualification</th>
                      <th scope="col">Date of Birth</th>
                      <th scope="col" class="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="user in filteredUsers" :key="user.id">
                      <td class="fw-medium">{{ user.full_name }}</td>
                      <td>{{ user.email }}</td>
                      <td>{{ user.qualification }}</td>
                      <td>{{ formatDateSimple(user.date_of_birth) }}</td>
                      <td>{{ formatDate(user.created_at) }}</td>
                      <td>
                        <div class="d-flex justify-content-end gap-2">
                          <button 
                            @click="viewUserDetails(user)"
                            class="btn btn-sm btn-outline-primary"
                            title="View Details"
                          >
                            <i class="bi bi-eye"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                    
                    <tr v-if="filteredUsers.length === 0">
                      <td colspan="6" class="text-center py-4">
                        <div class="text-muted">
                          <i class="bi bi-search fs-4 mb-3 d-block"></i>
                          <p>No users found</p>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- User Details Modal -->
    <div 
      class="modal fade" 
      id="userDetailsModal" 
      tabindex="-1" 
      aria-hidden="true" 
      ref="userModal"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">User Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedUser" class="user-details">
              <div class="d-flex justify-content-center mb-4">
                <div class="avatar-lg">
                  <div class="avatar-circle">
                    {{ userInitials }}
                  </div>
                </div>
              </div>
              
              <div class="user-info mb-4">
                <h4 class="text-center mb-1">{{ selectedUser.full_name }}</h4>
                <p class="text-center text-muted mb-0">{{ selectedUser.email }}</p>
              </div>
              
              <div class="list-group">
                <div class="list-group-item">
                  <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">Qualification</h6>
                    <span>{{ selectedUser.qualification }}</span>
                  </div>
                </div>
                <div class="list-group-item">
                  <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">Date of Birth</h6>
                    <span>{{ formatDateSimple(selectedUser.date_of_birth) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import { formatDistanceToNow, format } from 'date-fns'
import { Modal } from 'bootstrap'

const api = useApi()
const loading = ref(true)
const users = ref([])
const searchQuery = ref('')
const selectedUser = ref(null)
const userModal = ref(null)

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(
    user => user.full_name.toLowerCase().includes(query) ||
            user.email.toLowerCase().includes(query)
  )
})

const userInitials = computed(() => {
  if (!selectedUser.value) return ''
  
  const names = selectedUser.value.full_name.split(' ')
  if (names.length >= 2) {
    return `${names[0][0]}${names[1][0]}`.toUpperCase()
  }
  return names[0][0].toUpperCase()
})

onMounted(async () => {
  await loadUsers()
  
  // Initialize Bootstrap modal
  userModal.value = new Modal(document.getElementById('userDetailsModal'))
})

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/users')
    users.value = response.data
  } catch (error) {
    console.error('Error loading users:', error)
  } finally {
    loading.value = false
  }
}

const viewUserDetails = (user) => {
  selectedUser.value = user
  userModal.value.show()
}

const formatDate = (dateString) => {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true })
  } catch (e) {
    return dateString
  }
}

const formatDateSimple = (dateString) => {
  try {
    return format(new Date(dateString), 'MMM dd, yyyy')
  } catch (e) {
    return dateString
  }
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background-color: #f9fafb;
}

.content {
  min-height: calc(100vh - 56px);
}

@media (max-width: 992px) {
  .content {
    min-height: auto;
  }
}

.table th {
  font-weight: 600;
}

.avatar-lg {
  width: 80px;
  height: 80px;
}

.avatar-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: #4f46e5;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 600;
}

.user-info {
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 1rem;
}

.list-group-item {
  padding: 0.75rem 1rem;
}

.list-group-item h6 {
  color: #6b7280;
  font-weight: 600;
  margin-bottom: 0;
}
</style>