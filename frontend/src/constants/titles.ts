/** 与 backend/app/core/constants.py TITLE_LEVELS 保持一致 */

export interface TitleTier {
  level: number
  title: string
  minExp: number
}

export const TITLE_LEVELS: TitleTier[] = [
  { level: 1, title: '门外读者', minExp: 0 },
  { level: 2, title: '初窥门径', minExp: 30 },
  { level: 3, title: '书香初染', minExp: 80 },
  { level: 4, title: '闲章散笔', minExp: 150 },
  { level: 5, title: '夜读者', minExp: 250 },
  { level: 6, title: '书斋常客', minExp: 400 },
  { level: 7, title: '字里行间', minExp: 600 },
  { level: 8, title: '万卷书生', minExp: 900 },
  { level: 9, title: '阅尽千帆', minExp: 1300 },
  { level: 10, title: '欲阅宗师', minExp: 1800 },
]

export function defaultAvatarUrl(seed: number | string): string {
  return `https://api.dicebear.com/7.x/notionists/svg?seed=${seed}`
}

export function getTitleInfo(exp: number) {
  const safeExp = Math.max(0, exp)
  let current = TITLE_LEVELS[0]
  for (const tier of TITLE_LEVELS) {
    if (safeExp >= tier.minExp) current = tier
    else break
  }
  const next = TITLE_LEVELS.find((t) => t.level === current.level + 1)
  const expInLevel = safeExp - current.minExp
  const expToNext = next ? next.minExp - safeExp : 0
  const progress = next
    ? expInLevel / (next.minExp - current.minExp)
    : 1
  return {
    level: current.level,
    title: current.title,
    exp: safeExp,
    expInLevel,
    expToNext,
    progress: Math.min(1, Math.max(0, progress)),
  }
}
