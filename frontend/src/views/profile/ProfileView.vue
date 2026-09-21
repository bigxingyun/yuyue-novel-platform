<template>
  <div class="profile page-container">
    <header class="profile-hero card">
      <UserAvatar :src="userInfo?.avatar" :seed="userInfo?.id ?? 'yuyue'" size="xl" />
      <div class="profile-info">
        <h1 class="profile-name">{{ userInfo?.nickname }}</h1>
        <TitleBadge
          :level="titleInfo.level"
          :title="titleInfo.title"
          variant="accent"
          :show-level="true"
        />
        <ExpProgressBar
          class="profile-progress"
          :progress="titleInfo.progress"
          :exp-to-next="titleInfo.expToNext"
          :label="`经验 ${userInfo?.exp ?? 0}`"
        />
      </div>
      <button
        class="btn btn-primary btn-sm checkin-btn"
        :class="{ 'checkin-done': checkedIn }"
        @click="onCheckInClick"
      >
        <PhCalendarCheck :size="18" />
        {{ checkedIn ? '已签到' : '签到' }}
      </button>
    </header>

    <div v-if="authorAppBanner" class="author-status card">
      <span class="author-status-label">作者申请</span>
      <span class="author-status-tag" :class="authorAppBanner.status">
        {{ authorAppBanner.label }}
      </span>
      <p v-if="authorAppBanner.note" class="author-status-note">{{ authorAppBanner.note }}</p>
      <RouterLink
        v-if="authorAppBanner.status === 'pending' || authorAppBanner.status === 'rejected'"
        to="/profile/apply-author"
        class="author-status-link"
      >
        查看详情
      </RouterLink>
    </div>

    <nav class="profile-menu">
      <RouterLink
        v-for="item in menuItems"
        :key="item.to"
        :to="item.to"
        class="menu-item card card-interactive"
      >
        <component :is="item.icon" :size="22" weight="duotone" class="menu-icon" />
        <span class="menu-label">{{ item.label }}</span>
        <PhCaretRight :size="16" class="menu-arrow" />
      </RouterLink>
    </nav>

    <button class="btn btn-ghost logout-btn" @click="logout">退出登录</button>

    <Transition name="modal">
      <div v-if="checkInOpen" class="checkin-modal" @click="checkInOpen = false">
        <div class="checkin-card" @click.stop>
          <div class="checkin-badge">今日运势</div>
          <p class="checkin-fortune">{{ fortune }}</p>
          <p class="checkin-exp">+{{ expGained }} 经验</p>
          <div v-if="leveledUp" class="level-up-banner">
            <PhMedal :size="20" weight="duotone" />
            恭喜晋升 · {{ newTitle }}
          </div>
          <button class="btn btn-primary btn-block" @click="checkInOpen = false">收下</button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  PhCalendarCheck,
  PhCaretRight,
  PhClockCounterClockwise,
  PhGearSix,
  PhLock,
  PhMedal,
  PhPencilSimple,
  PhPenNib,
  PhStar,
  PhUser,
} from '@phosphor-icons/vue'
import ExpProgressBar from '@/components/common/ExpProgressBar.vue'
import TitleBadge from '@/components/common/TitleBadge.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { useUserStore } from '@/stores/user'
import { checkIn as apiCheckIn, fetchAuthorApplication, fetchCheckInStatus } from '@/api/profile'
import { getTitleInfo } from '@/constants/titles'
import { UserRole, ApplicationStatus } from '@/types/enums'
import { handleError, notify } from '@/utils/errorHandler'

const router = useRouter()
const userStore = useUserStore()
const checkInOpen = ref(false)
const checkedIn = ref(false)
const leveledUp = ref(false)
const newTitle = ref('')

const userInfo = computed(() => userStore.userInfo)
const titleInfo = computed(() =>
  getTitleInfo(userInfo.value?.exp ?? 0),
)

const fortune = ref('')
const expGained = ref(0)
const authorAppStatus = ref<string | null>(null)
const authorAppReviewNote = ref<string | null>(null)

const authorAppBanner = computed(() => {
  if (userInfo.value?.role !== UserRole.USER || !authorAppStatus.value) return null
  const status = authorAppStatus.value
  const labels: Record<string, string> = {
    [ApplicationStatus.PENDING]: '审核中',
    [ApplicationStatus.APPROVED]: '已通过',
    [ApplicationStatus.REJECTED]: '未通过',
  }
  const notes: Record<string, string> = {
    [ApplicationStatus.PENDING]: '你的申请正在审核，请耐心等待',
    [ApplicationStatus.REJECTED]: authorAppReviewNote.value || '可修改理由后重新提交',
  }
  return {
    status,
    label: labels[status] ?? status,
    note: notes[status],
  }
})

