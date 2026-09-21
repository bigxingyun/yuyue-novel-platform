<template>
  <div class="auth-page">
    <RouterLink to="/" class="mobile-brand">
      <span class="brand-mark">阅</span>
      <span>欲阅</span>
    </RouterLink>

    <div class="steps">
      <span class="step" :class="{ active: step >= 1 }">1. 注册码</span>
      <span class="step-line" />
      <span class="step" :class="{ active: step >= 2 }">2. 账号信息</span>
    </div>

    <h1 class="auth-title">创建账号</h1>
    <p class="auth-subtitle">使用管理员分发的注册码完成注册</p>

    <form v-if="step === 1" class="auth-form" @submit.prevent="nextStep">
      <div class="field">
        <label class="field-label" for="key">注册码</label>
        <input
          id="key"
          v-model="form.registrationKey"
          class="field-input"
          type="text"
          placeholder="XXXX-XXXX"
        />
      </div>
      <button type="submit" class="btn btn-primary btn-block">验证并继续</button>
    </form>

    <form v-else class="auth-form" @submit.prevent="onSubmit">
      <div class="field">
        <label class="field-label" for="nickname">昵称</label>
        <input
          id="nickname"
          v-model="form.nickname"
          class="field-input"
          maxlength="20"
          placeholder="2-20 个字符"
        />
      </div>
      <div class="field">
        <label class="field-label" for="password">密码</label>
        <input id="password" v-model="form.password" class="field-input" type="password" placeholder="至少 6 位" />
      </div>
      <div class="field">
        <label class="field-label" for="confirm">确认密码</label>
        <input id="confirm" v-model="form.confirm" class="field-input" type="password" />
      </div>
      <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
        {{ loading ? '注册中…' : '完成注册' }}
      </button>
      <button type="button" class="btn btn-ghost btn-block" @click="step = 1">返回上一步</button>
    </form>

    <p class="auth-footer">
      已有账号？
      <RouterLink to="/auth/login" class="link">登录</RouterLink>
    </p>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { notify } from '@/utils/errorHandler'

const router = useRouter()
const userStore = useUserStore()
const step = ref(1)
const loading = ref(false)

const form = reactive({
  registrationKey: '',
  nickname: '',
  password: '',
  confirm: '',
})

async function nextStep() {
  const key = form.registrationKey.trim().toUpperCase()
  if (!key) {
    notify('请输入注册码')
    return
  }
  form.registrationKey = key
  loading.value = true
  try {
    const { verifyRegistrationKey } = await import('@/api/auth')
    await verifyRegistrationKey(form.registrationKey)
    step.value = 2
  } catch (e) {
    const { handleError } = await import('@/utils/errorHandler')
    handleError(e)
  } finally {
    loading.value = false
  }
}

async function onSubmit() {
  const nickname = form.nickname.trim()
  if (nickname.length < 2 || nickname.length > 20) {
    notify('昵称长度为 2-20 个字符')
    return
  }
  if (form.password.length < 6) {
    notify('密码至少 6 位')
    return
  }
  if (form.password !== form.confirm) {
    notify('两次密码不一致')
    return
  }
  loading.value = true
  try {
    const { register } = await import('@/api/auth')
    const result = await register({
      registrationKey: form.registrationKey,
      nickname: nickname,
      password: form.password,
    })
    userStore.setAuth(result.accessToken, result.refreshToken, result.user)
    notify('注册成功', 'success')
    router.push('/square')
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
  margin-bottom: 24px;
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

.steps {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  font-size: 12px;
}

.step {
  color: var(--color-text-muted);
}

.step.active {
  color: var(--color-accent);
  font-weight: 500;
}

.step-line {
  flex: 1;
  height: 1px;
  background: var(--color-border);
  max-width: 40px;
}

.auth-title {
  font-family: var(--font-serif);
  font-size: 28px;
  margin-bottom: 8px;
}

.auth-subtitle {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-bottom: 28px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.link {
  color: var(--color-accent);
}

.auth-footer {
  margin-top: 28px;
  text-align: center;
  font-size: 14px;
  color: var(--color-text-secondary);
}
</style>
