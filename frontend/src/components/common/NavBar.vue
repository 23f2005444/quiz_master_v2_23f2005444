<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom sticky-top">
    <div class="container">
      <!-- Brand -->
      <RouterLink class="navbar-brand d-flex align-items-center" to="/">
        <div class="nav-logo me-2">
          <i class="bi bi-mortarboard-fill text-primary"></i>
        </div>
        <span class="fw-bold">QuizMaster</span>
      </RouterLink>

      <!-- Mobile Toggle -->
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Nav Links -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav mx-auto">
          <li class="nav-item">
            <RouterLink class="nav-link" to="/">Home</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/subjects">Subjects</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/about">About</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/contact">Contact</RouterLink>
          </li>
        </ul>

        <!-- Auth Buttons -->
        <div class="nav-buttons d-flex gap-2">
          <RouterLink to="/login" class="btn btn-outline-primary">
            Login
          </RouterLink>
          <RouterLink to="/register" class="btn btn-primary">
            Sign Up
          </RouterLink>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
  background-color: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px);
}

.nav-logo {
  width: 36px;
  height: 36px;
  background-color: var(--bs-primary-bg-subtle);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}

.nav-link {
  padding: 0.5rem 1rem !important;
  font-weight: 500;
  color: var(--bs-gray-700) !important;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--bs-primary) !important;
  background-color: var(--bs-primary-bg-subtle);
}

.btn {
  padding: 0.5rem 1.25rem;
  font-weight: 500;
  border-radius: 6px;
}

@media (max-width: 991.98px) {
  .navbar-collapse {
    padding: 1rem 0;
  }

  .nav-buttons {
    margin-top: 1rem;
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>