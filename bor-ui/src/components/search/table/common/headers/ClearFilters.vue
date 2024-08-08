<template>
  <div>
    <UButton
      class="border-primary-500 border-[1px] pl-3 pr-1 py-2"
      color="primary"
      icon="i-heroicons-x-mark-20-solid"
      label="Clear Filters"
      trailing
      variant="ghost"
      data-cy="search-table-clear-filters"
      @click="emit('action', true)"
    />
  </div>
</template>
<script setup lang="ts">
const emit = defineEmits<{ (e: 'action', value: boolean): void }>()

</script>
