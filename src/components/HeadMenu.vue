<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import config from '@/config';
import '../color.css';

// 菜单项
const menuItems = ref([
  { name: 'Home', link: '/', icon: '🏠' },
  { name: 'About', link: '/about', icon: '👤' },
  { name: 'Archive', link: '/archive', icon: '📚' },
  { name: 'Categories', link: '/category', icon: '📂' },
  { name: 'Tags', link: '/tags', icon: '🏷️' }
]);

const BlogName = ref(config.BlogName);

// 状态管理
const isMenuOpen = ref(false);
const isScrolled = ref(false);
const isSearchOpen = ref(false);
const searchQuery = ref('');
const scrollProgress = ref(0);
const isDarkMode = ref(false);

// 鼠标追踪
const mouseX = ref(0);
const mouseY = ref(0);
const headerRect = ref({ left: 0, top: 0, width: 0, height: 0 });

// Canvas 粒子效果
const particleCanvas = ref(null);
let particleAnimationFrame = null;
let particles = [];

// 粒子类
class HeaderParticle {
  constructor(canvasWidth, canvasHeight) {
    this.x = Math.random() * canvasWidth;
    this.y = Math.random() * canvasHeight;
    this.size = Math.random() * 2 + 0.5;
    this.speedX = Math.random() * 0.3 - 0.15;
    this.speedY = Math.random() * 0.3 - 0.15;
    this.opacity = Math.random() * 0.3 + 0.1;
  }

  update(canvasWidth, canvasHeight) {
    this.x += this.speedX;
    this.y += this.speedY;

    if (this.x > canvasWidth) this.x = 0;
    if (this.x < 0) this.x = canvasWidth;
    if (this.y > canvasHeight) this.y = 0;
    if (this.y < 0) this.y = canvasHeight;
  }

  draw(ctx, isDark) {
    ctx.fillStyle = isDark
      ? `rgba(200, 200, 255, ${this.opacity})`
      : `rgba(102, 126, 234, ${this.opacity})`;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fill();
  }
}

// 初始化粒子
function initParticles() {
  if (!particleCanvas.value) return;

  const canvas = particleCanvas.value;
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width;
  canvas.height = rect.height;

  particles = [];
  const particleCount = Math.floor((canvas.width * canvas.height) / 30000);
  for (let i = 0; i < particleCount; i++) {
    particles.push(new HeaderParticle(canvas.width, canvas.height));
  }
}

// 动画粒子
function animateParticles() {
  if (!particleCanvas.value) return;

  const canvas = particleCanvas.value;
  const ctx = canvas.getContext('2d');

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  particles.forEach(particle => {
    particle.update(canvas.width, canvas.height);
    particle.draw(ctx, isDarkMode.value);
  });

  particleAnimationFrame = requestAnimationFrame(animateParticles);
}

// 切换菜单
function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value;
  if (isMenuOpen.value) {
    isSearchOpen.value = false;
  }
}

// 切换搜索
function toggleSearch() {
  isSearchOpen.value = !isSearchOpen.value;
  if (isSearchOpen.value) {
    isMenuOpen.value = false;
    // 延迟聚焦到输入框
    setTimeout(() => {
      document.querySelector('.search-input')?.focus();
    }, 300);
  } else {
    searchQuery.value = '';
  }
}

// 切换主题
function toggleTheme() {
  isDarkMode.value = !isDarkMode.value;
  document.documentElement.classList.toggle('dark-mode', isDarkMode.value);

  // 保存到 localStorage
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light');
}

// 处理滚动
function handleScroll() {
  isScrolled.value = window.scrollY > 50;

  // 计算滚动进度
  const windowHeight = document.documentElement.scrollHeight - window.innerHeight;
  scrollProgress.value = (window.scrollY / windowHeight) * 100;
}

// 鼠标移动追踪
function handleMouseMove(e) {
  const rect = e.currentTarget.getBoundingClientRect();
  mouseX.value = ((e.clientX - rect.left) / rect.width);
  mouseY.value = ((e.clientY - rect.top) / rect.height);
  headerRect.value = rect;
}

// Logo 点击效果
function handleLogoClick() {
  // 触发波纹动画
  const logo = document.querySelector('.logo');
  logo?.classList.add('logo-clicked');
  setTimeout(() => {
    logo?.classList.remove('logo-clicked');
  }, 600);
}

