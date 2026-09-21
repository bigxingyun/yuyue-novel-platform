/** 阅读页设置 — localStorage 持久化 + 云端同步 */



export type ReaderTheme = 'paper' | 'green' | 'night'

export type PageMode = 'scroll' | 'slide'

export type FontFamily = 'serif' | 'sans' | 'kai' | 'song'

export type PageMargin = 'narrow' | 'medium' | 'wide'

export type LetterSpacing = 'tight' | 'normal' | 'wide'

export type TextColorPreset = 'default' | 'dark' | 'brown' | 'gray' | 'custom'



export interface ReaderSettings {

  fontSize: number

  lineHeight: number

  theme: ReaderTheme

  pageMode: PageMode

  fontFamily: FontFamily

  margin: PageMargin

  letterSpacing: LetterSpacing

  textColor: TextColorPreset

  customTextColor: string

  useCustomBg: boolean

  customBgColor: string

}



const STORAGE_KEY = 'yuyue_reader_settings'



export const DEFAULT_READER_SETTINGS: ReaderSettings = {

  fontSize: 18,

  lineHeight: 2,

  theme: 'paper',

  pageMode: 'scroll',

  fontFamily: 'serif',

  margin: 'medium',

  letterSpacing: 'normal',

  textColor: 'default',

  customTextColor: '#2a2a28',

  useCustomBg: false,

  customBgColor: '#f7f6f2',

}



const FONT_STACKS: Record<FontFamily, string> = {

  serif: 'var(--font-serif)',

  sans: 'var(--font-sans)',

  kai: '"KaiTi", "STKaiti", "楷体", serif',

  song: '"SimSun", "Songti SC", "宋体", serif',

}



const MARGIN_VALUES: Record<PageMargin, string> = {

  narrow: '12px',

  medium: '20px',

  wide: '32px',

}



const LETTER_SPACING_VALUES: Record<LetterSpacing, string> = {

  tight: '-0.02em',

  normal: '0.04em',

  wide: '0.12em',

}



const TEXT_COLOR_VALUES: Record<Exclude<TextColorPreset, 'default' | 'custom'>, string> = {

  dark: '#1a1a1a',

  brown: '#4a3f35',

  gray: '#5a5a5a',

}



export function normalizeReaderSettings(raw: Partial<ReaderSettings> | null | undefined): ReaderSettings {

  if (!raw) return { ...DEFAULT_READER_SETTINGS }

  return {

    fontSize: clamp(raw.fontSize ?? DEFAULT_READER_SETTINGS.fontSize, 14, 24),

    lineHeight: clamp(raw.lineHeight ?? DEFAULT_READER_SETTINGS.lineHeight, 1.6, 2.4),

    theme: isTheme(raw.theme) ? raw.theme : DEFAULT_READER_SETTINGS.theme,

    pageMode: normalizePageMode(raw.pageMode),

    fontFamily: isFontFamily(raw.fontFamily) ? raw.fontFamily : DEFAULT_READER_SETTINGS.fontFamily,

    margin: isMargin(raw.margin) ? raw.margin : DEFAULT_READER_SETTINGS.margin,

    letterSpacing: isLetterSpacing(raw.letterSpacing)

      ? raw.letterSpacing

      : DEFAULT_READER_SETTINGS.letterSpacing,

    textColor: isTextColor(raw.textColor) ? raw.textColor : DEFAULT_READER_SETTINGS.textColor,

    customTextColor: raw.customTextColor ?? DEFAULT_READER_SETTINGS.customTextColor,

    useCustomBg: !!raw.useCustomBg,

    customBgColor: raw.customBgColor ?? DEFAULT_READER_SETTINGS.customBgColor,

  }

}



export function loadReaderSettings(): ReaderSettings {

  try {

    const raw = localStorage.getItem(STORAGE_KEY)

    if (!raw) return { ...DEFAULT_READER_SETTINGS }

    return normalizeReaderSettings(JSON.parse(raw) as Partial<ReaderSettings>)

  } catch {

    return { ...DEFAULT_READER_SETTINGS }

  }

}



export function saveReaderSettings(settings: ReaderSettings) {

  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))

}



export function readerFontFamily(family: FontFamily): string {

  return FONT_STACKS[family]

}



export function readerHorizontalPadding(margin: PageMargin): string {

  return MARGIN_VALUES[margin]

}



export function readerLetterSpacing(spacing: LetterSpacing): string {

  return LETTER_SPACING_VALUES[spacing]

}



export function readerTextColor(settings: ReaderSettings): string | null {

  if (settings.textColor === 'default') return null

  if (settings.textColor === 'custom') return settings.customTextColor

  return TEXT_COLOR_VALUES[settings.textColor]

}



export function readerBackground(settings: ReaderSettings): string | null {

  if (!settings.useCustomBg) return null

  return settings.customBgColor

}



function clamp(n: number, min: number, max: number) {

  return Math.min(max, Math.max(min, n))

}



function isTheme(v: unknown): v is ReaderTheme {

  return v === 'paper' || v === 'green' || v === 'night'

}



function normalizePageMode(v: unknown): PageMode {
  if (v === 'slide' || v === 'flip') return 'slide'
  if (v === 'scroll') return 'scroll'
  return DEFAULT_READER_SETTINGS.pageMode
}



function isFontFamily(v: unknown): v is FontFamily {

  return v === 'serif' || v === 'sans' || v === 'kai' || v === 'song'

}



function isMargin(v: unknown): v is PageMargin {

  return v === 'narrow' || v === 'medium' || v === 'wide'

}



function isLetterSpacing(v: unknown): v is LetterSpacing {

  return v === 'tight' || v === 'normal' || v === 'wide'

}



function isTextColor(v: unknown): v is TextColorPreset {

  return v === 'default' || v === 'dark' || v === 'brown' || v === 'gray' || v === 'custom'

}

