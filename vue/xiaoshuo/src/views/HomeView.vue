<template>
  <div class="home">
    <div class="hero">
      <div class="banner-carousel">
        <div
          v-for="(banner, index) in banners"
          :key="index"
          class="banner-slide"
          :class="{ active: currentBanner === index }"
        >
          <img :src="banner" alt="banner">
        </div>
      </div>

      <button class="carousel-arrow left" @click="prevBanner">‹</button>
      <button class="carousel-arrow right" @click="nextBanner">›</button>

      <div class="carousel-indicators">
        <span
          v-for="(_, index) in banners"
          :key="index"
          :class="{ active: currentBanner === index }"
          @click="goToBanner(index)"
        ></span>
      </div>

      <div class="hero-content">
        <div class="content-wrapper">
          <h1>欢迎使用 AI 写作平台</h1>
          <p>利用人工智能技术，助您创作精彩小说</p>
          <router-link to="/novel" class="start-btn">开始创作</router-link>
        </div>
      </div>
    </div>

    <div class="quick-entry">
      <div class="section-header">
        <h2>🚀 快捷入口</h2>
      </div>
      <div class="entry-grid">
        <router-link to="/novel" class="entry-card">
          <span class="entry-icon">✍️</span>
          <span class="entry-title">智能续写</span>
          <span class="entry-desc">AI续写您的小说</span>
        </router-link>
        <router-link to="/novel" class="entry-card">
          <span class="entry-icon">💡</span>
          <span class="entry-title">灵感激发</span>
          <span class="entry-desc">获取创作灵感</span>
        </router-link>
        <router-link to="/novel" class="entry-card">
          <span class="entry-icon">⚙️</span>
          <span class="entry-title">设定构建</span>
          <span class="entry-desc">完善世界观设定</span>
        </router-link>
        <router-link to="/shelf" class="entry-card">
          <span class="entry-icon">📚</span>
          <span class="entry-title">我的书架</span>
          <span class="entry-desc">管理您的作品</span>
        </router-link>
      </div>
    </div>

    <div class="features">
      <div class="section-header">
        <h2>✨ 核心功能</h2>
      </div>
      <div class="feature-grid">
        <div class="feature-card">
          <h3>🎭 多种风格</h3>
          <p>支持古风武侠、现代都市、甜宠言情、悬疑推理、科幻未来、玄幻修仙等多种小说风格</p>
        </div>
        <div class="feature-card">
          <h3>✍️ 智能续写</h3>
          <p>AI自动为您续写故事，保持情节连贯、语言流畅，激发创作灵感</p>
        </div>
        <div class="feature-card">
          <h3>📚 个人书架</h3>
          <p>保存您的创作成果，随时查看和管理作品，章节编辑更方便</p>
        </div>
        <div class="feature-card">
          <h3>💡 灵感记录</h3>
          <p>随时记录创作灵感，整理人物设定，构建完整世界观</p>
        </div>
      </div>
    </div>

    

    <div class="cta-section">
      <h2>准备好开始您的创作之旅了吗？</h2>
      <p>加入我们，让AI助您实现写作梦想</p>
      <router-link to="/novel" class="cta-btn">立即开始</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const banners = [
  '/images/banner1.jpg',
  '/images/banner2.jpg',
  '/images/banner3.jpg',
  '/images/banner4.jpg',
  '/images/banner5.jpg'
]

const currentBanner = ref(0)
let timer = null

const goToBanner = (index) => {
  currentBanner.value = index
}

const nextBanner = () => {
  currentBanner.value = (currentBanner.value + 1) % banners.length
}

const prevBanner = () => {
  currentBanner.value = (currentBanner.value - 1 + banners.length) % banners.length
}

