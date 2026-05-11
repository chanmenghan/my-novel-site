<template>
  <div class="book-page">
    <header class="book-header">
      <button class="back-btn" @click="goBack">← 书架</button>
      <h1 class="book-title">{{ book.title || '加载中...' }}</h1>
      <button class="save-btn" @click="saveCurrent" :disabled="!isDirty">保存</button>
    </header>

    <div class="book-content">
      <section class="book-info">
        <div class="book-cover">
          <span class="cover-icon">📖</span>
        </div>
        <div class="book-details">
          <div class="detail-row">
            <span class="label">作者</span>
            <span class="value">{{ userStore.username }}</span>
          </div>
          <div class="detail-row">
            <span class="label">标签</span>
            <span class="value">{{ book.style || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="label">章节</span>
            <span class="value">{{ chapters.length }} 章</span>
          </div>
          <div class="detail-row">
            <span class="label">字数</span>
            <span class="value">{{ book.word_count || 0 }} 字</span>
          </div>
        </div>
      </section>

      <nav class="tab-nav">
        <div class="tab-item" :class="{ active: activeTab === 'catalog' }" @click="switchTab('catalog')">
          目录
        </div>
        <div class="tab-item" :class="{ active: activeTab === 'related' }" @click="switchTab('related')">
          相关
        </div>
      </nav>

      <main class="book-main">
        <aside class="sidebar">
          <template v-if="activeTab === 'catalog'">
            <div class="sidebar-header">
              <span>章节目录</span>
              <button class="add-btn" @click="openChapterDialog">+ 新建</button>
            </div>
            <div class="chapter-list">
              <div
                v-for="chapter in chapters"
                :key="chapter.id"
                class="chapter-item"
                :class="{ active: currentChapterId === chapter.id }"
                @click="selectChapter(chapter)"
              >
                <span class="chapter-title">{{ chapter.title || `第${chapter.sort_order + 1}章` }}</span>
                <span class="chapter-words">{{ chapter.word_count || 0 }}字</span>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="sidebar-header">
              <span>相关设定</span>
            </div>
            <div class="related-list">
              <div
                v-for="(item, key) in relatedItems"
                :key="key"
                class="related-item"
                :class="{ active: currentRelated === key }"
                @click="selectRelated(key)"
              >
                <span>{{ item.label }}</span>
                <span class="words">{{ item.word_count }}字</span>
              </div>
            </div>
          </template>
        </aside>

        <section class="editor">
          <template v-if="activeTab === 'catalog' && currentChapter">
            <div class="editor-header">
              <input
                v-model="currentChapter.title"
                class="title-input"
                placeholder="请输入章节标题"
                @input="markDirty"
              />
              <button class="delete-chapter-btn" @click="handleDeleteChapter">删除</button>
            </div>
            <textarea
              v-model="currentChapter.content"
              class="content-input"
              placeholder="开始创作..."
              @input="updateWordCount"
            ></textarea>
            <div class="editor-footer">
              <span class="word-count">本章字数：{{ currentChapter.word_count || 0 }}</span>
            </div>
          </template>

          <template v-else-if="activeTab === 'related'">
            <div class="editor-header">
              <input
                v-model="relatedItems[currentRelated].title"
                class="title-input"
                placeholder="请输入标题"
                @input="markDirtyRelated"
              />
            </div>
            <textarea
              v-model="relatedItems[currentRelated].content"
              class="content-input"
              placeholder="开始创作..."
              @input="updateRelatedWords"
            ></textarea>
            <div class="editor-footer">
              <span class="word-count">字数：{{ relatedItems[currentRelated].word_count }}</span>
            </div>
          </template>

          <div v-else class="empty-editor">
            <p>{{ activeTab === 'catalog' ? '请从左侧选择或创建章节' : '请从左侧选择相关设定' }}</p>
          </div>
        </section>
      </main>
    </div>
  </div>

  <div v-if="showChapterDialog" class="dialog-overlay" @click.self="closeChapterDialog">
    <div class="chapter-dialog">
      <div class="dialog-header">
        <h3>新建章节</h3>
        <button class="dialog-close" @click="closeChapterDialog">×</button>
      </div>
      <div class="dialog-body">
        <div class="chapter-prefix">第{{ chapters.length + 1 }}章</div>
        <input
          v-model="newChapterName"
          type="text"
          class="chapter-input"
          placeholder="请输入章节名"
          @keyup.enter="confirmAddChapter"
        />
      </div>
      <div class="dialog-footer">
        <button class="dialog-btn cancel" @click="closeChapterDialog">取消</button>
        <button class="dialog-btn confirm" @click="confirmAddChapter">确定</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const book = ref({ id: null, title: '', style: '', word_count: 0 })
const chapters = ref([])
const currentChapterId = ref(null)
const isDirty = ref(false)
const activeTab = ref('catalog')
const currentRelated = ref('world')
const settingsDirty = ref(false)
const showChapterDialog = ref(false)
const newChapterName = ref('')

const relatedItems = ref({
  world: { label: '作品设定', title: '', content: '', word_count: 0 },
  outline: { label: '作品大纲', title: '', content: '', word_count: 0 },
  character: { label: '角色设定', title: '', content: '', word_count: 0 },
  inspiration: { label: '灵感记录', title: '', content: '', word_count: 0 }
})

const currentChapter = computed(() => {
  return chapters.value.find(c => c.id === currentChapterId.value) || null
})

const goBack = async () => {
  if (isDirty.value) {
    await saveCurrent()
  }
  if (settingsDirty.value) {
    await saveSettings()
  }
  router.push('/shelf')
}

const fetchBook = async () => {
  const bookId = route.params.id
  if (!bookId || !userStore.token) return

  try {
    const res = await fetch(`/api/books/${bookId}`, {
      headers: { 'Authorization': `Bearer ${userStore.token}` }
    })
    const data = await res.json()
    if (data.code === 200) {
      book.value = {
        id: data.data.id,
        title: data.data.title,
        style: data.data.style,
        word_count: data.data.word_count || 0
      }
      chapters.value = data.data.chapters || []

      const settings = data.data.settings || {}
      relatedItems.value.world.content = settings.world || ''
      relatedItems.value.world.word_count = (settings.world || '').length
      relatedItems.value.outline.content = settings.outline || ''
      relatedItems.value.outline.word_count = (settings.outline || '').length
      relatedItems.value.character.content = settings.character || ''
      relatedItems.value.character.word_count = (settings.character || '').length
      relatedItems.value.inspiration.content = settings.inspiration || ''
      relatedItems.value.inspiration.word_count = (settings.inspiration || '').length

      if (chapters.value.length > 0) {
        selectChapter(chapters.value[0])
      }
    }
  } catch (error) {
    console.error('获取书籍失败:', error)
  }
}

const selectChapter = (chapter) => {
  if (isDirty.value) {
    saveCurrent()
  }
  currentChapterId.value = chapter.id
  isDirty.value = false
  activeTab.value = 'catalog'
}

const switchTab = (tab) => {
  activeTab.value = tab
  if (tab === 'related') {
    currentChapterId.value = null
  }
}

const selectRelated = (key) => {
  if (settingsDirty.value) {
    saveSettings()
  }
  currentRelated.value = key
  settingsDirty.value = false
}

const handleAddChapter = async () => {
  if (!book.value.id) return

  try {
    const res = await fetch(`/api/books/${book.value.id}/chapters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify({ title: '', content: '' })
    })
    const data = await res.json()
    if (data.code === 200) {
      await fetchBook()
      currentChapterId.value = data.data.id
      isDirty.value = false
    } else {
      alert(data.msg)
    }
  } catch (error) {
    alert('添加章节失败')
  }
}

const openChapterDialog = () => {
  newChapterName.value = ''
  showChapterDialog.value = true
}

const closeChapterDialog = () => {
  showChapterDialog.value = false
  newChapterName.value = ''
}

const confirmAddChapter = async () => {
  if (!book.value.id) return

  const chapterTitle = `第${chapters.value.length + 1}章 ${newChapterName.value}`

  try {
    const res = await fetch(`/api/books/${book.value.id}/chapters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify({ title: chapterTitle, content: '' })
    })
    const data = await res.json()
    if (data.code === 200) {
      await fetchBook()
      currentChapterId.value = data.data.id
      isDirty.value = false
      closeChapterDialog()
    } else {
      alert(data.msg)
    }
  } catch (error) {
    alert('添加章节失败')
  }
}

const handleDeleteChapter = async () => {
  if (!currentChapter.value) return
  if (!confirm('确定要删除这个章节吗？')) return

  try {
    const res = await fetch(
      `/api/books/${book.value.id}/chapters/${currentChapter.value.id}`,
      {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${userStore.token}` }
      }
    )
    const data = await res.json()
    if (data.code === 200) {
      await fetchBook()
      currentChapterId.value = chapters.value.length > 0 ? chapters.value[0].id : null
    } else {
      alert(data.msg)
    }
  } catch (error) {
    alert('删除章节失败')
  }
}

const updateWordCount = () => {
  if (currentChapter.value) {
    const content = currentChapter.value.content || ''
    currentChapter.value.word_count = content.length
    isDirty.value = true
  }
}

const markDirty = () => {
  isDirty.value = true
}

const markDirtyRelated = () => {
  settingsDirty.value = true
}

const updateRelatedWords = () => {
  const content = relatedItems.value[currentRelated.value].content || ''
  relatedItems.value[currentRelated.value].word_count = content.length
  settingsDirty.value = true
}

const saveCurrent = async () => {
  if (!currentChapter.value || !isDirty.value) return

  try {
    const res = await fetch(
      `/api/books/${book.value.id}/chapters/${currentChapter.value.id}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userStore.token}`
        },
        body: JSON.stringify({
          title: currentChapter.value.title,
          content: currentChapter.value.content
        })
      }
    )
    const data = await res.json()
    if (data.code === 200) {
      isDirty.value = false
      await fetchBook()
    }
  } catch (error) {
    console.error('保存失败')
  }
}

const saveSettings = async () => {
  if (!book.value.id || !settingsDirty.value) return

  try {
    const settings = {
      world: relatedItems.value.world.content,
      outline: relatedItems.value.outline.content,
      character: relatedItems.value.character.content,
      inspiration: relatedItems.value.inspiration.content
    }

    const res = await fetch(`/api/books/${book.value.id}/settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify({ settings })
    })
    const data = await res.json()
    if (data.code === 200) {
      settingsDirty.value = false
    }
  } catch (error) {
    console.error('保存设定失败')
  }
}

