import type { ChapterBlock } from '@/types/chapterBlock'
import { parseChapterBlocks } from '@/utils/parseChapterBlocks'

/** 以 content 为存储真相解析 blocks；content 为空时 fallback 到 API blocks。 */
export function resolveChapterBlocks(input: {
  content?: string
  blocks?: ChapterBlock[]
}): ChapterBlock[] {
  const trimmed = input.content?.trim()
  if (trimmed) return parseChapterBlocks(trimmed)
  return input.blocks ?? []
}
