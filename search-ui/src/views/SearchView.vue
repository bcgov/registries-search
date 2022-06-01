<template>
  <v-container id="search" class="container" fluid>
    <v-overlay v-model="search._loading" style="top: 50%; left: 50%;">
      <v-progress-circular class="v-loader" size="50" indeterminate />
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
        <search-bar />
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
// local
import { SearchBar, SearchResults } from '@/components/search'
import { useSearch } from '@/composables'

const { search } = useSearch()
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
