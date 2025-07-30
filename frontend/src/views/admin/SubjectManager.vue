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
            <h1 class="h3 mb-0">Subjects Management</h1>
            <button
              @click="openCreateModal"
              class="btn btn-primary d-flex align-items-center"
            >
              <i class="bi bi-plus-lg me-2"></i> Add Subject
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
                      placeholder="Search subjects..." 
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
                    @click="loadSubjects" 
                    class="btn btn-outline-secondary d-flex align-items-center"
                  >
                    <i class="bi bi-arrow-repeat me-2"></i> Refresh
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Subjects Table -->
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
                      <th scope="col">Name</th>
                      <th scope="col">Description</th>
                      <th scope="col">Status</th>
                      <th scope="col" class="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="subject in filteredSubjects" :key="subject.id">
                      <td class="fw-medium">{{ subject.name }}</td>
                      <td>{{ truncateText(subject.description, 60) }}</td>
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
                      <td>
                        <div class="d-flex justify-content-end gap-2">
                          <router-link 
                            :to="`/admin/subjects/${subject.id}/chapters`"
                            class="btn btn-sm btn-outline-primary"
                          >
                            <i class="bi bi-list-ul"></i>
                          </router-link>
                          <button
                            @click="openEditModal(subject)"
                            class="btn btn-sm btn-outline-secondary"
                          >
                            <i class="bi bi-pencil"></i>
                          </button>
                          <button
                            @click="confirmDelete(subject)"
                            class="btn btn-sm btn-outline-danger"
                          >
                            <i class="bi bi-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                    
                    <tr v-if="filteredSubjects.length === 0">
                      <td colspan="5" class="text-center py-4">
                        <div class="text-muted">
                          <i class="bi bi-search fs-4 mb-3 d-block"></i>
                          <p>No subjects found</p>
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
    
    <!-- Subject Modal -->
    <div 
      class="modal fade" 
      id="subjectModal" 
      tabindex="-1" 
      aria-labelledby="subjectModalLabel" 
      aria-hidden="true"
      ref="subjectModalRef"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="subjectModalLabel">
              {{ isEditing ? 'Edit Subject' : 'Add Subject' }}
            </h5>
            <button 
              type="button" 
              class="btn-close" 
              data-bs-dismiss="modal" 
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveSubject">
              <div class="mb-3">
                <label for="subjectName" class="form-label">Subject Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="subjectName" 
                  v-model="subjectForm.name"
                  required
                >
              </div>
              <div class="mb-3">
                <label for="subjectDescription" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="subjectDescription" 
                  rows="3" 
                  v-model="subjectForm.description"
                  required
                ></textarea>
              </div>
              <div class="form-check form-switch mb-3">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  role="switch" 
                  id="subjectStatus" 
                  v-model="subjectForm.is_active"
                >
                <label class="form-check-label" for="subjectStatus">
                  {{ subjectForm.is_active ? 'Active' : 'Inactive' }}
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
            <p>Are you sure you want to delete subject "<strong>{{ subjectToDelete?.name }}</strong>"?</p>
            <p class="text-warning mb-1">⚠️ This will also delete:</p>
            <ul class="text-warning mb-2">
              <li>All chapters in this subject</li>
              <li>All quizzes in those chapters</li>
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
              @click="deleteSubject" 
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
import AdminNavbar from '@/components/admin/AdminNavbar.vue'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import { formatDistanceToNow } from 'date-fns'

const api = useApi()
const subjectModalRef = ref(null)
const deleteModalRef = ref(null)
let subjectModalInstance = null
let deleteModalInstance = null
const loading = ref(true)
const subjects = ref([])
const searchQuery = ref('')
const statusFilter = ref('all')
const isEditing = ref(false)
const isSubmitting = ref(false)
const isDeleting = ref(false)
const subjectToDelete = ref(null)
const modal = ref(null)
const deleteModal = ref(null)

const subjectForm = ref({
  id: null,
  name: '',
  description: '',
  is_active: true
})

