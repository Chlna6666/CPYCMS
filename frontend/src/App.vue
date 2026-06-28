<!--
  CPYCMS - 根组件
  提供全局布局和路由出口
-->
<template>
  <div id="cpycms-app">
    <router-view v-slot="{ Component, route }">
      <Transition name="route-motion" mode="out-in">
        <component :is="Component" :key="route.fullPath" />
      </Transition>
    </router-view>
  </div>
</template>

<script setup lang="ts">
/**
 * 根组件 - 无需额外逻辑
 * 路由视图由子组件渲染
 */
</script>

<style>
/* 全局基础样式在 main.css 中定义 */
</style>
