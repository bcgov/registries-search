<template>
  <div class="grow">
    <slot name="title">
      <h2 class="ml-3 py-6">
        {{ title }}
        <span v-if="loading" class="ml-[2px]">
          <!-- <div class="rounded-full animate-spin w-6 h-6 py-1 bg-gradient-to-tr from-blue-500 to-blue-100">
            <div class="m-auto h-4 w-4 rounded-full bg-gray-200"></div>
          </div> -->
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

<script setup lang="ts">

defineProps<{
  loading?: boolean,
  resultsDescription?: string,
  title?: string
  totalItems?: number
  subtitle?: string
}>()
</script>
