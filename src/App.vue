<script setup>
import { onMounted } from 'vue';
import globalVar from './globalVar';
import config from './config';
import { themeManager } from './composables/useTheme';
import './color.css'; // Import comprehensive theme CSS

onMounted(() => {
  document.title = config.BlogName + "|" + config.ShortDesc;

  // Initialize the new theme system
  themeManager.validateThemeConfig();
  themeManager.initializeTheme();
});
</script>

<template>
  <div id="app">
    <router-view v-slot="{ Component, route }">
      <transition :name="route.meta?.transitionName || 'page'" mode="out-in">
        <div :key="route.path" class="page-container">
          <component :is="Component" v-if="Component" />
        </div>
      </transition>
    </router-view>
  </div>
</template>

<style>
/* Apply theme variables to the app root */
#app {
  color: var(--theme-body-text);
  min-height: 100vh;
  transition: var(--theme-transition-colors);
}

/* Ensure body uses theme variables */
body {
  background-color: var(--theme-body-bg);
  color: var(--theme-body-text);
  margin: 0;
  padding: 0;
}

/* Page container for transitions */
.page-container {
  width: 100%;
  min-height: 100vh;
}

/* === Page Transition Animations === */
/* Default page transition: fade + slide */
.page-enter-active,
.page-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}

/* Fade transition (faster) */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Slide transition */
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(50px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-50px);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-50px);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(50px);
}

/* Scale transition (for modal-like pages) */
.scale-enter-active,
.scale-leave-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.scale-enter-from {
  opacity: 0;
  transform: scale(0.9);
}

.scale-leave-to {
  opacity: 0;
  transform: scale(1.05);
}

/* Zoom transition (for gallery pages) */
.zoom-enter-active,
.zoom-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.zoom-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}

.zoom-leave-to {
  opacity: 0;
  transform: scale(1.1) translateY(-20px);
}
</style>