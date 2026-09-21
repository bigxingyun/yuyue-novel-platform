<template>
  <div class="sub-page page-container">
    <SubPageHeader title="修改密码" />
    <form class="form card" @submit.prevent="onSave">
      <div class="field">
        <label class="field-label">旧密码</label>
        <input v-model="oldPwd" class="field-input" type="password" />
      </div>
      <div class="field">
        <label class="field-label">新密码</label>
        <input v-model="newPwd" class="field-input" type="password" />
      </div>
      <div class="field">
        <label class="field-label">确认新密码</label>
        <input v-model="confirmPwd" class="field-input" type="password" />
      </div>
      <button type="submit" class="btn btn-primary btn-block">确认修改</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import SubPageHeader from '@/components/common/SubPageHeader.vue'
import { changePassword } from '@/api/users'
import { handleError, notify } from '@/utils/errorHandler'

const router = useRouter()
const oldPwd = ref('')
const newPwd = ref('')
const confirmPwd = ref('')

async function onSave() {
  if (newPwd.value !== confirmPwd.value) {
    notify('两次新密码不一致')
    return
  }
  try {
    await changePassword(oldPwd.value, newPwd.value)
    notify('密码已更新', 'success')
    router.back()
  } catch (e) {
    handleError(e)
  }
}
</script>

<style scoped>
.form {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 480px;
}
</style>
