<template>
  <div class="landing">
    <header class="landing-header">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">阅</span>
        <span class="brand-name">欲阅</span>
      </RouterLink>
      <div class="landing-header-actions">
        <template v-if="isLoggedIn">
          <span class="welcome">欢迎，{{ userInfo?.nickname }}</span>
          <RouterLink to="/square" class="btn btn-primary btn-sm">进入广场</RouterLink>
        </template>
        <template v-else>
          <RouterLink to="/auth/login" class="btn btn-ghost btn-sm">登录</RouterLink>
          <RouterLink to="/auth/register" class="btn btn-primary btn-sm">注册</RouterLink>
        </template>
      </div>
    </header>

    <section class="hero">
      <div class="hero-content">
        <p class="hero-eyebrow">短篇小说阅读平台</p>
        <h1 class="hero-title">
          在段落之间<br />
          <em>遇见故事</em>
        </h1>
        <p class="hero-desc">在阅读中相遇</p>
        <div class="hero-cta">
          <RouterLink v-if="isLoggedIn" to="/square" class="btn btn-primary">
            进入书籍广场
            <PhArrowRight :size="18" />
          </RouterLink>
          <template v-else>
            <RouterLink to="/auth/register" class="btn btn-primary">
              开始阅读
              <PhArrowRight :size="18" />
            </RouterLink>
            <RouterLink to="/auth/login" class="btn btn-secondary">已有账号</RouterLink>
          </template>
        </div>
      </div>
      <div class="hero-visual">
        <div class="hero-book-stack">
          <img
            v-for="(book, i) in featuredBooks"
            :key="book.id"
            :src="book.cover"
            :alt="book.title"
            class="hero-book"
            :style="{ '--i': i }"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { PhArrowRight } from '@phosphor-icons/vue'
import { fetchBookList } from '@/api/books'
import { useUserStore } from '@/stores/user'
import type { BookListItem } from '@/types/book'

const userStore = useUserStore()
const featuredBooks = ref<BookListItem[]>([])

const isLoggedIn = computed(() => userStore.isLoggedIn)
const userInfo = computed(() => userStore.userInfo)

onMounted(async () => {
  try {
    const result = await fetchBookList({ pageSize: 3 })
    featuredBooks.value = result.items
  } catch {
    featuredBooks.value = []
  }
})
</script>

<style scoped>
.landing {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}

.landing-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: var(--content-max-width);
  margin: 0 auto;
  width: 100%;
  padding: 20px;
  height: var(--header-height);
  flex-shrink: 0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: var(--color-accent);
  color: #fff;
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 700;
}

.brand-name {
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.08em;
}

.landing-header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.welcome {
  font-size: 14px;
  color: var(--color-text-secondary);
  display: none;
}

@media (min-width: 640px) {
  .welcome {
    display: inline;
  }
}

.hero {
  flex: 1;
  display: grid;
  gap: 40px;
  max-width: var(--content-max-width);
  margin: 0 auto;
  width: 100%;
  padding: 24px 20px 48px;
  align-items: center;
}

@media (min-width: 900px) {
  .hero {
    grid-template-columns: 1fr 1fr;
    padding-top: 32px;
    padding-bottom: 64px;
  }
}

.hero-eyebrow {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-accent);
  margin-bottom: 16px;
}

.hero-title {
  font-family: var(--font-serif);
  font-size: clamp(2.2rem, 5vw, 3.2rem);
  line-height: 1.15;
  letter-spacing: 0.02em;
  margin-bottom: 20px;
}

.hero-title em {
  font-style: italic;
  color: var(--color-accent);
}

.hero-desc {
  font-family: var(--font-serif);
  font-size: 18px;
  color: var(--color-text-secondary);
  letter-spacing: 0.12em;
  margin-bottom: 32px;
}

.hero-cta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-book-stack {
  position: relative;
  width: min(100%, 320px);
  height: 380px;
}

.hero-book {
  position: absolute;
  width: 200px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  object-fit: cover;
  aspect-ratio: 5/7;
  transition: transform 0.4s ease;
}

.hero-book:nth-child(1) {
  left: 0;
  top: 20px;
  transform: rotate(-8deg);
  z-index: 1;
}

.hero-book:nth-child(2) {
  left: 60px;
  top: 0;
  transform: rotate(2deg);
  z-index: 2;
}

.hero-book:nth-child(3) {
  left: 120px;
  top: 30px;
  transform: rotate(10deg);
  z-index: 3;
}

.hero-book-stack:hover .hero-book:nth-child(1) {
  transform: rotate(-12deg) translateY(-8px);
}

.hero-book-stack:hover .hero-book:nth-child(2) {
  transform: rotate(0deg) translateY(-12px);
}

.hero-book-stack:hover .hero-book:nth-child(3) {
  transform: rotate(14deg) translateY(-8px);
}
</style>
