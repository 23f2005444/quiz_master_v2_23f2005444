<template>
  <div class="page-layout">
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
    
    <div class="main-content" :class="{ 'with-sidebar': sidebarVisible && !isMobile }">
      <UserNavbar @toggle-sidebar="toggleSidebar" />
      
      <div class="container-fluid p-3 p-md-4">
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4">
          <div>
            <h2 class="mb-1">My Quiz Attempts</h2>
            <p class="text-muted">View all your quiz attempts and results</p>
          </div>
          <router-link to="/subjects" class="btn btn-primary mt-2 mt-md-0">
            <i class="bi bi-play-fill me-2"></i> Start New Quiz
          </router-link>
        </div>
        
        <div class="card mb-4 shadow-sm">
          <div class="card-body p-3">
            <div class="row g-3">
              <div class="col-12 col-md-5 col-lg-4">
                <div class="input-group">
                  <span class="input-group-text bg-white border-end-0">
                    <i class="bi bi-search"></i>
                  </span>
                  <input
                    type="text"
                    class="form-control border-start-0"
                    placeholder="Search quizzes..."
                    v-model="searchQuery"
                  />
                </div>
              </div>
              <div class="col-12 col-sm-6 col-md-4 col-lg-3">
                <select class="form-select" v-model="statusFilter">
                  <option value="all">All Results</option>
                  <option value="passed">Passed Quizzes</option>
                  <option value="failed">Failed Quizzes</option>
                </select>
              </div>
              <div class="col-12 col-sm-6 col-md-3 col-lg-3 d-flex">
                <button @click="loadAttempts" class="btn btn-outline-secondary ms-auto">
                  <i class="bi bi-arrow-repeat me-2"></i> Refresh
                </button>
                
                <button 
                  class="btn btn-outline-success ms-2" 
                  @click="startExport"
                  :disabled="exportState.isExporting"
                >
                  <span v-if="exportState.isExporting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  <i v-else class="bi bi-file-earmark-excel me-2"></i>
                  {{ exportState.isExporting ? 'Exporting...' : 'Export CSV' }}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Loading your attempts...</p>
        </div>
        
        <div v-else-if="filteredAttempts.length === 0" class="text-center my-5">
          <div class="empty-state">
            <i class="bi bi-clipboard-data empty-icon"></i>
            <h5>No attempts found</h5>
            <p class="text-muted mb-4">You haven't attempted any quizzes yet, or your search filters don't match any attempts.</p>
            <router-link to="/subjects" class="btn btn-primary">
              <i class="bi bi-play-fill me-2"></i> Start Your First Quiz
            </router-link>
          </div>
        </div>
        
        <div v-else>
          <!-- Desktop view -->
          <div class="table-responsive d-none d-md-block">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>Quiz</th>
                  <th>Subject</th>
                  <th>Date</th>
                  <th>Score</th>
                  <th>Time Taken</th>
                  <th>Status</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="attempt in filteredAttempts" :key="attempt.id">
                  <td>
                    <div class="fw-medium">{{ attempt.quiz_title }}</div>
                    <div class="text-muted small">{{ attempt.chapter_name }}</div>
                  </td>
                  <td>{{ attempt.subject_name }}</td>
                  <td>{{ formatDate(attempt.created_at) }}</td>
                  <td>
                    <div class="fw-medium">{{ attempt.score }}/{{ attempt.total_marks }}</div>
                    <div class="text-muted small">{{ attempt.score_percentage }}%</div>
                  </td>
                  <td>{{ formatDuration(attempt.time_taken) }}</td>
                  <td>
                    <span 
                      :class="`badge ${attempt.score_percentage >= 60 ? 'bg-success' : 'bg-danger'}`"
                    >
                      {{ attempt.score_percentage >= 60 ? 'PASSED' : 'FAILED' }}
                    </span>
                  </td>
                  <td class="text-end">
                    <router-link :to="`/attempts/${attempt.id}`" class="btn btn-sm btn-outline-primary">
                      View Results
                    </router-link>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Mobile view -->
          <div class="d-md-none">
            <div v-for="attempt in filteredAttempts" :key="attempt.id" class="card mb-3 attempt-card">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h6 class="card-title mb-0">{{ attempt.quiz_title }}</h6>
                  <span 
                    :class="`badge ${attempt.score_percentage >= 60 ? 'bg-success' : 'bg-danger'}`"
                  >
                    {{ attempt.score_percentage >= 60 ? 'PASSED' : 'FAILED' }}
                  </span>
                </div>
                <p class="card-subtitle text-muted small mb-3">
                  {{ attempt.chapter_name }} ({{ attempt.subject_name }})
                </p>
                
                <div class="d-flex justify-content-between mb-2 small">
                  <span class="text-muted">Date:</span>
                  <span>{{ formatDate(attempt.created_at) }}</span>
                </div>
                <div class="d-flex justify-content-between mb-2 small">
                  <span class="text-muted">Score:</span>
                  <span>{{ attempt.score }}/{{ attempt.total_marks }} ({{ attempt.score_percentage }}%)</span>
                </div>
                <div class="d-flex justify-content-between mb-3 small">
                  <span class="text-muted">Time Taken:</span>
                  <span>{{ formatDuration(attempt.time_taken) }}</span>
                </div>
                
                <div class="d-grid">
                  <router-link :to="`/attempts/${attempt.id}`" class="btn btn-sm btn-outline-primary">
                    <i class="bi bi-eye me-2"></i> View Results
                  </router-link>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Pagination (when there are more than 10 items) -->
          <div v-if="filteredAttempts.length > 10" class="d-flex justify-content-center mt-4">
            <nav aria-label="Quiz attempts pagination">
              <ul class="pagination">
                <li class="page-item disabled">
                  <a class="page-link" href="#" tabindex="-1" aria-disabled="true">Previous</a>
                </li>
                <li class="page-item active"><a class="page-link" href="#">1</a></li>
                <li class="page-item"><a class="page-link" href="#">2</a></li>
                <li class="page-item"><a class="page-link" href="#">3</a></li>
                <li class="page-item">
                  <a class="page-link" href="#">Next</a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
        
        <!-- Export Success Modal -->
        <div class="modal fade" id="exportSuccessModal" tabindex="-1" aria-labelledby="exportSuccessModalLabel" aria-hidden="true">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="exportSuccessModalLabel">
                  <i class="bi bi-check-circle-fill text-success me-2"></i>
                  Export Successful
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body text-center">
                <div class="mb-3">
                  <i class="bi bi-file-earmark-excel-fill text-success" style="font-size: 3rem;"></i>
                </div>
                <h6>Your quiz attempts have been exported successfully!</h6>
                <p class="text-muted mb-0">The CSV file has been downloaded to your device.</p>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Close</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import UserNavbar from '@/components/user/UserNavbar.vue'