// 搜索处理
function handleSearch() {
  if (searchQuery.value.trim()) {
    console.log('Searching for:', searchQuery.value);
    // 这里可以添加实际的搜索逻辑
  }
}

// 监听主题变化，更新粒子颜色
watch(isDarkMode, () => {
  if (particles.length > 0) {
    // 粒子会在下一帧自动使用新颜色
  }
});

// 初始化
onMounted(() => {
  window.addEventListener('scroll', handleScroll);

  // 加载保存的主题
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    isDarkMode.value = true;
    document.documentElement.classList.add('dark-mode');
  }

  // 初始化粒子
  initParticles();
  animateParticles();

  // 监听窗口大小变化
  window.addEventListener('resize', initParticles);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('resize', initParticles);

  if (particleAnimationFrame) {
    cancelAnimationFrame(particleAnimationFrame);
  }
});
</script>

<template>
  <!-- 滚动进度条 -->
  <div class="scroll-progress" :style="{ width: scrollProgress + '%' }"></div>

  <!-- Header container -->
  <header :class="['header-menu', { scrolled: isScrolled, 'dark': isDarkMode }]" @mousemove="handleMouseMove"
    :style="{ '--mouse-x': mouseX, '--mouse-y': mouseY }">

    <!-- 粒子背景 -->
    <canvas ref="particleCanvas" class="particle-canvas"></canvas>

    <!-- 鼠标光晕 -->
    <div class="mouse-glow"></div>

    <!-- Logo 区域 -->
    <div class="logo-container">
      <div class="logo" @click="handleLogoClick">
        <span class="logo-text">{{ BlogName }}</span>
        <div class="logo-ripple"></div>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="header-tools">
      <!-- 搜索按钮 -->
      <button class="tool-btn search-btn" @click="toggleSearch" :class="{ active: isSearchOpen }">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
          <path d="M16 16l5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
      </button>

      <!-- 主题切换按钮 -->
      <button class="tool-btn theme-btn" @click="toggleTheme">
        <div class="theme-icon">
          <svg v-if="!isDarkMode" class="sun-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="2" />
            <path
              d="M12 2v2M12 20v2M20 12h2M2 12h2M17.66 6.34l1.41-1.41M4.93 19.07l1.41-1.41M17.66 17.66l1.41 1.41M4.93 4.93l1.41 1.41"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <svg v-else class="moon-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
      </button>

      <!-- 汉堡菜单 -->
      <div class="hamburger" @click="toggleMenu">
        <div :class="['line', { 'line1-animate': isMenuOpen }]"></div>
        <div :class="['line', { 'line2-animate': isMenuOpen }]"></div>
        <div :class="['line', { 'line3-animate': isMenuOpen }]"></div>
      </div>
    </div>

    <!-- 导航菜单 -->
    <nav class="nav-links" :class="{ active: isMenuOpen }">
      <!-- 移动端遮罩 -->
      <div class="mobile-overlay" @click="toggleMenu" v-if="isMenuOpen"></div>

      <ul>
        <li v-for="(item, index) in menuItems" :key="index" class="nav-item" :style="{ '--item-index': index }">
          <router-link :to="item.link" class="nav-link" @click="isMenuOpen = false">
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-text">{{ item.name }}</span>
            <div class="nav-magnetic"></div>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- 搜索栏 -->
    <transition name="search">
      <div v-if="isSearchOpen" class="search-panel">
        <div class="search-container">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
            <path d="M16 16l5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <input type="text" class="search-input" v-model="searchQuery" @keyup.enter="handleSearch"
            placeholder="Search articles..." />
          <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
          </button>
        </div>
      </div>
    </transition>
  </header>
</template>

<style scoped>
/* === 全局变量 === */
:root {
  --header-bg-light: rgba(255, 255, 255, 0.85);
  --header-bg-dark: rgba(20, 20, 30, 0.9);
  --text-light: #2c3e50;
  --text-dark: #e0e0e0;
}

/* === 滚动进度条 === */
.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  z-index: 10000;
  transition: width 0.1s ease-out;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

/* === Header Container === */
.header-menu {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.2rem 3rem;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 9999;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--header-bg-light);
  backdrop-filter: blur(30px) saturate(180%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  overflow: visible;
}

.header-menu.dark {
  background: var(--header-bg-dark);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-dark);
}

