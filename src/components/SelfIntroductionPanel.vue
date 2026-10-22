<script setup lang="ts">
import { computed } from 'vue';
import { Icon } from '@iconify/vue';
import config from '@/config';
import globalVar from '@/globalVar';

const coverUrl = config.HeroBackgroundImg || config.BackgroundImg;
const links = config.Links.slice(0, 10).map(link => ({
  ...link,
  icon: `mdi:${link.name.toLowerCase()}`,
}));
const stats = computed(() => [
  { label: '文章', count: Object.keys(globalVar.markdowns).length, to: '/archive' },
  { label: '标签', count: Object.keys(globalVar.tags).length, to: '/tags' },
  { label: '分类', count: Object.keys(globalVar.categories).length, to: '/category' },
]);
</script>

<template>
  <section class="user-info profile-card" :aria-label="`${config.Name} 的个人资料`">
    <!-- 沿用博客图片建立个人识别，界面文字与交互色仍由当前主题控制。 -->
    <div class="profile-cover" aria-hidden="true">
      <img v-if="coverUrl" :src="coverUrl" alt="" loading="lazy" />
    </div>

    <div class="profile-body">
      <div class="profile-identity">
        <router-link to="/about" class="profile-avatar-link" :aria-label="`了解 ${config.Name}`">
          <img class="profile-avatar" :src="config.HeadImg" :alt="`${config.Name} 的头像`"
            width="88" height="88" loading="lazy" />
        </router-link>
        <router-link to="/about" class="profile-about">
          关于我
          <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="m8 5 5 5-5 5" stroke="currentColor" stroke-width="1.5"
              stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </router-link>
      </div>

      <h2 class="profile-name">{{ config.Name }}</h2>
      <p v-if="config.Description" class="profile-description">{{ config.Description }}</p>

      <nav class="profile-stats" aria-label="博客内容统计">
        <router-link v-for="stat in stats" :key="stat.to" :to="stat.to" class="profile-stat"
          :aria-label="`${stat.label}：${stat.count}，查看全部`">
          <span class="profile-stat-count">{{ stat.count.toLocaleString() }}</span>
          <span class="profile-stat-label">{{ stat.label }}</span>
        </router-link>
      </nav>

      <nav v-if="links.length" class="profile-socials" aria-label="社交链接">
        <a v-for="link in links" :key="link.name" :href="link.url" class="profile-social"
          target="_blank" rel="noopener noreferrer" :aria-label="`${link.name}（在新标签页打开）`"
          :title="link.name">
          <Icon :icon="link.icon" width="20" height="20" aria-hidden="true" />
          <span class="profile-tooltip" aria-hidden="true">{{ link.name }}</span>
        </a>
      </nav>
    </div>
  </section>
</template>

<style scoped>
.profile-card {
  /* 局部角色复用主题，避免四套主题各维护一份组件样式。 */
  --profile-bg: var(--theme-panel-bg);
  --profile-ink: var(--theme-heading-text);
  --profile-muted: color-mix(in srgb, var(--theme-panel-text) 72%, var(--profile-bg));
  position: relative;
  isolation: isolate;
  width: 100%;
  min-width: 0;
  border: 1px solid var(--theme-border-light);
  border-radius: 22px;
  background: var(--profile-bg);
  color: var(--profile-ink);
  box-shadow: 0 8px 28px -12px var(--theme-shadow-md);
  text-align: left;
  box-sizing: border-box;
}

.profile-cover {
  height: 112px;
  overflow: hidden;
  border-radius: 21px 21px 0 0;
  background: var(--theme-surface-active);
  position: relative;
}

.profile-cover img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 50% 28%;
}

.profile-cover::after {
  content: '';
  position: absolute;
  inset: 0;
  /* 随主题调节图片亮度，暗色侧栏中不出现刺眼的白色横幅。 */
  background: color-mix(in srgb, var(--profile-bg) 24%, transparent);
  pointer-events: none;
}

.profile-body { padding: 0 24px 22px; }

.profile-identity {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  position: relative;
  margin-top: -40px;
  margin-bottom: 15px;
}

.profile-avatar-link {
  display: block;
  flex-shrink: 0;
  padding: 5px;
  border-radius: 50%;
  background: var(--profile-bg);
  line-height: 0;
}

.profile-avatar {
  display: block;
  width: 88px;
  height: 88px;
  border-radius: 50%;
  object-fit: cover;
  background: var(--theme-surface-active);
}

.profile-about {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  min-height: 36px;
  padding: 0 10px;
  margin-bottom: 7px;
  border: 1px solid var(--theme-border-light);
  border-radius: 18px;
  color: var(--theme-link-color);
  font-size: 0.75rem;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
}

.profile-about svg { width: 16px; height: 16px; }
.profile-about:hover { background: var(--theme-surface-active); border-color: var(--theme-link-color); }

.profile-name {
  margin: 0;
  color: var(--profile-ink);
  font-size: 1.65rem;
  font-weight: 750;
  line-height: 1.25;
  letter-spacing: -0.04em;
  overflow-wrap: anywhere;
}

.profile-description {
  margin: 10px 0 0;
  color: var(--profile-muted);
  font-size: 0.875rem;
  line-height: 1.75;
  overflow-wrap: anywhere;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  padding: 14px 0;
  margin-top: 22px;
  border: 1px solid var(--theme-border-light);
  border-radius: 14px;
  background: var(--theme-surface-hover);
}

.profile-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 5px;
  min-width: 0;
  min-height: 48px;
  color: var(--profile-ink);
  text-decoration: none;
  border-radius: 4px;
}

.profile-stat + .profile-stat { border-left: 1px solid var(--theme-border-light); }
.profile-stat-count { font-size: 1.35rem; font-weight: 700; line-height: 1.2; font-variant-numeric: tabular-nums; }
.profile-stat-label { font-size: 0.75rem; color: var(--profile-muted); }
.profile-stat:hover .profile-stat-count { color: var(--theme-link-color); }

.profile-socials {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
  padding-top: 20px;
}

.profile-social {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  min-width: 0;
  min-height: 42px;
  border: 1px solid var(--theme-border-light);
  border-radius: 11px;
  color: var(--profile-muted);
  text-decoration: none;
  transition: color 180ms ease, background-color 180ms ease, border-color 180ms ease;
}

.profile-social:hover,
.profile-social:focus-visible {
  color: var(--theme-link-color);
  border-color: color-mix(in srgb, var(--theme-link-color) 45%, var(--profile-bg));
  background: var(--theme-nav-active-bg);
}

.profile-tooltip {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
  padding: 5px 9px;
  border: 1px solid var(--theme-border-light);
  border-radius: 6px;
  background: var(--profile-bg);
  color: var(--profile-ink);
  box-shadow: 0 3px 10px var(--theme-shadow-sm);
  font-size: 0.7rem;
  line-height: 1.5;
  white-space: nowrap;
  pointer-events: none;
  visibility: hidden;
}

.profile-social:hover .profile-tooltip,
.profile-social:focus-visible .profile-tooltip { visibility: visible; }
.profile-card a:focus-visible { outline: 2px solid var(--theme-link-color); outline-offset: 3px; }

@media (prefers-reduced-motion: reduce) {
  .profile-card a { transition: none; }
}
</style>
