import { updateReadingProgress } from '@/api/reading'

const QUEUE_KEY = 'yuyue_progress_queue'

interface QueuedProgress {
  bookId: number
  chapterId: number
  offset: number
  at: number
}

function loadQueue(): QueuedProgress[] {
  try {
    const raw = localStorage.getItem(QUEUE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as QueuedProgress[]
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function saveQueue(queue: QueuedProgress[]) {
  localStorage.setItem(QUEUE_KEY, JSON.stringify(queue))
}

export function enqueueProgress(item: { bookId: number; chapterId: number; offset: number }) {
  const queue = loadQueue().filter(
    (q) => !(q.bookId === item.bookId && q.chapterId === item.chapterId),
  )
  queue.push({ ...item, at: Date.now() })
  saveQueue(queue)
}

export async function flushProgressQueue() {
  const queue = loadQueue()
  if (!queue.length) return

  const remaining: QueuedProgress[] = []
  for (const item of queue) {
    try {
      await updateReadingProgress({
        bookId: item.bookId,
        chapterId: item.chapterId,
        offset: item.offset,
      })
    } catch {
      remaining.push(item)
    }
  }
  saveQueue(remaining)
}

export function setupProgressQueueSync() {
  if (typeof window === 'undefined') return
  window.addEventListener('online', () => {
    flushProgressQueue()
  })
}