.header-menu.scrolled {
  width: 95%;
  left: 2.5%;
  top: 1rem;
  padding: 0.9rem 2rem;
  border-radius: 60px;
  background: var(--header-bg-light);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow:
    0 10px 50px -10px rgba(102, 126, 234, 0.15),
    0 5px 20px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.header-menu.scrolled.dark {
  background: var(--header-bg-dark);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow:
    0 10px 50px -10px rgba(0, 0, 0, 0.5),
    0 5px 20px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.particle-canvas {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.6;
  border-radius: inherit;
}

.mouse-glow {
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.12) 0%, transparent 70%);
  pointer-events: none;
  left: calc(var(--mouse-x) * 100%);
  top: calc(var(--mouse-y) * 100%);
  transform: translate(-50%, -50%);
  transition: opacity 0.3s ease;
  opacity: 0;
  filter: blur(40px);
}

.header-menu:hover .mouse-glow {
  opacity: 1;
}

.header-menu.dark .mouse-glow {
  background: radial-gradient(circle, rgba(147, 112, 219, 0.15) 0%, transparent 70%);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  font-size: 1.8rem;
  font-weight: 900;
  letter-spacing: -1px;
  cursor: pointer;
  position: relative;
  padding: 0.5rem 1rem;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.logo-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  position: relative;
  z-index: 1;
  display: inline-block;
  transition: all 0.4s ease;
}

.dark .logo-text {
  background: linear-gradient(135deg, #a78bfa 0%, #c084fc 100%);
  -webkit-background-clip: text;
  background-clip: text;
}

.logo:hover .logo-text {
  transform: scale(1.05);
  filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.5));
}

.logo-ripple {
  position: absolute;
  inset: 0;
  border-radius: 12px;
  border: 2px solid #667eea;
  opacity: 0;
  transform: scale(0.8);
}

.logo-clicked .logo-ripple {
  animation: logoRipple 0.6s ease-out;
}

@keyframes logoRipple {
  0% {
    opacity: 1;
    transform: scale(0.8);
  }

  100% {
    opacity: 0;
    transform: scale(1.3);
  }
}

.logo::after {
  content: '';
  position: absolute;
  right: 0;
  top: 8px;
  width: 8px;
  height: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  box-shadow: 0 0 15px rgba(102, 126, 234, 0.8);
  animation: logoPulse 3s infinite;
}

@keyframes logoPulse {

  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }

  50% {
    transform: scale(1.5);
    opacity: 0.5;
  }
}

