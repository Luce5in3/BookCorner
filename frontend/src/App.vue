<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // 初始化认证状态
  authStore.init()
})
</script>

<template>
  <router-view />
</template>

<style>
#app {
  width: 100%;
  height: 100%;
}
</style>