import UserSidebar from '@/components/user/UserSidebar.vue'
import { useApi } from '@/composables/useApi'
import { format } from 'date-fns'
import * as bootstrap from 'bootstrap'

const api = useApi()
const loading = ref(true)
const attempts = ref([])
const searchQuery = ref('')
const statusFilter = ref('all')
const sidebarVisible = ref(false)
const isMobile = ref(false)

const exportState = ref({
  isExporting: false,
  error: null,
  success: false
})

const filteredAttempts = computed(() => {
  let filtered = [...attempts.value]
  
  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(attempt => 
      attempt.quiz_title.toLowerCase().includes(query) ||
      attempt.chapter_name.toLowerCase().includes(query) ||
      attempt.subject_name.toLowerCase().includes(query)
    )
  }
  
  // Apply status filter
  if (statusFilter.value === 'passed') {
    filtered = filtered.filter(attempt => attempt.score_percentage >= 60)
  } else if (statusFilter.value === 'failed') {
    filtered = filtered.filter(attempt => attempt.score_percentage < 60)
  }
  
  return filtered
})

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

onMounted(async () => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  await loadAttempts()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

const loadAttempts = async () => {
  loading.value = true
  try {
    const response = await api.get('/user/attempts')
    attempts.value = response.data || []
  } catch (error) {
    console.error('Error loading attempts:', error)
    attempts.value = []
  } finally {
    loading.value = false
  }
}

const startExport = async () => {
  if (exportState.value.isExporting) return
  
  try {
    exportState.value.isExporting = true
    exportState.value.error = null
    exportState.value.success = false
    
    
    // Check if user has any attempts to export
    if (filteredAttempts.value.length === 0) {
      alert('No quiz attempts found to export.')
      return
    }
    
    const response = await api.post('/exports/user/quiz-attempts', {}, {
      responseType: 'blob'
    })
    
    // Create download link immediately
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    // Generate filename with timestamp
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')
    const filename = `quiz_attempts_${timestamp}.csv`
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    // Show success state
    exportState.value.success = true
    showSuccessModal()
    
    
  } catch (error) {
    console.error('Export error:', error)
    exportState.value.error = error.response?.data?.error || error.message || 'Failed to export data'
    
    alert(`Export failed: ${exportState.value.error}`)
  } finally {
    exportState.value.isExporting = false
  }
}

const showSuccessModal = () => {
  try {
    const modalElement = document.getElementById('exportSuccessModal')
    if (modalElement) {
      const modal = new bootstrap.Modal(modalElement)
      modal.show()
    }
  } catch (error) {
    console.error('Error showing success modal:', error)
    // Fallback to simple alert
    alert('Export completed successfully! Your CSV file has been downloaded.')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    return format(new Date(dateString), 'MMM dd, yyyy, h:mm a')
  } catch (e) {
    return dateString
  }
}

const formatDuration = (minutes) => {
  if (!minutes || minutes <= 0) return '0 mins'
  
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  
  if (hours === 0) {
    return `${mins} min${mins !== 1 ? 's' : ''}`
  } else {
    return `${hours} hr${hours !== 1 ? 's' : ''} ${mins} min${mins !== 1 ? 's' : ''}`
  }
}
</script>

<style scoped>
.page-layout {
  min-height: 100vh;
  display: flex;
  width: 100%;
  position: relative;
}

.main-content {
  flex-grow: 1;
  transition: margin-left 0.3s;
  width: 100%;
  background-color: #f8f9fa;
}

.main-content.with-sidebar {
  margin-left: 250px;
}

.card {
  border-radius: 10px;
  border: none;
  overflow: hidden;
}

.attempt-card {
  transition: transform 0.2s;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.attempt-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.table th, .table td {
  vertical-align: middle;
}

.badge {
  font-weight: 500;
  padding: 0.5em 0.75em;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1.5rem;
  color: #dee2e6;
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
  h2 {
    font-size: 1.5rem;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  .empty-icon {
    font-size: 2.5rem;
  }
}
</style>