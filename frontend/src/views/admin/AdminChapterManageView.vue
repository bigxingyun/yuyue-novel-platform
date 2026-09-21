<template>
  <div class="admin-page">
    <div class="admin-page-header">
      <div>
        <RouterLink :to="{ name: 'admin-books' }" class="back-link">← 书籍管理</RouterLink>
        <h1 class="admin-title">{{ bookTitle || '章节内容' }}</h1>
        <p class="admin-subtitle">管理员可编辑章节正文与图片</p>
      </div>
    </div>

    <ul v-if="chapters.length" class="chapter-list">
      <li v-for="(ch, index) in chapters" :key="ch.id" class="chapter-item card">
        <div class="chapter-info">
          <span class="chapter-order">{{ index + 1 }}</span>
          <div>
            <h3>{{ ch.title }}</h3>
            <p>{{ ch.wordCount }} 字 · {{ ch.updatedAt }}</p>
          </div>
        </div>
        <button class="btn btn-ghost btn-sm" @click="openEditor(ch)">编辑内容</button>
      </li>
    </ul>
    <p v-else class="state-hint card">暂无章节</p>

    <Transition name="modal">
      <div v-if="editorOpen" class="editor-modal" @click="closeEditor">
        <div class="editor-card card" @click.stop>
          <h2 class="editor-title">编辑章节 · {{ form.title }}</h2>
          <div class="field">
            <label class="field-label">章节标题</label>
            <input v-model="form.title" class="field-input" />
          </div>

          <div class="editor-split">
            <div class="editor-source">
              <label class="field-label">原始正文</label>
              <textarea
                v-model="form.content"
                class="field-input editor-textarea"
                rows="12"
                placeholder="段落之间用空行分隔；图片使用 [img:/uploads/...] 格式"
              />
            </div>
            <div class="editor-blocks">
              <label class="field-label">块编辑预览</label>
              <div class="block-editor-panel card">
                <AuthorChapterContentEditor
                  :blocks="previewBlocks"
                  @insert-image="onInsertImageAt"
                  @remove-image="onRemoveImage"
                  @replace-image="onReplaceImage"
                />
              </div>
            </div>
          </div>

          <div class="editor-actions">
            <button class="btn btn-ghost" @click="closeEditor">取消</button>
            <button class="btn btn-primary" :disabled="saving || uploading" @click="saveChapter">
              {{ saving ? '保存中…' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import AuthorChapterContentEditor from '@/components/reader/AuthorChapterContentEditor.vue'
import {
  fetchAdminChapter,
  fetchAdminChapters,
  updateAdminChapter,
  type AdminChapter,
} from '@/api/admin'
import { uploadImageForContent } from '@/api/upload'
import { insertImageAfterParagraph, removeImageAt } from '@/utils/parseChapterBlocks'
import { resolveChapterBlocks } from '@/utils/resolveChapterBlocks'
import { handleError, notify } from '@/utils/errorHandler'

const route = useRoute()
const bookId = computed(() => Number(route.params.bookId))

const bookTitle = ref('')
const chapters = ref<AdminChapter[]>([])
const editorOpen = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const uploading = ref(false)
const form = reactive({ title: '', content: '' })

const previewBlocks = computed(() => resolveChapterBlocks({ content: form.content }))

function resolveInsertIndex(paragraphIndex: number) {
  if (paragraphIndex >= 0) return paragraphIndex
  const textCount = previewBlocks.value.filter((b) => b.type === 'text').length
  return Math.max(0, textCount - 1)
}

async function pickAndUpload(): Promise<string | null> {
  return new Promise((resolve) => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/jpeg,image/png,image/webp,image/gif'
    input.onchange = async () => {
      const file = input.files?.[0]
      if (!file) {
        resolve(null)
        return
      }
      uploading.value = true
      try {
        resolve(await uploadImageForContent(file))
      } catch (e) {
        handleError(e)
        resolve(null)
      } finally {
        uploading.value = false
      }
    }
    input.click()
  })
}

async function onInsertImageAt(paragraphIndex: number) {
  const url = await pickAndUpload()
  if (!url) return
  const idx = resolveInsertIndex(paragraphIndex)
  form.content = insertImageAfterParagraph(form.content, idx, url)
  notify('图片已插入', 'success')
}

function onRemoveImage(afterParagraphIndex: number, url: string) {
  form.content = removeImageAt(form.content, afterParagraphIndex, url)
  notify('图片已删除', 'success')
}

async function onReplaceImage(afterParagraphIndex: number, oldUrl: string) {
  const url = await pickAndUpload()
  if (!url) return
  let content = removeImageAt(form.content, afterParagraphIndex, oldUrl)
  content = insertImageAfterParagraph(content, afterParagraphIndex, url)
  form.content = content
  notify('图片已替换', 'success')
}

async function load() {
  try {
    const list = await fetchAdminChapters(bookId.value)
    chapters.value = list
    if (list.length) {
      const detail = await fetchAdminChapter(list[0].id)
      bookTitle.value = detail.bookTitle
    }
  } catch (e) {
    handleError(e)
  }
}

onMounted(load)

async function openEditor(ch: AdminChapter) {
  editingId.value = ch.id
  try {
    const detail = await fetchAdminChapter(ch.id)
    form.title = detail.title
    form.content = detail.content
    bookTitle.value = detail.bookTitle
    editorOpen.value = true
  } catch (e) {
    handleError(e)
  }
}

function closeEditor() {
  editorOpen.value = false
}

async function saveChapter() {
  if (!editingId.value || !form.title.trim()) return
  saving.value = true
  try {
    await updateAdminChapter(editingId.value, {
      title: form.title.trim(),
      content: form.content,
    })
    notify('章节已保存', 'success')
    closeEditor()
    await load()
  } catch (e) {
    handleError(e)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.back-link {
  display: inline-block;
  margin-bottom: 8px;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.back-link:hover {
  color: var(--color-accent);
}

.admin-subtitle {
  margin: 4px 0 0;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.chapter-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.chapter-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4);
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.chapter-order {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  background: var(--color-accent-soft);
  color: var(--color-accent);
  font-size: var(--text-sm);
  font-weight: 600;
}

.chapter-info h3 {
  font-size: var(--text-base);
  margin-bottom: 2px;
}

.chapter-info p {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.state-hint {
  padding: 48px 24px;
  text-align: center;
  color: var(--color-text-muted);
}

.editor-modal {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(0, 0, 0, 0.45);
}

.editor-card {
  width: min(960px, 100%);
  max-height: 90vh;
  overflow-y: auto;
  padding: var(--space-6);
}

.editor-title {
  font-family: var(--font-serif);
  margin-bottom: var(--space-4);
}

.editor-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

@media (max-width: 767px) {
  .editor-split {
    grid-template-columns: 1fr;
  }
}

.editor-textarea {
  min-height: 280px;
  font-family: var(--font-serif);
  line-height: 1.7;
}

.block-editor-panel {
  min-height: 280px;
  max-height: 360px;
  overflow-y: auto;
  padding: var(--space-4);
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-4);
}
</style>
