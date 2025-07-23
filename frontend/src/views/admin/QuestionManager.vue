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
                    <router-link :to="chapter && chapter.subject_id ? `/admin/subjects/${chapter.subject_id}/chapters` : '/admin/subjects'">
                      {{ subject?.name || 'Chapters' }}
                    </router-link>
                  </li>
                  <li class="breadcrumb-item">
                    <router-link :to="quiz && quiz.chapter_id ? `/admin/chapters/${quiz.chapter_id}/quizzes` : '/admin/subjects'">
                      {{ chapter?.name || 'Quizzes' }}
                    </router-link>
                  </li>
                  <li class="breadcrumb-item active" aria-current="page">
                    {{ quiz?.title || 'Questions' }}
                  </li>
                </ol>
              </nav>
              <h1 class="h3">Questions - {{ quiz?.title || '' }}</h1>
              <p v-if="quiz" class="text-muted">
                {{ quiz.description }}
              </p>
              <div v-if="quiz" class="d-flex flex-wrap gap-3 mt-3">
                <div class="badge bg-light text-dark p-2">
                  <i class="bi bi-calendar me-2"></i> Date: {{ formatDateSimple(quiz.date_of_quiz) }}
                </div>
                <div class="badge bg-light text-dark p-2">
                  <i class="bi bi-clock me-2"></i> Duration: {{ formatDuration(quiz.time_duration) }}
                </div>
                <div class="badge bg-light text-dark p-2">
                  <i class="bi bi-check-circle me-2"></i> Passing: {{ quiz.passing_score }}
                </div>
                <div class="badge bg-light text-dark p-2">
                  <i class="bi bi-award me-2"></i> Total Marks: {{ quiz.total_marks }}
                </div>
              </div>
            </div>
            
            <button
              @click="openCreateModal"
              class="btn btn-primary d-flex align-items-center"
            >
              <i class="bi bi-plus-lg me-2"></i> Add Question
            </button>
          </div>
          
          <!-- Search -->
          <div class="card mb-4 border-0 shadow-sm">
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-9">
                  <div class="input-group">
                    <span class="input-group-text bg-white">
                      <i class="bi bi-search"></i>
                    </span>
                    <input 
                      v-model="searchQuery" 
                      type="text" 
                      class="form-control" 
                      placeholder="Search questions..." 
                    />
                  </div>
                </div>
                <div class="col-md-3 d-flex justify-content-md-end">
                  <button 
                    @click="loadQuestions" 
                    class="btn btn-outline-secondary d-flex align-items-center"
                  >
                    <i class="bi bi-arrow-repeat me-2"></i> Refresh
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Questions List -->
          <div v-if="loading" class="text-center p-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <div v-else>
            <div v-if="filteredQuestions.length === 0" class="text-center py-5">
              <div class="text-muted">
                <i class="bi bi-question-circle fs-1 mb-3 d-block"></i>
                <h5>No Questions Found</h5>
                <p>Start by adding questions to this quiz</p>
              </div>
            </div>
            
            <div v-else class="question-list">
              <div v-for="(question, index) in filteredQuestions" :key="question.id" class="card mb-4 border-0 shadow-sm">
                <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
                  <h5 class="mb-0">Question {{ index + 1 }}</h5>
                  <div>
                    <span class="badge bg-primary me-2">{{ question.marks }} marks</span>
                    <div class="btn-group">
                      <button 
                        @click="openEditModal(question)" 
                        class="btn btn-sm btn-outline-secondary"
                        title="Edit Question"
                      >
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button 
                        @click="confirmDelete(question)" 
                        class="btn btn-sm btn-outline-danger"
                        title="Delete Question"
                      >
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
                  </div>
                </div>
                <div class="card-body">
                  <p class="card-text question-text mb-4">{{ question.question_text }}</p>
                  
                  <div class="options-list">
                    <div 
                      v-for="i in 4" 
                      :key="i" 
                      class="option-item mb-2 p-3" 
                      :class="{ 'correct-option': question.correct_option === i }"
                    >
                      <div class="d-flex align-items-center">
                        <div 
                          class="option-label me-3" 
                          :class="{ 'option-label-correct': question.correct_option === i }"
                        >
                          {{ ['A', 'B', 'C', 'D'][i-1] }}
                        </div>
                        <div>{{ question['option_' + i] }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Question Modal -->
    <div 
      class="modal fade" 
      id="questionModal" 
      tabindex="-1" 
      aria-labelledby="questionModalLabel" 
      aria-hidden="true"
      ref="questionModalRef"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="questionModalLabel">
              {{ isEditing ? 'Edit Question' : 'Add Question' }}
            </h5>
            <button 
              type="button" 
              class="btn-close" 
              data-bs-dismiss="modal" 
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveQuestion">
              <div class="mb-3">
                <label for="questionText" class="form-label">Question</label>
                <textarea 
                  class="form-control" 
                  id="questionText" 
                  rows="3" 
                  v-model="questionForm.question_text"
                  required
                ></textarea>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Options</label>
                <div v-for="i in 4" :key="i" class="input-group mb-2">
                  <span class="input-group-text">{{ ['A', 'B', 'C', 'D'][i-1] }}</span>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="questionForm['option_' + i]"
                    :placeholder="`Option ${['A', 'B', 'C', 'D'][i-1]}`"
                    required
                  >
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="correctOption" class="form-label">Correct Option</label>
                  <select 
                    class="form-select" 
                    id="correctOption" 
                    v-model="questionForm.correct_option"
                    required
                  >
                    <option :value="1">Option A</option>
                    <option :value="2">Option B</option>
                    <option :value="3">Option C</option>
                    <option :value="4">Option D</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label for="marks" class="form-label">Marks</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="marks" 
                    v-model="questionForm.marks"
                    min="1"
                    required
                  >
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
    
    <!-- Delete Confirmation Modal -->
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
            <p>Are you sure you want to delete this question?</p>
            <p class="text-danger mb-0">This action cannot be undone.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-danger" 
              @click="deleteQuestion" 
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
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '@/composables/useApi'
import { useRoute, useRouter } from 'vue-router'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import { format } from 'date-fns'

const api = useApi()
const route = useRoute()
const router = useRouter()
const quizId = parseInt(route.params.id)

const loading = ref(true)
const quiz = ref(null)
const chapter = ref(null)
const subject = ref(null)
const questions = ref([])
const searchQuery = ref('')

const isEditing = ref(false)
const isSubmitting = ref(false)
const isDeleting = ref(false)
const questionToDelete = ref(null)

// Modal references
const questionModalRef = ref(null)
const deleteModalRef = ref(null)
let questionModalInstance = null
let deleteModalInstance = null

const questionForm = ref({
  id: null,
  question_text: '',
  option_1: '',
  option_2: '',
  option_3: '',
  option_4: '',
  correct_option: 1,
  marks: 1
})

const filteredQuestions = computed(() => {
  if (!searchQuery.value) return questions.value
  
  const query = searchQuery.value.toLowerCase()
  return questions.value.filter(
    question => question.question_text.toLowerCase().includes(query)
  )
})

onMounted(async () => {
  try {
    if (!quizId || isNaN(quizId)) {
      console.error('Invalid quiz ID:', quizId)
      loading.value = false
      router.push('/admin/subjects')
      return
    }
    
    await Promise.all([loadQuiz(), loadQuestions()])
    
    // Initialize Bootstrap modals after a small delay to ensure DOM is ready
    setTimeout(() => {
      if (questionModalRef.value) {
        questionModalInstance = new bootstrap.Modal(questionModalRef.value)
      }
      
      if (deleteModalRef.value) {
        deleteModalInstance = new bootstrap.Modal(deleteModalRef.value)
      }
    }, 100)
  } catch (error) {
    console.error('Error in onMounted:', error)
    loading.value = false
  }
})

const loadQuiz = async () => {
  try {
    if (!quizId || isNaN(quizId)) {
      console.error('Invalid quiz ID')
      return
    }
    
    const response = await api.get(`/admin/quizzes/${quizId}`)
    quiz.value = response.data
    
    // Load chapter info only if quiz is loaded successfully
    if (quiz.value && quiz.value.chapter_id) {
      const chapterResponse = await api.get(`/admin/chapters/${quiz.value.chapter_id}`)
      chapter.value = chapterResponse.data
      
      // Load subject info if chapter is loaded successfully
      if (chapter.value && chapter.value.subject_id) {
        const subjectResponse = await api.get(`/admin/subjects/${chapter.value.subject_id}`)
        subject.value = subjectResponse.data
      }
    }
  } catch (error) {
    console.error('Error loading quiz:', error)
  }
}

const loadQuestions = async () => {
  loading.value = true
  try {
    if (!quizId || isNaN(quizId)) {
      console.error('Invalid quiz ID')
      loading.value = false
      return
    }
    
    const response = await api.get(`/admin/quizzes/${quizId}/questions`)
    questions.value = response.data
  } catch (error) {
    console.error('Error loading questions:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEditing.value = false
  resetForm()
  
  if (questionModalInstance) {
    questionModalInstance.show()
  } else if (questionModalRef.value) {
    questionModalInstance = new bootstrap.Modal(questionModalRef.value)
    questionModalInstance.show()
  }
}

const openEditModal = (question) => {
  isEditing.value = true
  questionForm.value = {
    id: question.id,
    question_text: question.question_text,
    option_1: question.option_1,
    option_2: question.option_2,
    option_3: question.option_3,
    option_4: question.option_4,
    correct_option: parseInt(question.correct_option),
    marks: parseInt(question.marks)
  }
  
  if (questionModalInstance) {
    questionModalInstance.show()
  } else if (questionModalRef.value) {
    questionModalInstance = new bootstrap.Modal(questionModalRef.value)
    questionModalInstance.show()
  }
}

const confirmDelete = (question) => {
  questionToDelete.value = question
  
  if (deleteModalInstance) {
    deleteModalInstance.show()
  } else if (deleteModalRef.value) {
    deleteModalInstance = new bootstrap.Modal(deleteModalRef.value)
    deleteModalInstance.show()
  }
}

const saveQuestion = async () => {
  isSubmitting.value = true
  
  try {
    // Ensure numeric fields are numbers
    const formattedData = {
      ...questionForm.value,
      correct_option: parseInt(questionForm.value.correct_option),
      marks: parseInt(questionForm.value.marks)
    }
    
    if (isEditing.value) {
      await api.put(`/admin/questions/${formattedData.id}`, formattedData)
    } else {
      await api.post(`/admin/quizzes/${quizId}/questions`, formattedData)
    }
    
    await loadQuestions()
    
    // Close the modal using the instance directly
    if (questionModalInstance) {
      questionModalInstance.hide()
    } else if (questionModalRef.value) {
      // Try to create a new instance if none exists
      const newModal = new bootstrap.Modal(questionModalRef.value)
      newModal.hide()
    } else {
      // Manual fallback
      const modalElement = document.querySelector('#questionModal')
      if (modalElement) {
        modalElement.classList.remove('show')
        modalElement.style.display = 'none'
        document.body.classList.remove('modal-open')
        
        // Remove backdrop
        const backdrops = document.getElementsByClassName('modal-backdrop')
        if (backdrops.length > 0) {
          for (let i = 0; i < backdrops.length; i++) {
            if (backdrops[i].parentNode) {
              backdrops[i].parentNode.removeChild(backdrops[i])
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('Error saving question:', error)
    alert('Failed to save question. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

const deleteQuestion = async () => {
  if (!questionToDelete.value) return
  
  isDeleting.value = true
  
  try {
    await api.delete(`/admin/questions/${questionToDelete.value.id}`)
    await loadQuestions()
    
    // Close the modal using the instance directly
    if (deleteModalInstance) {
      deleteModalInstance.hide()
    } else if (deleteModalRef.value) {
      // Try to create a new instance if none exists
      const newModal = new bootstrap.Modal(deleteModalRef.value)
      newModal.hide()
    } else {
      // Manual fallback
      const modalElement = document.querySelector('#deleteModal')
      if (modalElement) {
        modalElement.classList.remove('show')
        modalElement.style.display = 'none'
        document.body.classList.remove('modal-open')
        
        // Remove backdrop
        const backdrops = document.getElementsByClassName('modal-backdrop')
        if (backdrops.length > 0) {
          for (let i = 0; i < backdrops.length; i++) {
            if (backdrops[i].parentNode) {
              backdrops[i].parentNode.removeChild(backdrops[i])
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('Error deleting question:', error)
    alert('Failed to delete question. Please try again.')
  } finally {
    isDeleting.value = false
  }
}

const resetForm = () => {
  questionForm.value = {
    id: null,
    question_text: '',
    option_1: '',
    option_2: '',
    option_3: '',
    option_4: '',
    correct_option: 1,
    marks: 1
  }
}

const getOptionLetter = (index) => {
  return String.fromCharCode(65 + index - 1) // 1 -> A, 2 -> B, etc.
}

const formatDateSimple = (dateString) => {
  try {
    return format(new Date(dateString), 'MMM dd, yyyy')
  } catch (e) {
    console.error('Error formatting date:', e)
    return dateString
  }
}

const formatDuration = (minutes) => {
  if (!minutes) return '0 mins'
  
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

.question-text {
  font-size: 1.1rem;
  font-weight: 500;
}

.options-list {
  padding-left: 1rem;
}

.option-item {
  border-radius: 0.5rem;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
}

.correct-option {
  background-color: #ecfdf5;
  border-color: #10b981;
}

.option-label {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: #e5e7eb;
  font-weight: 600;
}

.option-label-correct {
  background-color: #10b981;
  color: white;
}

@media (max-width: 992px) {
  .content {
    min-height: auto;
  }
}
</style>