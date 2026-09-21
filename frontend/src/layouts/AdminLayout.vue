<template>

  <div class="admin-layout">

    <aside class="admin-sidebar">

      <RouterLink to="/profile" class="admin-back-profile">

        <PhArrowLeft :size="16" weight="bold" />

        <span>返回个人中心</span>

      </RouterLink>

      <p class="admin-brand-text">管理后台</p>

      <nav class="admin-nav">

        <RouterLink

          v-for="item in navItems"

          :key="item.to"

          :to="item.to"

          class="admin-nav-item"

          active-class="active"

        >

          {{ item.label }}

        </RouterLink>

      </nav>

    </aside>

    <main class="admin-main">

      <router-view />

    </main>

  </div>

</template>



<script setup lang="ts">

import { PhArrowLeft } from '@phosphor-icons/vue'

import '@/styles/admin.css'



const navItems = [

  { to: '/admin/applications', label: '作者审核' },

  { to: '/admin/users', label: '用户管理' },

  { to: '/admin/keys', label: '密钥管理' },

  { to: '/admin/books', label: '书籍管理' },
  { to: '/admin/comments', label: '评论审核' },
]

</script>



<style scoped>

.admin-layout {

  display: grid;

  grid-template-columns: 176px minmax(0, 1fr);

  min-height: 100dvh;

  background: var(--color-bg);

}



.admin-sidebar {

  display: flex;

  flex-direction: column;

  padding: 16px 12px;

  background: #1a1d24;

  color: #c8c5be;

}



.admin-back-profile {

  display: inline-flex;

  align-items: center;

  gap: 6px;

  padding: 8px 10px;

  margin-bottom: 16px;

  border-radius: var(--radius-md);

  font-size: 13px;

  color: #a8a49c;

  transition: background var(--transition), color var(--transition);

}



.admin-back-profile:hover {

  background: rgba(255, 255, 255, 0.06);

  color: #e8e6e1;

}



.admin-brand-text {

  margin: 0 10px 20px;

  font-family: var(--font-serif);

  font-size: 17px;

  font-weight: 600;

  color: #f0ede8;

}



.admin-nav {

  display: flex;

  flex-direction: column;

  gap: 2px;

  flex: 1;

}



.admin-nav-item {

  padding: 9px 12px;

  border-radius: var(--radius-md);

  font-size: 14px;

  color: #a8a49c;

  transition: background var(--transition), color var(--transition);

}



.admin-nav-item:hover {

  background: rgba(255, 255, 255, 0.06);

  color: #e8e6e1;

}



.admin-nav-item.active {

  background: rgba(196, 149, 106, 0.18);

  color: #e8c9a8;

  font-weight: 500;

}



.admin-main {

  padding: 24px 32px 40px;

  overflow-y: auto;

  min-width: 0;

}



@media (max-width: 768px) {

  .admin-layout {

    grid-template-columns: 1fr;

    grid-template-rows: auto 1fr;

  }



  .admin-sidebar {

    flex-direction: row;

    flex-wrap: wrap;

    align-items: center;

    gap: 8px;

    padding: 10px 12px;

  }



  .admin-back-profile {

    margin-bottom: 0;

  }



  .admin-brand-text {

    margin: 0;

    flex: 1;

  }



  .admin-nav {

    flex-direction: row;

    flex-wrap: wrap;

    width: 100%;

  }



  .admin-main {

    padding: 16px;

  }

}

</style>


