<template>
  <div class="user-layout">
    <header class="user-header">
      <div class="header-content">
        <router-link to="/dashboard" class="logo">
          <span class="logo-icon">⚖️</span>
          <span class="logo-text">体重记录小助手</span>
        </router-link>
        <nav class="nav-desktop">
          <router-link to="/dashboard" class="nav-link">首页</router-link>
          <router-link to="/records" class="nav-link">记录</router-link>
          <router-link to="/batch" class="nav-link">批量录入</router-link>
          <router-link to="/chart" class="nav-link">趋势</router-link>
          <router-link to="/goal" class="nav-link">目标</router-link>
          <router-link to="/profile" class="nav-link">我的</router-link>
        </nav>
        <button class="menu-toggle" @click="showMenu = !showMenu">
          <span class="menu-bar"></span>
          <span class="menu-bar"></span>
          <span class="menu-bar"></span>
        </button>
      </div>
      <transition name="slide">
        <nav v-if="showMenu" class="nav-mobile">
          <router-link to="/dashboard" class="nav-link" @click="showMenu = false">🏠 首页</router-link>
          <router-link to="/records" class="nav-link" @click="showMenu = false">📝 记录</router-link>
          <router-link to="/batch" class="nav-link" @click="showMenu = false">📋 批量录入</router-link>
          <router-link to="/chart" class="nav-link" @click="showMenu = false">📊 趋势</router-link>
          <router-link to="/goal" class="nav-link" @click="showMenu = false">🎯 目标</router-link>
          <router-link to="/profile" class="nav-link" @click="showMenu = false">👤 我的</router-link>
        </nav>
      </transition>
    </header>
    <main class="user-main">
      <router-view />
    </main>
    <footer class="user-footer">
      <p>💖 坚持记录，遇见更好的自己</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const showMenu = ref(false)
</script>

<style scoped>
.user-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.user-header {
  background: white;
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: var(--max-width);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-lg);
  height: var(--header-height);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  text-decoration: none;
  color: var(--text-primary);
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-primary);
}

.nav-desktop {
  display: flex;
  gap: var(--spacing-xs);
}

.nav-link {
  padding: 8px 16px;
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  transition: all 0.3s ease;
  text-decoration: none;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-primary);
  background: var(--bg-hover);
}

.menu-toggle {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  padding: 4px;
}

.menu-bar {
  width: 24px;
  height: 2px;
  background: var(--color-primary);
  border-radius: 2px;
  transition: all 0.3s ease;
}

.nav-mobile {
  display: none;
  flex-direction: column;
  background: white;
  padding: var(--spacing-md);
  border-top: 1px solid var(--bg-secondary);
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@media screen and (max-width: 767px) {
  .nav-desktop { display: none; }
  .menu-toggle { display: flex; }
  .nav-mobile { display: flex; }

  .nav-mobile .nav-link {
    padding: 12px 16px;
    font-size: var(--font-size-base);
    border-radius: var(--radius-md);
  }

  .header-content {
    padding: 0 var(--spacing-md);
    height: var(--header-height-mobile);
  }

  .logo-text { font-size: var(--font-size-base); }
}

.user-main {
  flex: 1;
  max-width: var(--max-width);
  width: 100%;
  margin: 0 auto;
  padding: var(--spacing-lg);
}

@media screen and (max-width: 767px) {
  .user-main { padding: var(--spacing-md); }
}

.user-footer {
  text-align: center;
  padding: var(--spacing-lg);
  color: var(--text-light);
  font-size: var(--font-size-sm);
  background: var(--bg-secondary);
}
</style>
