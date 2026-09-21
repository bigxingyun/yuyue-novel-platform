<template>
  <div class="auth-page">
    <RouterLink to="/" class="mobile-brand">
      <span class="brand-mark">阅</span>
      <span>欲阅</span>
    </RouterLink>

    <h1 class="auth-title">找回密码</h1>
    <p class="auth-subtitle">输入账号与管理员提供的找回密钥</p>

    <form class="auth-form" @submit.prevent="onSubmit">
      <div class="field">
        <label class="field-label" for="account">账号</label>
        <input id="account" v-model="form.account" class="field-input" placeholder="昵称或用户 ID" />
      </div>
      <div class="field">
        <label class="field-label" for="recoveryKey">找回密钥</label>
        <input id="recoveryKey" v-model="form.recoveryKey" class="field-input" placeholder="由管理员分发" />
      </div>
      <div class="field">
        <label class="field-label" for="newPassword">新密码</label>
        <input id="newPassword" v-model="form.newPassword" class="field-input" type="password" />
      </div>
      <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
        {{ loading ? '提交中…' : '重置密码' }}
      </button>
    </form>

    <p class="auth-footer">
      <RouterLink to="/auth/login" class="link">返回登录</RouterLink>
    </p>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { recoverPassword } from '@/api/auth'
import { handleError, notify } from '@/utils/errorHandler'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  account: '',
  recoveryKey: '',
  newPassword: '',
})

async function onSubmit() {
  const account = form.account.trim()
  const recoveryKey = form.recoveryKey.trim()
  if (!account) {
    notify('请输入账号')
    return
  }
  if (!recoveryKey) {
    notify('请输入找回密钥')
    return
  }
  if (form.newPassword.length < 6) {
    notify('新密码至少 6 位')
    return
  }
  loading.value = true
  try {
    await recoverPassword({
      account,
      recoveryKey,
      newPassword: form.newPassword,
    })
    notify('密码已重置', 'success')
    router.push('/auth/login')
  } catch (e) {
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

.link {
  color: var(--color-accent);
}

.auth-footer {
  margin-top: 28px;
  text-align: center;
  font-size: 14px;
}
</style>