const filteredSubjects = computed(() => {
  let filtered = [...subjects.value]
  
  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      subject => subject.name.toLowerCase().includes(query) ||
                subject.description.toLowerCase().includes(query)
    )
  }
  
  // Apply status filter
  if (statusFilter.value !== 'all') {
    const isActive = statusFilter.value === 'active'
    filtered = filtered.filter(subject => subject.is_active === isActive)
  }
  
  return filtered
})

onMounted(async () => {
  try {
    await loadSubjects();
    
    // Use a simpler approach to initialize modals
    setTimeout(() => {
      if (subjectModalRef.value) {
        subjectModalInstance = new bootstrap.Modal(subjectModalRef.value)
      }
      
      if (deleteModalRef.value) {
        deleteModalInstance = new bootstrap.Modal(deleteModalRef.value)
      }
    }, 100);
  } catch (error) {
    console.error('Error in onMounted:', error);
  }
});

const loadSubjects = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/subjects')
    subjects.value = response.data
  } catch (error) {
    console.error('Error loading subjects:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEditing.value = false;
  resetForm();
  
  if (subjectModalInstance) {
    subjectModalInstance.show();
  } else if (subjectModalRef.value) {
    subjectModalInstance = new bootstrap.Modal(subjectModalRef.value);
    subjectModalInstance.show();
  }
};

const openEditModal = (subject) => {
  isEditing.value = true;
  subjectForm.value = {
    id: subject.id,
    name: subject.name,
    description: subject.description,
    is_active: subject.is_active
  };
  
  if (subjectModalInstance) {
    subjectModalInstance.show();
  } else if (subjectModalRef.value) {
    subjectModalInstance = new bootstrap.Modal(subjectModalRef.value);
    subjectModalInstance.show();
  }
};

// Update your confirmDelete function
const confirmDelete = (subject) => {
  subjectToDelete.value = subject;
  
  if (deleteModalInstance) {
    deleteModalInstance.show();
  } else if (deleteModalRef.value) {
    deleteModalInstance = new bootstrap.Modal(deleteModalRef.value);
    deleteModalInstance.show();
  }
};

// Update your saveSubject function
const saveSubject = async () => {
  isSubmitting.value = true;
  
  try {
    if (isEditing.value) {
      await api.put(`/admin/subjects/${subjectForm.value.id}`, subjectForm.value);
    } else {
      await api.post('/admin/subjects', subjectForm.value);
    }
    
    await loadSubjects();
    
    // Close the modal using the instance directly
    if (subjectModalInstance) {
      subjectModalInstance.hide();
    } else if (subjectModalRef.value) {
      // Try to create a new instance if none exists
      const newModal = new bootstrap.Modal(subjectModalRef.value);
      newModal.hide();
    } else {
      // Manual fallback
      const modalElement = document.querySelector('#subjectModal');
      if (modalElement) {
        modalElement.classList.remove('show');
        modalElement.style.display = 'none';
        document.body.classList.remove('modal-open');
        
        // Remove backdrop
        const backdrops = document.getElementsByClassName('modal-backdrop');
        if (backdrops.length > 0) {
          for (let i = 0; i < backdrops.length; i++) {
            document.body.removeChild(backdrops[i]);
          }
        }
      }
    }
  } catch (error) {
    console.error('Error saving subject:', error);
    alert('Failed to save subject. Please try again.');
  } finally {
    isSubmitting.value = false;
  }
};

// Update your deleteSubject function
const deleteSubject = async () => {
  if (!subjectToDelete.value) return;
  
  isDeleting.value = true;
  
  try {
    await api.delete(`/admin/subjects/${subjectToDelete.value.id}`);
    await loadSubjects();
    
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
            document.body.removeChild(backdrops[i]);
          }
        }
      }
    }
  } catch (error) {
    console.error('Error deleting subject:', error);
    alert('Failed to delete subject. Please try again.');
  } finally {
    isDeleting.value = false;
  }
};

const resetForm = () => {
  subjectForm.value = {
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