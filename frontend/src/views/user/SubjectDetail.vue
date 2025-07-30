<template>
  <div class="page-layout">
\    <div 
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
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Loading subject details...</p>
        </div>
        
        <div v-else>
          <nav aria-label="breadcrumb" class="mb-4">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/subjects">Subjects</router-link></li>
              <li class="breadcrumb-item active" aria-current="page">{{ subject.name }}</li>
            </ol>
          </nav>
          
          <div class="card mb-4 shadow-sm">
            <div class="card-body p-3 p-md-4">
              <h2 class="card-title mb-3">{{ subject.name }}</h2>
              <p class="card-text">{{ subject.description }}</p>
              
              <div class="mt-3">
                <span class="badge bg-light text-dark me-2">
                  <i class="bi bi-book me-1"></i> {{ chapters.length }} chapters
                </span>
                <span class="badge bg-light text-dark">
                  <i class="bi bi-calendar-date me-1"></i> Added {{ formatDate(subject.created_at) }}
                </span>
              </div>
            </div>
          </div>
          
          <h4 class="mb-4">Chapters</h4>
          
          <div v-if="chapters.length === 0" class="text-center my-5">
            <i class="bi bi-journal-x text-muted fs-1 mb-3"></i>
            <h5>No chapters available</h5>
            <p class="text-muted">This subject doesn't have any chapters yet.</p>
          </div>
          
          <div v-else class="row g-3 g-md-4">
            <div v-for="chapter in chapters" :key="chapter.id" class="col-12 col-md-6 col-lg-4">
              <div class="card h-100">
                <div class="card-body">
                  <h5 class="card-title">{{ chapter.name }}</h5>
                  <p class="card-text text-muted">{{ chapter.description }}</p>
                  <div class="d-flex justify-content-between align-items-center mt-3">
                    <span class="badge bg-light text-dark">
                      <i class="bi bi-question-circle me-1"></i> {{ chapter.quiz_count }} quizzes
                    </span>
                  </div>
                </div>
                <div class="card-footer bg-white border-top-0">
                  <router-link :to="`/chapters/${chapter.id}/quizzes`" class="btn btn-outline-primary">
                    <i class="bi bi-arrow-right me-2"></i> View Quizzes
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import UserNavbar from '@/components/user/UserNavbar.vue'
import UserSidebar from '@/components/user/UserSidebar.vue'
import { useApi } from '@/composables/useApi'
import { format } from 'date-fns'

const api = useApi()
const route = useRoute()
const subjectId = parseInt(route.params.id)

const loading = ref(true)
const subject = ref({})
const chapters = ref([])
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
    
    // Load subject details
    const subjectResponse = await api.get(`/subjects/${subjectId}`)
    subject.value = subjectResponse.data
    
    // Load chapters
    const chaptersResponse = await api.get(`/subjects/${subjectId}/chapters`)
    chapters.value = chaptersResponse.data
  } catch (error) {
    console.error('Error loading subject details:', error)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

const formatDate = (dateString) => {
  try {
    return format(new Date(dateString), 'MMM dd, yyyy')
  } catch (e) {
    return dateString
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
}

.main-content.with-sidebar {
  margin-left: 250px;
}

.breadcrumb a {
  text-decoration: none;
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
  
  .btn {
    padding: 0.375rem 0.75rem;
  }
}
</style>