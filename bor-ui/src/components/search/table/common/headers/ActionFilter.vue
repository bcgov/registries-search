<template>
  <v-btn
    class="search-table__clear"
    :append-icon="'mdi-window-close'"
    color="primary"
    variant="outlined"
    @click="emit('clear', true)"
  >
    Clear Filters
  </v-btn>
</template>
<script setup lang="ts">
const emit = defineEmits<{(e: 'clear', value: boolean): void }>()
</script>
