/** 上传资源 URL：正文存储用相对路径，展示用可访问地址。 */

const UPLOADS_PREFIX = '/uploads/'

export function normalizeStorageUrl(url: string): string {
  const trimmed = url.trim()
  if (!trimmed) return trimmed

  const markerMatch = trimmed.match(/^\[img:(.+)\]$/)
  const inner = markerMatch ? markerMatch[1] : trimmed

  if (inner.startsWith(UPLOADS_PREFIX)) return inner

  try {
    const parsed = new URL(inner, typeof window !== 'undefined' ? window.location.origin : 'http://local')
    const path = parsed.pathname
    if (path.startsWith(UPLOADS_PREFIX)) return path
  } catch {
    /* 非 URL 字符串 */
  }

  const uploadsIdx = inner.indexOf(UPLOADS_PREFIX)
  if (uploadsIdx >= 0) return inner.slice(uploadsIdx)

  return inner
}

export function resolveMediaUrl(url: string): string {
  const normalized = normalizeStorageUrl(url)
  if (!normalized) return ''
  if (normalized.startsWith('http://') || normalized.startsWith('https://')) return normalized
  if (typeof window !== 'undefined') {
    return `${window.location.origin}${normalized.startsWith('/') ? normalized : `/${normalized}`}`
  }
  return normalized
}

export function toImageMarker(url: string): string {
  return `[img:${normalizeStorageUrl(url)}]`
}
