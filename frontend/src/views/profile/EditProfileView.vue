<template>

  <div class="sub-page page-container">

    <SubPageHeader title="修改资料" />

    <form class="form card" @submit.prevent="onSave">

      <div class="avatar-edit">

        <img :src="avatarPreview" alt="" />

        <input ref="fileInputRef" type="file" accept="image/*" class="hidden-input" @change="onAvatarChange" />

        <button type="button" class="btn btn-secondary btn-sm" :disabled="uploading" @click="fileInputRef?.click()">

          {{ uploading ? '上传中…' : '更换头像' }}

        </button>

      </div>

      <div class="field">

        <label class="field-label">昵称</label>

        <input v-model="nickname" class="field-input" maxlength="20" />

      </div>

      <button type="submit" class="btn btn-primary btn-block" :disabled="saving">

        {{ saving ? '保存中…' : '保存' }}

      </button>

    </form>

  </div>

</template>



<script setup lang="ts">

import { computed, onMounted, ref } from 'vue'

import SubPageHeader from '@/components/common/SubPageHeader.vue'

import { uploadImage } from '@/api/upload'

import { fetchCurrentUser, updateProfile } from '@/api/users'

import { useUserStore } from '@/stores/user'

import { handleError, notify } from '@/utils/errorHandler'



const userStore = useUserStore()

const nickname = ref('')

const avatar = ref('')

const originalNickname = ref('')

const originalAvatar = ref('')

const fileInputRef = ref<HTMLInputElement | null>(null)

const uploading = ref(false)

const saving = ref(false)



const avatarPreview = computed(

  () => avatar.value || 'https://api.dicebear.com/7.x/notionists/svg?seed=yuyue',

)



onMounted(async () => {

  try {

    const user = await fetchCurrentUser()

    nickname.value = user.nickname

    avatar.value = user.avatar || ''

    originalNickname.value = user.nickname

    originalAvatar.value = user.avatar || ''

  } catch (e) {

    handleError(e)

    nickname.value = userStore.userInfo?.nickname ?? ''

    avatar.value = userStore.userInfo?.avatar ?? ''

    originalNickname.value = nickname.value

    originalAvatar.value = avatar.value

  }

})



async function onAvatarChange(e: Event) {

  const file = (e.target as HTMLInputElement).files?.[0]

  if (!file) return

  uploading.value = true

  try {

    avatar.value = await uploadImage(file)

    notify('头像已上传，记得保存', 'success')

  } catch (err) {

    handleError(err)

  } finally {

    uploading.value = false

    if (fileInputRef.value) fileInputRef.value.value = ''

  }

}



async function onSave() {

  const trimmed = nickname.value.trim()

  if (trimmed.length < 2) {

    notify('昵称至少 2 个字符')

    return

  }



  const payload: { nickname?: string; avatar?: string } = {}

  if (trimmed !== originalNickname.value) payload.nickname = trimmed

  if (avatar.value !== originalAvatar.value) payload.avatar = avatar.value



  if (!payload.nickname && !payload.avatar) {

    notify('没有需要保存的修改')

    return

  }



  saving.value = true

  try {

    const user = await updateProfile(payload)

    if (userStore.userInfo) {

      userStore.userInfo.nickname = user.nickname

      userStore.userInfo.avatar = user.avatar

    }

    originalNickname.value = user.nickname

    originalAvatar.value = user.avatar || ''

    nickname.value = user.nickname

    avatar.value = user.avatar || ''

    notify('资料已保存', 'success')

  } catch (e) {

    handleError(e)

  } finally {

    saving.value = false

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



.avatar-edit {

  display: flex;

  align-items: center;

  gap: 16px;

}



.avatar-edit img {

  width: 64px;

  height: 64px;

  border-radius: 50%;

  object-fit: cover;

}



.hidden-input {

  display: none;

}

</style>

