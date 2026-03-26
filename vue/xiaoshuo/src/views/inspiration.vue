<template>
  <div class="inspiration-page">
    <div class="page-header">
      <h1>💡 灵感工坊</h1>
      <p class="subtitle">激发创意火花，为您的故事寻找灵感源泉</p>
    </div>

    <div class="content-wrapper">
      <div class="left-panel">
        <div class="input-section">
          <div class="config-bar">
            <div class="config-item">
              <label>灵感类型：</label>
              <select v-model="inspirationType">
                <option value="场景">场景描写</option>
                <option value="人物">人物塑造</option>
                <option value="情节">情节设计</option>
                <option value="世界观">世界观构建</option>
                <option value="对白">精彩对白</option>
                <option value="标题">标题拟定</option>
              </select>
            </div>
          </div>

          <textarea
            v-model="inputText"
            placeholder="描述您想要的灵感类型或关键词，让AI为您生成创意..."
          ></textarea>

          <div class="button-container">
            <button @click="generateInspiration" :disabled="isLoading">
              {{ isLoading && loadingType === 'generate' ? '生成中...' : '✨ 获取灵感' }}
            </button>
            <button class="random-btn" @click="randomInspiration" :disabled="isLoading">
              {{ isLoading && loadingType === 'random' ? '生成中...' : '🎲 随机灵感' }}
            </button>
            <button class="copy-btn" @click="copyInput">📋 复制</button>
            <button class="clear-btn" @click="clearInput">🔄 清空</button>
          </div>
        </div>

        <div class="result-section">
          <div class="result-header">
            <h2>💡 AI灵感成果</h2>
            <div class="result-actions">
              <button class="copy-btn" @click="copyResult">复制</button>
              <button class="export-btn" @click="exportResult">📤 导出</button>
            </div>
          </div>
          <div class="result-content">
            <div v-if="isLoading && loadingType === 'generate'" class="loading">AI正在激发灵感...</div>
            <pre v-else-if="resultContent">{{ resultContent }}</pre>
            <p v-else class="placeholder">点击「获取灵感」或「随机灵感」按钮开始创作</p>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="panel-title">📝 灵感记录</div>
        <div class="writing-area">
          <textarea
            v-model="writingContent"
            @keydown.enter="handleEnter"
            placeholder="记录您的灵感碎片..."
          ></textarea>
        </div>
        <div class="writing-actions">
          <button class="save-to-btn" @click="openSaveDialog">💾 保存到</button>
        </div>
      </div>
    </div>

    <SaveToDialog
      :visible="showSaveDialog"
      :content="writingContent"
      @close="showSaveDialog = false"
      @saved="onContentSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import SaveToDialog from '../components/SaveToDialog.vue'

const API_URL = 'http://localhost:5000/api/chat'

const inputText = ref('')
const inspirationType = ref('场景')
const resultContent = ref('')
const writingContent = ref('')
const isLoading = ref(false)
const loadingType = ref('')
const showSaveDialog = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('inspirationWritingContent')
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
    localStorage.setItem('inspirationWritingContent', newText)
  }

  if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    localStorage.setItem('inspirationWritingContent', writingContent.value)
    alert('灵感已保存')
  }
}

const generateInspiration = async () => {
  isLoading.value = true
  loadingType.value = 'generate'

  let prompt = ''
  if (inputText.value.trim()) {
    prompt = `请根据"${inputText.value}"生成5个${inspirationType.value}方面的创意灵感，每个灵感用简短的段落描述，要有创意性和实用性。`
  } else {
    prompt = `请为${inspirationType.value}生成5个创意灵感，要新颖独特，能激发创作欲望。`
  }

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
      alert('生成失败：' + data.msg)
    }
  } catch (error) {
    alert('网络错误：' + error.message)
  } finally {
    isLoading.value = false
    loadingType.value = ''
  }
}

const randomInspiration = async () => {
  isLoading.value = true
  loadingType.value = 'random'

  const prompt = '请随机生成一个独特的小说创作灵感，可以是出人意料的情节转折、鲜明的人物设定、或是有趣的世界观设定。'

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
  if (confirm('确定要清除输入内容吗？')) inputText.value = ''
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
  a.download = '灵感记录.txt'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  alert('导出成功')
}

const openSaveDialog = () => {
  if (!writingContent.value.trim()) {
    alert('工作台内容为空，请先创作内容')
    return
  }
  showSaveDialog.value = true
}

const onContentSaved = () => {
  console.log('内容已保存')
}
</script>

<style scoped>
.inspiration-page {
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

.config-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
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

.config-item select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.input-section,
.result-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 15px rgba(0,0,0,0.08);
  margin-bottom: 30px;
}

textarea {
  width: 100%;
  min-height: 120px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 20px;
  line-height: 1.8;
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

.random-btn {
  background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);
}

.random-btn:hover:not(:disabled) {
  box-shadow: 0 4px 15px rgba(156, 39, 176, 0.4);
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
  min-height: 150px;
  max-height: 300px;
  overflow-y: auto;
  line-height: 1.8;
}

.result-content pre {
  white-space: pre-wrap;
  color: #333;
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
  width: 100%;
  box-sizing: border-box;
}

.right-panel {
  position: relative;
}

.writing-actions {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  gap: 10px;
}

.save-to-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.save-to-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
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