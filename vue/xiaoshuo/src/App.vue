<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-left">
        <router-link to="/" class="navbar-brand">
          <span class="brand-icon">✍️</span>
          <span class="brand-text">AI写作平台</span>
        </router-link>
      </div>

      <div class="navbar-menu">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="navbar-item"
          :class="{ active: isActive(item) }"
        >
          <span class="item-icon">{{ item.icon }}</span>
          <span class="item-text">{{ item.name }}</span>
        </router-link>
      </div>

      <div class="navbar-right">
        <div v-if="userStore.isLoggedIn" class="user-info" @click="toggleUserMenu">
          <span class="user-name">{{ userStore.username }}</span>
          <div class="user-avatar">{{ userStore.username.charAt(0).toUpperCase() }}</div>
          <div v-if="showUserMenu" class="user-dropdown">
            <router-link to="/user" class="dropdown-item" @click="showUserMenu = false">
              👤 个人中心
            </router-link>
            <div class="dropdown-item" @click="handleLogout">🚪 退出登录</div>
          </div>
        </div>
        <router-link v-else to="/login" class="user-avatar">👤</router-link>
      </div>
    </div>
  </nav>
  <router-view />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from './stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const menuItems = [
  { path: '/', name: '主页', icon: '🏠' },
  { path: '/novel', name: '工作台', icon: '💡' },
  { path: '/shelf', name: '书架', icon: '📚' },
]

const showUserMenu = ref(false)

const isActive = (item) => {
  if (item.path === '/') {
    return route.path === '/'
  }
  if (item.path === '/novel') {
    return route.path.startsWith('/novel')
  }
  return route.path.startsWith(item.path)
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const handleLogout = () => {
  userStore.logout()
  showUserMenu.value = false
  router.push('/')
}

const handleClickOutside = (e) => {
  if (showUserMenu.value && !e.target.closest('.user-info')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f5f5;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
}

.navbar-left {
  display: flex;
  align-items: center;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: white;
}

.brand-icon {
  font-size: 28px;
}

.brand-text {
  font-size: 22px;
  font-weight: bold;
  letter-spacing: 1px;
}

.navbar-menu {
  display: flex;
  gap: 8px;
}

.navbar-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  padding: 10px 18px;
  border-radius: 25px;
  transition: all 0.3s ease;
  position: relative;
}

.navbar-item:hover {
  color: white;
  background-color: rgba(255, 255, 255, 0.15);
}

.navbar-item.active {
  color: white;
  background-color: rgba(255, 255, 255, 0.25);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.navbar-item.active::after {
  content: '';
  position: absolute;
  bottom: 5px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background-color: white;
  border-radius: 2px;
}

.item-icon {
  font-size: 18px;
}

.item-text {
  font-size: 15px;
}

.navbar-right {
  display: flex;
  align-items: center;
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 20px;
  transition: background-color 0.3s ease;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

.user-name {
  font-size: 14px;
  font-weight: 500;
}

.user-avatar {
  width: 38px;
  height: 38px;
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-avatar:hover {
  transform: scale(1.05);
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 10px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 150px;
  overflow: hidden;
}

.dropdown-item {
  display: block;
  padding: 12px 20px;
  color: #333;
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

@media (max-width: 992px) {
  .navbar-container {
    padding: 0 15px;
    height: 60px;
  }

  .brand-text {
    font-size: 18px;
  }

  .brand-icon {
    font-size: 24px;
  }

  .item-text {
    display: none;
  }

  .navbar-item {
    padding: 10px 14px;
    border-radius: 50%;
  }

  .navbar-item.active::after {
    display: none;
  }

  .user-name {
    display: none;
  }
}

@media (max-width: 600px) {
  .navbar-menu {
    gap: 4px;
  }

  .navbar-item {
    padding: 8px 12px;
    font-size: 14px;
  }

  .item-icon {
    font-size: 16px;
  }
}
</style>