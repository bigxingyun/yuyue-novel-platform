import type { ChapterBlock } from '@/types/chapterBlock'
import { normalizeStorageUrl, toImageMarker } from '@/utils/mediaUrl'

const IMG_MARKER = /^\[img:(.+)\]$/

export function parseChapterBlocks(content: string): ChapterBlock[] {
  const blocks: ChapterBlock[] = []
  let paragraphIndex = -1

  for (const raw of content.split('\n\n')) {
    const block = raw.trim()
    if (!block) continue

    const match = block.match(IMG_MARKER)
    if (match) {
      blocks.push({
        type: 'image',
        url: normalizeStorageUrl(match[1]),
        afterParagraphIndex: paragraphIndex,
      })
    } else {
      paragraphIndex += 1
      blocks.push({
        type: 'text',
        text: block,
        paragraphIndex,
      })
    }
  }

  return blocks
}

export function splitParagraphs(content: string): string[] {
  return parseChapterBlocks(content)
    .filter((b): b is Extract<ChapterBlock, { type: 'text' }> => b.type === 'text')
    .map((b) => b.text)
}

export function insertImageAfterParagraph(
  content: string,
  paragraphIndex: number,
  url: string,
): string {
  const marker = toImageMarker(url)
  const blocks = parseChapterBlocks(content)
  const result: string[] = []
  let inserted = false

  for (const block of blocks) {
    if (block.type === 'text') {
      result.push(block.text)
      if (block.paragraphIndex === paragraphIndex) {
        result.push(marker)
        inserted = true
      }
    } else {
      result.push(toImageMarker(block.url))
    }
  }

  if (!inserted) {
    result.push(marker)
  }

  return result.join('\n\n')
}

export function removeImageAt(content: string, afterParagraphIndex: number, url: string): string {
  const blocks = parseChapterBlocks(content)
  let removed = false
  const result: string[] = []

  for (const block of blocks) {
    if (
      !removed &&
      block.type === 'image' &&
      block.afterParagraphIndex === afterParagraphIndex &&
      block.url === url
    ) {
      removed = true
      continue
    }
    result.push(block.type === 'text' ? block.text : `[img:${block.url}]`)
  }

  return result.join('\n\n')
}
