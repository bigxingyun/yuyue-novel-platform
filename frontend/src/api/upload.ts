import http from '@/api/http'
import { normalizeStorageUrl, resolveMediaUrl } from '@/utils/mediaUrl'

async function uploadImageRaw(file: File): Promise<string> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await http.post<{ code: number; data: { url: string } }>('/upload/image', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  if (data.code !== 0 || !data.data?.url) {
    throw new Error('上传失败')
  }
  return normalizeStorageUrl(data.data.url as string)
}

/** 头像、封面等 UI 展示用（完整 URL） */
export async function uploadImage(file: File): Promise<string> {
  return resolveMediaUrl(await uploadImageRaw(file))
}

/** 章节正文 marker 用（仅存 /uploads/...） */
export async function uploadImageForContent(file: File): Promise<string> {
  return uploadImageRaw(file)
}
