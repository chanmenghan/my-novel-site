<template>
  <div class="screenplay-page">
    <div class="page-header">
      <h1>🎬 剧本创作工坊</h1>
      <p class="subtitle">基于多智能体系统的剧本创作平台</p>
    </div>

    <div class="content-wrapper">
      <div class="left-panel">
        <div class="input-section">
          <div class="config-bar">
            <div class="config-item">
              <label>创作类型：</label>
              <select v-model="genre">
                <option value="都市重生">都市重生</option>
                <option value="玄幻修仙">玄幻修仙</option>
                <option value="都市言情">都市言情</option>
                <option value="系统流">系统流</option>
                <option value="穿越">穿越</option>
                <option value="悬疑">悬疑</option>
              </select>
            </div>
            <div class="config-item">
              <label>启用知识库：</label>
              <input type="checkbox" v-model="enableRag" class="checkbox" />
            </div>
            <div class="config-item">
              <label>启用技能模板：</label>
              <input type="checkbox" v-model="enableSkills" class="checkbox" />
            </div>
          </div>

          <div class="input-group">
            <label>作品标题：</label>
            <input
              v-model="title"
              type="text"
              placeholder="输入您的作品标题，如：重生之都市医圣"
            />
          </div>

          <div class="input-group">
            <label>创意概要：</label>
            <textarea
              v-model="description"
              placeholder="描述您的故事创意，如：天才医生被陷害致死，重生回大学时代，凭借前世记忆和医术，一步步复仇崛起"
            ></textarea>
          </div>

          <div class="button-container">
            <button @click="generateScreenplay" :disabled="isLoading">
              {{ isLoading ? '🎬 创作中...' : '✨ 开始创作' }}
            </button>
            <button class="copy-btn" @click="copyInput">📋 复制</button>
            <button class="clear-btn" @click="clearInput">🔄 清空</button>
          </div>
        </div>

        <div class="result-section" v-if="characters.length > 0 || screenplayDraft">
          <div class="result-header">
            <h2>📖 创作成果</h2>
            <div class="result-actions">
              <button class="copy-btn" @click="copyResult">复制</button>
              <button class="export-btn" @click="exportResult">📤 导出</button>
            </div>
          </div>

          <div v-if="isLoading" class="loading">
            <div class="loading-spinner"></div>
            <p>AI正在创作中，请稍候...</p>
            <p class="loading-tip">生成人物设定 → 规划剧情大纲 → 创作正文</p>
          </div>

          <div v-else class="result-content">
            <div v-if="characters.length > 0" class="characters-section">
              <h3>👥 人物设定 ({{ characters.length }})</h3>
              <div v-for="(char, index) in characters" :key="index" class="character-card">
                <div class="character-name">{{ char.name }}</div>
                <div class="character-info">
                  <span v-if="char.age">年龄：{{ char.age }}</span>
                  <span v-if="char.gender">性别：{{ char.gender }}</span>
                </div>
                <div class="character-detail">
                  <strong>性格特点：</strong>{{ char.personality }}
                </div>
                <div class="character-detail">
                  <strong>背景故事：</strong>{{ char.background }}
                </div>
                <div class="character-detail" v-if="char.relationships && Object.keys(char.relationships).length > 0">
                  <strong>人物关系：</strong>
                  <span v-if="typeof char.relationships === 'string'">{{ char.relationships }}</span>
                  <span v-else>{{ formatRelationships(char.relationships) }}</span>
                </div>
              </div>
            </div>

            <div v-if="plotOutline" class="plot-section">
              <h3>📋 剧情大纲</h3>
              <div class="plot-item" v-if="plotOutline.main_arc">
                <strong>🎯 主线剧情：</strong>
                <p>{{ plotOutline.main_arc }}</p>
              </div>
              <div class="plot-item" v-if="plotOutline.sub_arcs && plotOutline.sub_arcs.length > 0">
                <strong>🔮 副线剧情：</strong>
                <ul>
                  <li v-for="(arc, i) in plotOutline.sub_arcs" :key="i">{{ arc }}</li>
                </ul>
              </div>
              <div class="plot-item" v-if="plotOutline.turning_points && plotOutline.turning_points.length > 0">
                <strong>⚡ 转折点：</strong>
                <ul>
                  <li v-for="(point, i) in plotOutline.turning_points" :key="i">{{ point }}</li>
                </ul>
              </div>
              <div class="plot-item" v-if="plotOutline.climax">
                <strong>🔥 高潮设计：</strong>
                <p>{{ plotOutline.climax }}</p>
              </div>
            </div>

            <div v-if="subplots && subplots.length > 0" class="subplots-section">
              <h3>🌉 支线剧情 ({{ subplots.length }})</h3>
              <div v-for="(subplot, index) in subplots" :key="index" class="subplot-card">
                <div class="subplot-title">{{ subplot.title }}</div>
                <div class="subplot-meta">
                  <span class="subplot-type">{{ subplot.type }}</span>
                </div>
                <div class="subplot-summary">{{ subplot.summary }}</div>
                <div class="subplot-connections" v-if="subplot.connection_points && subplot.connection_points.length > 0">
                  <strong>联动点：</strong>{{ subplot.connection_points.join(' | ') }}
                </div>
              </div>
            </div>

            <div v-if="dialogues && dialogues.length > 0" class="dialogues-section">
              <h3>💬 精彩对白 ({{ dialogues.length }})</h3>
              <div v-for="(dlg, index) in dialogues" :key="index" class="dialogue-card">
                <div class="dialogue-speaker">{{ dlg.speaker }}</div>
                <div class="dialogue-text">"{{ dlg.dialogue }}"</div>
                <div class="dialogue-meta" v-if="dlg.emotion || dlg.subtext">
                  <span v-if="dlg.emotion" class="emotion">情感：{{ dlg.emotion }}</span>
                  <span v-if="dlg.subtext" class="subtext">潜台词：{{ dlg.subtext }}</span>
                </div>
              </div>
            </div>

            <div v-if="evaluation" class="evaluation-section">
              <h3>📊 质量评估</h3>
              <div class="quality-score">
                <div class="score-value">{{ (evaluation.score * 100).toFixed(0) }}分</div>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: (evaluation.score * 100) + '%' }"></div>
                </div>
              </div>
              <div class="evaluation-content">
                <div class="eval-item strengths" v-if="evaluation.strengths && evaluation.strengths.length > 0">
                  <strong>✅ 优点：</strong>
                  <ul>
                    <li v-for="(s, i) in evaluation.strengths" :key="i">{{ s }}</li>
                  </ul>
                </div>
                <div class="eval-item weaknesses" v-if="evaluation.weaknesses && evaluation.weaknesses.length > 0">
                  <strong>⚠️ 缺点：</strong>
                  <ul>
                    <li v-for="(w, i) in evaluation.weaknesses" :key="i">{{ w }}</li>
                  </ul>
                </div>
                <div class="eval-item suggestions" v-if="evaluation.suggestions && evaluation.suggestions.length > 0">
                  <strong>💡 建议：</strong>
                  <ul>
                    <li v-for="(s, i) in evaluation.suggestions" :key="i">{{ s }}</li>
                  </ul>
                </div>
              </div>
            </div>

            <div v-if="screenplayDraft" class="draft-section">
              <h3>📜 第一章正文</h3>
              <pre class="draft-content">{{ screenplayDraft }}</pre>
            </div>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="panel-title">📝 创作笔记</div>
        <div class="writing-area">
          <textarea
            v-model="writingContent"
            placeholder="记录您的创作灵感、笔记或修改意见..."
          ></textarea>
        </div>
        <div class="writing-actions">
          <button class="save-to-btn" @click="openSaveDialog">💾 保存</button>
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

