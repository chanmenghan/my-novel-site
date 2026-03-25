<template>
  <div class="setting-page">
    <div class="page-header">
      <h1>📐 构建设定</h1>
      <p class="subtitle">构建世界观、人物设定与故事背景</p>
    </div>

    <div class="content-wrapper">
      <div class="left-panel">
        <div class="tabs">
          <button
            :class="{ active: activeTab === 'world' }"
            @click="switchTab('world')"
          >
            🌍 世界观
          </button>
          <button
            :class="{ active: activeTab === 'character' }"
            @click="switchTab('character')"
          >
            👤 人物设定
          </button>
          <button
            :class="{ active: activeTab === 'background' }"
            @click="switchTab('background')"
          >
            📜 故事背景
          </button>
        </div>

        <div class="input-section">
          <h2 v-if="activeTab === 'world'">🌍 世界观设定</h2>
          <h2 v-if="activeTab === 'character'">👤 人物设定</h2>
          <h2 v-if="activeTab === 'background'">📜 故事背景</h2>

          <div v-if="activeTab === 'character'" class="character-list">
            <div v-for="(char, index) in characters" :key="index" class="character-card">
              <div class="character-header">
                <input v-model="char.name" placeholder="角色姓名" class="char-name" />
                <button class="delete-btn" @click="deleteCharacter(index)">🗑️</button>
              </div>
              <textarea
                v-model="char.description"
                placeholder="角色描述：外貌、性格、背景故事..."
              ></textarea>
            </div>
            <button class="add-btn" @click="addCharacter">➕ 添加角色</button>
          </div>

          <textarea
            v-else
            v-model="currentSetting"
            :placeholder="getPlaceholder()"
          ></textarea>

          <div class="button-container">
            <button @click="generateSuggestion" :disabled="isLoading">
              {{ isLoading ? '生成中...' : '✨ 生成建议' }}
            </button>
            <button class="save-btn" @click="saveCurrentSetting">💾 保存</button>
            <button class="copy-btn" @click="copyInput">📋 复制</button>
            <button class="clear-btn" @click="clearInput">🔄 清空</button>
          </div>
        </div>

        <div class="result-section">
          <div class="result-header">
            <h2>💡 AI建议</h2>
            <div class="result-actions">
              <button class="copy-btn" @click="copySuggestion">复制</button>
              <button class="export-btn" @click="exportSuggestion">📤 导出</button>
            </div>
          </div>
          <div class="result-content">
            <div v-if="isLoading" class="loading">AI正在生成建议...</div>
            <pre v-else-if="currentAiSuggestion">{{ currentAiSuggestion }}</pre>
            <p v-else class="placeholder">点击「生成建议」按钮获取AI建议</p>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="panel-title">📝 设定笔记</div>
        <div class="writing-area">
          <textarea
            v-model="writingContent"
            @keydown.enter="handleEnter"
            placeholder="记录您的设定笔记..."
          ></textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const API_URL = '/api/chat'

const activeTab = ref('world')

const settings = ref({
  world: {
    content: '',
    aiSuggestion: ''
  },
  character: {
    content: '',
    aiSuggestion: '',
    characters: [{ name: '', description: '' }]
  },
  background: {
    content: '',
    aiSuggestion: ''
  }
})

const writingContent = ref('')
const isLoading = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('settingWritingContent')
  if (saved) writingContent.value = saved

  const savedSettings = localStorage.getItem('novelSettings')
  if (savedSettings) {
    const data = JSON.parse(savedSettings)
    if (data.world) settings.value.world = data.world
    if (data.character) settings.value.character = data.character
    if (data.background) settings.value.background = data.background
  }
})

const handleEnter = (e) => {
  if (e.key === 'Enter') {
    e.preventDefault()
    const start = e.target.selectionStart
    const end = e.target.selectionEnd
    const text = writingContent.value

    const beforeCursor = text.substring(0, start)
    const lastLineStart = beforeCursor.lastIndexOf('\n') + 1
    const currentLine = beforeCursor.substring(lastLineStart).trim()

    let newText = ''
    if (currentLine !== '') {
      newText = text.substring(0, end) + '\n\n　　' + text.substring(end)
      setTimeout(() => { e.target.selectionStart = e.target.selectionEnd = end + 4 }, 0)
    } else {
      newText = text.substring(0, end) + '　　' + text.substring(end)
      setTimeout(() => { e.target.selectionStart = e.target.selectionEnd = end + 2 }, 0)
    }

    writingContent.value = newText
    localStorage.setItem('settingWritingContent', newText)
  }

  if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    localStorage.setItem('settingWritingContent', writingContent.value)
    alert('笔记已保存')
  }
}

const currentSetting = computed({
  get() {
    if (activeTab.value === 'character') {
      return settings.value.character.characters.map(c => c.name ? `${c.name}：${c.description}` : '').filter(Boolean).join('\n\n')
    }
    return settings.value[activeTab.value].content
  },
  set(value) {
    if (activeTab.value === 'character') {
      return
    }
    settings.value[activeTab.value].content = value
  }
})

const currentAiSuggestion = computed(() => {
  return settings.value[activeTab.value].aiSuggestion
})

const characters = computed({
  get() {
    return settings.value.character.characters
  },
  set(val) {
    settings.value.character.characters = val
  }
})

const getPlaceholder = () => {
  switch (activeTab.value) {
    case 'world':
      return '描述您的故事世界观：地理环境、社会结构、文化习俗、魔法/科技体系等...'
    case 'background':
      return '描述故事发生的时间、地点、历史背景、重大事件...'
    default:
      return ''
  }
}

