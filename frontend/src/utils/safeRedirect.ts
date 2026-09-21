/** 登录后安全跳转：仅允许站内相对路径 */
export function safeRedirectPath(raw: string | undefined | null, fallback = '/square'): string {
  if (!raw || typeof raw !== 'string') return fallback
  const path = raw.trim()
  if (!path.startsWith('/') || path.startsWith('//')) return fallback
  if (/^https?:/i.test(path)) return fallback
  return path
}
