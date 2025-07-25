<template>
  <div class="page-layout">
    <!-- Overlay for mobile when sidebar is visible -->
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
            <h2 class="mb-1">Available Subjects</h2>
            <p class="text-muted">Browse all available subjects and start learning</p>
          </div>
        </div>
        
        <div class="row mb-4">
          <div class="col-12 col-md-6 col-lg-4">
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="bi bi-search"></i>
              </span>
              <input
                type="text"
                class="form-control border-start-0"
                placeholder="Search subjects..."
                v-model="searchQuery"
              />
            </div>
          </div>
        </div>
        
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Loading subjects...</p>
        </div>
        
        <div v-else-if="filteredSubjects.length === 0" class="text-center my-5">
          <i class="bi bi-journals fs-1 text-muted mb-3"></i>
          <h5>No subjects found</h5>
          <p class="text-muted">Try adjusting your search query</p>
        </div>
        
        <div v-else class="row g-3 g-md-4">
          <div v-for="subject in filteredSubjects" :key="subject.id" class="col-12 col-md-6 col-lg-4">
            <router-link :to="`/subjects/${subject.id}`" class="text-decoration-none">
              <div class="card h-100">
                <div class="card-body">
                  <h5 class="card-title">{{ subject.name }}</h5>
                  <p class="card-text">{{ subject.description }}</p>
                  <div class="d-flex justify-content-between align-items-center mt-3">
                    <span class="badge bg-light text-dark">
                      <i class="bi bi-book me-1"></i> {{ subject.chapter_count }} chapters
                    </span>
                    <span class="badge bg-light text-dark">
                      <i class="bi bi-question-circle me-1"></i> {{ subject.quiz_count }} quizzes
                    </span>
                  </div>
                </div>
                <div class="card-footer bg-white border-top-0 text-primary">
                  <i class="bi bi-arrow-right"></i> Explore chapters
                </div>
              </div>
            </router-link>
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

const api = useApi()
const loading = ref(true)
const subjects = ref([])
const searchQuery = ref('')
const sidebarVisible = ref(false)
const isMobile = ref(false)

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
  try {
    // Check screen size initially
    checkScreenSize()
    
    // Add resize listener
    window.addEventListener('resize', checkScreenSize)
    
    const response = await api.get('/subjects/details')
    subjects.value = response.data
  } catch (error) {
    console.error('Error loading subjects:', error)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

const filteredSubjects = computed(() => {
  if (!searchQuery.value) return subjects.value
  
  const query = searchQuery.value.toLowerCase()
  return subjects.value.filter(subject => 
    subject.name.toLowerCase().includes(query) || 
    subject.description.toLowerCase().includes(query)
  )
})
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

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.card-title {
  font-weight: 600;
}

.badge {
  font-weight: 500;
  padding: 0.5em 0.75em;
}

/* Sidebar backdrop overlay for mobile */
.sidebar-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1030;
}

/* Responsive styles */
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
  
  .input-group {
    width: 100%;
  }
}
</style>