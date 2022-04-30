<template>
  <v-container id="dashboard" class="view-container px-15 py-10 ma-0" fluid>
    <v-overlay v-model="loading">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <div class="container pa-0">
      <v-row no-gutters>
        <v-col>
          <v-row
            no-gutters
            id="search-header"
            class="dashboard-title pl-6 pt-3 pb-3 soft-corners-top">
            <v-col cols="auto">
              <b>Business Search</b>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <search-bar />
          </v-row>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import SearchBar from '@/components/SearchBar.vue';

const loading = ref(false)
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.dashboard-title {
  background-color: $BCgovBlue0;
  color: $gray9;
  font-size: 1rem;
}
</style>
