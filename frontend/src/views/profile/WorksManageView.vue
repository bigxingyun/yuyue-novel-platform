<template>
  <div class="sub-page page-container">
    <SubPageHeader title="作品管理" />
    <div class="works-toolbar">
      <button class="btn btn-primary btn-sm" @click="showCreate = true">
        <PhPlus :size="16" />
        新建作品
      </button>
    </div>

    <ul v-if="works.length" class="works-list">
      <li v-for="work in works" :key="work.id" class="work-item card">
        <img :src="work.cover" alt="" class="work-cover" />
        <div class="work-body">
          <h3>{{ work.title }}</h3>
          <span class="work-status" :class="work.status">{{ statusLabel(work.status) }}</span>
          <p v-if="work.status === 'unpublished' && work.adminDelisted" class="work-hint">
            已被管理员下架，修改后请联系管理员审核上架
          </p>
          <p>{{ work.wordCount }} 字 · {{ work.chapterCount }} 章</p>
        </div>
        <div class="work-actions">
          <button class="btn btn-ghost btn-sm" @click="openEdit(work)">编辑</button>
          <RouterLink :to="`/profile/works/${work.id}/chapters`" class="btn btn-secondary btn-sm">
            章节管理
          </RouterLink>
          <button
            v-if="work.status === 'published'"
            class="btn btn-ghost btn-sm"
            @click="goPinComment(work)"
          >
            发置顶评
          </button>
          <button
            v-if="work.status === 'draft'"
            class="btn btn-ghost btn-sm"
            @click="togglePublish(work)"
          >
            发布
          </button>
          <button
            v-else-if="work.status === 'published'"
            class="btn btn-ghost btn-sm"
            @click="togglePublish(work)"
          >
            下架
          </button>
          <button
            v-else-if="work.status === 'unpublished' && !work.adminDelisted"
            class="btn btn-ghost btn-sm"
            @click="togglePublish(work)"
          >
            重新上架
          </button>
          <button
            v-if="work.status === 'draft'"
            class="btn btn-ghost btn-sm"
            @click="removeWork(work.id)"
          >
            删除
          </button>
        </div>
      </li>
    </ul>
    <p v-else class="empty-hint">暂无作品，点击上方按钮创建</p>

    <Transition name="modal">
      <div v-if="showCreate" class="create-modal" @click="showCreate = false">
        <form class="create-card card" @click.stop @submit.prevent="submitCreate">
          <h2 class="create-title">新建作品</h2>
          <div class="field">
            <label class="field-label">书名</label>
            <input v-model="createForm.title" class="field-input" placeholder="给你的故事起个名字" />
          </div>
          <div class="field">
            <label class="field-label">简介</label>
            <textarea
              v-model="createForm.description"
              class="field-input"
              rows="3"
              placeholder="一句话介绍你的作品…"
            />
          </div>
          <div class="field">
            <label class="field-label">分类</label>
            <select v-model="createForm.category" class="field-input">
              <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="field cover-field">
            <label class="field-label">封面</label>
            <div class="cover-edit">
              <img :src="createForm.cover || defaultCoverPreview" alt="" class="edit-cover-preview" />
              <input
                ref="createCoverInputRef"
                type="file"
                accept="image/*"
                class="hidden-input"
                @change="onCreateCoverChange"
              />
              <button
                type="button"
                class="btn btn-secondary btn-sm"
                :disabled="uploadingCreateCover"
                @click="createCoverInputRef?.click()"
              >
                {{ uploadingCreateCover ? '上传中…' : '上传封面' }}
              </button>
            </div>
          </div>
          <div class="create-actions">
            <button type="button" class="btn btn-ghost" @click="showCreate = false">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="creating">
              {{ creating ? '创建中…' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </Transition>

    <Transition name="modal">
      <div v-if="editingWork" class="create-modal" @click="editingWork = null">
        <form class="create-card card" @click.stop @submit.prevent="submitEdit">
          <h2 class="create-title">编辑作品</h2>
          <div class="cover-edit">
            <img :src="editForm.cover || defaultCoverPreview" alt="" class="edit-cover-preview" />
            <input ref="coverInputRef" type="file" accept="image/*" class="hidden-input" @change="onCoverChange" />
            <button type="button" class="btn btn-secondary btn-sm" :disabled="uploadingCover" @click="coverInputRef?.click()">
              {{ uploadingCover ? '上传中…' : '更换封面' }}
            </button>
          </div>
          <div class="field">
            <label class="field-label">书名</label>
            <input v-model="editForm.title" class="field-input" />
          </div>
          <div class="field">
            <label class="field-label">简介</label>
            <textarea v-model="editForm.description" class="field-input" rows="3" />
          </div>
          <div class="field">
            <label class="field-label">分类</label>
            <select v-model="editForm.category" class="field-input">
              <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="create-actions">
            <button type="button" class="btn btn-ghost" @click="editingWork = null">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="savingEdit">
              {{ savingEdit ? '保存中…' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { PhPlus } from '@phosphor-icons/vue'
import SubPageHeader from '@/components/common/SubPageHeader.vue'
import { uploadImage } from '@/api/upload'
import {
  createAuthorBook,
  deleteAuthorBook,
  fetchAuthorBooks,
  fetchAuthorChapters,
  publishAuthorBook,
  unpublishAuthorBook,
  updateAuthorBook,
  type AuthorBook,
} from '@/api/author'
import { handleError, notify } from '@/utils/errorHandler'

const router = useRouter()
const categories = ['玄幻', '都市', '科幻', '悬疑', '言情', '历史', '其他']

const works = ref<AuthorBook[]>([])
const showCreate = ref(false)
const creating = ref(false)
const editingWork = ref<AuthorBook | null>(null)
const savingEdit = ref(false)
const uploadingCover = ref(false)
const uploadingCreateCover = ref(false)
const coverInputRef = ref<HTMLInputElement | null>(null)
const createCoverInputRef = ref<HTMLInputElement | null>(null)
const createForm = reactive({ title: '', description: '', category: '其他', cover: '' })
const editForm = reactive({ title: '', description: '', category: '其他', cover: '' })

const defaultCoverPreview = 'https://picsum.photos/seed/yuyue-new-book/400/560'

async function load() {
  try {
    works.value = await fetchAuthorBooks()
  } catch (e) {
    handleError(e)
  }
}

onMounted(load)

function statusLabel(s: string) {
  return { draft: '草稿', published: '已发布', unpublished: '已下架' }[s] ?? s
}

async function goPinComment(work: AuthorBook) {
  try {
    const chapters = await fetchAuthorChapters(work.id)
    if (!chapters.length) {
      notify('请先添加章节')
      return
    }
    router.push(`/read/${work.id}/${chapters[0].id}?focus=chapter-comment`)
  } catch (e) {
    handleError(e)
  }
}

function openEdit(work: AuthorBook) {
  editingWork.value = work
  editForm.title = work.title
  editForm.description = work.description
  editForm.category = work.category
  editForm.cover = work.cover
}

async function onCoverChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadingCover.value = true
  try {
    editForm.cover = await uploadImage(file)
    notify('封面上传成功', 'success')
  } catch (err) {
    handleError(err)
  } finally {
    uploadingCover.value = false
    if (coverInputRef.value) coverInputRef.value.value = ''
  }
}

async function onCreateCoverChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadingCreateCover.value = true
  try {
    createForm.cover = await uploadImage(file)
    notify('封面已上传', 'success')
  } catch (err) {
    handleError(err)
  } finally {
    uploadingCreateCover.value = false
    if (createCoverInputRef.value) createCoverInputRef.value.value = ''
  }
}

async function submitCreate() {
  if (!createForm.title.trim()) {
    notify('请填写书名')
    return
  }
  creating.value = true
  try {
    await createAuthorBook({
      title: createForm.title.trim(),
      description: createForm.description.trim(),
      category: createForm.category,
      cover: createForm.cover || undefined,
    })
    notify('作品已创建，请添加章节后发布', 'success')
    showCreate.value = false
    createForm.title = ''
    createForm.description = ''
    createForm.category = '其他'
    createForm.cover = ''
    await load()
  } catch (e) {
    handleError(e)
  } finally {
    creating.value = false
  }
}

async function submitEdit() {
  if (!editingWork.value || !editForm.title.trim()) {
    notify('请填写书名')
    return
  }
  savingEdit.value = true
  try {
    await updateAuthorBook(editingWork.value.id, {
      title: editForm.title.trim(),
      description: editForm.description.trim(),
      category: editForm.category,
      cover: editForm.cover,
    })
    notify('作品已更新', 'success')
    editingWork.value = null
    await load()
  } catch (e) {
    handleError(e)
  } finally {
    savingEdit.value = false
  }
}

async function togglePublish(work: AuthorBook) {
  try {
    if (work.status === 'published') {
      await unpublishAuthorBook(work.id)
      notify('已下架', 'success')
    } else {
      await publishAuthorBook(work.id)
      notify('已发布', 'success')
    }
    await load()
  } catch (e) {
    handleError(e)
  }
}

async function removeWork(id: number) {
  if (!confirm('确定删除该草稿？')) return
  try {
    await deleteAuthorBook(id)
    notify('已删除', 'success')
    await load()
  } catch (e) {
    handleError(e)
  }
}
</script>

<style scoped>
.works-toolbar {
  margin-bottom: 20px;
}

.works-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.work-item {
  display: flex;
  gap: 14px;
  padding: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.work-cover {
  width: 56px;
  height: 78px;
  object-fit: cover;
  border-radius: 6px;
}

.work-body {
  flex: 1;
  min-width: 140px;
}

.work-body h3 {
  font-size: 16px;
  margin-bottom: 6px;
}

.work-status {
  display: inline-block;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  margin-bottom: 6px;
}

.work-status.draft {
  background: var(--color-border-soft);
  color: var(--color-text-secondary);
}

.work-status.published {
  background: rgba(45, 90, 74, 0.12);
  color: var(--color-success);
}

.work-hint {
  margin: 6px 0 0;
  font-size: 12px;
  color: #b43c3c;
  line-height: 1.45;
}

.work-body p {
  font-size: 13px;
  color: var(--color-text-muted);
}

.work-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.empty-hint {
  text-align: center;
  color: var(--color-text-muted);
  padding: 48px 0;
}

.create-modal {
  position: fixed;
  inset: 0;
  z-index: 500;
  background: rgba(20, 23, 30, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.create-card {
  width: 100%;
  max-width: 480px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.create-title {
  font-family: var(--font-serif);
  font-size: 20px;
}

.create-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
}

.cover-edit {
  display: flex;
  align-items: center;
  gap: 16px;
}

.edit-cover-preview {
  width: 72px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
}

.hidden-input {
  display: none;
}
</style>
