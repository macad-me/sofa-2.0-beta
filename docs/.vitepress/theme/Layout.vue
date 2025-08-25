<template>
  <div class="sofa-app">
    <CustomNavBar />
    <div class="layout-container">
      <!-- Sidebar for non-home pages -->
      <aside v-if="showSidebar" class="sidebar">
        <VPSidebar />
      </aside>
      
      <!-- Main content -->
      <main class="main-content" :class="{ 'with-sidebar': showSidebar }">
        <Content />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useData, Content } from 'vitepress'
import { VPSidebar } from 'vitepress/theme'
import CustomNavBar from './components/CustomNavBar.vue'

const { page, frontmatter } = useData()

const showSidebar = computed(() => {
  // Don't show sidebar on home page or if explicitly disabled
  return page.value.relativePath !== 'index.md' && frontmatter.value.sidebar !== false
})
</script>

<style scoped>
.sofa-app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-container {
  flex: 1;
  display: flex;
}

.sidebar {
  width: 272px;
  background: var(--vp-c-bg-soft);
  border-right: 1px solid var(--vp-c-divider);
  overflow-y: auto;
  position: sticky;
  top: 64px;
  height: calc(100vh - 64px);
}

.main-content {
  flex: 1;
  min-width: 0;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.main-content > * {
  width: 100%;
}

.main-content.with-sidebar {
  max-width: calc(100vw - 272px);
}

/* Mobile responsive */
@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
    position: static;
    border-right: none;
    border-bottom: 1px solid var(--vp-c-divider);
  }
  
  .main-content.with-sidebar {
    max-width: 100%;
  }
  
  .main-content {
    padding: 1rem;
  }
}
</style>