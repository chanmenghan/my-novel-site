<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1>AI 写作平台</h1>
        <p>登录后享受更多功能</p>
      </div>

      <div class="login-tabs">
        <button :class="{ active: activeTab === 'login' }" @click="activeTab = 'login'">登录</button>
        <button :class="{ active: activeTab === 'register' }" @click="activeTab = 'register'">注册</button>
      </div>

      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-item">
          <label>用户名</label>
          <input
            v-model="formData.username"
            type="text"
            placeholder="请输入用户名"
            :disabled="loading"
          />
        </div>

        <div class="form-item">
          <label>密码</label>
          <input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            :disabled="loading"
          />
        </div>

        <div v-if="errorMsg" class="error-message">{{ errorMsg }}</div>
        <div v-if="successMsg" class="success-message">{{ successMsg }}</div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '处理中...' : (activeTab === 'login' ? '登录' : '注册') }}
        </button>
      </form>

      <div class="back-home">
        <router-link to="/">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const formData = ref({
  username: '',
  password: ''
})

watch(activeTab, () => {
  errorMsg.value = ''
  successMsg.value = ''
  formData.value = { username: '', password: '' }
})

const handleSubmit = async () => {
  errorMsg.value = ''
  successMsg.value = ''

  if (!formData.value.username.trim()) {
    errorMsg.value = '请输入用户名'
    return
  }

  if (!formData.value.password) {
    errorMsg.value = '请输入密码'
    return
  }

  if (formData.value.username.length < 3) {
    errorMsg.value = '用户名至少3个字符'
    return
  }

  if (formData.value.password.length < 6) {
    errorMsg.value = '密码至少6个字符'
    return
  }

  loading.value = true

  try {
    if (activeTab.value === 'login') {
      const result = await userStore.login(formData.value.username, formData.value.password)
      if (result.success) {
        successMsg.value = '登录成功！'
        setTimeout(() => {
          router.push('/shelf')
        }, 500)
      } else {
        errorMsg.value = result.message
      }
    } else {
      const result = await userStore.register(formData.value.username, formData.value.password)
      if (result.success) {
        successMsg.value = '注册成功！请登录'
        activeTab.value = 'login'
      } else {
        errorMsg.value = result.message
      }
    }
  } catch (error) {
    errorMsg.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: calc(100vh - 60px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-container {
  background: #fff;
  border-radius: 20px;
  padding: 48px 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.25);
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.login-header h1 {
  font-size: 26px;
  color: #1a1a2e;
  margin: 0 0 8px 0;
  font-weight: 600;
  letter-spacing: 2px;
  display: block;
  width: 100%;
}

.login-header p {
  color: #6b7280;
  font-size: 14px;
  margin: 8px 0 0 0;
  display: block;
  width: 100%;
}

.login-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 32px;
  background: #f3f4f6;
  padding: 6px;
  border-radius: 12px;
}

.login-tabs button {
  flex: 1;
  padding: 12px 16px;
  border: none;
  background: transparent;
  color: #6b7280;
  font-size: 15px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.login-tabs button.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.login-tabs button:not(.active):hover {
  color: #374151;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.form-item input {
  padding: 14px 16px;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  font-size: 15px;
  color: #1a1a2e;
  transition: all 0.3s ease;
}

.form-item input::placeholder {
  color: #9ca3af;
}

.form-item input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
}

.form-item input:disabled {
  background: #f9fafb;
  cursor: not-allowed;
  color: #9ca3af;
}

.error-message {
  color: #dc2626;
  font-size: 13px;
  text-align: center;
  padding: 12px 16px;
  background: #fef2f2;
  border-radius: 8px;
  border: 1px solid #fecaca;
}

.success-message {
  color: #16a34a;
  font-size: 13px;
  text-align: center;
  padding: 12px 16px;
  background: #f0fdf4;
  border-radius: 8px;
  border: 1px solid #bbf7d0;
}

.submit-btn {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 8px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.back-home {
  text-align: center;
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid #f3f4f6;
}

.back-home a {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.2s;
}

.back-home a:hover {
  color: #764ba2;
  text-decoration: underline;
}
</style>