onMounted(() => {
  timer = setInterval(nextBanner, 4000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.home {
  overflow-x: hidden;
}

.hero {
  position: relative;
  height: 100vh;
  overflow: hidden;
}

.banner-carousel {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.banner-slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 1s ease-in-out;
}

.banner-slide.active {
  opacity: 1;
}

.banner-slide img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.carousel-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.3);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 30px;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-arrow:hover {
  background: rgba(255, 255, 255, 0.5);
}

.carousel-arrow.left {
  left: 20px;
}

.carousel-arrow.right {
  right: 20px;
}

.carousel-indicators {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 12px;
  z-index: 10;
}

.carousel-indicators span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s;
}

.carousel-indicators span.active {
  background: white;
  transform: scale(1.2);
}

.carousel-indicators span:hover {
  background: rgba(255, 255, 255, 0.8);
}

.hero-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 5;
  text-align: center;
  color: white;
  width: 100%;
}

.content-wrapper {
  display: inline-block;
  background: rgba(0, 0, 0, 0.3);
  padding: 40px 60px;
  border-radius: 16px;
  backdrop-filter: blur(4px);
}

.hero-content h1 {
  font-size: 48px;
  margin-bottom: 20px;
  text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
}

.hero-content p {
  font-size: 20px;
  margin-bottom: 30px;
  opacity: 0.95;
  text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.5);
}

.start-btn {
  display: inline-block;
  padding: 15px 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 50px;
  font-size: 18px;
  font-weight: bold;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
}

.start-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
}

.section-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-header h2 {
  font-size: 28px;
  color: #333;
  margin: 0;
}

.quick-entry {
  max-width: 1200px;
  margin: 60px auto;
  padding: 0 20px;
}

.entry-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.entry-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
}

.entry-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.15);
}

.entry-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.entry-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.entry-desc {
  font-size: 14px;
  color: #999;
}

.features {
  max-width: 1200px;
  margin: 60px auto;
  padding: 0 20px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
}

.feature-card {
  padding: 30px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}

.feature-card h3 {
  font-size: 20px;
  margin-bottom: 15px;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.8;
  margin: 0;
}



.cta-section {
  text-align: center;
  padding: 80px 20px;
  background: #f8f9fa;
}

.cta-section h2 {
  font-size: 32px;
  color: #333;
  margin-bottom: 15px;
}

.cta-section p {
  font-size: 18px;
  color: #666;
  margin-bottom: 30px;
}

.cta-btn {
  display: inline-block;
  padding: 18px 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 50px;
  font-size: 18px;
  font-weight: bold;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
}

.cta-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.6);
}

@media (max-width: 992px) {
  .entry-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 576px) {
  .entry-grid {
    grid-template-columns: 1fr;
  }

  .content-wrapper {
    padding: 20px 25px;
  }

  .hero-content h1 {
    font-size: 24px;
  }

  .carousel-indicators {
    bottom: 20px;
  }

  .carousel-indicators span {
    width: 10px;
    height: 10px;
  }
}

@media (max-width: 768px) {
  .carousel-arrow {
    display: none;
  }

  .hero-content h1 {
    font-size: 28px;
    margin-bottom: 15px;
  }

  .hero-content p {
    font-size: 14px;
    margin-bottom: 20px;
  }

  .content-wrapper {
    padding: 25px 30px;
    margin: 0 15px;
  }

  .start-btn {
    padding: 12px 30px;
    font-size: 16px;
  }

  .entry-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .entry-card {
    padding: 20px 15px;
  }

  .entry-icon {
    font-size: 36px;
    margin-bottom: 10px;
  }

  .entry-title {
    font-size: 14px;
  }

  .entry-desc {
    font-size: 12px;
  }

  .section-header h2 {
    font-size: 22px;
  }

  .feature-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .feature-card {
    padding: 20px;
  }

  .feature-card h3 {
    font-size: 16px;
  }

  .feature-card p {
    font-size: 14px;
  }

  .cta-section {
    padding: 50px 20px;
  }

  .cta-section h2 {
    font-size: 24px;
  }

  .cta-section p {
    font-size: 14px;
  }

  .cta-btn {
    padding: 14px 35px;
    font-size: 16px;
  }
}
</style>
