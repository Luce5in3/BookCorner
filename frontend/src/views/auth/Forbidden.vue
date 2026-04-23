<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-apple-black">
    <div class="text-center">
      <h1 class="text-[80px] font-semibold text-white leading-[1.07] tracking-[-0.28px] mb-4">403</h1>
      <p class="text-[21px] text-white/80 leading-[1.19] tracking-[0.231px] mb-8">抱歉，您没有权限访问此页面</p>
      <div class="flex items-center justify-center gap-3">
        <button 
          class="px-4 py-2 bg-transparent text-[14px] text-bright-blue border border-bright-blue rounded-pill cursor-pointer hover:underline transition-colors tracking-[-0.224px]"
          @click="router.go(-1)"
        >
          返回上一页 &gt;
        </button>
        <button 
          class="px-4 py-2 bg-apple-blue text-[14px] text-white rounded-standard border-none cursor-pointer hover:opacity-90 transition-opacity tracking-[-0.224px]"
          @click="router.push('/')"
        >
          返回首页
        </button>
      </div>
    </div>
  </div>
</template>
