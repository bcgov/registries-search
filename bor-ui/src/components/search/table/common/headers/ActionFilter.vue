<template>
  <div :class="outerClass ? outerClass : ''">
    <v-btn
      class="search-table__clear"
      :append-icon="'mdi-window-close'"
      color="primary"
      variant="outlined"
      @click="emit('clear', true)"
    >
      Clear Filters
    </v-btn>
  </div>
</template>
<script setup lang="ts">
defineProps<{ outerClass?: string }>()
const emit = defineEmits<{(e: 'clear', value: boolean): void }>()
</script>
