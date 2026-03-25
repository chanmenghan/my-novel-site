<template>
  <div class="continuation-page">
    <div class="page-header">
      <h1>✍️ 智能续写</h1>
      <p class="subtitle">AI智能续写，让您的故事继续流淌</p>
    </div>

    <div class="content-wrapper">
      <div class="left-panel">
        <div class="input-section">
          <div class="config-bar">
            <div class="config-item">
              <label>小说风格：</label>
              <select v-model="styleSelect">
                <option value="古风武侠">古风武侠</option>
                <option value="现代都市">现代都市</option>
                <option value="甜宠言情">甜宠言情</option>
                <option value="悬疑推理">悬疑推理</option>
                <option value="科幻未来">科幻未来</option>
                <option value="玄幻修仙">玄幻修仙</option>
                <option value="脑洞反转">脑洞反转</option>
              </select>
            </div>
            <div class="config-item">
              <label>续写字数：</label>
              <input type="range" v-model="wordCount" min="100" max="800" step="50">
              <span class="word-count-display">{{ wordCount }}</span>
            </div>
          </div>

          <textarea
            v-model="inputText"
            placeholder="请输入小说的开头或已有内容，让AI为您续写..."
          ></textarea>

          <div class="button-container">
            <button class="random-btn" @click="generateRandomStart" :disabled="isLoading">
              {{ isLoading && loadingType === 'random' ? '生成中...' : '🎲 随机开头' }}
            </button>
            <button @click="generateContent" :disabled="isLoading">
              {{ isLoading && loadingType === 'generate' ? '生成中...' : '🖋️ 续写下文' }}
            </button>
            <button class="copy-btn" @click="copyInput">📋 复制</button>
            <button class="clear-btn" @click="clearInput">🔄 清空</button>
          </div>
        </div>

        <div class="result-section">
          <div class="result-header">
            <h2>AI续写结果</h2>
            <div class="result-actions">
              <button class="copy-btn" @click="copyResult">复制</button>
              <button class="export-btn" @click="exportResult">📤 导出</button>
            </div>
          </div>
          <div class="result-content">
            <div v-if="isLoading && loadingType === 'generate'" class="loading">AI正在创作中...</div>
            <div v-else-if="errorMessage" class="error">{{ errorMessage }}</div>
            <pre v-else>{{ resultContent || '请输入内容并点击「续写下文」按钮' }}</pre>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="panel-title">📝 工作台</div>
        <div class="writing-area">
          <textarea
            v-model="writingContent"
            @keydown.enter="handleEnter"
            placeholder="在这里开始您的创作..."
          ></textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_URL = 'http://localhost:5000/api/chat'

const inputText = ref('')
const styleSelect = ref('古风武侠')
const wordCount = ref(200)
const resultContent = ref('')
const writingContent = ref('')
const isLoading = ref(false)
const loadingType = ref('')
const errorMessage = ref('')

onMounted(() => {
  const saved = localStorage.getItem('writingAreaContent')
  if (saved) writingContent.value = saved
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
    localStorage.setItem('writingAreaContent', newText)
  }

  if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    localStorage.setItem('writingAreaContent', writingContent.value)
    alert('内容已保存')
  }
}

const generateContent = async () => {
  if (!inputText.value.trim()) {
    errorMessage.value = '请输入小说开头或提示'
    return
  }

  isLoading.value = true
  loadingType.value = 'generate'
  errorMessage.value = ''

  const prompt = `请以${styleSelect.value}的风格续写以下小说内容，字数约${wordCount.value}字，保持情节连贯，语言流畅：\n\n${inputText.value}`

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: prompt })
    })
    const data = await res.json()
    if (data.code === 200) {
      resultContent.value = data.data.answer
    } else {
      errorMessage.value = data.msg
    }
  } catch (error) {
    errorMessage.value = '网络错误：' + error.message
  } finally {
    isLoading.value = false
    loadingType.value = ''
  }
}

const generateRandomStart = async () => {
  isLoading.value = true
  loadingType.value = 'random'

  const prompt = `请为${styleSelect.value}风格的小说生成一个精彩的开头，约100-150字，要吸引读者继续阅读`

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: prompt })
    })
    const data = await res.json()
    if (data.code === 200) {
      inputText.value = data.data.answer
    } else {
      alert('生成失败：' + data.msg)
    }
  } catch (error) {
    alert('网络错误：' + error.message)
  } finally {
    isLoading.value = false
    loadingType.value = ''
  }
}

const copyInput = () => {
  if (!inputText.value.trim()) {
    alert('输入框中没有内容可以复制')
    return
  }
  navigator.clipboard.writeText(inputText.value).then(() => alert('已复制到剪贴板')).catch(() => alert('复制失败'))
}

const clearInput = () => {
  if (confirm('确定要清除输入框内容吗？')) inputText.value = ''
}

const copyResult = () => {
  if (!resultContent.value.trim()) {
    alert('没有可复制的内容')
    return
  }
  navigator.clipboard.writeText(resultContent.value).then(() => alert('已复制到剪贴板')).catch(() => alert('复制失败'))
}

const exportResult = () => {
  if (!resultContent.value.trim()) {
    alert('没有可导出的内容')
    return
  }
  const blob = new Blob([resultContent.value], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'AI续写小说.txt'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  alert('导出成功')
}
</script>

<style scoped>
.continuation-page {
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
  border-bottom: 2px solid #0066cc;
}

.config-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-item label {
  font-weight: 500;
  color: #333;
}

.config-item select,
.config-item input[type="range"] {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.word-count-display {
  display: inline-block;
  min-width: 40px;
  text-align: center;
  font-weight: bold;
  color: #0066cc;
}

.input-section,
.result-section {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

textarea {
  width: 100%;
  min-height: 150px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 20px;
}

.button-container {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

button {
  padding: 10px 20px;
  background: #0066cc;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

button:hover:not(:disabled) {
  background: #0052a3;
  transform: translateY(-2px);
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.random-btn {
  background: #9C27B0;
}

.random-btn:hover:not(:disabled) {
  background: #7B1FA2;
}

.copy-btn {
  background: #4CAF50;
}

.copy-btn:hover:not(:disabled) {
  background: #45a049;
}

.clear-btn {
  background: #f44336;
}

.clear-btn:hover:not(:disabled) {
  background: #da190b;
}

.export-btn {
  background: #FF9800;
}

.export-btn:hover:not(:disabled) {
  background: #F57C00;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.result-section h2 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.result-actions {
  display: flex;
  gap: 10px;
}

.result-content {
  line-height: 1.8;
  white-space: pre-wrap;
  max-height: 300px;
  overflow-y: auto;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  background-color: #ffebee;
  color: #c62828;
  padding: 15px;
  border-radius: 4px;
}

.writing-area {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  height: calc(100vh - 250px);
}

.writing-area textarea {
  height: 100%;
  min-height: 400px;
  border: none;
  outline: none;
  font-size: 16px;
  line-height: 1.8;
}

@media (max-width: 992px) {
  .content-wrapper {
    flex-direction: column;
  }

  .writing-area {
    height: auto;
  }
}
</style>