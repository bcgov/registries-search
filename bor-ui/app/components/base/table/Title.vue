<script setup lang="ts">
defineProps<{
  loading?: boolean
  resultsDescription?: string
  title?: string
  totalItems?: number
  subtitle?: string
}>()
</script>

<template>
  <div class="grow">
    <slot name="title">
      <h2 class="ml-3 py-6">
        {{ title }}
        <span v-if="loading" class="ml-[2px]">
          <UIcon name="i-mdi-loading" class="flex-shrink-0 h-6 w-6 animate-spin align-middle" />
        </span>
        <span v-else-if="resultsDescription" style="font-weight: normal">
          ({{ resultsDescription }})
        </span>
        <span v-else-if="totalItems" style="font-weight: normal">({{ totalItems }})</span>
      </h2>
    </slot>
    <slot name="subtitle">
      <h4 v-if="subtitle" class="ml-3 mb-6">
        {{ subtitle }}
      </h4>
    </slot>
  </div>
</template>
