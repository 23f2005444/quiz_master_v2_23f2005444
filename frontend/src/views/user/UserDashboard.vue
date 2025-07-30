<script setup>
import UserNavbar from '@/components/user/UserNavbar.vue'
import UserSidebar from '@/components/user/UserSidebar.vue'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useApi } from '@/composables/useApi'
import { useAuth } from '@/composables/useAuth'
import { format, formatDistanceToNow } from 'date-fns'

const api = useApi()
const auth = useAuth()
const loading = ref(true)
const error = ref(null)
const sidebarVisible = ref(false)
const isMobile = ref(false)
const debugInfo = ref(null)

// Dashboard data
const stats = ref({
  totalAttempts: 0,
  averageScore: 0,
  completedQuizzes: 0,
  availableQuizzes: 0
})

// Recent data
const recentQuizzes = ref([])
const recentAttempts = ref([])
const availableSubjects = ref([])

const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value
}

const checkScreenSize = () => {
  isMobile.value = window.innerWidth < 992
  if (isMobile.value) {
    sidebarVisible.value = false
  } else {
    sidebarVisible.value = true
  }
}

// Get user from auth
const user = computed(() => {
  return auth.user || {}
})

onMounted(async () => {
  try {
    loading.value = true
    error.value = null
    
    // Debugging auth state
    const token = localStorage.getItem('token')
    debugInfo.value = {
      token: token ? `${token.substring(0, 20)}...` : 'No token',
      isAuthenticated: auth.isAuthenticated.value,
      user: auth.user,
      role: auth.role.value
    }
    
    console.log('Auth Debug Info:', {
      token: token ? 'Token exists' : 'No token',
      tokenLength: token ? token.length : 0,
      isAuthenticated: auth.isAuthenticated.value,
      user: auth.user,
      role: auth.role.value
    })
    
    // Initial screen size check
    checkScreenSize()
    
    window.addEventListener('resize', checkScreenSize)
    
    // Load dashboard data
    await loadDashboardData()
  } catch (err) {
    error.value = 'Failed to load dashboard data. Please try again.'
  } finally {
    loading.value = false
  }
})

const loadDashboardData = async () => {
  try {
    await Promise.all([
      loadStats(),
      loadRecentAttempts(),
      loadRecentQuizzes(),
      loadSubjects()
    ])
  } catch (err) {
    throw err
  }
}

const loadStats = async () => {
  try {
    const response = await api.get('/user/dashboard')
    stats.value = response.data
  } catch (err) {
  }
}

const loadRecentAttempts = async () => {
  try {
    const response = await api.get('/user/attempts/recent')
    recentAttempts.value = response.data || []
  } catch (err) {

    recentAttempts.value = []
  }
}

const loadRecentQuizzes = async () => {
  try {
    const response = await api.get('/user/quizzes/available')
    recentQuizzes.value = response.data || []
  } catch (err) {
    recentQuizzes.value = []
  }
}

const filteredAvailableQuizzes = computed(() => {
  return recentQuizzes.value.filter(quiz => quiz.is_available === true);
});

const loadSubjects = async () => {
  try {
    const response = await api.get('/subjects/details')
    availableSubjects.value = response.data || []
  } catch (err) {
    availableSubjects.value = []
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    return format(new Date(dateString), 'MMM dd, yyyy')
  } catch (e) {
    return dateString
  }
}

const formatRelativeTime = (dateString) => {
  if (!dateString) return ''
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true })
  } catch (e) {
    return dateString
  }
}

</script>

