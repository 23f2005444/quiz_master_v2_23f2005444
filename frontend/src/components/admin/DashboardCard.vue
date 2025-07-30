<template>
  <div class="card h-100 border-0 shadow-sm">
    <div class="card-body">
      <div class="d-flex align-items-center mb-3">
        <div class="icon-wrapper" :style="{ backgroundColor: iconBgColor }">
          <i :class="['bi', icon]"></i>
        </div>
        <div class="ms-3">
          <h6 class="card-subtitle mb-1 text-muted">{{ title }}</h6>
          <h2 class="card-title mb-0 fw-bold">{{ value }}</h2>
        </div>
      </div>
      
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: '#4338ca'
  }
})

const iconBgColor = computed(() => {
  return `${props.color}20` 
})
</script>

<style scoped>
.card {
  border-radius: 0.75rem;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  font-size: 1.5rem;
}

.icon-wrapper i {
  color: v-bind('color');
}

h2 {
  font-size: 1.75rem;
}
</style>