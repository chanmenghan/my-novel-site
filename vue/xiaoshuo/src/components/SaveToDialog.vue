<template>
  <div v-if="visible" class="dialog-overlay" @click.self="closeDialog">
    <div class="dialog">
      <div class="dialog-header">
        <h2>保存到</h2>
        <button class="close-btn" @click="closeDialog">×</button>
      </div>

      <div class="dialog-content">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="!userStore.isLoggedIn" class="empty-message">
          请先登录
        </div>
        <div v-else-if="books.length === 0" class="empty-message">
          暂无作品，请先创建作品
        </div>
        <div v-else class="book-list">
          <div v-for="book in books" :key="book.id" class="book-item">
            <div class="book-header" @click="toggleBook(book.id)">
              <span class="book-icon">📚</span>
              <span class="book-title">{{ book.title }}</span>
              <span class="expand-icon">{{ expandedBookId === book.id ? '▼' : '▶' }}</span>
            </div>
            <div v-if="expandedBookId === book.id" class="chapter-list">
              <div v-if="loadingChapters" class="loading-small">加载章节...</div>
              <div v-else-if="book.chapters && book.chapters.length > 0">
                <div
                  v-for="chapter in book.chapters"
                  :key="chapter.id"
                  class="chapter-item"
                  @click="selectChapter(book.id, chapter)"
                >
                  <span class="chapter-title">{{ chapter.title || '第' + chapter.sort_order + '章' }}</span>
                  <span class="chapter-words">{{ chapter.word_count }}字</span>
                </div>
              </div>
              <div v-else class="empty-chapters">暂无章节</div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="selectedChapter" class="selected-info">
        <p>已选择：{{ selectedChapter.bookTitle }} - {{ selectedChapter.chapterTitle }}</p>
        <div class="save-options">
          <label>
            <input type="checkbox" v-model="appendMode" />
            追加到章节末尾
          </label>
          <label v-if="!appendMode">
            <input type="checkbox" v-model="replaceMode" />
            替换章节内容
          </label>
        </div>
        <button class="confirm-btn" @click="confirmSave" :disabled="saving">
          {{ saving ? '保存中...' : '确认保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useUserStore } from '../stores/user'

const props = defineProps({
  visible: Boolean,
  content: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'saved'])

const userStore = useUserStore()

const books = ref([])
const expandedBookId = ref(null)
const loading = ref(false)
const loadingChapters = ref(false)
const selectedChapter = ref(null)
const appendMode = ref(true)
const replaceMode = ref(false)
const saving = ref(false)

watch(() => props.visible, async (newVal) => {
  if (newVal) {
    await fetchBooks()
    selectedChapter.value = null
    expandedBookId.value = null
  }
})

const fetchBooks = async () => {
  if (!userStore.token) return

  loading.value = true
  try {
    const res = await fetch('http://localhost:5000/api/books', {
      headers: { 'Authorization': `Bearer ${userStore.token}` }
    })
    const data = await res.json()
    if (data.code === 200) {
      books.value = data.data
      for (const book of books.value) {
        await fetchChapters(book)
      }
    }
  } catch (error) {
    console.error('获取作品失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchChapters = async (book) => {
  try {
    const res = await fetch(`http://localhost:5000/api/books/${book.id}`, {
      headers: { 'Authorization': `Bearer ${userStore.token}` }
    })
    const data = await res.json()
    if (data.code === 200) {
      book.chapters = data.data.chapters || []
    }
  } catch (error) {
    console.error('获取章节失败:', error)
  }
}

const toggleBook = async (bookId) => {
  if (expandedBookId.value === bookId) {
    expandedBookId.value = null
  } else {
    expandedBookId.value = bookId
    const book = books.value.find(b => b.id === bookId)
    if (book && (!book.chapters || book.chapters.length === 0)) {
      loadingChapters.value = true
      await fetchChapters(book)
      loadingChapters.value = false
    }
  }
}

const selectChapter = (bookId, chapter) => {
  const book = books.value.find(b => b.id === bookId)
  selectedChapter.value = {
    bookId,
    chapterId: chapter.id,
    bookTitle: book.title,
    chapterTitle: chapter.title || '第' + chapter.sort_order + '章'
  }
}

const confirmSave = async () => {
  if (!selectedChapter.value || !props.content) return

  saving.value = true
  try {
    let newContent
    if (appendMode.value) {
      newContent = (selectedChapter.value.currentContent || '') + '\n\n' + props.content
    } else {
      newContent = props.content
    }

    const res = await fetch(`http://localhost:5000/api/books/${selectedChapter.value.bookId}/chapters/${selectedChapter.value.chapterId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify({
        content: newContent,
        title: selectedChapter.value.chapterTitle
      })
    })
    const data = await res.json()
    if (data.code === 200) {
      alert('保存成功！')
      emit('saved')
      closeDialog()
    } else {
      alert(data.msg || '保存失败')
    }
  } catch (error) {
    alert('保存失败：' + error.message)
  } finally {
    saving.value = false
  }
}

const closeDialog = () => {
  emit('close')
}
</script>

<style scoped>
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
  z-index: 2000;
}

.dialog {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.dialog-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0 5px;
}

.dialog-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.loading, .empty-message, .empty-chapters {
  text-align: center;
  color: #666;
  padding: 20px;
}

.loading-small {
  text-align: center;
  color: #999;
  font-size: 14px;
  padding: 10px;
}

.book-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.book-item {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.book-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  background: #f8f9fa;
  cursor: pointer;
  transition: background 0.2s;
}

.book-header:hover {
  background: #e9ecef;
}

.book-icon {
  font-size: 18px;
}

.book-title {
  flex: 1;
  font-weight: 500;
  color: #333;
}

.expand-icon {
  color: #666;
  font-size: 12px;
}

.chapter-list {
  padding: 10px;
  background: white;
}

.chapter-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.2s;
}

.chapter-item:hover {
  background: #f0f0f0;
}

.chapter-title {
  color: #333;
  font-size: 14px;
}

.chapter-words {
  color: #999;
  font-size: 12px;
}

.selected-info {
  padding: 20px;
  border-top: 1px solid #eee;
  background: #f8f9fa;
}

.selected-info p {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 14px;
}

.save-options {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.save-options label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
}

.confirm-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.confirm-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.confirm-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
