<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="forbidden-container">
    <div class="forbidden-content">
      <el-icon size="80" color="#F56C6C"><CircleCloseFilled /></el-icon>
      <h1>403</h1>
      <p>抱歉，您没有权限访问此页面</p>
      <el-button type="primary" @click="router.go(-1)">返回上一页</el-button>
      <el-button @click="router.push('/')">返回首页</el-button>
    </div>
  </div>
</template>

<style scoped>
.forbidden-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
}

.forbidden-content {
  text-align: center;
}

.forbidden-content h1 {
  font-size: 80px;
  color: #F56C6C;
  margin: 20px 0 10px;
}

.forbidden-content p {
  font-size: 18px;
  color: #666;
  margin-bottom: 30px;
}
</style>