const menuItems = computed(() => {
  const role = userInfo.value?.role
  const items = [
    { to: '/profile/edit', label: '修改资料', icon: PhUser },
    { to: '/profile/password', label: '修改密码', icon: PhLock },
    { to: '/profile/titles', label: '阅读头衔', icon: PhMedal },
    { to: '/profile/exp', label: '经验记录', icon: PhStar },
    { to: '/profile/history', label: '阅读历史', icon: PhClockCounterClockwise },
  ]
  if (role === UserRole.USER) {
    items.push({ to: '/profile/apply-author', label: '申请成为作者', icon: PhPenNib })
  }
  if (
    role === UserRole.AUTHOR ||
    role === UserRole.ADMIN ||
    role === UserRole.SUPERADMIN
  ) {
    items.push({ to: '/profile/works', label: '作品管理', icon: PhPencilSimple })
  }
  if (role === UserRole.ADMIN || role === UserRole.SUPERADMIN) {
    items.push({ to: '/admin/applications', label: '管理后台', icon: PhGearSix })
  }
  return items
})

onMounted(async () => {
  try {
    const status = await fetchCheckInStatus()
    checkedIn.value = status.checkedIn
    if (status.fortuneText) fortune.value = status.fortuneText
  } catch {
    /* ignore */
  }
  if (userInfo.value?.role === UserRole.USER) {
    try {
      const app = await fetchAuthorApplication()
      if (app) {
        authorAppStatus.value = app.status
        authorAppReviewNote.value = app.reviewNote ?? null
      }
    } catch {
      /* ignore */
    }
  }
})

async function onCheckInClick() {
  if (checkedIn.value) {
    checkInOpen.value = true
    return
  }
  await checkIn()
}

async function checkIn() {
  try {
    const result = await apiCheckIn()
    fortune.value = result.fortuneText
    expGained.value = result.expGained
    leveledUp.value = !!result.leveledUp
    newTitle.value = result.newTitle ?? result.title ?? ''
    if (userStore.userInfo) {
      userStore.userInfo.exp = result.exp
      userStore.userInfo.level = result.level
      userStore.userInfo.title = result.title
    }
    checkedIn.value = true
    checkInOpen.value = true
    notify('签到成功', 'success')
  } catch (e) {
    handleError(e)
  }
}

async function logout() {
  await userStore.logout()
  notify('已退出登录')
  router.push('/')
}
</script>

<style scoped>
.profile-hero {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
}

.author-status {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px 14px;
  padding: 14px 18px;
  margin-bottom: var(--space-5);
}

.author-status-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.author-status-tag {
  padding: 2px 10px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 500;
}

.author-status-tag.pending {
  background: #fff3cd;
  color: #856404;
}

.author-status-tag.approved {
  background: var(--color-accent-soft);
  color: var(--color-accent);
}

.author-status-tag.rejected {
  background: #fde8e8;
  color: #b43c3c;
}

.author-status-note {
  flex: 1 1 100%;
  margin: 0;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.author-status-link {
  font-size: var(--text-sm);
  color: var(--color-accent);
}

.profile-info {
  flex: 1;
  min-width: 160px;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.profile-name {
  font-family: var(--font-serif);
  font-size: var(--text-xl);
}

.profile-progress {
  max-width: 280px;
}

.checkin-btn {
  margin-left: auto;
}

.checkin-btn.checkin-done {
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border-soft);
}

.profile-menu {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-bottom: var(--space-8);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: var(--space-4) var(--space-5);
}

.menu-icon {
  color: var(--color-accent);
}

.menu-label {
  flex: 1;
  font-size: var(--text-base);
}

.menu-arrow {
  color: var(--color-text-muted);
}

.logout-btn {
  width: auto;
  align-self: center;
  padding: 4px 8px;
  font-size: var(--text-sm);
  margin-top: var(--space-2);
  color: var(--color-text-muted);
}

.checkin-modal {
  position: fixed;
  inset: 0;
  z-index: 500;
  background: rgba(20, 23, 30, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
}

.checkin-card {
  width: 100%;
  max-width: 360px;
  padding: var(--space-8) var(--space-6);
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  text-align: center;
  box-shadow: var(--shadow-lg);
}

.checkin-badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: var(--radius-full);
  background: var(--color-accent-soft);
  color: var(--color-accent);
  font-size: var(--text-sm);
  margin-bottom: var(--space-5);
}

.checkin-fortune {
  font-family: var(--font-serif);
  font-size: var(--text-lg);
  line-height: 1.6;
  margin-bottom: var(--space-4);
}

.checkin-exp {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-accent);
  margin-bottom: var(--space-4);
}

.level-up-banner {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  margin-bottom: var(--space-5);
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, rgba(139, 41, 66, 0.12), rgba(139, 41, 66, 0.06));
  color: var(--color-accent);
  font-size: var(--text-sm);
  font-weight: 600;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}

.modal-enter-active .checkin-card,
.modal-leave-active .checkin-card {
  transition: transform 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .checkin-card,
.modal-leave-to .checkin-card {
  transform: scale(0.95);
}
</style>
