<template>
  <div class="shelf-page">
    <div class="container">
      <h1>我的书架</h1>

      <div v-if="!userStore.isLoggedIn" class="login-prompt">
        <p>请先登录后再访问书架</p>
        <button class="login-btn" @click="goToLogin">去登录</button>
      </div>

      <template v-else>
        <div class="shelf-controls">
          <button class="add-btn" @click="showAddDialog = true">📚 添加作品</button>
        </div>

        <div v-if="books.length === 0" class="empty-state">
          <p>书架空空如也，快去创作你的第一部作品吧！</p>
          <router-link to="/novel" class="start-link">开始创作</router-link>
        </div>

        <div v-else class="books-grid">
          <div v-for="book in books" :key="book.id" class="book-card" @click="openBook(book)">
            <div class="book-cover">
              <span class="book-icon">📖</span>
            </div>
            <div class="book-info">
              <h3>{{ book.title }}</h3>
              <p class="book-style">{{ book.style }}</p>
              <p class="book-date">{{ book.date }}</p>
              <div class="book-actions">
                <button @click.stop="editBook(book)">编辑</button>
                <button @click.stop="deleteBook(book.id)">删除</button>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <div v-if="showAddDialog" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog">
        <h2>{{ editingBook ? '编辑作品' : '添加作品' }}</h2>
        <div class="form-item">
          <label>作品名称</label>
          <input v-model="bookForm.title" type="text" placeholder="请输入作品名称" />
        </div>
        <div class="form-item">
          <label>作品风格</label>
          <select v-model="bookForm.style">
            <option value="古风武侠">古风武侠</option>
            <option value="现代都市">现代都市</option>
            <option value="甜宠言情">甜宠言情</option>
            <option value="悬疑推理">悬疑推理</option>
            <option value="科幻未来">科幻未来</option>
            <option value="玄幻修仙">玄幻修仙</option>
            <option value="脑洞反转">脑洞反转</option>
          </select>
        </div>
        <div class="dialog-buttons">
          <button @click="closeDialog">取消</button>
          <button @click="saveBook">{{ editingBook ? '保存' : '添加' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const books = ref([])
const showAddDialog = ref(false)
const editingBook = ref(null)
const bookForm = ref({
  title: '',
  style: '现代都市'
})

const goToLogin = () => {
  router.push('/login')
}

const fetchBooks = async () => {
  if (!userStore.token) return

  try {
    const res = await fetch('http://localhost:5000/api/books', {
      headers: { 'Authorization': `Bearer ${userStore.token}` }
    })
    const data = await res.json()
    if (data.code === 200) {
      books.value = data.data
    }
  } catch (error) {
    console.error('获取书架失败:', error)
  }
}

const saveBook = async () => {
  if (!bookForm.value.title.trim()) {
    alert('请输入作品名称')
    return
  }

  if (editingBook.value) {
    try {
      const res = await fetch(`http://localhost:5000/api/books/${editingBook.value.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userStore.token}`
        },
        body: JSON.stringify({
          title: bookForm.value.title,
          style: bookForm.value.style
        })
      })
      const data = await res.json()
      if (data.code === 200) {
        await fetchBooks()
      } else {
        alert(data.msg)
      }
    } catch (error) {
      alert('更新失败')
    }
  } else {
    try {
      const res = await fetch('http://localhost:5000/api/books', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userStore.token}`
        },
        body: JSON.stringify({
          title: bookForm.value.title,
          style: bookForm.value.style
        })
      })
      const data = await res.json()
      if (data.code === 200) {
        await fetchBooks()
      } else {
        alert(data.msg)
      }
    } catch (error) {
      alert('添加失败')
    }
  }

  closeDialog()
}

const editBook = (book) => {
  editingBook.value = book
  bookForm.value = {
    title: book.title,
    style: book.style
  }
  showAddDialog.value = true
}

const deleteBook = async (id) => {
  if (!confirm('确定要删除这部作品吗？')) return

  try {
    const res = await fetch(`http://localhost:5000/api/books/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${userStore.token}` }
    })
    const data = await res.json()
    if (data.code === 200) {
      await fetchBooks()
    } else {
      alert(data.msg)
    }
  } catch (error) {
    alert('删除失败')
  }
}

const openBook = (book) => {
  router.push(`/shelf/${book.id}`)
}

const closeDialog = () => {
  showAddDialog.value = false
  editingBook.value = null
  bookForm.value = { title: '', style: '现代都市' }
}

onMounted(() => {
  if (userStore.isLoggedIn) {
    fetchBooks()
  }
})
</script>

<style scoped>
.shelf-page {
  min-height: calc(100vh - 60px);
  padding: 40px 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 32px;
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

.shelf-controls {
  text-align: center;
  margin-bottom: 40px;
}

.add-btn {
  padding: 12px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.add-btn:hover {
  transform: translateY(-2px);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.empty-state p {
  color: #666;
  font-size: 18px;
  margin-bottom: 20px;
}

.start-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.start-link:hover {
  text-decoration: underline;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 30px;
}

.book-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
  cursor: pointer;
}

.book-card:hover {
  transform: translateY(-5px);
}

.book-cover {
  height: 150px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}

.book-icon {
  font-size: 60px;
}

.book-info {
  padding: 20px;
}

.book-info h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 18px;
}

.book-style {
  color: #667eea;
  font-size: 14px;
  margin-bottom: 5px;
}

.book-date {
  color: #999;
  font-size: 12px;
  margin-bottom: 15px;
}

.book-actions {
  display: flex;
  gap: 10px;
}

.book-actions button {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.book-actions button:first-child {
  background-color: #667eea;
  color: white;
}

.book-actions button:last-child {
  background-color: #f44336;
  color: white;
}

.book-actions button:hover {
  opacity: 0.9;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.dialog {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
}

.dialog h2 {
  margin: 0 0 20px 0;
  color: #333;
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
}

.form-item input,
.form-item select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.dialog-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.dialog-buttons button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.dialog-buttons button:first-child {
  background-color: #ddd;
  color: #333;
}

.dialog-buttons button:last-child {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}
</style>