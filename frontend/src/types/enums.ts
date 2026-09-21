/**
 * 项目级枚举 — 命名与取值的唯一来源（前端）
 * 必须与 backend/app/core/constants.py 保持一致
 */

export const UserRole = {
  GUEST: 'guest',
  USER: 'user',
  AUTHOR: 'author',
  ADMIN: 'admin',
  SUPERADMIN: 'superadmin',
} as const
export type UserRole = (typeof UserRole)[keyof typeof UserRole]

export const UserStatus = {
  ACTIVE: 'active',
  BANNED: 'banned',
} as const
export type UserStatus = (typeof UserStatus)[keyof typeof UserStatus]

export const BookStatus = {
  DRAFT: 'draft',
  PUBLISHED: 'published',
  UNPUBLISHED: 'unpublished',
} as const
export type BookStatus = (typeof BookStatus)[keyof typeof BookStatus]

export const KeyStatus = {
  UNUSED: 'unused',
  USED: 'used',
  EXPIRED: 'expired',
} as const
export type KeyStatus = (typeof KeyStatus)[keyof typeof KeyStatus]

export const ApplicationStatus = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected',
} as const
export type ApplicationStatus = (typeof ApplicationStatus)[keyof typeof ApplicationStatus]

export const DeviceType = {
  DESKTOP: 'desktop',
  ANDROID: 'android',
  IOS: 'ios',
} as const
export type DeviceType = (typeof DeviceType)[keyof typeof DeviceType]

/** 与 docs/CONVENTIONS.md §3.5 一致 */
export const ErrorCode = {
  OK: 0,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  INTERNAL_ERROR: 500,
  REGISTRATION_KEY_INVALID: 40001,
  NICKNAME_TAKEN: 40002,
  TOKEN_EXPIRED: 40101,
  ACCOUNT_BANNED: 40301,
  AUTHOR_REQUIRED: 40302,
  ADMIN_REQUIRED: 40303,
  BOOK_NOT_FOUND: 40401,
  CHAPTER_NOT_FOUND: 40402,
  ALREADY_CHECKED_IN: 40901,
  /** 前端专用：网络/超时错误 */
  NETWORK_ERROR: -1,
} as const
export type ErrorCode = (typeof ErrorCode)[keyof typeof ErrorCode]
