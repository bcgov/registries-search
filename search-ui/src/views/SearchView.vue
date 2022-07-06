<template>
  <v-container id="search" class="container" fluid>
    <v-overlay v-model="search._loading" style="top: 50%; left: 50%;">
      <v-progress-circular class="v-loader" size="50" indeterminate />
    </v-overlay>
    <div>
      <v-row no-gutters class="pt-4 pl-4">
        <v-col>
          <div class="search-info">
            Search for businesses registered or incorporated in B.C.<span class="lift-text mr-1">*</span> or
            for owners of Firms registered in B.C.
          </div>
        </v-col>
      </v-row>
    </div>
    <div class="container pa-0">
      <v-row no-gutters>
        <search-bar />
      </v-row>
    </div>    
    <div class="pl-4">
      *Note: The beta version of business search will not retrieve Railways, Financial Institutions, or
       businesses incorporated under Private acts.
    </div>
    <template v-if="search.results!=null">
    <div>
      <v-row class="result-info pt-30px pl-8" no-gutters v-if="totalResultsLength > 0">   
        <v-col cols="12">
        <b>Search Results({{ totalResultsLength }})</b>
        </v-col>           
    </v-row>
    </div>
    <div class="container pa-0 mt-10">
      <v-row no-gutters>
        <search-results/>
      </v-row>
    </div>    
    </template>    
  </v-container>
</template>

<script setup lang="ts">
// local
import { SearchBar, SearchResults } from '@/components/search'
import { useSearch } from '@/composables'
import { computed } from 'vue'

const { search } = useSearch()

const totalResultsLength = computed(() => search.results?.length || 0 ) 
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.search-info {
  font-size: 16px;
  color: $gray7;
  display: flex;   
}

.lift-text{
  line-height: 10px;
  font-size: 0.75rem;
  font-weight: bold;
}
</style>
