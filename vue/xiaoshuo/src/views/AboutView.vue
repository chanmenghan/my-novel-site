<template>
  <div class="user-page">
    <div class="container">
      <h1>个人中心</h1>

      <div v-if="!userStore.isLoggedIn" class="login-prompt">
        <p>请先登录后再访问个人中心</p>
        <button class="login-btn" @click="goToLogin">去登录</button>
      </div>

      <div v-else class="user-content">
        <div class="user-header-card">
          <div class="avatar-large">
            {{ userStore.username.charAt(0).toUpperCase() }}
          </div>
          <div class="user-info">
            <h2>{{ userStore.username }}</h2>
            <p class="user-status">在线</p>
          </div>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-value">{{ stats.books }}</div>
            <div class="stat-label">作品数</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">✍️</div>
            <div class="stat-value">{{ stats.words }}</div>
            <div class="stat-label">总字数</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📅</div>
            <div class="stat-value">{{ stats.days }}</div>
            <div class="stat-label">注册天数</div>
          </div>
        </div>

        <div class="menu-section">
          <h3>账户管理</h3>
          <div class="menu-list">
            <div class="menu-item">
              <span class="menu-icon">👤</span>
              <span class="menu-text">个人信息</span>
              <span class="menu-arrow">›</span>
            </div>
            <div class="menu-item">
              <span class="menu-icon">🔐</span>
              <span class="menu-text">修改密码</span>
              <span class="menu-arrow">›</span>
            </div>
            <div class="menu-item">
              <span class="menu-icon">📱</span>
              <span class="menu-text">绑定手机</span>
              <span class="menu-arrow">›</span>
            </div>
            <div class="menu-item">
              <span class="menu-icon">✉️</span>
              <span class="menu-text">绑定邮箱</span>
              <span class="menu-arrow">›</span>
            </div>
          </div>
        </div>

        <div class="menu-section">
          <h3>其他设置</h3>
          <div class="menu-list">
            <div class="menu-item">
              <span class="menu-icon">🎨</span>
              <span class="menu-text">偏好设置</span>
              <span class="menu-arrow">›</span>
            </div>
            <div class="menu-item">
              <span class="menu-icon">🔔</span>
              <span class="menu-text">消息通知</span>
              <span class="menu-arrow">›</span>
            </div>
            <div class="menu-item">
              <span class="menu-icon">❓</span>
              <span class="menu-text">帮助中心</span>
              <span class="menu-arrow">›</span>
            </div>
            <div class="menu-item">
              <span class="menu-icon">📜</span>
              <span class="menu-text">使用协议</span>
              <span class="menu-arrow">›</span>
            </div>
          </div>
        </div>

        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const stats = ref({
  books: 2,
  words: 15818,
  days: 1
})

const goToLogin = () => {
  router.push('/')
}

const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    userStore.logout()
    router.push('/')
  }
}
</script>

<style scoped>
.user-page {
  min-height: calc(100vh - 60px);
  padding: 40px 20px;
}

.container {
  max-width: 600px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 28px;
}

.login-prompt {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.login-prompt p {
  color: #666;
  font-size: 16px;
  margin-bottom: 20px;
}

.login-btn {
  padding: 12px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  cursor: pointer;
}

.user-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-header-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-large {
  width: 80px;
  height: 80px;
  background: white;
  color: #667eea;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
}

.user-info h2 {
  margin: 0 0 5px 0;
  font-size: 24px;
}

.user-status {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.stat-icon {
  font-size: 28px;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 13px;
  color: #999;
  margin-top: 5px;
}

.menu-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.menu-section h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.menu-list {
  display: flex;
  flex-direction: column;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background-color: #f8f9fa;
  margin: 0 -20px;
  padding-left: 20px;
  padding-right: 20px;
}

.menu-icon {
  font-size: 20px;
  margin-right: 15px;
}

.menu-text {
  flex: 1;
  font-size: 15px;
  color: #333;
}

.menu-arrow {
  font-size: 20px;
  color: #ccc;
}

.logout-btn {
  width: 100%;
  padding: 14px;
  background: white;
  color: #f44336;
  border: 1px solid #f44336;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.logout-btn:hover {
  background: #f44336;
  color: white;
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }

  .stat-card {
    padding: 15px 10px;
  }

  .stat-icon {
    font-size: 22px;
  }

  .stat-value {
    font-size: 18px;
  }

  .stat-label {
    font-size: 11px;
  }
}
</style>