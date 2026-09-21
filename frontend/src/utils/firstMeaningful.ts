/** 返回第一个非空白字符串；均缺失时返回 ''。 */
export function firstMeaningfulContent(...candidates: (string | undefined | null)[]): string {
  for (const c of candidates) {
    if (c !== undefined && c !== null && c.trim() !== '') return c
  }
  return ''
}
