<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import config from '@/config';
import '../color.css';

// Sample menu items; you can replace them with data from an API or other source
const menuItems = ref([
  { name: 'Home', link: '#' },
  { name: 'Projects', link: '#' },
  { name: 'Blog', link: '#' },
  { name: 'Contact', link: '#' }
]);

const BlogName = ref(config.BlogName);

// State for toggling the menu open/closed (useful for mobile view)
const isMenuOpen = ref(false);

// State to track if the page is scrolled
const isScrolled = ref(false);

// Toggles the menu in mobile view
function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value;
}

// Handles the scroll event
function handleScroll() {
  isScrolled.value = window.scrollY > 0;
}

// Add event listener on mount and remove on unmount
onMounted(() => {
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<template>
  <!-- Header container -->
  <header :class="['header-menu', isScrolled ? 'scrolled' : '']">
    <div class="logo">
      <span>{{ BlogName }}</span>
    </div>

    <!-- Hamburger icon for mobile -->
    <div class="hamburger" @click="toggleMenu">
      <div :class="['line', isMenuOpen ? 'line1-animate' : '']"></div>
      <div :class="['line', isMenuOpen ? 'line2-animate' : '']"></div>
      <div :class="['line', isMenuOpen ? 'line3-animate' : '']"></div>
    </div>

    <!-- Navigation list -->
    <nav class="nav-links" :class="{ 'active': isMenuOpen }">
      <ul>
        <li v-for="(item, index) in menuItems" :key="index" class="nav-item">
          <a :href="item.link" class="nav-link">{{ item.name }}</a>
        </li>
      </ul>
    </nav>
  </header>
</template>

<style scoped>
/* Header container */
.header-menu {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  transition: all 0.4s ease-in-out;
  border-bottom-left-radius: 1rem;
  border-bottom-right-radius: 1rem;
  background: var(--header-background-color);
  backdrop-filter: blur(50px);
}

.header-menu.scrolled {
  border-radius: 2rem;
  background: var(--header-background-color-scrolled);
  box-shadow: 0 4px 15px var(--header-box-shadow);
  transform: translateY(10px) scale(0.95);
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--logo-text-color);
  user-select: none;
}

/* Hamburger icon container */
.hamburger {
  display: none;
  flex-direction: column;
  gap: 5px;
  cursor: pointer;
}

.line {
  width: 25px;
  height: 3px;
  background-color: var(--hamburger-line-color);
  transition: 0.4s ease;
}

/* Animation for hamburger lines when toggling */
.line1-animate {
  transform: rotate(-45deg) translate(-5px, 6px);
}
.line2-animate {
  opacity: 0;
}
.line3-animate {
  transform: rotate(45deg) translate(-5px, -6px);
}

/* Navigation */
.nav-links {
  display: flex;
  gap: 1rem;
  transition: all 0.4s ease-in-out;
}

.nav-links ul {
  display: flex;
  list-style: none;
}

.nav-item {
  position: relative;
}

.nav-link {
  padding: 0.5rem 0.75rem;
  color: var(--nav-link-color);
  text-decoration: none;
  font-weight: 500;
  border-radius: 5px;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background-color: var(--nav-link-hover-background-color);
  transform: scale(1.05);
}

@media (max-width: 768px) {
  .hamburger {
    display: flex;
  }

  .nav-links {
    position: absolute;
    top: 0;
    right: 0;
    background: var(--mobile-nav-background-color);
    height: 100vh;
    width: 60%;
    flex-direction: column;
    transform: translateX(100%);
    padding-top: 5rem;
    box-shadow: -2px 0 8px var(--mobile-nav-box-shadow);
  }

  .nav-links ul {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
    margin: 0 1.5rem;
  }

  .nav-links.active {
    transform: translateX(0);
    transition: transform 0.5s ease;
  }
}
</style>