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
                  <li class="breadcrumb-item active" aria-current="page">
                    {{ subject ? subject.name : 'Chapters' }}
                  </li>
                </ol>
              </nav>
              <h1 class="h3">Chapters - {{ subject ? subject.name : '' }}</h1>
              <p v-if="subject" class="text-muted">
                {{ subject.description }}
              </p>
            </div>
            
            <button
              @click="openCreateModal"
              class="btn btn-primary d-flex align-items-center"
            >
              <i class="bi bi-plus-lg me-2"></i> Add Chapter
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
                      placeholder="Search chapters..." 
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
                    @click="loadChapters" 
                    class="btn btn-outline-secondary d-flex align-items-center"
                  >
                    <i class="bi bi-arrow-repeat me-2"></i> Refresh
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Chapters Table -->
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
                      <th scope="col">#</th>
                      <th scope="col">Name</th>
                      <th scope="col">Description</th>
                      <th scope="col">Status</th>
                      <th scope="col" class="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="chapter in filteredChapters" :key="chapter.id">
                      <td>{{ chapter.sequence_number }}</td>
                      <td class="fw-medium">{{ chapter.name }}</td>
                      <td>{{ truncateText(chapter.description, 60) }}</td>
                      <td>
                        <span
                          :class="[
                            'badge',
                            chapter.is_active ? 'text-bg-success' : 'text-bg-danger'
                          ]"
                        >
                          {{ chapter.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>
                        <div class="d-flex justify-content-end gap-2">
                          <router-link 
                            :to="`/admin/chapters/${chapter.id}/quizzes`"
                            class="btn btn-sm btn-outline-primary"
                            title="Manage Quizzes"
                          >
                            <i class="bi bi-list-ul"></i>
                          </router-link>
                          <button
                            @click="openEditModal(chapter)"
                            class="btn btn-sm btn-outline-secondary"
                            title="Edit Chapter"
                          >
                            <i class="bi bi-pencil"></i>
                          </button>
                          <button
                            @click="confirmDelete(chapter)"
                            class="btn btn-sm btn-outline-danger"
                            title="Delete Chapter"
                          >
                            <i class="bi bi-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                    
                    <tr v-if="filteredChapters.length === 0">
                      <td colspan="6" class="text-center py-4">
                        <div class="text-muted">
                          <i class="bi bi-search fs-4 mb-3 d-block"></i>
                          <p>No chapters found</p>
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
    
    <!-- Chapter Modal -->
    <div 
      class="modal fade" 
      id="chapterModal" 
      tabindex="-1" 
      aria-labelledby="chapterModalLabel" 
      aria-hidden="true"
      ref="chapterModalRef"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="chapterModalLabel">
              {{ isEditing ? 'Edit Chapter' : 'Add Chapter' }}
            </h5>
            <button 
              type="button" 
              class="btn-close" 
              data-bs-dismiss="modal" 
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveChapter">
              <div class="mb-3">
                <label for="chapterName" class="form-label">Chapter Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="chapterName" 
                  v-model="chapterForm.name"
                  required
                >
              </div>
              <div class="mb-3">
                <label for="chapterDescription" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="chapterDescription" 
                  rows="3" 
                  v-model="chapterForm.description"
                  required
                ></textarea>
              </div>
              <div class="form-check form-switch mb-3">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  role="switch" 
                  id="chapterStatus" 
                  v-model="chapterForm.is_active"
                >
                <label class="form-check-label" for="chapterStatus">
                  {{ chapterForm.is_active ? 'Active' : 'Inactive' }}
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
            <p>Are you sure you want to delete chapter "<strong>{{ chapterToDelete?.name }}</strong>"?</p>
            <p class="text-warning mb-1">⚠️ This will also delete:</p>
            <ul class="text-warning mb-2">
              <li>All quizzes in this chapter</li>
              <li>All questions in those quizzes</li>
              <li>All quiz attempts and scores</li>
            </ul>
            <p class="text-danger mb-0">This action cannot be undone.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-danger" 
              @click="deleteChapter" 
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
import { formatDistanceToNow } from 'date-fns'

const api = useApi()
const route = useRoute()
const subjectId = parseInt(route.params.id)

const loading = ref(true)
const subject = ref(null)
const chapters = ref([])
const searchQuery = ref('')
const statusFilter = ref('all')
const isEditing = ref(false)
const isSubmitting = ref(false)
const isDeleting = ref(false)
const chapterToDelete = ref(null)

// References for bootstrap modals
const chapterModalRef = ref(null)
const deleteModalRef = ref(null)
let chapterModalInstance = null
let deleteModalInstance = null

const chapterForm = ref({
  id: null,
  name: '',
  description: '',
  is_active: true
})

const filteredChapters = computed(() => {
  let filtered = [...chapters.value]
  
  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      chapter => chapter.name.toLowerCase().includes(query) ||
                chapter.description.toLowerCase().includes(query)
    )
  }
  
  // Apply status filter
  if (statusFilter.value !== 'all') {
    const isActive = statusFilter.value === 'active'
    filtered = filtered.filter(chapter => chapter.is_active === isActive)
  }
  
  return filtered
})

