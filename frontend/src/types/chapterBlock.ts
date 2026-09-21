export interface TextBlock {
  type: 'text'
  text: string
  paragraphIndex: number
}

export interface ImageBlock {
  type: 'image'
  url: string
  afterParagraphIndex: number
}

export type ChapterBlock = TextBlock | ImageBlock
