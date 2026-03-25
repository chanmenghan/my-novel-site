<template>
  <div class="novel-container">
    <div class="novel-layout">
      <aside class="sidebar" v-if="currentRoute">
        <router-link to="/novel/inspiration" class="sidebar-item" :class="{ active: route.name === 'inspiration' }">
          <span class="sidebar-icon">💡</span>
          <span class="sidebar-text">灵感工坊</span>
        </router-link>
        <router-link to="/novel/continuation" class="sidebar-item" :class="{ active: route.name === 'continuation' }">
          <span class="sidebar-icon">✍️</span>
          <span class="sidebar-text">智能续写</span>
        </router-link>
        <router-link to="/novel/setting" class="sidebar-item" :class="{ active: route.name === 'setting' }">
          <span class="sidebar-icon">📐</span>
          <span class="sidebar-text">构建设定</span>
        </router-link>
      </aside>

      <div class="main-area">
        <div v-if="!currentRoute" class="modules-grid">
          <router-link to="/novel/inspiration" class="module-card">
            <div class="module-icon">💡</div>
            <h2>灵感工坊</h2>
            <p>激发创意火花，为您的故事寻找灵感源泉</p>
          </router-link>

          <router-link to="/novel/continuation" class="module-card">
            <div class="module-icon">✍️</div>
            <h2>智能续写</h2>
            <p>AI智能续写，让您的故事继续流淌</p>
          </router-link>

          <router-link to="/novel/setting" class="module-card">
            <div class="module-icon">📐</div>
            <h2>构建设定</h2>
            <p>构建世界观、人物设定与故事背景</p>
          </router-link>
        </div>

        <router-view v-else />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentRoute = computed(() => {
  return route.name !== 'novel'
})
</script>

<style scoped>
.novel-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px;
}

.novel-layout {
  display: flex;
  gap: 30px;
}

.sidebar {
  width: 200px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: white;
  border-radius: 12px;
  text-decoration: none;
  color: #666;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.sidebar-item:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: translateX(5px);
}

.sidebar-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.sidebar-icon {
  font-size: 20px;
}

.sidebar-text {
  flex: 1;
}

.main-area {
  flex: 1;
  min-width: 0;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.module-card {
  background: white;
  border-radius: 16px;
  padding: 40px 30px;
  text-align: center;
  text-decoration: none;
  color: inherit;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.module-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
}

.module-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.module-card h2 {
  font-size: 24px;
  color: #333;
  margin: 0 0 15px 0;
}

.module-card p {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

@media (max-width: 992px) {
  .novel-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    flex-direction: row;
    overflow-x: auto;
    gap: 10px;
  }

  .sidebar-item {
    flex-direction: column;
    padding: 15px 20px;
    min-width: 100px;
    text-align: center;
  }

  .sidebar-icon {
    font-size: 24px;
  }

  .modules-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .modules-grid {
    grid-template-columns: 1fr;
  }

  .module-card {
    padding: 30px 20px;
  }

  .module-icon {
    font-size: 48px;
  }

  .module-card h2 {
    font-size: 20px;
  }
}
</style>