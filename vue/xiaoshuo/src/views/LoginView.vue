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
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.login-header p {
  color: #666;
  font-size: 14px;
}

.login-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

.login-tabs button {
  flex: 1;
  padding: 12px;
  border: none;
  background: #f5f5f5;
  color: #666;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.login-tabs button.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.form-item input {
  padding: 14px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.form-item input:focus {
  outline: none;
  border-color: #667eea;
}

.form-item input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  background: #fdeaea;
  border-radius: 6px;
}

.success-message {
  color: #27ae60;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  background: #eafaf1;
  border-radius: 6px;
}

.submit-btn {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.back-home {
  text-align: center;
  margin-top: 20px;
}

.back-home a {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
}

.back-home a:hover {
  text-decoration: underline;
}
</style>