onMounted(() => {
  fetchBook()
})
</script>

<style scoped>
.book-page {
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
}

.book-header {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 20;
}

.book-content {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.back-btn {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f3f4f6;
  color: #333;
}

.book-title {
  flex: 1;
  text-align: center;
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.save-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 6px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.save-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.save-btn:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.book-info {
  display: flex;
  gap: 24px;
  padding: 20px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.book-cover {
  width: 100px;
  height: 130px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.cover-icon {
  font-size: 36px;
}

.book-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
  justify-content: center;
}

.detail-row {
  display: flex;
  gap: 12px;
  font-size: 14px;
}

.detail-row .label {
  color: #999;
  min-width: 50px;
}

.detail-row .value {
  color: #333;
}

.tab-nav {
  display: flex;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 49px;
  z-index: 10;
}

.tab-item {
  flex: 1;
  padding: 14px;
  text-align: center;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-item.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.book-main {
  flex: 1;
  display: flex;
  overflow: hidden;
  height: calc(100vh - 60px - 49px - 48px);
}

.sidebar {
  width: 260px;
  min-width: 160px;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  height: 100%;
}

.sidebar-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.add-btn {
  padding: 6px 12px;
  background: #667eea;
  border: none;
  border-radius: 4px;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
}

.chapter-list,
.related-list {
  flex: 1;
  overflow-y: auto;
  height: calc(100% - 57px);
}

.editor {
  flex: 5;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
  height: 100%;
}

.editor-header {
  flex-shrink: 0;
}

.content-input {
  flex: 1;
}

.chapter-item,
.related-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background 0.2s;
}

.chapter-item:hover,
.related-item:hover {
  background: #f9fafb;
}

.chapter-item.active {
  background: #eef2ff;
  border-left: 3px solid #667eea;
}

.related-item.active {
  background: #eef2ff;
  border-left: 3px solid #667eea;
}

.chapter-title,
.related-item span:first-child {
  font-size: 14px;
  color: #333;
}

.chapter-words,
.words {
  font-size: 12px;
  color: #999;
}

.editor {
  flex: 5;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
}

.editor-header {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.title-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 500;
  color: #333;
  outline: none;
  transition: border-color 0.2s;
}

.title-input:focus {
  border-color: #667eea;
}

.delete-chapter-btn {
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-chapter-btn:hover {
  background: #fee;
  border-color: #fcc;
  color: #c00;
}

.content-input {
  flex: 1;
  width: 100%;
  padding: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.8;
  color: #333;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
}

.content-input:focus {
  border-color: #667eea;
}

.editor-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 12px;
}

.word-count {
  font-size: 13px;
  color: #999;
}

.empty-editor {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  color: #999;
  font-size: 14px;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.chapter-dialog {
  background: #fff;
  border-radius: 12px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.dialog-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.dialog-close:hover {
  color: #333;
}

.dialog-body {
  padding: 20px;
}

.chapter-prefix {
  font-size: 15px;
  color: #666;
  margin-bottom: 12px;
  font-weight: 500;
}

.chapter-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
  box-sizing: border-box;
}

.chapter-input:focus {
  border-color: #667eea;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
  justify-content: flex-end;
}

.dialog-btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  border: none;
}

.dialog-btn.cancel {
  background: #f5f5f5;
  color: #666;
}

.dialog-btn.cancel:hover {
  background: #eee;
}

.dialog-btn.confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.dialog-btn.confirm:hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .book-header {
    position: relative;
    top: 0;
  }

  .book-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
    position: relative;
    top: 0;
  }

  .tab-nav {
    position: relative;
    top: 0;
  }

  .book-main {
    flex-direction: column;
    height: calc(100vh - 60px - 49px - 48px);
    min-height: calc(100vh - 60px - 49px - 48px);
  }

  .sidebar {
    width: 100%;
    min-width: unset;
    max-height: 200px;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
    flex: unset;
    height: 200px;
  }

  .chapter-list,
  .related-list {
    height: calc(100% - 57px);
  }

  .editor {
    flex: 1;
    padding: 15px;
    height: calc(100vh - 60px - 49px - 48px - 200px - 57px);
  }

  .book-details {
    align-items: center;
  }

  .detail-row {
    justify-content: center;
  }

  .title-input {
    font-size: 16px;
    padding: 10px 12px;
  }

  .content-input {
    padding: 15px;
    font-size: 14px;
  }
}
</style>