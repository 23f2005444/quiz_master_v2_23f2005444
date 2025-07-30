<template>
  <div class="admin-layout">
    <AdminNavbar />
    <div class="d-flex">
      <div class="d-none d-lg-block">
        <AdminSidebar />
      </div>
      
      <div class="content p-4 w-100">
        <div class="container-fluid">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
              <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                  <li class="breadcrumb-item">
                    <router-link to="/admin/subjects">Subjects</router-link>
                  </li>
                  <li class="breadcrumb-item">
                    <router-link :to="`/admin/subjects/${subject?.id}/chapters`">{{ subject?.name || 'Subject' }}</router-link>
                  </li>
                  <li class="breadcrumb-item active" aria-current="page">
                    {{ chapter?.name || 'Quizzes' }}
                  </li>
                </ol>
              </nav>
              <h1 class="h3">Quizzes - {{ chapter?.name || '' }}</h1>
              <p v-if="chapter" class="text-muted">
                {{ chapter.description }}
              </p>
            </div>
            
            <button
              @click="openCreateModal"
              class="btn btn-primary d-flex align-items-center"
            >
              <i class="bi bi-plus-lg me-2"></i> Add Quiz
            </button>
          </div>
          
          <!-- Search & Filter -->
            <div class="card mb-4 border-0 shadow-sm">
              <div class="card-body">
                <div class="row g-3">
                  <div class="col-md-6">
                    <div class="input-group">
                      <span class="input-group-text bg-white">
                        <i class="bi bi-search"></i>
                      </span>
                      <input 
                        v-model="searchQuery" 
                        type="text" 
                        class="form-control" 
                        placeholder="Search quizzes..." 
                      />
                    </div>
                  </div>
                  <div class="col-md-3">
                    <select v-model="statusFilter" class="form-select">
                      <option value="all">All Status</option>
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                      <option value="locked">Locked</option>
                      <option value="available">Available</option>
                      <option value="scheduled">Scheduled</option>
                      <option value="expired">Expired</option>
                    </select>
                  </div>
                  <div class="col-md-3 d-flex justify-content-md-end">
                    <button 
                      @click="loadQuizzes"
                      class="btn btn-outline-secondary d-flex align-items-center"
                    >
                      <i class="bi bi-arrow-repeat me-2"></i> Refresh
                    </button>
                  </div>
                </div>
              </div>
            </div>
          
          <!-- Quizzes Table -->
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
                        <th scope="col">Title</th>
                        <th scope="col">Description</th>
                        <th scope="col">Schedule</th>
                        <th scope="col">Duration</th>
                        <th scope="col">Status</th>
                        <th scope="col">Availability</th>
                        <th scope="col" class="text-end">Actions</th>
                      </tr>
                    </thead>
                  <tbody>
                    <tr v-for="quiz in filteredQuizzes" :key="quiz.id">
                      <td class="fw-medium">{{ quiz.title }}</td>
                      <td>{{ truncateText(quiz.description, 40) }}</td>
                      <td>
                        <div class="small">
                          <div>{{ formatDateTime(quiz.start_date, quiz.start_time) }}</div>
                          <div v-if="quiz.end_date" class="text-muted">
                            to {{ formatDateTime(quiz.end_date, quiz.end_time) }}
                          </div>
                        </div>
                      </td>
                      <td>{{ formatDuration(quiz.time_duration) }}</td>
                      <td>
                        <span
                          :class="[
                            'badge',
                            quiz.is_active ? 'text-bg-success' : 'text-bg-danger'
                          ]"
                        >
                          {{ quiz.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>
                        <div class="availability-status">
                          <span
                            :class="[
                              'badge',
                              getAvailabilityBadgeClass(quiz)
                            ]"
                          >
                            {{ getAvailabilityText(quiz) }}
                          </span>
                          <div v-if="getCountdownText(quiz)" class="small text-muted mt-1">
                            {{ getCountdownText(quiz) }}
                          </div>
                        </div>
                      </td>
                      <td>
                        <div class="d-flex justify-content-end gap-2">
                          <router-link 
                            :to="`/admin/quizzes/${quiz.id}/questions`"
                            class="btn btn-sm btn-outline-primary"
                            title="Manage Questions"
                          >
                            <i class="bi bi-question-circle"></i>
                          </router-link>
                          <button
                            @click="openEditModal(quiz)"
                            class="btn btn-sm btn-outline-secondary"
                            title="Edit Quiz"
                          >
                            <i class="bi bi-pencil"></i>
                          </button>
                          <button
                            @click="toggleQuizLock(quiz, !quiz.is_locked)"
                            :class="quiz.is_locked ? 'btn-outline-success' : 'btn-outline-warning'"
                            class="btn btn-sm"
                            :title="quiz.is_locked ? 'Unlock Quiz' : 'Lock Quiz'"
                          >
                            <i :class="quiz.is_locked ? 'bi-unlock' : 'bi-lock'"></i>
                          </button>
                          <button
                            @click="confirmDelete(quiz)"
                            class="btn btn-sm btn-outline-danger"
                            title="Delete Quiz"
                          >
                            <i class="bi bi-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                    
                    <tr v-if="filteredQuizzes.length === 0">
                      <td colspan="7" class="text-center py-4">
                        <div class="text-muted">
                          <i class="bi bi-search fs-4 mb-3 d-block"></i>
                          <p>No quizzes found</p>
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
    
    <!-- Enhanced Quiz Modal with Scheduling -->
    <div 
      class="modal fade" 
      id="quizModal" 
      tabindex="-1" 
      aria-labelledby="quizModalLabel" 
      aria-hidden="true"
      ref="quizModalRef"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="quizModalLabel">
              {{ isEditing ? 'Edit Quiz' : 'Add Quiz' }}
            </h5>
            <button 
              type="button" 
              class="btn-close" 
              data-bs-dismiss="modal" 
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveQuiz">
              <!-- Basic Information -->
              <div class="row mb-3">
                <div class="col-12">
                  <label for="quizTitle" class="form-label">Quiz Title</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="quizTitle" 
                    v-model="quizForm.title"
                    required
                  >
                </div>
              </div>
              
              <div class="mb-3">
                <label for="quizDescription" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="quizDescription" 
                  rows="3" 
                  v-model="quizForm.description"
                  required
                ></textarea>
              </div>
              
              <!-- Scheduling Section -->
              <h6 class="mb-3 text-primary">
                <i class="bi bi-calendar-clock me-2"></i>Quiz Scheduling
              </h6>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="startDate" class="form-label">Start Date</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    id="startDate" 
                    v-model="quizForm.start_date"
                    required
                  >
                </div>
                <div class="col-md-6">
                  <label for="startTime" class="form-label">Start Time</label>
                   <input 
                    type="time" 
                    class="form-control" 
                    id="startTime" 
                    v-model="quizForm.start_time"
                    required
                  >
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="endDate" class="form-label">End Date (Optional)</label>
                   <input 
                    type="date" 
                    class="form-control" 
                    id="endDate" 
                    v-model="quizForm.end_date"
                  >
                </div>
                <div class="col-md-6">
                  <label for="endTime" class="form-label">End Time (Optional)</label>
                  <input 
                    type="time" 
                    class="form-control" 
                    id="endTime" 
                    v-model="quizForm.end_time"
                  >
                </div>
              </div>
              
              <!-- Quiz Settings -->
              <h6 class="mb-3 text-primary">
                <i class="bi bi-gear me-2"></i>Quiz Settings
              </h6>
              
              <div class="row mb-3">
                <div class="col-md-4">
                  <label for="quizDuration" class="form-label">Duration (minutes)</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="quizDuration" 
                    v-model="quizForm.time_duration"
                    min="1"
                    required
                  >
                </div>
                <div class="col-md-4">
                  <label for="quizPassing" class="form-label">Passing Score (%)</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="quizPassing" 
                    v-model="quizForm.passing_score"
                    min="0"
                    max="100"
                    required
                  >
                </div>
                <div class="col-md-4">
                  <label for="quizTotal" class="form-label">Total Marks</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="quizTotal" 
                    v-model="quizForm.total_marks"
                    min="1"
                    required
                  >
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <div class="form-check form-switch">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      role="switch" 
                      id="autoLock" 
                      v-model="quizForm.auto_lock_after_expiry"
                    >
                    <label class="form-check-label" for="autoLock">
                      Auto-lock after expiry
                    </label>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-check form-switch">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      role="switch" 
                      id="quizStatus" 
                      v-model="quizForm.is_active"
                    >
                    <label class="form-check-label" for="quizStatus">
                      {{ quizForm.is_active ? 'Active' : 'Inactive' }}
                    </label>
                  </div>
                </div>
              </div>
              
              <div class="d-flex justify-content-end">
                <button 
                  type="button" 
                  class="btn btn-outline-secondary me-2" 
                  data-bs-dismiss="modal"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  class="btn btn-primary" 
                  :disabled="isSubmitting"
                >
                  <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {{ isEditing ? 'Update' : 'Create' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal remains the same -->
    <div 
      class="modal fade" 
      id="deleteModal" 
      tabindex="-1" 
      aria-hidden="true" 
      ref="deleteModalRef"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Deletion</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete quiz "<strong>{{ quizToDelete?.title }}</strong>"?</p>
            <p class="text-warning mb-1">⚠️ This will also delete:</p>
            <ul class="text-warning mb-2">
              <li>All questions in this quiz</li>
              <li>All quiz attempts and scores</li>
            </ul>
            <p class="text-danger mb-0">This action cannot be undone.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-danger" 
              @click="deleteQuiz" 
              :disabled="isDeleting"
            >
              <span v-if="isDeleting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import * as bootstrap from 'bootstrap'
import { ref, computed, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'
import { useRoute } from 'vue-router'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import { formatDistanceToNow, format, parseISO, isAfter, isBefore } from 'date-fns'

const api = useApi()
const route = useRoute()
const chapterId = parseInt(route.params.id)

const loading = ref(true)
const chapter = ref(null)
const subject = ref(null)
const quizzes = ref([])
const searchQuery = ref('')
const statusFilter = ref('all')
const isEditing = ref(false)
const isSubmitting = ref(false)
const isDeleting = ref(false)
const quizToDelete = ref(null)

// Modal references
const quizModalRef = ref(null)
const deleteModalRef = ref(null)
let quizModalInstance = null
let deleteModalInstance = null

const today = new Date().toISOString().split('T')[0]
const currentTime = new Date().toTimeString().slice(0, 5)

const quizForm = ref({
  id: null,
  title: '',
  description: '',
  start_date: today,
  start_time: currentTime,
  end_date: '',
  end_time: '',
  time_duration: 30,
  passing_score: 60,
  total_marks: 100,
  auto_lock_after_expiry: true,
  is_active: true
})

const filteredQuizzes = computed(() => {
  let filtered = [...quizzes.value]
  
  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      quiz => quiz.title.toLowerCase().includes(query) ||
              quiz.description.toLowerCase().includes(query)
    )
  }
  
  // Apply status filter
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(quiz => {
      switch (statusFilter.value) {
        case 'active':
          return quiz.is_active
        case 'inactive':
          return !quiz.is_active
        case 'locked':
          return quiz.is_locked
        case 'available':
          return quiz.is_available
        case 'scheduled':
          return quiz.time_until_start !== null
        case 'expired':
          return quiz.end_date && quiz.end_time && isQuizExpired(quiz)
        default:
          return true
      }
    })
  }
  
  return filtered
})

onMounted(async () => {
  try {
    await Promise.all([loadChapter(), loadQuizzes()])
    
    setTimeout(() => {
      if (quizModalRef.value) {
        quizModalInstance = new bootstrap.Modal(quizModalRef.value)
      }
      
      if (deleteModalRef.value) {
        deleteModalInstance = new bootstrap.Modal(deleteModalRef.value)
      }
    }, 100)
  } catch (error) {
    console.error('Error in onMounted:', error)
  }
})

const loadChapter = async () => {
  try {
    const response = await api.get(`/admin/chapters/${chapterId}`)
    chapter.value = response.data
    
    if (chapter.value && chapter.value.subject_id) {
      const subjectResponse = await api.get(`/admin/subjects/${chapter.value.subject_id}`)
      subject.value = subjectResponse.data
    }
  } catch (error) {
    console.error('Error loading chapter:', error)
  }
}

const loadQuizzes = async () => {
  loading.value = true
  try {
    const response = await api.get(`/admin/chapters/${chapterId}/quizzes`)
    quizzes.value = response.data
  } catch (error) {
    console.error('Error loading quizzes:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEditing.value = false
  resetForm()
  
  if (quizModalInstance) {
    quizModalInstance.show()
  }
}

const openEditModal = (quiz) => {
  isEditing.value = true
  quizForm.value = {
    id: quiz.id,
    title: quiz.title,
    description: quiz.description,
    start_date: quiz.start_date || today,
    start_time: quiz.start_time || currentTime,
    end_date: quiz.end_date || '',
    end_time: quiz.end_time || '',
    time_duration: parseInt(quiz.time_duration) || 30,
    passing_score: parseInt(quiz.passing_score) || 60,
    total_marks: parseInt(quiz.total_marks) || 100,
    auto_lock_after_expiry: quiz.auto_lock_after_expiry !== false, // Default to true
    is_active: quiz.is_active !== false // Default to true
  }
  
  if (quizModalInstance) {
    quizModalInstance.show()
  }
}

const saveQuiz = async () => {
  isSubmitting.value = true
  
  try {
    const formattedData = {
      title: quizForm.value.title,
      description: quizForm.value.description,
      start_date: quizForm.value.start_date,
      start_time: quizForm.value.start_time,
      end_date: quizForm.value.end_date || null,
      end_time: quizForm.value.end_time || null,
      time_duration: parseInt(quizForm.value.time_duration),
      passing_score: parseInt(quizForm.value.passing_score),
      total_marks: parseInt(quizForm.value.total_marks),
      auto_lock_after_expiry: Boolean(quizForm.value.auto_lock_after_expiry),
      is_active: Boolean(quizForm.value.is_active)
    }
    
    
    if (isEditing.value) {
      await api.put(`/admin/quizzes/${quizForm.value.id}`, formattedData)
    } else {
      await api.post(`/admin/chapters/${chapterId}/quizzes`, formattedData)
    }
    
    await loadQuizzes()
    
    if (quizModalInstance) {
      quizModalInstance.hide()
    }
  } catch (error) {
    console.error('Error saving quiz:', error)
    
    // Show more specific error message
    const errorMessage = error.response?.data?.msg || error.message || 'Failed to save quiz'
    alert(`Error: ${errorMessage}`)
  } finally {
    isSubmitting.value = false
  }
}

const toggleQuizLock = async (quiz, lockState) => {
  try {
    const endpoint = lockState ? 'lock' : 'unlock'
    await api.put(`/admin/quizzes/${quiz.id}/${endpoint}`)
    await loadQuizzes()
  } catch (error) {
    console.error('Error toggling quiz lock:', error)
    alert('Failed to toggle quiz lock. Please try again.')
  }
}

const resetForm = () => {
  quizForm.value = {
    id: null,
    title: '',
    description: '',
    start_date: today,
    start_time: currentTime,
    end_date: '',
    end_time: '',
    time_duration: 30,
    passing_score: 60,
    total_marks: 100,
    auto_lock_after_expiry: true,
    is_active: true
  }
}

const getAvailabilityBadgeClass = (quiz) => {
  if (quiz.is_locked) return 'text-bg-warning'
  if (quiz.is_available) return 'text-bg-success'
  if (quiz.time_until_start) return 'text-bg-info'
  if (isQuizExpired(quiz)) return 'text-bg-danger'
  return 'text-bg-secondary'
}

const getAvailabilityText = (quiz) => {
  if (quiz.is_locked) return 'Locked'
  if (quiz.is_available) return 'Available'
  if (quiz.time_until_start) return 'Scheduled'
  if (isQuizExpired(quiz)) return 'Expired'
  return 'Inactive'
}

const getCountdownText = (quiz) => {
  if (quiz.time_until_start) {
    return `Starts in ${quiz.time_until_start}`
  }
  if (quiz.time_until_end) {
    return `Ends in ${quiz.time_until_end}`
  }
  return ''
}

const isQuizExpired = (quiz) => {
  if (!quiz.end_date || !quiz.end_time) return false
  const now = new Date()
  const endDateTime = new Date(`${quiz.end_date}T${quiz.end_time}`)
  return isAfter(now, endDateTime)
}

const formatDateTime = (date, time) => {
  if (!date) return 'Not set'
  try {
    const dateTimeStr = time ? `${date}T${time}` : date
    return format(parseISO(dateTimeStr), 'MMM dd, yyyy HH:mm')
  } catch (e) {
    return `${date} ${time || ''}`
  }
}

const formatDuration = (minutes) => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  
  if (hours === 0) {
    return `${mins} min${mins !== 1 ? 's' : ''}`
  } else {
    return `${hours} hr${hours !== 1 ? 's' : ''} ${mins} min${mins !== 1 ? 's' : ''}`
  }
}

const truncateText = (text, maxLength) => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const confirmDelete = (quiz) => {
  quizToDelete.value = quiz
  
  if (deleteModalInstance) {
    deleteModalInstance.show()
  } else if (deleteModalRef.value) {
    deleteModalInstance = new bootstrap.Modal(deleteModalRef.value)
    deleteModalInstance.show()
  }
}

const deleteQuiz = async () => {
  if (!quizToDelete.value) return
  
  isDeleting.value = true
  
  try {
    await api.delete(`/admin/quizzes/${quizToDelete.value.id}`)
    await loadQuizzes()
    
    // Close the modal
    if (deleteModalInstance) {
      deleteModalInstance.hide()
    } else if (deleteModalRef.value) {
      const newModal = new bootstrap.Modal(deleteModalRef.value)
      newModal.hide()
    }
  } catch (error) {
    console.error('Error deleting quiz:', error)
    alert('Failed to delete quiz. Please try again.')
  } finally {
    isDeleting.value = false
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

.availability-status {
  min-width: 120px;
}

.table th {
  font-weight: 600;
}

.btn-group-sm > .btn,
.btn-sm {
  padding: 0.25rem 0.5rem;
}

@media (max-width: 992px) {
  .content {
    min-height: auto;
  }
}
</style>