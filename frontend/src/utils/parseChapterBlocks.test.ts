import { describe, expect, it } from 'vitest'
import { insertImageAfterParagraph, parseChapterBlocks } from '@/utils/parseChapterBlocks'
import { resolveChapterBlocks } from '@/utils/resolveChapterBlocks'

describe('parseChapterBlocks', () => {
  it('parses text and image in order', () => {
    const content = 'A\n\nB\n\n[img:/uploads/x.png]\n\nC'
    const blocks = parseChapterBlocks(content)
    expect(blocks).toHaveLength(4)
    expect(blocks[2]).toMatchObject({ type: 'image', url: '/uploads/x.png', afterParagraphIndex: 1 })
  })

  it('inserts image after paragraph index', () => {
    const content = 'A\n\nB'
    const next = insertImageAfterParagraph(content, 0, '/uploads/new.png')
    const blocks = parseChapterBlocks(next)
    expect(blocks[1]).toMatchObject({ type: 'image', afterParagraphIndex: 0 })
  })
})

describe('resolveChapterBlocks', () => {
  it('prefers content over stale blocks', () => {
    const blocks = resolveChapterBlocks({
      content: 'Only\n\n[img:/uploads/a.png]',
      blocks: [{ type: 'text', text: 'Stale', paragraphIndex: 0 }],
    })
    expect(blocks).toHaveLength(2)
    expect(blocks[1].type).toBe('image')
  })

  it('falls back to API blocks when content is whitespace only', () => {
    const blocks = resolveChapterBlocks({
      content: '   \n\n  ',
      blocks: [{ type: 'text', text: 'From API', paragraphIndex: 0 }],
    })
    expect(blocks).toHaveLength(1)
    expect(blocks[0]).toMatchObject({ type: 'text', text: 'From API' })
  })
})
