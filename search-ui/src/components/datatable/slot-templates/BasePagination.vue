<template>
  <v-row class="base-table__pagination px-3" justify="end" no-gutters style="align-items: center">
    <v-col cols="auto">
      <label>Page:</label>
    </v-col>
    <v-col cols="auto">
      <v-btn class="base-table__pagination__btn" icon :disabled="page === 1" @click="page -= 1">
        <v-icon>mdi-chevron-left</v-icon>
      </v-btn>
    </v-col>
    <v-col cols="auto">
      {{ page }} of {{ maxPages }}
    </v-col>
    <v-col cols="auto">
      <v-btn class="base-table__pagination__btn" icon :disabled="page === maxPages" @click="page += 1">
        <v-icon>mdi-chevron-right</v-icon>
      </v-btn>
    </v-col>
  </v-row>
</template>
<script setup lang="ts">
import { ref } from 'vue';

const page = ref(1)
const maxPages = 10
</script>