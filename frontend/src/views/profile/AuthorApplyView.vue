<template>

  <div class="sub-page page-container">

    <SubPageHeader title="申请成为作者" />



    <div v-if="loading" class="hint">加载中…</div>



    <div v-else-if="application" class="status-card card">

      <div class="status-head">

        <span class="status-tag" :class="application.status">

          {{ statusLabel(application.status) }}

        </span>

      </div>

      <p class="status-reason">{{ application.reason }}</p>

      <p v-if="application.reviewNote" class="status-note">审核备注：{{ application.reviewNote }}</p>

      <p v-if="application.status === 'pending'" class="hint">申请已提交，请耐心等待管理员审核</p>

      <p v-else-if="application.status === 'rejected'" class="hint">申请未通过，可修改说明后重新提交</p>

    </div>



    <form

      v-if="!application || application.status === 'rejected'"

      class="form card"

      @submit.prevent="onSubmit"

    >

      <p class="hint">成为作者后可发布和管理自己的作品。申请需管理员审核。</p>

      <div class="field">

        <label class="field-label">申请说明</label>

        <textarea

          v-model="reason"

          class="field-input"

          rows="5"

          placeholder="简要介绍你的创作计划或已有作品…"

        />

      </div>

      <button type="submit" class="btn btn-primary btn-block" :disabled="submitting">

        {{ submitting ? '提交中…' : application?.status === 'rejected' ? '重新提交' : '提交申请' }}

      </button>

    </form>

  </div>

</template>



<script setup lang="ts">

import { onMounted, ref } from 'vue'

import { useRouter } from 'vue-router'

import SubPageHeader from '@/components/common/SubPageHeader.vue'

import {

  fetchAuthorApplication,

  submitAuthorApplication,

  type AuthorApplicationStatus,

} from '@/api/profile'

import { handleError, notify } from '@/utils/errorHandler'



const router = useRouter()

const reason = ref('')

const application = ref<AuthorApplicationStatus | null>(null)

const loading = ref(true)

const submitting = ref(false)



function statusLabel(s: string) {

  return { pending: '待审核', approved: '已通过', rejected: '已拒绝' }[s] ?? s

}



onMounted(async () => {

  try {

    application.value = await fetchAuthorApplication()

    if (application.value?.reason) reason.value = application.value.reason

  } catch (e) {

    handleError(e)

  } finally {

    loading.value = false

  }

})



async function onSubmit() {

  if (reason.value.trim().length < 10) {

    notify('申请说明至少 10 字')

    return

  }

  submitting.value = true

  try {

    await submitAuthorApplication(reason.value.trim())

    notify('申请已提交，请等待审核', 'success')

    application.value = { status: 'pending', reason: reason.value.trim() }

    router.back()

  } catch (e) {

    handleError(e)

  } finally {

    submitting.value = false

  }

}

</script>



<style scoped>

.form,

.status-card {

  padding: 24px;

  max-width: 560px;

  display: flex;

  flex-direction: column;

  gap: 20px;

  margin-bottom: 16px;

}



.hint {

  font-size: 14px;

  color: var(--color-text-secondary);

  line-height: 1.6;

}



.status-head {

  margin-bottom: 4px;

}



.status-tag {

  display: inline-block;

  padding: 4px 12px;

  border-radius: var(--radius-full);

  font-size: 13px;

}



.status-tag.pending {

  background: var(--color-accent-soft);

  color: var(--color-accent);

}



.status-tag.approved {

  background: rgba(45, 90, 74, 0.12);

  color: var(--color-success);

}



.status-tag.rejected {

  background: rgba(180, 60, 60, 0.1);

  color: #b43c3c;

}



.status-reason {

  font-size: 14px;

  line-height: 1.6;

  color: var(--color-text-secondary);

}



.status-note {

  font-size: 13px;

  color: var(--color-text-muted);

}

</style>