const API_BASE_URL = 'http://localhost:5000'

const title = ref('')
const genre = ref('都市重生')
const description = ref('')
const enableRag = ref(true)
const enableSkills = ref(true)
const characters = ref([])
const plotOutline = ref(null)
const screenplayDraft = ref('')
const subplots = ref([])
const dialogues = ref([])
const evaluation = ref(null)
const writingContent = ref('')
const isLoading = ref(false)
const showSaveDialog = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('screenplayWritingContent')
  if (saved) writingContent.value = saved
})

const generateScreenplay = async () => {
  if (!title.value.trim()) {
    alert('请输入作品标题')
    return
  }
  if (!description.value.trim()) {
    alert('请输入创意概要')
    return
  }

  isLoading.value = true
  characters.value = []
  plotOutline.value = null
  screenplayDraft.value = ''

  try {
    const response = await fetch(`${API_BASE_URL}/api/screenplay/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        creative_brief: {
          title: title.value,
          genre: genre.value,
          description: description.value
        },
        enable_rag: enableRag.value,
        enable_skills: enableSkills.value
      })
    })

    const data = await response.json()

    if (response.ok) {
      const rawCharacters = data.characters || []
      characters.value = rawCharacters.map(c => ({
        name: c.姓名 || c.name || '',
        age: c.年龄 || c.age || null,
        gender: c.性别 || c.gender || '',
        personality: c.性格特点 || c.personality || '',
        background: c.背景故事 || c.background || '',
        relationships: c.与其他人物的关系 || c.relationships || {}
      }))
      plotOutline.value = data.plot_outline || null
      screenplayDraft.value = data.screenplay_draft || ''
      subplots.value = data.subplots || []
      dialogues.value = data.dialogues || []
      evaluation.value = data.evaluation || null
    } else {
      alert('生成失败：' + (data.detail || '未知错误'))
    }
  } catch (error) {
    alert('网络错误：' + error.message)
  } finally {
    isLoading.value = false
  }
}

const copyInput = () => {
  const text = `标题：${title.value}\n类型：${genre.value}\n创意概要：${description.value}`
  navigator.clipboard.writeText(text).then(() => alert('已复制到剪贴板')).catch(() => alert('复制失败'))
}

const clearInput = () => {
  if (confirm('确定要清空所有内容吗？')) {
    title.value = ''
    description.value = ''
    characters.value = []
    plotOutline.value = null
    screenplayDraft.value = ''
    subplots.value = []
    dialogues.value = []
    evaluation.value = null
  }
}

const formatRelationships = (rels) => {
  if (typeof rels === 'string') return rels
  if (typeof rels === 'object' && rels !== null) {
    return Object.entries(rels).map(([key, value]) => `${key}: ${value}`).join(' | ')
  }
  return JSON.stringify(rels)
}

const copyResult = () => {
  const text = generateFullText()
  navigator.clipboard.writeText(text).then(() => alert('已复制到剪贴板')).catch(() => alert('复制失败'))
}

const exportResult = () => {
  const text = generateFullText()
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${title.value || '剧本'}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  alert('导出成功')
}

const generateFullText = () => {
  let text = `【${title.value}】\n类型：${genre.value}\n\n`

  if (characters.value.length > 0) {
    text += '【人物设定】\n'
    characters.value.forEach((char, i) => {
      text += `\n${i + 1}. ${char.name}\n`
      text += `   年龄：${char.age || '未知'} | 性别：${char.gender || '未知'}\n`
      text += `   性格：${char.personality || '暂无'}\n`
      text += `   背景：${char.background || '暂无'}\n`
      if (char.relationships) {
        text += `   关系：${typeof char.relationships === 'string' ? char.relationships : formatRelationships(char.relationships)}\n`
      }
    })
    text += '\n'
  }

  if (plotOutline.value) {
    text += '【剧情大纲】\n'
    if (plotOutline.value.main_arc) text += `主线：${plotOutline.value.main_arc}\n`
    if (plotOutline.value.sub_arcs && plotOutline.value.sub_arcs.length > 0) {
      text += `副线：${plotOutline.value.sub_arcs.join(' | ')}\n`
    }
    if (plotOutline.value.turning_points && plotOutline.value.turning_points.length > 0) {
      text += `转折点：${plotOutline.value.turning_points.join(' | ')}\n`
    }
    if (plotOutline.value.climax) text += `高潮：${plotOutline.value.climax}\n`
    text += '\n'
  }

  if (subplots.value && subplots.value.length > 0) {
    text += '【支线剧情】\n'
    subplots.value.forEach((sp, i) => {
      text += `\n${i + 1}. ${sp.title} (${sp.type})\n`
      text += `   ${sp.summary}\n`
      if (sp.connection_points && sp.connection_points.length > 0) {
        text += `   联动点：${sp.connection_points.join(' | ')}\n`
      }
    })
    text += '\n'
  }

  if (dialogues.value && dialogues.value.length > 0) {
    text += '【精彩对白】\n'
    dialogues.value.forEach((dlg, i) => {
      text += `\n${i + 1}. ${dlg.speaker}：\n`
      text += `   "${dlg.dialogue}"\n`
      if (dlg.emotion) text += `   情感：${dlg.emotion}\n`
      if (dlg.subtext) text += `   潜台词：${dlg.subtext}\n`
    })
    text += '\n'
  }

  if (evaluation.value) {
    text += `【质量评估】评分：${(evaluation.value.score * 100).toFixed(0)}分\n`
    if (evaluation.value.strengths && evaluation.value.strengths.length > 0) {
      text += `优点：${evaluation.value.strengths.join(' | ')}\n`
    }
    if (evaluation.value.weaknesses && evaluation.value.weaknesses.length > 0) {
      text += `缺点：${evaluation.value.weaknesses.join(' | ')}\n`
    }
    if (evaluation.value.suggestions && evaluation.value.suggestions.length > 0) {
      text += `建议：${evaluation.value.suggestions.join(' | ')}\n`
    }
    text += '\n'
  }

  if (screenplayDraft.value) {
    text += '【第一章正文】\n\n'
    text += screenplayDraft.value
  }

  return text
}

const openSaveDialog = () => {
  if (!writingContent.value.trim()) {
    alert('创作笔记为空，请先记录内容')
    return
  }
  showSaveDialog.value = true
}

const onContentSaved = () => {
  console.log('内容已保存')
}
</script>

<style scoped>
.screenplay-page {
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
  flex: 2;
  min-width: 0;
}

.right-panel {
  flex: 1;
  min-width: 0;
  position: relative;
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

.config-item .checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #667eea;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.input-group input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  box-sizing: border-box;
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
  box-sizing: border-box;
}

.button-container {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

button {
  padding: 12px 24px;
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
  max-height: 600px;
  overflow-y: auto;
  line-height: 1.8;
}

.loading {
  text-align: center;
  padding: 40px 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading p {
  color: #666;
  margin: 10px 0;
}

.loading-tip {
  font-size: 14px;
  color: #999;
}

.characters-section,
.plot-section,
.draft-section,
.subplots-section,
.dialogues-section,
.evaluation-section {
  margin-bottom: 30px;
}

.characters-section h3,
.plot-section h3,
.draft-section h3,
.subplots-section h3,
.dialogues-section h3,
.evaluation-section h3 {
  color: #667eea;
  margin-bottom: 15px;
  font-size: 18px;
}

.character-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.character-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.character-info {
  color: #666;
  font-size: 14px;
  margin-bottom: 8px;
}

.character-info span {
  margin-right: 15px;
}

.character-detail {
  color: #555;
  font-size: 14px;
  margin-bottom: 5px;
}

.plot-item {
  margin-bottom: 15px;
}

.plot-item strong {
  color: #333;
}

.plot-item p {
  margin: 8px 0;
  color: #555;
}

.plot-item ul {
  margin: 8px 0;
  padding-left: 20px;
  color: #555;
}

.plot-item li {
  margin-bottom: 5px;
}

.draft-content {
  white-space: pre-wrap;
  color: #333;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  font-family: inherit;
  line-height: 1.8;
  max-height: 400px;
  overflow-y: auto;
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

.subplots-section {
  margin-top: 20px;
}

.subplot-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.subplot-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.subplot-meta {
  margin-bottom: 8px;
}

.subplot-type {
  display: inline-block;
  background: #667eea;
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.subplot-summary {
  color: #555;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 8px;
}

.subplot-connections {
  color: #666;
  font-size: 13px;
}

.dialogue-card {
  background: #fff9e6;
  border-left: 4px solid #ffc107;
  padding: 15px;
  margin-bottom: 15px;
  border-radius: 0 8px 8px 0;
}

.dialogue-speaker {
  font-weight: bold;
  color: #d48806;
  margin-bottom: 8px;
}

.dialogue-text {
  font-size: 15px;
  color: #333;
  line-height: 1.6;
  font-style: italic;
  margin-bottom: 8px;
}

.dialogue-meta {
  display: flex;
  gap: 15px;
  font-size: 13px;
  color: #666;
}

.dialogue-meta .emotion {
  color: #e91e63;
}

.dialogue-meta .subtext {
  color: #9e9e9e;
}

.evaluation-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
}

.quality-score {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.score-value {
  font-size: 32px;
  font-weight: bold;
  color: #667eea;
}

.score-bar {
  flex: 1;
  height: 12px;
  background: #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 6px;
  transition: width 0.5s ease;
}

.evaluation-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.eval-item {
  padding: 15px;
  border-radius: 8px;
}

.eval-item.strengths {
  background: #e8f5e9;
}

.eval-item.weaknesses {
  background: #fff3e0;
}

.eval-item.suggestions {
  background: #e3f2fd;
}

.eval-item ul {
  margin: 10px 0 0 0;
  padding-left: 20px;
  color: #555;
}

.eval-item li {
  margin-bottom: 5px;
}
</style>
