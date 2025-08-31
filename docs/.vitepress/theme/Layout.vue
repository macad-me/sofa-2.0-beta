<template>
  <div>
    <!-- Custom navbar at the top -->
    <CustomNavBar />
    
    <!-- VitePress default layout -->
    <DefaultTheme.Layout />
  </div>
</template>

<script setup>
import DefaultTheme from 'vitepress/theme'
import CustomNavBar from './components/CustomNavBar.vue'
</script>

<style>
/* Hide default VitePress navbar */
.VPNav {
  display: none !important;
}

/* Ensure custom navbar stays at top */
.custom-nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: 64px;
  background: var(--vp-c-bg);
  border-bottom: 1px solid var(--vp-c-divider);
}

/* Adjust content and sidebar for custom navbar height */
.VPContent {
  padding-top: 64px !important;
}

.VPSidebar {
  top: 64px !important;
  height: calc(100vh - 64px) !important;
}

/* Hide sidebar on home page */
.layout-home .VPSidebar {
  display: none !important;
}

/* Ensure doc content doesn't overlap navbar */
.VPDoc {
  padding-top: 2rem !important;
}
</style>