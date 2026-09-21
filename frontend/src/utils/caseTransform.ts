/**
 * snake_case ↔ camelCase 转换
 * 仅在 API 边界使用（见 docs/CONVENTIONS.md §2.2）
 */

function toCamelKey(key: string): string {
  return key.replace(/_([a-z])/g, (_, c: string) => c.toUpperCase())
}

function toSnakeKey(key: string): string {
  return key.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`)
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return Object.prototype.toString.call(value) === '[object Object]'
}

export function keysToCamel<T>(input: T): T {
  if (Array.isArray(input)) {
    return input.map((item) => keysToCamel(item)) as T
  }
  if (!isPlainObject(input)) {
    return input
  }
  return Object.fromEntries(
    Object.entries(input).map(([key, value]) => [toCamelKey(key), keysToCamel(value)]),
  ) as T
}

export function keysToSnake<T>(input: T): T {
  if (Array.isArray(input)) {
    return input.map((item) => keysToSnake(item)) as T
  }
  if (!isPlainObject(input)) {
    return input
  }
  return Object.fromEntries(
    Object.entries(input).map(([key, value]) => [toSnakeKey(key), keysToSnake(value)]),
  ) as T
}
