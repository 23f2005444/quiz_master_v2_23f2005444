<template>
  <div class="admin-layout">
    <AdminNavbar />
    <div class="d-flex">
      <div class="d-none d-lg-block">
        <AdminSidebar />
      </div>
      
      <div class="content p-4 w-100">
        <div class="container-fluid">
          <h1 class="h3 mb-4">Dashboard</h1>
          
          <div v-if="loading" class="d-flex justify-content-center my-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <div v-else>
            <!-- Stats Cards -->
            <div class="row g-4 mb-4">
              <div class="col-md-6 col-xl-3">
                <DashboardCard 
                  title="Total Users" 
                  :value="stats.users_count" 
                  icon="bi-people-fill" 
                  color="#4f46e5" 
                />
              </div>
              <div class="col-md-6 col-xl-3">
                <DashboardCard 
                  title="Subjects" 
                  :value="stats.subjects_count" 
                  icon="bi-book-fill" 
                  color="#0891b2" 
                />
              </div>
              <div class="col-md-6 col-xl-3">
                <DashboardCard 
                  title="Quizzes" 
                  :value="stats.quizzes_count" 
                  icon="bi-card-checklist" 
                  color="#ca8a04" 
                />
              </div>
              <div class="col-md-6 col-xl-3">
                <DashboardCard 
                  title="Questions" 
                  :value="stats.questions_count" 
                  icon="bi-question-circle-fill" 
                  color="#16a34a" 
                />
              </div>
            </div>
            
            <!-- Recent Subjects -->
            <div class="card mb-4 shadow-sm border-0">
              <div class="card-header bg-white py-3">
                <h5 class="mb-0">Recent Subjects</h5>
              </div>
              <div class="card-body p-0">
                <div class="table-responsive">
                  <table class="table table-hover mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Status</th>
                        <th>Created At</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="subject in recentSubjects" :key="subject.id">
                        <td class="fw-medium">{{ subject.name }}</td>
                        <td>{{ truncateText(subject.description, 50) }}</td>
                        <td>
                          <span
                            :class="[
                              'badge',
                              subject.is_active ? 'text-bg-success' : 'text-bg-danger'
                            ]"
                          >
                            {{ subject.is_active ? 'Active' : 'Inactive' }}
                          </span>
                        </td>
                        <td>{{ formatDate(subject.created_at) }}</td>
                      </tr>
                      <tr v-if="recentSubjects.length === 0">
                        <td colspan="4" class="text-center py-3 text-muted">
                          No subjects found
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="card-footer bg-white border-top py-3">
                <router-link to="/admin/subjects" class="btn btn-sm btn-primary">
                  View All Subjects
                </router-link>
              </div>
            </div>
            
            <!-- Recent Users -->
            <div class="card shadow-sm border-0">
              <div class="card-header bg-white py-3">
                <h5 class="mb-0">Recent Users</h5>
              </div>
              <div class="card-body p-0">
                <div class="table-responsive">
                  <table class="table table-hover mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Qualification</th>
                        <th>Joined Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="user in recentUsers" :key="user.id">
                        <td class="fw-medium">{{ user.full_name }}</td>
                        <td>{{ user.email }}</td>
                        <td>{{ user.qualification }}</td>
                        <td>{{ formatDate(user.created_at) }}</td>
                      </tr>
                      <tr v-if="recentUsers.length === 0">
                        <td colspan="4" class="text-center py-3 text-muted">
                          No users found
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="card-footer bg-white border-top py-3">
                <router-link to="/admin/users" class="btn btn-sm btn-primary">
                  View All Users
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import DashboardCard from '@/components/admin/DashboardCard.vue'
import { useApi } from '@/composables/useApi'
import { formatDistanceToNow } from 'date-fns'

const api = useApi()
const loading = ref(true)
const stats = ref({
  users_count: 0,
  subjects_count: 0,
  chapters_count: 0,
  quizzes_count: 0,
  questions_count: 0
})

const recentSubjects = ref([])
const recentUsers = ref([])

onMounted(async () => {
  try {
    // Debug token
    const token = localStorage.getItem('token')
    
    if (token) {
      try {
        const base64Url = token.split('.')[1]
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
        const payload = JSON.parse(window.atob(base64))
        
        const testResponse = await api.get('/admin/debug-token')
      } catch (e) {
      }
    }
    
    const dashboardResponse = await api.get('/admin/dashboard')
    stats.value = dashboardResponse.data

    const subjectsResponse = await api.get('/admin/subjects')
    recentSubjects.value = subjectsResponse.data.slice(0, 5)

    const usersResponse = await api.get('/admin/users')
    recentUsers.value = usersResponse.data.slice(0, 5)

  } catch (error) {
  } finally {
    loading.value = false
  }
})

const truncateText = (text, maxLength) => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const formatDate = (dateString) => {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true })
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
</style>