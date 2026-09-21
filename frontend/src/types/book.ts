import type { ChapterBlock } from '@/types/chapterBlock'

export interface ChapterBrief {
  id: number
  title: string
  wordCount: number
}

export interface BookListItem {
  id: number
  title: string
  author: string
  category: string
  cover: string
  wordCount: number
  updatedAt: string
}

export interface ReadingProgress {
  chapterId: number
  offset: number
}

export interface BookDetail {
  id: number
  title: string
  author: string
  authorId: number
  category: string
  description: string
  cover: string
  wordCount: number
  updatedAt: string
  chapters: ChapterBrief[]
  progress?: ReadingProgress | null
  inShelf: boolean
}

export interface ChapterDetail {
  id: number
  bookId: number
  title: string
  content: string
  paragraphs: string[]
  blocks: ChapterBlock[]
  wordCount: number
}

export interface BookComment {
  id: number
  user: string
  avatar: string
  time: string
  content: string
}

export interface UpdateLog {
  chapterId: number
  date: string
  chapterTitle: string
  addedWords: number
}
