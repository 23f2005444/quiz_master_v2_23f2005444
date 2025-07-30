<template>
  <div class="admin-layout">
    <AdminNavbar />
    <div class="d-flex">
      <div class="d-none d-lg-block">
        <AdminSidebar />
      </div>
      
      <div class="content p-4 w-100">
        <div class="container-fluid">
          <h1 class="h3 mb-4">Email Tasks Management</h1>
          
          <div class="row g-4">
            <!-- Daily Reminders Card -->
            <div class="col-12 col-lg-6">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-header bg-white py-3">
                  <h5 class="mb-0">
                    <i class="bi bi-bell me-2"></i>
                    Daily Quiz Reminders
                  </h5>
                </div>
                <div class="card-body p-4">
                  <p class="text-muted">
                    Send reminders to users about available quizzes.
                  </p>
                  
                  <div v-if="dailyTaskStatus" class="alert" :class="getStatusClass(dailyTaskStatus)">
                    <div class="d-flex align-items-center">
                      <div v-if="dailyTaskStatus.state === 'PENDING' || dailyTaskStatus.state === 'STARTED'" class="spinner-border spinner-border-sm me-2" role="status"></div>
                      <i v-else-if="dailyTaskStatus.state === 'SUCCESS'" class="bi bi-check-circle-fill me-2"></i>
                      <i v-else-if="dailyTaskStatus.state === 'FAILURE'" class="bi bi-exclamation-triangle-fill me-2"></i>
                      <div>
                        <div class="fw-bold">Status: {{ dailyTaskStatus.state }}</div>
                        <div v-if="dailyTaskStatus.state === 'SUCCESS' && dailyTaskStatus.result" class="small">
                          {{ dailyTaskStatus.result.message }}
                        </div>
                        <div v-else-if="dailyTaskStatus.error" class="small">
                          Error: {{ dailyTaskStatus.error }}
                        </div>
                        <div v-else class="small">
                          {{ dailyTaskStatus.status || 'Processing...' }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="card-footer bg-white py-3 border-top">
                  <button 
                    @click="triggerDailyReminders"
                    class="btn btn-primary" 
                    :disabled="isTriggering.daily"
                  >
                    <span v-if="isTriggering.daily" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    <i v-else class="bi bi-send me-2"></i>
                    Send Daily Reminders Now
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Monthly Reports Card -->
            <div class="col-12 col-lg-6">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-header bg-white py-3">
                  <h5 class="mb-0">
                    <i class="bi bi-file-earmark-bar-graph me-2"></i>
                    Monthly Activity Reports
                  </h5>
                </div>
                <div class="card-body p-4">
                  <p class="text-muted">
                    Generate and send monthly performance reports to all users.
                  </p>
                  
                  <div v-if="monthlyTaskStatus" class="alert" :class="getStatusClass(monthlyTaskStatus)">
                    <div class="d-flex align-items-center">
                      <div v-if="monthlyTaskStatus.state === 'PENDING' || monthlyTaskStatus.state === 'STARTED'" class="spinner-border spinner-border-sm me-2" role="status"></div>
                      <i v-else-if="monthlyTaskStatus.state === 'SUCCESS'" class="bi bi-check-circle-fill me-2"></i>
                      <i v-else-if="monthlyTaskStatus.state === 'FAILURE'" class="bi bi-exclamation-triangle-fill me-2"></i>
                      <div>
                        <div class="fw-bold">Status: {{ monthlyTaskStatus.state }}</div>
                        <div v-if="monthlyTaskStatus.state === 'SUCCESS' && monthlyTaskStatus.result" class="small">
                          {{ monthlyTaskStatus.result.message }}
                        </div>
                        <div v-else-if="monthlyTaskStatus.error" class="small">
                          Error: {{ monthlyTaskStatus.error }}
                        </div>
                        <div v-else class="small">
                          {{ monthlyTaskStatus.status || 'Processing...' }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="card-footer bg-white py-3 border-top">
                  <button 
                    @click="triggerMonthlyReports"
                    class="btn btn-primary" 
                    :disabled="isTriggering.monthly"
                  >
                    <span v-if="isTriggering.monthly" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    <i v-else class="bi bi-send me-2"></i>
                    Send Monthly Reports Now
                  </button>
                </div>
              </div>
            </div>
            
            <!-- MailHog Info Card -->
            <div class="col-12">
              <div class="card border-0 shadow-sm">
                <div class="card-header bg-white py-3">
                  <h5 class="mb-0">
                    <i class="bi bi-envelope me-2"></i>
                    Email Testing with MailHog
                  </h5>
                </div>
                <div class="card-body p-4">
                  <div class="alert alert-info">
                    <i class="bi bi-info-circle me-2"></i>
                    <strong>Check your emails in MailHog:</strong> 
                    <a href="http://localhost:8025" target="_blank" class="fw-bold">Open MailHog Web Interface</a>
                  </div>
                  <p>All emails are captured by MailHog and can be viewed in the web interface. No real emails are sent during development.</p>
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
import { ref } from 'vue'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import { useApi } from '@/composables/useApi'

const api = useApi()
const isTriggering = ref({ daily: false, monthly: false })
const dailyTaskId = ref(null)
const monthlyTaskId = ref(null)
const dailyTaskStatus = ref(null)
const monthlyTaskStatus = ref(null)
const pollingIntervals = ref({ daily: null, monthly: null })

// Trigger daily reminders task
const triggerDailyReminders = async () => {
  isTriggering.value.daily = true
  try {
    console.log('Triggering daily reminders...')
    const response = await api.post('/admin/trigger-daily-reminders')
    dailyTaskId.value = response.data.task_id
    
    // Start polling for status
    pollTaskStatus('daily', dailyTaskId.value)
  } catch (error) {
    console.error('Error triggering daily reminders:', error)
    alert('Failed to trigger daily reminders: ' + (error.response?.data?.message || error.message))
  } finally {
    isTriggering.value.daily = false
  }
}

// Trigger monthly reports task
const triggerMonthlyReports = async () => {
  isTriggering.value.monthly = true
  try {
    console.log('Triggering monthly reports...')
    const response = await api.post('/admin/trigger-monthly-reports')
    monthlyTaskId.value = response.data.task_id
    
    // Start polling for status
    pollTaskStatus('monthly', monthlyTaskId.value)
  } catch (error) {
    console.error('Error triggering monthly reports:', error)
    alert('Failed to trigger monthly reports: ' + (error.response?.data?.message || error.message))
  } finally {
    isTriggering.value.monthly = false
  }
}

// Poll task status
const pollTaskStatus = (taskType, taskId) => {
  // Clear any existing interval
  if (pollingIntervals.value[taskType]) {
    clearInterval(pollingIntervals.value[taskType])
  }
  
  // Set up new polling interval
  pollingIntervals.value[taskType] = setInterval(async () => {
    try {
      const response = await api.get(`/admin/email-tasks/status/${taskId}`)
      
      if (taskType === 'daily') {
        dailyTaskStatus.value = response.data
      } else {
        monthlyTaskStatus.value = response.data
      }
      
      console.log(`${taskType} task status:`, response.data)
      
      // If task is completed or failed, stop polling
      if (['SUCCESS', 'FAILURE', 'REVOKED'].includes(response.data.state)) {
        clearInterval(pollingIntervals.value[taskType])
        pollingIntervals.value[taskType] = null
      }
    } catch (error) {
      console.error(`Error polling ${taskType} task status:`, error)
      clearInterval(pollingIntervals.value[taskType])
      pollingIntervals.value[taskType] = null
    }
  }, 2000) // Poll every 2 seconds
}

// Get appropriate alert class based on task status
const getStatusClass = (status) => {
  if (!status) return 'alert-secondary'
  
  switch (status.state) {
    case 'SUCCESS':
      return 'alert-success'
    case 'FAILURE':
    case 'REVOKED':
      return 'alert-danger'
    case 'PENDING':
    case 'STARTED':
    case 'PROGRESS':
      return 'alert-info'
    default:
      return 'alert-secondary'
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