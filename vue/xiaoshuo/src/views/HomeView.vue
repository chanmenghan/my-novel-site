<template>
  <div class="home">
    <div class="hero">
      <h1>欢迎使用 AI 写作平台</h1>
      <p>利用人工智能技术，助您创作精彩小说</p>
      <router-link to="/novel" class="start-btn">开始创作</router-link>
    </div>

    <div class="features">
      <div class="feature-card">
        <h3>🎭 多种风格</h3>
        <p>支持古风武侠、现代都市、甜宠言情等多种小说风格</p>
      </div>
      <div class="feature-card">
        <h3>✍️ 智能续写</h3>
        <p>AI自动为您续写故事，保持情节连贯、语言流畅</p>
      </div>
      <div class="feature-card">
        <h3>📚 个人书架</h3>
        <p>保存您的创作成果，随时查看和管理作品</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  min-height: calc(100vh - 60px);
}

.hero {
  text-align: center;
  padding: 80px 20px;
  background: url('/images/poster.jpg') center center / cover no-repeat;
  color: white;
  min-height: 400px;
  position: relative;
}

.hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
}

.hero h1,
.hero p,
.hero .start-btn {
  position: relative;
  z-index: 1;
}

.hero h1 {
  font-size: 48px;
  margin-bottom: 20px;
}

.hero p {
  font-size: 20px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.start-btn {
  display: inline-block;
  padding: 15px 40px;
  background-color: white;
  color: #667eea;
  text-decoration: none;
  border-radius: 50px;
  font-size: 18px;
  font-weight: bold;
  transition: transform 0.3s ease;
}

.start-btn:hover {
  transform: scale(1.05);
}

.features {
  display: flex;
  gap: 30px;
  max-width: 1200px;
  margin: 60px auto;
  padding: 0 20px;
  flex-wrap: wrap;
  justify-content: center;
}

.feature-card {
  flex: 1;
  min-width: 280px;
  max-width: 350px;
  padding: 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  text-align: center;
}

.feature-card h3 {
  font-size: 24px;
  margin-bottom: 15px;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 32px;
  }

  .hero p {
    font-size: 16px;
  }

  .features {
    flex-direction: column;
    align-items: center;
  }

  .feature-card {
    width: 100%;
  }
}
</style>
