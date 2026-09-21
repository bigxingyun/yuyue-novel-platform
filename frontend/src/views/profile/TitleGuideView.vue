<template>
  <div class="sub-page page-container">
    <SubPageHeader title="阅读头衔" />

    <section v-if="titlesInfo" class="title-summary card">
      <TitleBadge
        :level="titlesInfo.level"
        :title="titlesInfo.title"
        variant="accent"
        :show-level="true"
      />
      <p class="summary-exp">累计经验 {{ titlesInfo.exp }}</p>
      <ExpProgressBar
        :progress="titlesInfo.progress"
        :exp-to-next="titlesInfo.expToNext"
        label="升级进度"
      />
    </section>

    <div class="title-grid">
      <article
        v-for="tier in titlesInfo?.tiers ?? []"
        :key="tier.level"
        class="title-card card"
        :class="{
          unlocked: tier.unlocked,
          current: tier.current,
          locked: !tier.unlocked,
        }"
      >
        <div class="title-card-level">Lv.{{ tier.level }}</div>
        <h3 class="title-card-name">{{ tier.title }}</h3>
        <p class="title-card-exp">{{ tier.minExp }} 经验起</p>
        <span v-if="tier.current" class="title-card-badge">当前</span>
        <span v-else-if="tier.unlocked" class="title-card-badge unlocked">已解锁</span>
        <span v-else class="title-card-badge locked">未解锁</span>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import ExpProgressBar from '@/components/common/ExpProgressBar.vue'
import SubPageHeader from '@/components/common/SubPageHeader.vue'
import TitleBadge from '@/components/common/TitleBadge.vue'
import { fetchTitles, type TitlesInfo } from '@/api/profile'
import { handleError } from '@/utils/errorHandler'

const titlesInfo = ref<TitlesInfo | null>(null)

onMounted(async () => {
  try {
    titlesInfo.value = await fetchTitles()
  } catch (e) {
    handleError(e)
  }
})
</script>

<style scoped>
.title-summary {
  padding: var(--space-5);
  margin-bottom: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  max-width: 560px;
}

.summary-exp {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.title-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-3);
}

.title-card {
  position: relative;
  padding: var(--space-4);
  text-align: center;
  transition: transform var(--transition), box-shadow var(--transition);
}

.title-card.current {
  border-color: var(--color-accent-muted);
  box-shadow: var(--shadow-md);
}

.title-card.locked {
  opacity: 0.55;
}

.title-card-level {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-bottom: var(--space-1);
}

.title-card-name {
  font-family: var(--font-serif);
  font-size: var(--text-lg);
  margin-bottom: var(--space-2);
}

.title-card-exp {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.title-card-badge {
  display: inline-block;
  margin-top: var(--space-3);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 10px;
  font-weight: 500;
}

.title-card-badge.unlocked {
  background: var(--color-accent-soft);
  color: var(--color-accent);
}

.title-card-badge.locked {
  background: var(--color-bg-elevated);
  color: var(--color-text-muted);
}

.title-card.current .title-card-badge {
  background: var(--color-accent);
  color: #fff;
}
</style>
