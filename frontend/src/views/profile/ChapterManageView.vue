<template>
  <div class="sub-page page-container">
    <SubPageHeader :title="bookTitle || '章节管理'" />

    <div class="chapter-toolbar">
      <button class="btn btn-primary btn-sm" @click="openEditor()">
        <PhPlus :size="16" />
        新增章节
      </button>
    </div>

    <ul v-if="chapters.length" class="chapter-list">
      <li
        v-for="(ch, index) in chapters"
        :key="ch.id"
        class="chapter-item card"
        :class="{ dragging: dragIndex === index, 'drop-target': dropIndex === index }"
        @dragover="onDragOver(index, $event)"
        @dragleave="dropIndex = null"
        @drop="onDrop(index)"
      >
        <div class="chapter-info">
          <span
            class="drag-handle"
            title="拖拽排序"
            draggable="true"
            @dragstart="onDragStart(index, $event)"
            @dragend="onDragEnd"
          >⋮⋮</span>
          <span class="chapter-order">{{ index + 1 }}</span>
          <div>
            <h3>{{ ch.title }}</h3>
            <p>{{ ch.wordCount }} 字 · 更新于 {{ ch.updatedAt }}</p>
          </div>
        </div>
        <div class="chapter-actions">
          <button class="btn btn-ghost btn-sm" :disabled="index === 0" @click="moveUp(index)">
            上移
          </button>
          <button
            class="btn btn-ghost btn-sm"
            :disabled="index === chapters.length - 1"
            @click="moveDown(index)"
          >
            下移
          </button>
          <button class="btn btn-ghost btn-sm" @click="openEditor(ch)">编辑</button>
          <button class="btn btn-ghost btn-sm" @click="removeChapter(ch.id)">删除</button>
        </div>
      </li>
    </ul>
    <p v-else class="empty-hint">暂无章节，请先新增</p>

    <Transition name="modal">
      <div v-if="editorOpen" class="editor-modal" @click="closeEditor">
        <div class="editor-card card" @click.stop>
          <h2 class="editor-title">{{ editingId ? '编辑章节' : '新增章节' }}</h2>
          <div class="field">
            <label class="field-label">章节标题</label>
            <input v-model="form.title" class="field-input" placeholder="第一章 …" />
          </div>

          <div class="editor-split">
            <div class="editor-source">
              <label class="field-label">原始正文</label>
              <textarea
                v-model="form.content"
                class="field-input editor-textarea"
                rows="14"
                placeholder="段落之间用空行分隔…"
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

          <p class="editor-hint">共约 {{ wordEstimate }} 字 · 图片格式：[img:/uploads/...]</p>

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
import { PhPlus } from '@phosphor-icons/vue'
import SubPageHeader from '@/components/common/SubPageHeader.vue'
import AuthorChapterContentEditor from '@/components/reader/AuthorChapterContentEditor.vue'
import { uploadImageForContent } from '@/api/upload'
import { insertImageAfterParagraph, removeImageAt } from '@/utils/parseChapterBlocks'
import { resolveChapterBlocks } from '@/utils/resolveChapterBlocks'
import {
  createAuthorChapter,
  deleteAuthorChapter,
  fetchAuthorBooks,
  fetchAuthorChapterContent,
  fetchAuthorChapters,
  reorderAuthorChapters,
  updateAuthorChapter,
  type AuthorChapter,
} from '@/api/author'
import { handleError, notify } from '@/utils/errorHandler'

const route = useRoute()
const bookId = computed(() => Number(route.params.bookId))

const bookTitle = ref('')
const chapters = ref<AuthorChapter[]>([])
const editorOpen = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const uploading = ref(false)

const form = reactive({ title: '', content: '' })
const dragIndex = ref<number | null>(null)
const dropIndex = ref<number | null>(null)
let editorLoadToken = 0

const wordEstimate = computed(() => form.content.replace(/\n/g, '').replace(/ /g, '').length)
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
    const [books, list] = await Promise.all([
      fetchAuthorBooks(),
      fetchAuthorChapters(bookId.value),
    ])
    bookTitle.value = books.find((b) => b.id === bookId.value)?.title ?? ''
    chapters.value = list
  } catch (e) {
    handleError(e)
  }
}

onMounted(load)

