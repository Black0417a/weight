<template>
  <div class="admin-layout">
    <div v-if="showSidebar" class="sidebar-backdrop" @click="showSidebar = false"></div>
    <aside class="admin-sidebar" :class="{ 'sidebar-open': showSidebar }">
      <div class="sidebar-header">
        <span class="sidebar-logo">⚙️</span>
        <h2>管理后台</h2>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/admin/dashboard" class="sidebar-link" @click="showSidebar = false">
          <span>📊</span> 仪表盘
        </router-link>
        <router-link to="/admin/users" class="sidebar-link" @click="showSidebar = false">
          <span>👥</span> 用户管理
        </router-link>
        <router-link to="/admin/reward-rules" class="sidebar-link" @click="showSidebar = false">
          <span>🎁</span> 奖励规则
        </router-link>
        <router-link to="/admin/reward-records" class="sidebar-link" @click="showSidebar = false">
          <span>📨</span> 奖励记录
        </router-link>
        <router-link to="/admin/config" class="sidebar-link" @click="showSidebar = false">
          <span>🔧</span> 系统设置
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>
    </aside>
    <div class="admin-main">
      <header class="admin-topbar">
        <button class="sidebar-toggle" @click="showSidebar = !showSidebar">
          <span class="toggle-bar"></span>
          <span class="toggle-bar"></span>
          <span class="toggle-bar"></span>
        </button>
        <h2 class="topbar-title">体重记录管理系统</h2>
      </header>
      <div class="admin-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const showSidebar = ref(false)

const handleLogout = () => {
  authStore.adminLogout()
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

.admin-sidebar {
  width: var(--sidebar-width);
  background: linear-gradient(180deg, #2c3e50, #34495e);
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 200;
  transition: transform 0.3s ease;
}

.sidebar-header {
  padding: var(--spacing-lg);
  text-align: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.sidebar-logo { font-size: 32px; display: block; margin-bottom: var(--spacing-sm); }

.sidebar-header h2 {
  font-size: var(--font-size-base);
  font-weight: 400;
  color: #ecf0f1;
}

.sidebar-nav {
  flex: 1;
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 12px 16px;
  color: #bdc3c7;
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
  text-decoration: none;
  font-size: var(--font-size-sm);
}

.sidebar-link:hover,
.sidebar-link.router-link-active {
  background: rgba(255,255,255,0.1);
  color: #ecf0f1;
}

.sidebar-footer {
  padding: var(--spacing-md);
  border-top: 1px solid rgba(255,255,255,0.1);
}

.logout-btn {
  width: 100%;
  padding: 10px;
  background: rgba(255,107,107,0.2);
  color: #ff6b6b;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  transition: all 0.3s ease;
}

.logout-btn:hover { background: rgba(255,107,107,0.4); }

.admin-main {
  flex: 1;
  margin-left: var(--sidebar-width);
  background: #f5f6fa;
}

.admin-topbar {
  background: white;
  padding: 0 var(--spacing-lg);
  height: var(--header-height);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  position: sticky;
  top: 0;
  z-index: 50;
}

.sidebar-toggle {
  display: none;
  flex-direction: column;
  gap: 4px;
  background: none;
  padding: 4px;
}

.toggle-bar {
  width: 22px;
  height: 2px;
  background: #2c3e50;
  border-radius: 2px;
}

.topbar-title {
  font-size: var(--font-size-base);
  color: #2c3e50;
  font-weight: 500;
}

.admin-content {
  padding: var(--spacing-lg);
  max-width: 1200px;
}

.sidebar-backdrop {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);
  z-index: 199;
}

@media screen and (min-width: 1200px) {
  .sidebar-backdrop {
    display: none !important;
  }
}

@media screen and (max-width: 1199px) {
  .admin-sidebar { transform: translateX(-100%); }
  .admin-sidebar.sidebar-open {
    transform: translateX(0);
    box-shadow: 4px 0 20px rgba(0,0,0,0.3);
  }
  .admin-main { margin-left: 0; }
  .sidebar-toggle { display: flex; }
  .sidebar-backdrop {
    display: block !important;
  }
}

@media screen and (max-width: 767px) {
  .admin-topbar { height: 56px; padding: 0 var(--spacing-md); }
  .admin-content { padding: var(--spacing-md); }
}
</style>
