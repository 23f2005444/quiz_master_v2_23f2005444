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
                    <router-link :to="`/admin/subjects/${subject?.id}/chapters`">
                      {{ subject?.name || 'Chapters' }}
                    </router-link>
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
                      <th scope="col">Date</th>
                      <th scope="col">Duration</th>
                      <th scope="col">Passing Score</th>
                      <th scope="col">Total Marks</th>
                      <th scope="col">Status</th>
                      <th scope="col" class="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="quiz in filteredQuizzes" :key="quiz.id">
                      <td class="fw-medium">{{ quiz.title }}</td>
                      <td>{{ formatDateSimple(quiz.date_of_quiz) }}</td>
                      <td>{{ formatDuration(quiz.time_duration) }}</td>
                      <td>{{ quiz.passing_score }}</td>
                      <td>{{ quiz.total_marks }}</td>
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
                        <div class="d-flex justify-content-end gap-2">
                          <router-link 
                            :to="`/admin/quizzes/${quiz.id}/questions`"
                            class="btn btn-sm btn-outline-primary"
                            title="Manage Questions"
                          >
                            <i class="bi bi-list-ul"></i>
                          </router-link>
                          <button
                            @click="openEditModal(quiz)"
                            class="btn btn-sm btn-outline-secondary"
                            title="Edit Quiz"
                          >
                            <i class="bi bi-pencil"></i>
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
    
    <!-- Quiz Modal -->
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
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="quizDate" class="form-label">Date</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    id="quizDate" 
                    v-model="quizForm.date_of_quiz"
                    required
                  >
                </div>
                <div class="col-md-6">
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
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="quizPassing" class="form-label">Passing Score</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="quizPassing" 
                    v-model="quizForm.passing_score"
                    min="1"
                    :max="quizForm.total_marks"
                    required
                  >
                </div>
                <div class="col-md-6">
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
              
              <div class="form-check form-switch mb-3">
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
    
    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" aria-hidden="true" ref="deleteModalRef">
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
import { formatDistanceToNow, format } from 'date-fns'

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

const quizForm = ref({
  id: null,
  title: '',
  description: '',
  date_of_quiz: today, // Already a string in YYYY-MM-DD format
  time_duration: 30,   // Ensure this is a number
  passing_score: 60,   // Ensure this is a number
  total_marks: 100,    // Ensure this is a number
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
    const isActive = statusFilter.value === 'active'
    filtered = filtered.filter(quiz => quiz.is_active === isActive)
  }
  
  return filtered
})

onMounted(async () => {
  try {
    await Promise.all([loadChapter(), loadQuizzes()])
    
    // Initialize Bootstrap modals after a small delay to ensure DOM is ready
    setTimeout(() => {
      if (quizModalRef.value) {
        quizModalInstance = new bootstrap.Modal(quizModalRef.value)
      }
      
      if (deleteModalRef.value) {
        deleteModalInstance = new bootstrap.Modal(deleteModalRef.value)
      }
    }, 100);
  } catch (error) {
    console.error('Error in onMounted:', error)
  }
})

const loadChapter = async () => {
  try {
    const response = await api.get(`/admin/chapters/${chapterId}`)
    chapter.value = response.data
    
    // Load subject info
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
    quizModalInstance.show();
  } else if (quizModalRef.value) {
    quizModalInstance = new bootstrap.Modal(quizModalRef.value);
    quizModalInstance.show();
  }
}

const openEditModal = (quiz) => {
  isEditing.value = true
  quizForm.value = {
    id: quiz.id,
    title: quiz.title,
    description: quiz.description,
    date_of_quiz: quiz.date_of_quiz.split('T')[0],
    time_duration: quiz.time_duration,
    passing_score: quiz.passing_score,
    total_marks: quiz.total_marks,
    is_active: quiz.is_active
  }
  
  if (quizModalInstance) {
    quizModalInstance.show();
  } else if (quizModalRef.value) {
    quizModalInstance = new bootstrap.Modal(quizModalRef.value);
    quizModalInstance.show();
  }
}

