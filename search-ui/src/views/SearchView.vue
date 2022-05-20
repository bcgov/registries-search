<template>
  <v-container id="search" class="container" fluid>
    <v-overlay v-model="isLoading">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>
    <div>
      <v-row no-gutters>
        <v-col>
          <h1>Business Search</h1>
        </v-col>
      </v-row>
      <v-row no-gutters class="pt-4">
        <v-col class="search-info select-search-text">
          <span>
            Search for businesses registered in B.C. and access business documents
            (for a fee).
          </span>
        </v-col>
      </v-row>
    </div>
    <div class="container pa-0">               
      <v-row no-gutters>
        <search-bar @is-loading="setLoading"/>
      </v-row>         
    </div>
    <div class="container pa-0 mt-10">               
      <v-row no-gutters>
        <search-results/>
      </v-row>         
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import SearchBar from '@/components/SearchBar.vue'
import SearchResults from '@/components/SearchResults.vue'


const isLoading = ref(false)

const setLoading = (loading: boolean) => {
  isLoading.value = loading
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