.header-tools {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tool-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.tool-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.tool-btn:hover::before,
.tool-btn.active::before {
  opacity: 1;
}

.tool-btn svg {
  width: 20px;
  height: 20px;
  position: relative;
  z-index: 1;
  transition: all 0.4s ease;
}

.tool-btn:hover {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
}

.tool-btn:hover svg,
.tool-btn.active svg {
  color: white;
}

.dark .tool-btn {
  background: rgba(167, 139, 250, 0.15);
  color: #a78bfa;
}

.theme-icon {
  position: relative;
  width: 20px;
  height: 20px;
}

.sun-icon,
.moon-icon {
  position: absolute;
  inset: 0;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.sun-icon {
  transform: rotate(0deg) scale(1);
  opacity: 1;
}

.moon-icon {
  transform: rotate(180deg) scale(0);
  opacity: 0;
}

.dark .sun-icon {
  transform: rotate(-180deg) scale(0);
  opacity: 0;
}

.dark .moon-icon {
  transform: rotate(0deg) scale(1);
  opacity: 1;
}

.hamburger {
  display: none;
  flex-direction: column;
  gap: 6px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.hamburger:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: scale(1.05);
}

.line {
  width: 28px;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.dark .line {
  background: linear-gradient(90deg, #a78bfa, #c084fc);
}

.line1-animate {
  transform: rotate(45deg) translate(9px, 9px);
}

.line2-animate {
  opacity: 0;
  transform: translateX(-20px);
}

.line3-animate {
  transform: rotate(-45deg) translate(9px, -9px);
}

.nav-links {
  display: flex;
  gap: 0.5rem;
  transition: all 0.4s ease-in-out;
}

.nav-links ul {
  display: flex;
  list-style: none;
  align-items: center;
  gap: 0.5rem;
}

.nav-item {
  position: relative;
  animation: navItemAppear 0.6s ease-out backwards;
  animation-delay: calc(var(--item-index) * 0.1s);
}

@keyframes navItemAppear {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.nav-link {
  padding: 0.7rem 1.2rem;
  color: var(--text-light);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  border-radius: 16px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  overflow: hidden;
}

.dark .nav-link {
  color: var(--text-dark);
}

.nav-icon {
  font-size: 1.1rem;
  transition: all 0.4s ease;
}

.nav-text {
  position: relative;
  z-index: 1;
}

.nav-magnetic {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border-radius: 16px;
  transform: scale(0);
  opacity: 0;
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.nav-link:hover .nav-magnetic {
  transform: scale(1);
  opacity: 1;
}

.nav-link:hover {
  transform: translateY(-3px);
  color: #667eea;
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
}

.nav-link:hover .nav-icon {
  transform: scale(1.2) rotate(10deg);
  filter: drop-shadow(0 0 5px rgba(102, 126, 234, 0.5));
}

.dark .nav-link:hover {
  color: #a78bfa;
}

.router-link-active.nav-link {
  color: #667eea;
  background: rgba(102, 126, 234, 0.08);
}

.dark .router-link-active.nav-link {
  color: #a78bfa;
  background: rgba(167, 139, 250, 0.12);
}

.router-link-active.nav-link::after {
  content: '';
  position: absolute;
  bottom: 8px;
  left: 50%;
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
  transform: translateX(-50%);
  box-shadow: 0 0 10px currentColor;
}

.search-panel {
  position: absolute;
  top: calc(100% + 1rem);
  right: 3rem;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(30px);
  border-radius: 20px;
  padding: 1rem;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(102, 126, 234, 0.1);
  min-width: 350px;
  z-index: 100;
}

.dark .search-panel {
  background: rgba(30, 30, 40, 0.98);
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(167, 139, 250, 0.2);
}

.search-container {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.6rem 1rem;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.search-container:focus-within {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.08);
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.search-icon {
  width: 20px;
  height: 20px;
  color: #667eea;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 1rem;
  color: var(--text-light);
  outline: none;
}

.dark .search-input {
  color: var(--text-dark);
}

.search-input::placeholder {
  color: rgba(0, 0, 0, 0.4);
}

.dark .search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.search-clear {
  width: 24px;
  height: 24px;
  border: none;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.search-clear svg {
  width: 14px;
  height: 14px;
  color: #667eea;
}

.search-clear:hover {
  background: #667eea;
  transform: rotate(90deg);
}

.search-clear:hover svg {
  color: white;
}

.search-enter-active,
.search-leave-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.search-enter-from {
  opacity: 0;
  transform: translateY(-20px) scale(0.9);
}

.search-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

@media (max-width: 968px) {
  .nav-links {
    display: none;
  }

  .hamburger {
    display: flex;
  }

  .nav-links.active {
    display: flex;
    position: fixed;
    top: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(30px);
    height: 100vh;
    width: 100%;
    max-width: 400px;
    flex-direction: column;
    transform: translateX(0);
    padding-top: 6rem;
    box-shadow: -20px 0 60px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    animation: slideIn 0.5s cubic-bezier(0.19, 1, 0.22, 1);
  }

  .dark .nav-links.active {
    background: rgba(20, 20, 30, 0.98);
  }

  @keyframes slideIn {
    from {
      transform: translateX(100%);
    }

    to {
      transform: translateX(0);
    }
  }

  .nav-links ul {
    flex-direction: column;
    gap: 1.5rem;
    align-items: stretch;
    width: 90%;
    margin: 0 auto;
  }

  .nav-link {
    font-size: 1.3rem;
    padding: 1rem 1.5rem;
    justify-content: center;
  }

  .mobile-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: -1;
    animation: fadeIn 0.3s ease;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }

    to {
      opacity: 1;
    }
  }

  .search-panel {
    right: 1rem;
    left: 1rem;
    min-width: auto;
  }

  .header-menu.scrolled {
    width: 95%;
    left: 2.5%;
  }
}

@media (max-width: 480px) {
  .header-menu {
    padding: 1rem 1.5rem;
  }

  .logo {
    font-size: 1.4rem;
  }

  .tool-btn {
    width: 36px;
    height: 36px;
  }

  .tool-btn svg {
    width: 18px;
    height: 18px;
  }
}
</style>