async function openEditor(ch?: AuthorChapter) {
  const token = ++editorLoadToken
  if (ch) {
    editingId.value = ch.id
    form.title = ch.title
    form.content = ''
    try {
      const detail = await fetchAuthorChapterContent(ch.id)
      if (token !== editorLoadToken) return
      form.content = detail.content
    } catch (e) {
      if (token !== editorLoadToken) return
      handleError(e)
      return
    }
  } else {
    editingId.value = null
    form.title = ''
    form.content = ''
  }
  editorOpen.value = true
}

function closeEditor() {
  editorLoadToken += 1
  editorOpen.value = false
}

async function saveChapter() {
  if (!form.title.trim()) {
    notify('请填写章节标题')
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      await updateAuthorChapter(editingId.value, {
        title: form.title.trim(),
        content: form.content,
      })
      notify('章节已更新', 'success')
    } else {
      await createAuthorChapter(bookId.value, {
        title: form.title.trim(),
        content: form.content,
      })
      notify('章节已创建', 'success')
    }
    editorOpen.value = false
    await load()
  } catch (e) {
    handleError(e)
  } finally {
    saving.value = false
  }
}

async function removeChapter(id: number) {
  if (!confirm('确定删除该章节？')) return
  try {
    await deleteAuthorChapter(id)
    notify('已删除', 'success')
    await load()
  } catch (e) {
    handleError(e)
  }
}

async function moveUp(index: number) {
  if (index <= 0) return
  const ids = chapters.value.map((c) => c.id)
  ;[ids[index - 1], ids[index]] = [ids[index], ids[index - 1]]
  await applyReorder(ids)
}

function onDragStart(index: number, e: DragEvent) {
  dragIndex.value = index
  e.dataTransfer?.setData('text/plain', String(index))
  if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move'
}

function onDragOver(index: number, e: DragEvent) {
  e.preventDefault()
  dropIndex.value = index
  if (e.dataTransfer) e.dataTransfer.dropEffect = 'move'
}

function onDragEnd() {
  dragIndex.value = null
  dropIndex.value = null
}

async function onDrop(targetIndex: number) {
  const from = dragIndex.value
  onDragEnd()
  if (from === null || from === targetIndex) return
  const ids = chapters.value.map((c) => c.id)
  const [moved] = ids.splice(from, 1)
  ids.splice(targetIndex, 0, moved)
  await applyReorder(ids)
}

async function moveDown(index: number) {
  if (index >= chapters.value.length - 1) return
  const ids = chapters.value.map((c) => c.id)
  ;[ids[index], ids[index + 1]] = [ids[index + 1], ids[index]]
  await applyReorder(ids)
}

async function applyReorder(ids: number[]) {
  try {
    chapters.value = await reorderAuthorChapters(bookId.value, ids)
    notify('排序已更新', 'success')
  } catch (e) {
    handleError(e)
    await load()
  }
}
</script>

<style scoped>
.chapter-toolbar {
  margin-bottom: 20px;
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chapter-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.chapter-info {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  flex: 1;
  min-width: 200px;
}

.drag-handle {
  cursor: grab;
  color: var(--color-text-muted);
  font-size: 14px;
  line-height: 1;
  padding: 4px 2px;
  user-select: none;
}

.chapter-item.dragging {
  opacity: 0.5;
}

.chapter-item.drop-target {
  outline: 2px dashed var(--color-accent);
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
  font-size: 13px;
  font-weight: 500;
  flex-shrink: 0;
}

.chapter-info h3 {
  font-size: 15px;
  margin-bottom: 4px;
}

.chapter-info p {
  font-size: 12px;
  color: var(--color-text-muted);
}

.chapter-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.empty-hint {
  text-align: center;
  color: var(--color-text-muted);
  padding: 48px 0;
}

.editor-modal {
  position: fixed;
  inset: 0;
  z-index: 500;
  background: rgba(20, 23, 30, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.editor-card {
  width: 100%;
  max-width: 960px;
  max-height: 90dvh;
  overflow-y: auto;
  padding: 24px;
}

.editor-title {
  font-family: var(--font-serif);
  font-size: 20px;
  margin-bottom: 20px;
}

.editor-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 8px;
}

@media (max-width: 767px) {
  .editor-split {
    grid-template-columns: 1fr;
  }
}

.editor-textarea {
  resize: vertical;
  min-height: 280px;
  font-family: var(--font-serif);
  line-height: 1.8;
}

.block-editor-panel {
  min-height: 280px;
  max-height: 360px;
  overflow-y: auto;
  padding: 16px;
}

.editor-hint {
  font-size: 12px;
  color: var(--color-text-muted);
  margin: 8px 0 16px;
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