const switchTab = (tab) => {
  activeTab.value = tab
}

const addCharacter = () => {
  settings.value.character.characters.push({ name: '', description: '' })
}

const deleteCharacter = (index) => {
  if (settings.value.character.characters.length > 1) {
    settings.value.character.characters.splice(index, 1)
  } else {
    alert('至少需要保留一个角色')
  }
}

const generateSuggestion = async () => {
  isLoading.value = true

  let prompt = ''
  const tab = activeTab.value

  if (tab === 'world') {
    prompt = settings.value.world.content.trim()
      ? `请根据"${settings.value.world.content}"完善并扩展这个世界观设定，提供更多细节和创意。`
      : '请为小说生成一个独特的世界观设定，包括地理环境、社会结构、文化特色等。'
  } else if (tab === 'character') {
    const charInfo = settings.value.character.characters.filter(c => c.name || c.description)
    prompt = charInfo.length > 0
      ? `请根据以下人物设定提供完善建议：\n${charInfo.map(c => `【${c.name}】${c.description}`).join('\n')}`
      : '请为小说生成一个引人入胜的主要角色设定。'
  } else {
    prompt = settings.value.background.content.trim()
      ? `请根据"${settings.value.background.content}"完善这个故事背景。`
      : '请为小说生成一个引人入胜的故事背景设定。'
  }

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: prompt })
    })
    const data = await res.json()
    if (data.code === 200) {
      settings.value[tab].aiSuggestion = data.data.answer
    } else {
      alert('生成失败：' + data.msg)
    }
  } catch (error) {
    alert('网络错误：' + error.message)
  } finally {
    isLoading.value = false
  }
}

const saveCurrentSetting = () => {
  localStorage.setItem('novelSettings', JSON.stringify(settings.value))
  alert('设定已保存')
}

const copyInput = () => {
  if (!currentSetting.value.trim()) {
    alert('没有可复制的内容')
    return
  }
  navigator.clipboard.writeText(currentSetting.value).then(() => alert('已复制到剪贴板')).catch(() => alert('复制失败'))
}

const clearInput = () => {
  if (confirm('确定要清空当前设定吗？')) {
    if (activeTab.value === 'character') {
      settings.value.character.characters = [{ name: '', description: '' }]
    } else {
      settings.value[activeTab.value].content = ''
    }
  }
}

const copySuggestion = () => {
  if (!currentAiSuggestion.value) {
    alert('没有可复制的内容')
    return
  }
  navigator.clipboard.writeText(currentAiSuggestion.value).then(() => alert('已复制到剪贴板')).catch(() => alert('复制失败'))
}

const exportSuggestion = () => {
  if (!currentAiSuggestion.value) {
    alert('没有可导出的内容')
    return
  }
  const blob = new Blob([currentAiSuggestion.value], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'AI建议.txt'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  alert('导出成功')
}
</script>

<style scoped>
.setting-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 32px;
  color: #333;
  margin-bottom: 10px;
}

.subtitle {
  color: #666;
  font-size: 16px;
}

.content-wrapper {
  display: flex;
  gap: 30px;
  align-items: flex-start;
}

.left-panel {
  flex: 1;
  min-width: 0;
}

.right-panel {
  flex: 1;
  min-width: 0;
}

.panel-title {
  font-size: 20px;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #667eea;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 25px;
}

.tabs button {
  flex: 1;
  padding: 12px 20px;
  background: white;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.tabs button.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.tabs button:hover:not(.active) {
  border-color: #667eea;
  color: #667eea;
}

.input-section,
.result-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 15px rgba(0,0,0,0.08);
  margin-bottom: 30px;
}

.input-section h2,
.result-section h2 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
}

textarea {
  width: 100%;
  min-height: 150px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 20px;
  line-height: 1.8;
}

.character-list {
  margin-bottom: 20px;
}

.character-card {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.character-header {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.char-name {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 15px;
}

.delete-btn {
  padding: 10px 14px;
  background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
  font-size: 14px;
}

.character-card textarea {
  min-height: 100px;
  margin-bottom: 0;
  background: white;
}

.add-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
  font-size: 14px;
}

.button-container {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

button {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.save-btn {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}

.save-btn:hover:not(:disabled) {
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
}

.copy-btn {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}

.copy-btn:hover:not(:disabled) {
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
}

.clear-btn {
  background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
}

.clear-btn:hover:not(:disabled) {
  box-shadow: 0 4px 15px rgba(244, 67, 54, 0.4);
}

.export-btn {
  background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
}

.export-btn:hover:not(:disabled) {
  box-shadow: 0 4px 15px rgba(255, 152, 0, 0.4);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.result-actions {
  display: flex;
  gap: 10px;
}

.result-content {
  min-height: 150px;
  max-height: 250px;
  overflow-y: auto;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.result-content pre {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #333;
  font-size: 14px;
  margin: 0;
}

.placeholder {
  color: #999;
  text-align: center;
  padding: 40px 0;
  margin: 0;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.writing-area {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 15px rgba(0,0,0,0.08);
  height: calc(100vh - 250px);
}

.writing-area textarea {
  height: 100%;
  min-height: 400px;
  border: none;
  outline: none;
  font-size: 15px;
  line-height: 1.8;
  margin-bottom: 0;
}

@media (max-width: 992px) {
  .content-wrapper {
    flex-direction: column;
  }

  .writing-area {
    height: auto;
  }

  .tabs {
    flex-wrap: wrap;
  }

  .tabs button {
    flex: 1 1 calc(50% - 5px);
  }
}
</style>