const confirmDelete = (quiz) => {
  quizToDelete.value = quiz
  
  if (deleteModalInstance) {
    deleteModalInstance.show();
  } else if (deleteModalRef.value) {
    deleteModalInstance = new bootstrap.Modal(deleteModalRef.value);
    deleteModalInstance.show();
  }
}

const saveQuiz = async () => {
  isSubmitting.value = true
  
  try {
    // Format the date properly for SQLite
    const formattedData = {
      ...quizForm.value,
      // Make sure date is in ISO format 'YYYY-MM-DD'
      date_of_quiz: quizForm.value.date_of_quiz,
      // Ensure these are numbers, not strings
      time_duration: parseInt(quizForm.value.time_duration),
      passing_score: parseInt(quizForm.value.passing_score),
      total_marks: parseInt(quizForm.value.total_marks)
    }
    
    if (isEditing.value) {
      await api.put(`/admin/quizzes/${formattedData.id}`, formattedData)
    } else {
      await api.post(`/admin/chapters/${chapterId}/quizzes`, formattedData)
    }
    
    await loadQuizzes()
    
    // Close the modal using the instance directly
    if (quizModalInstance) {
      quizModalInstance.hide();
    } else if (quizModalRef.value) {
      // Try to create a new instance if none exists
      const newModal = new bootstrap.Modal(quizModalRef.value);
      newModal.hide();
    } else {
      // Manual fallback
      const modalElement = document.querySelector('#quizModal');
      if (modalElement) {
        modalElement.classList.remove('show');
        modalElement.style.display = 'none';
        document.body.classList.remove('modal-open');
        
        // Remove backdrop
        const backdrops = document.getElementsByClassName('modal-backdrop');
        if (backdrops.length > 0) {
          for (let i = 0; i < backdrops.length; i++) {
            if (backdrops[i].parentNode) {
              backdrops[i].parentNode.removeChild(backdrops[i]);
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('Error saving quiz:', error)
    alert('Failed to save quiz. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

const deleteQuiz = async () => {
  if (!quizToDelete.value) return
  
  isDeleting.value = true
  
  try {
    await api.delete(`/admin/quizzes/${quizToDelete.value.id}`)
    await loadQuizzes()
    
    // Close the modal using the instance directly
    if (deleteModalInstance) {
      deleteModalInstance.hide();
    } else if (deleteModalRef.value) {
      // Try to create a new instance if none exists
      const newModal = new bootstrap.Modal(deleteModalRef.value);
      newModal.hide();
    } else {
      // Manual fallback
      const modalElement = document.querySelector('#deleteModal');
      if (modalElement) {
        modalElement.classList.remove('show');
        modalElement.style.display = 'none';
        document.body.classList.remove('modal-open');
        
        // Remove backdrop
        const backdrops = document.getElementsByClassName('modal-backdrop');
        if (backdrops.length > 0) {
          for (let i = 0; i < backdrops.length; i++) {
            if (backdrops[i].parentNode) {
              backdrops[i].parentNode.removeChild(backdrops[i]);
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('Error deleting quiz:', error)
    alert('Failed to delete quiz. Please try again.')
  } finally {
    isDeleting.value = false
  }
}

const resetForm = () => {
  quizForm.value = {
    id: null,
    title: '',
    description: '',
    date_of_quiz: new Date().toISOString().split('T')[0], // Always get today's date
    time_duration: 30,
    passing_score: 60,
    total_marks: 100,
    is_active: true
  }
}

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

const formatDateSimple = (dateString) => {
  try {
    return format(new Date(dateString), 'MMM dd, yyyy')
  } catch (e) {
    return dateString
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

.btn-group-sm > .btn,
.btn-sm {
  padding: 0.25rem 0.5rem;
}
</style>