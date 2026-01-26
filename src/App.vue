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
    <router-view />
  </div>
</template>

<style>
/* Apply theme variables to the app root */
#app {
  background-color: var(--theme-body-bg);
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
</style>