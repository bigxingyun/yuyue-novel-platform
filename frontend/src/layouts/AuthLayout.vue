<template>
  <div class="auth-layout">
    <div class="auth-visual">
      <div class="auth-visual-inner">
        <RouterLink to="/" class="auth-brand">
          <span class="brand-mark">阅</span>
          <span>欲阅</span>
        </RouterLink>
        <blockquote class="auth-quote">
          <p>短篇里有长夜，段落间藏着回声。</p>
          <footer>在欲阅，每一段都值得被细读</footer>
        </blockquote>
      </div>
    </div>
    <div class="auth-form-panel">
      <RouterView v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  display: grid;
  min-height: 100dvh;
}

@media (min-width: 900px) {
  .auth-layout {
    grid-template-columns: 1fr 1fr;
  }
}

.auth-visual {
  display: none;
  background:
    linear-gradient(145deg, rgba(139, 41, 66, 0.92), rgba(45, 74, 62, 0.88)),
    url('https://picsum.photos/seed/yuyue-auth-bg/1200/1600') center / cover;
  color: #fff;
}

@media (min-width: 900px) {
  .auth-visual {
    display: flex;
    align-items: flex-end;
    padding: 48px;
  }
}

.auth-visual-inner {
  max-width: 400px;
}

.auth-brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 48px;
  font-family: var(--font-serif);
  font-size: 22px;
  font-weight: 600;
}

.brand-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  font-size: 22px;
}

.auth-quote p {
  font-family: var(--font-serif);
  font-size: clamp(1.5rem, 3vw, 2rem);
  line-height: 1.45;
  margin-bottom: 16px;
}

.auth-quote footer {
  font-size: 14px;
  opacity: 0.75;
}

.auth-form-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
  background: var(--color-bg);
}
</style>
