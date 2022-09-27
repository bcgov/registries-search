<template>
  <v-container class="pa-0">
    <p v-if="baseText" v-html="baseText" />
    <div v-if="extraText" class="pt-5" no-gutters>
      <p v-for="(text, index) in extraText" :key="index" v-html="text" />
    </div>
  </v-container>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{
  baseText: string,
  extraText?: string[]
}>()
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
