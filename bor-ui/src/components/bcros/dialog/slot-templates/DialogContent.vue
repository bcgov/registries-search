<template>
  <p v-if="baseText" v-html="baseText" />
  <div v-if="extraText" class="pt-5" no-gutters>
    <p v-for="(text, index) in extraText" :key="index" v-html="text" />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  baseText: string,
  extraText?: string[]
}>()
</script>
