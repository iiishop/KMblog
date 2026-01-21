<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import config from '@/config';
import '../color.css';

// Sample menu items; you can replace them with data from an API or other source
const menuItems = ref([
  { name: 'Home', link: '/' },
  { name: 'About', link: '#' },
  { name: 'Archive', link: '/archive' },
  { name: 'Categories', link: '/category' },
  { name: 'Tags', link: '/tags' }
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
          <router-link :to="item.link" class="nav-link">{{ item.name }}</router-link>
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
  padding: 1rem 3rem;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  /* 初始去圆角，类似现代App顶部 */
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  /* 极细分割线 */
}

/* 滚动后的灵动胶囊形态 */
.header-menu.scrolled {
  width: 90%;
  /* 悬浮居中 */
  left: 5%;
  top: 1rem;
  padding: 0.8rem 2.5rem;
  border-radius: 50px;
  /* 胶囊圆角 */
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow:
    0 10px 40px -10px rgba(0, 0, 0, 0.08),
    0 2px 10px rgba(0, 0, 0, 0.05);
}

.logo {
  font-size: 1.6rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, var(--logo-text-color), #666);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  /* 渐变文字 */
  user-select: none;
  position: relative;
  cursor: pointer;
}

/* Logo 旁边的小装饰点 */
.logo::after {
  content: '';
  position: absolute;
  right: -12px;
  top: 5px;
  width: 6px;
  height: 6px;
  background: var(--nav-link-hover-background-color, #ff6b6b);
  border-radius: 50%;
  box-shadow: 0 0 10px var(--nav-link-hover-background-color, #ff6b6b);
  animation: pulseLogo 3s infinite;
}

@keyframes pulseLogo {

  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }

  50% {
    transform: scale(1.5);
    opacity: 0.6;
  }
}

/* Hamburger icon container */
.hamburger {
  display: none;
  flex-direction: column;
  gap: 6px;
  /* 增加间距 */
  cursor: pointer;
  padding: 5px;
  transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.hamburger:hover {
  transform: scale(1.1);
}

.line {
  width: 28px;
  height: 3px;
  background-color: var(--hamburger-line-color);
  border-radius: 3px;
  /* 圆角线框 */
  transition: 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  /* 有回弹动画 */
}

/* Animation for hamburger lines when toggling */
.line1-animate {
  transform: rotate(45deg) translate(5px, 8px);
  width: 32px;
  /* 选中时变长 */
}

.line2-animate {
  opacity: 0;
  transform: translateX(-10px);
}

.line3-animate {
  transform: rotate(-45deg) translate(5px, -8px);
  width: 32px;
}

/* Navigation */
.nav-links {
  display: flex;
  gap: 0.5rem;
  /* 间距拉近，由padding撑开 */
  transition: all 0.4s ease-in-out;
}

.nav-links ul {
  display: flex;
  list-style: none;
  align-items: center;
  gap: 1.5rem;
  /* 列表项间距 */
}

.nav-item {
  position: relative;
}

/* --- 极简主义下划线/背景动画效果 --- */
.nav-link {
  padding: 0.6rem 1rem;
  color: var(--nav-link-color);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  border-radius: 12px;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
  cursor: pointer;
}

/* 悬停时的“磁吸”胶囊背景 */
.nav-link::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--nav-link-hover-background-color, rgba(0, 0, 0, 0.05));
  border-radius: 12px;
  z-index: -1;
  transform: scale(0.6);
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-link:hover::before {
  opacity: 1;
  transform: scale(1);
}

.nav-link:hover {
  transform: translateY(-2px);
  /* 轻微上浮 */
  color: var(--logo-text-color);
  /* 悬停颜色加深 */
}

/* 选中态/Active Link (可选，如果路由匹配会自动加上router-link-active类) */
.router-link-active.nav-link {
  color: var(--logo-text-color);
}

.router-link-active.nav-link::after {
  content: '';
  position: absolute;
  bottom: 6px;
  left: 50%;
  width: 4px;
  height: 4px;
  background: currentColor;
  border-radius: 50%;
  transform: translateX(-50%);
}

@media (max-width: 768px) {
  .hamburger {
    display: flex;
  }

  /* 移动端菜单：高级侧滑抽屉 */
  .nav-links {
    position: fixed;
    /* 改为fixed全屏遮罩 */
    top: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    height: 100vh;
    width: 100%;
    max-width: 300px;
    /* 限制最大宽度 */
    flex-direction: column;
    transform: translateX(100%);
    padding-top: 6rem;
    box-shadow: -10px 0 30px rgba(0, 0, 0, 0.1);
    z-index: 999;
  }

  .nav-links ul {
    flex-direction: column;
    gap: 2rem;
    align-items: center;
    /* 居中对齐 */
    width: 100%;
  }

  .nav-links.active {
    transform: translateX(0);
    transition: transform 0.5s cubic-bezier(0.19, 1, 0.22, 1);
  }

  .nav-link {
    font-size: 1.2rem;
    /* 移动端字体加大 */
  }
}
</style>