<template>
  <div class="user-layout">
    <header class="user-header">
      <div class="header-content">
        <router-link to="/dashboard" class="logo">
          <span class="logo-icon">⚖️</span>
          <span class="logo-text">体重记录小助手</span>
        </router-link>
        <nav class="nav-desktop">
          <router-link to="/dashboard" class="nav-link"><span class="nav-icon">🏠</span>首页</router-link>
          <router-link to="/records" class="nav-link"><span class="nav-icon">📝</span>记录</router-link>
          <router-link to="/chart" class="nav-link"><span class="nav-icon">📈</span>趋势</router-link>
          <router-link to="/goal" class="nav-link"><span class="nav-icon">🎯</span>目标</router-link>
          <router-link to="/profile" class="nav-link"><span class="nav-icon">👤</span>我的</router-link>
        </nav>
      </div>
    </header>
    <main class="user-main">
      <router-view />
    </main>
    <nav class="nav-mobile-bottom">
      <router-link to="/dashboard" class="tab-item">
        <span class="tab-icon">📊</span>
        <span class="tab-label">首页</span>
      </router-link>
      <router-link to="/records" class="tab-item">
        <span class="tab-icon">📝</span>
        <span class="tab-label">记录</span>
      </router-link>
      <router-link to="/chart" class="tab-item">
        <span class="tab-icon">📈</span>
        <span class="tab-label">趋势</span>
      </router-link>
      <router-link to="/goal" class="tab-item">
        <span class="tab-icon">🎯</span>
        <span class="tab-label">目标</span>
      </router-link>
      <router-link to="/profile" class="tab-item">
        <span class="tab-icon">👤</span>
        <span class="tab-label">我的</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
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

.logo-icon { font-size: 28px; }

.logo-text {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-primary);
}

.nav-desktop { display: flex; gap: var(--spacing-xs); }

.nav-link {
  padding: 8px 16px;
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  transition: all 0.3s ease;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-primary);
  background: var(--bg-hover);
}

.nav-icon { font-size: 16px; }

.nav-mobile-bottom {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-top: 1px solid #ffe0e0;
  z-index: 100;
  justify-content: space-around;
  padding: 4px 0 env(safe-area-inset-bottom, 8px);
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px 0;
  text-decoration: none;
  color: var(--text-light);
  transition: color 0.3s ease;
  flex: 1;
}

.tab-icon { font-size: 22px; line-height: 1; }

.tab-label {
  font-size: 10px;
  margin-top: 2px;
}

.tab-item.router-link-active {
  color: var(--color-primary);
}

.user-main {
  flex: 1;
  max-width: var(--max-width);
  width: 100%;
  margin: 0 auto;
  padding: var(--spacing-lg);
}

@media screen and (max-width: 767px) {
  .header-content {
    padding: 0 var(--spacing-md);
    height: var(--header-height-mobile);
    justify-content: center;
  }
  .nav-desktop { display: none; }
  .logo-text { font-size: var(--font-size-base); }
  .nav-mobile-bottom { display: flex; }
  .user-main {
    padding: var(--spacing-md);
    padding-bottom: 70px;
  }
}
</style>
