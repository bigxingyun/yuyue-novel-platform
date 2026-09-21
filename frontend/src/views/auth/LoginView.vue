<template>
  <div class="auth-page">
    <RouterLink to="/" class="mobile-brand">
      <span class="brand-mark">阅</span>
      <span>欲阅</span>
    </RouterLink>

    <h1 class="auth-title">欢迎回来</h1>
    <p class="auth-subtitle">登录后继续你的阅读旅程</p>

    <form class="auth-form" @submit.prevent="onSubmit">
      <div class="field">
        <label class="field-label" for="account">账号</label>
        <input
          id="account"
          v-model="form.account"
          class="field-input"
          type="text"
          placeholder="昵称或用户 ID"
          autocomplete="username"
        />
      </div>
      <div class="field">
        <label class="field-label" for="password">密码</label>
        <input
          id="password"
          v-model="form.password"
          class="field-input"
          type="password"
          placeholder="请输入密码"
          autocomplete="current-password"
        />
      </div>
      <div class="auth-row">
        <RouterLink to="/auth/recover" class="link">忘记密码？</RouterLink>
      </div>
      <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
        {{ loading ? '登录中…' : '登录' }}
      </button>
    </form>

    <p class="auth-footer">
      还没有账号？
      <RouterLink to="/auth/register" class="link">注册</RouterLink>
    </p>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { notify } from '@/utils/errorHandler'
import { safeRedirectPath } from '@/utils/safeRedirect'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const form = reactive({
  account: '',
  password: '',
})

async function onSubmit() {
  if (!form.account.trim() || !form.password) {
    notify('请填写账号和密码')
    return
  }
  loading.value = true
  try {
    const { login } = await import('@/api/auth')
    const result = await login(form.account.trim(), form.password)
    userStore.setAuth(result.accessToken, result.refreshToken, result.user)
    notify('登录成功', 'success')
    router.push(safeRedirectPath(route.query.redirect as string))
  } catch (e) {
    const { handleError } = await import('@/utils/errorHandler')
    handleError(e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  width: 100%;
  max-width: 400px;
}

.mobile-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 32px;
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 600;
}

@media (min-width: 900px) {
  .mobile-brand {
    display: none;
  }
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
  font-size: 16px;
}

.auth-title {
  font-family: var(--font-serif);
  font-size: 28px;
  margin-bottom: 8px;
}

.auth-subtitle {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-bottom: 32px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.auth-row {
  display: flex;
  justify-content: flex-end;
  margin-top: -8px;
}

.link {
  font-size: 13px;
  color: var(--color-accent);
}

.link:hover {
  text-decoration: underline;
}

.auth-footer {
  margin-top: 28px;
  text-align: center;
  font-size: 14px;
  color: var(--color-text-secondary);
}
</style>
