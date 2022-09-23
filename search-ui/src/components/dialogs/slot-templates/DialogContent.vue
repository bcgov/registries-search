<template>
  <v-container class="pa-0">
    <v-row v-if="baseText" no-gutters>
      <v-col cols="auto">
        <p class="base-dialog__text ma-0" v-html="baseText" />
      </v-col>
    </v-row>
    <v-row v-if="extraText.length > 0" class="pt-5" no-gutters>
      <v-col cols="auto">
        <p v-for="(text, index) in extraText" class="base-dialog__text ma-0" :key="index" v-html="text" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
  baseText: { default: '' },
  extraText: { default: (): string[] => []}
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