<template>
  <div class="dashboard-layout">
    <div 
      v-if="isMobile && sidebarVisible" 
      class="sidebar-backdrop"
      @click="toggleSidebar"
    ></div>
    
    <!-- Sidebar -->
    <UserSidebar 
      :class="{ 'sidebar-visible': sidebarVisible }"
      @close="sidebarVisible = false"
    />

    <!-- Main Content -->
    <div class="main-content" :class="{ 'with-sidebar': sidebarVisible && !isMobile }">
      <UserNavbar @toggle-sidebar="toggleSidebar" />

      <div class="container-fluid p-3 p-md-4">
        <!-- Welcome Header -->
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4">
          <div>
            <h2 class="mb-1">Welcome, {{ user.full_name || 'User' }}</h2>
            <p class="text-muted">Here's an overview of your learning progress</p>
          </div>
          <router-link to="/subjects" class="btn btn-primary mt-2 mt-md-0">
            <i class="bi bi-play-fill"></i> Start New Quiz
          </router-link>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Loading your dashboard...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
          <button @click="loadDashboardData" class="btn btn-outline-danger btn-sm ms-2">
            <i class="bi bi-arrow-repeat"></i> Retry
          </button>
        </div>

        <!-- Content -->
        <div v-else>
          <!-- Statistics Cards -->
          <div class="row g-3 g-md-4 mb-4">
            <div class="col-6 col-md-3">
              <div class="card bg-primary text-white h-100">
                <div class="card-body">
                  <h6 class="card-title">Quiz Attempts</h6>
                  <h2 class="card-text">{{ stats.totalAttempts }}</h2>
                  <i class="bi bi-journal-check position-absolute top-50 end-0 me-3 opacity-50" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>

            <div class="col-6 col-md-3">
              <div class="card bg-success text-white h-100">
                <div class="card-body">
                  <h6 class="card-title">Average Score</h6>
                  <h2 class="card-text">{{ stats.averageScore }}%</h2>
                  <i class="bi bi-graph-up position-absolute top-50 end-0 me-3 opacity-50" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>

            <div class="col-6 col-md-3">
              <div class="card bg-info text-white h-100">
                <div class="card-body">
                  <h6 class="card-title">Completed</h6>
                  <h2 class="card-text">{{ stats.completedQuizzes }}</h2>
                  <i class="bi bi-check-circle position-absolute top-50 end-0 me-3 opacity-50" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>

            <div class="col-6 col-md-3">
              <div class="card bg-warning text-white h-100">
                <div class="card-body">
                  <h6 class="card-title">Available</h6>
                  <h2 class="card-text">{{ availableQuizCount }}</h2>
                  <i class="bi bi-lightning position-absolute top-50 end-0 me-3 opacity-50" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Activity and Available Content -->
          <div class="row g-4">
            <!-- Recent Quiz Attempts -->
            <div class="col-12 col-lg-6">
              <div class="card h-100">
                <div class="card-header bg-white py-3">
                  <div class="d-flex justify-content-between align-items-center">
                    <h5 class="card-title mb-0">Recent Quiz Attempts</h5>
                    <router-link to="/attempts" class="btn btn-sm btn-outline-primary">View All</router-link>
                  </div>
                </div>
                <div class="card-body p-0">
                  <div class="list-group list-group-flush">
                    <div v-if="recentAttempts.length === 0" class="text-center py-4 text-muted">
                      <i class="bi bi-clipboard-x fs-1 mb-2"></i>
                      <p>No quiz attempts yet</p>
                      <router-link to="/subjects" class="btn btn-sm btn-primary">
                        Start your first quiz
                      </router-link>
                    </div>
                    
                    <router-link 
                      v-for="attempt in recentAttempts" 
                      :key="attempt.id" 
                      :to="`/attempts/${attempt.id}`"
                      class="list-group-item list-group-item-action"
                    >
                      <div class="d-flex w-100 justify-content-between align-items-start">
                        <h6 class="mb-1">{{ attempt.quiz_title }}</h6>
                        <small>{{ formatRelativeTime(attempt.created_at) }}</small>
                      </div>
                      <div class="d-flex justify-content-between align-items-center">
                        <p class="mb-1 text-muted small">{{ attempt.chapter_name }} ({{ attempt.subject_name }})</p>
                        <span 
                          :class="`badge ${attempt.score_percentage >= 60 ? 'bg-success' : 'bg-danger'}`"
                        >
                          {{ attempt.score_percentage }}%
                        </span>
                      </div>
                    </router-link>
                  </div>
                </div>
              </div>
            </div>

            <!-- Available Quizzes -->
            <div class="col-12 col-lg-6">
              <div class="card h-100">
                <div class="card-header bg-white py-3">
                  <div class="d-flex justify-content-between align-items-center">
                    <h5 class="card-title mb-0">Available Quizzes</h5>
                    <router-link to="/subjects" class="btn btn-sm btn-outline-primary">Browse All</router-link>
                  </div>
                </div>
                <div class="card-body p-0">
                  <div class="list-group list-group-flush">
                    <div v-if="recentQuizzes.length === 0" class="text-center py-4 text-muted">
                      <i class="bi bi-lightning fs-1 mb-2"></i>
                      <p>No available quizzes right now</p>
                    </div>
                    
                    <router-link 
                      v-for="quiz in filteredAvailableQuizzes" 
                      :key="quiz.id"
                      :to="`/quizzes/${quiz.id}`"
                      class="list-group-item list-group-item-action d-flex justify-content-between align-items-center p-3"
                    >
                      <div>
                        <h6 class="mb-1">{{ quiz.title }}</h6>
                        <p class="mb-1 small text-muted">{{ quiz.subject_name }} - {{ quiz.chapter_name }}</p>
                        <div class="d-flex align-items-center">
                          <span class="badge bg-primary me-2">{{ quiz.time_duration }} mins</span>
                          <span v-if="quiz.time_until_end" class="small text-danger">
                            <i class="bi bi-clock me-1"></i> Expires {{ formatRelativeTime(quiz.end_date) }}
                          </span>
                        </div>
                      </div>
                      <div>
                        <i class="bi bi-chevron-right text-muted"></i>
                      </div>
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Available Subjects -->
          <div class="mt-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h4>Available Subjects</h4>
              <router-link to="/subjects" class="btn btn-sm btn-outline-primary">View All</router-link>
            </div>
            
            <div class="row g-3 g-md-4">
              <div v-if="availableSubjects.length === 0" class="col-12 text-center py-5 text-muted">
                <i class="bi bi-journal-x fs-1 mb-3"></i>
                <h5>No subjects available</h5>
                <p>Check back later for new content</p>
              </div>
              
              <div 
                v-for="subject in availableSubjects.slice(0, 4)" 
                :key="subject.id" 
                class="col-12 col-sm-6 col-xl-3"
              >
                <router-link :to="`/subjects/${subject.id}`" class="text-decoration-none">
                  <div class="card h-100 subject-card">
                    <div class="card-body">
                      <h5 class="card-title">{{ subject.name }}</h5>
                      <p class="card-text text-muted">{{ subject.description }}</p>
                      <div class="d-flex justify-content-between mt-3">
                        <span class="badge bg-light text-dark">
                          <i class="bi bi-book me-1"></i> {{ subject.chapter_count }} chapters
                        </span>
                        <span class="badge bg-light text-dark">
                          <i class="bi bi-question-circle me-1"></i> {{ subject.quiz_count }} quizzes
                        </span>
                      </div>
                      <div class="text-primary mt-2">
                        <i class="bi bi-arrow-right me-1"></i> Explore chapters
                      </div>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-layout {
  min-height: 100vh;
  display: flex;
  width: 100%;
  position: relative;
}

.main-content {
  flex-grow: 1;
  transition: margin-left 0.3s;
  width: 100%;
}

.main-content.with-sidebar {
  margin-left: 250px;
}

.card {
  transition: transform 0.2s;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  border: none;
}

.subject-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.card-title {
  font-weight: 600;
}

.list-group-item-action:hover {
  background-color: #f8f9fa;
}

.badge {
  font-weight: 500;
  padding: 0.5em 0.75em;
}

a {
  text-decoration: none;
}

.sidebar-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1030;
}

@media (max-width: 991.98px) {
  .main-content {
    margin-left: 0 !important;
  }
  
  .sidebar-visible {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1040;
    height: 100vh;
    transform: translateX(0) !important;
  }
}

@media (max-width: 767.98px) {
  .card-body {
    padding: 1rem;
  }
  
  h2 {
    font-size: 1.5rem;
  }
  
  h4 {
    font-size: 1.2rem;
  }
}
</style>