onMounted(async () => {
  try {
    await Promise.all([loadSubject(), loadChapters()])
    
    // Initialize Bootstrap modals after a small delay to ensure DOM is ready
    setTimeout(() => {
      if (chapterModalRef.value) {
        chapterModalInstance = new bootstrap.Modal(chapterModalRef.value)
      }
      
      if (deleteModalRef.value) {
        deleteModalInstance = new bootstrap.Modal(deleteModalRef.value)
      }
    }, 100);
  } catch (error) {
    console.error('Error in onMounted:', error)
  }
})

const loadSubject = async () => {
  try {
    // Make sure subjectId is a valid number
    if (!subjectId || isNaN(subjectId)) {
      console.error('Invalid subject ID:', subjectId);
      // Redirect to subjects list or show error
      return;
    }
    
    const response = await api.get(`/admin/subjects/${subjectId}`);
    subject.value = response.data;
  } catch (error) {
    console.error('Error loading subject:', error);
  }
}

const loadChapters = async () => {
  loading.value = true
  try {
    const response = await api.get(`/admin/subjects/${subjectId}/chapters`)
    chapters.value = response.data
  } catch (error) {
    console.error('Error loading chapters:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEditing.value = false
  resetForm()
  
  if (chapterModalInstance) {
    chapterModalInstance.show();
  } else if (chapterModalRef.value) {
    chapterModalInstance = new bootstrap.Modal(chapterModalRef.value);
    chapterModalInstance.show();
  }
}

const openEditModal = (chapter) => {
  isEditing.value = true
  chapterForm.value = {
    id: chapter.id,
    name: chapter.name,
    description: chapter.description,
    is_active: chapter.is_active
  }
  
  if (chapterModalInstance) {
    chapterModalInstance.show();
  } else if (chapterModalRef.value) {
    chapterModalInstance = new bootstrap.Modal(chapterModalRef.value);
    chapterModalInstance.show();
  }
}

const confirmDelete = (chapter) => {
  chapterToDelete.value = chapter
  
  if (deleteModalInstance) {
    deleteModalInstance.show();
  } else if (deleteModalRef.value) {
    deleteModalInstance = new bootstrap.Modal(deleteModalRef.value);
    deleteModalInstance.show();
  }
}

const saveChapter = async () => {
  isSubmitting.value = true
  
  try {
    if (isEditing.value) {
      await api.put(`/admin/chapters/${chapterForm.value.id}`, chapterForm.value)
    } else {
      await api.post(`/admin/subjects/${subjectId}/chapters`, chapterForm.value)
    }
    
    await loadChapters()
    
    // Close the modal using the instance directly
    if (chapterModalInstance) {
      chapterModalInstance.hide();
    } else if (chapterModalRef.value) {
      // Try to create a new instance if none exists
      const newModal = new bootstrap.Modal(chapterModalRef.value);
      newModal.hide();
    } else {
      // Manual fallback
      const modalElement = document.querySelector('#chapterModal');
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
    alert('Failed to save chapter. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

const deleteChapter = async () => {
  if (!chapterToDelete.value) return
  
  isDeleting.value = true
  
  try {
    await api.delete(`/admin/chapters/${chapterToDelete.value.id}`)
    await loadChapters()
    
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
    alert('Failed to delete chapter. Please try again.')
  } finally {
    isDeleting.value = false
  }
}

const resetForm = () => {
  chapterForm.value = {
    id: null,
    name: '',
    description: '',
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