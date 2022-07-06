<template>
  <v-container id="search"  fluid>
    <v-overlay v-model="search._loading" style="top: 50%; left: 50%;">
      <v-progress-circular class="v-loader" size="50" indeterminate />
    </v-overlay>
    <div>
      <v-row no-gutters class="pt-4 pl-4">
        <v-col>
          <span class="search-info">
            Search for businesses registered or incorporated in B.C.<span class="lift-text mr-1">*</span> or
            for owners of Firms registered in B.C.
          </span>
        </v-col>
      </v-row>
    </div>
    <div class="container pa-0 search-bar">
      <v-row no-gutters>
        <search-bar />
      </v-row>
    </div>    
    <div class="pl-4">
      *Note: The beta version of business search will not retrieve Railways, Financial Institutions, or
       businesses incorporated under Private acts.
    </div>
    <template v-if="search.results!=null">
    <div class="result-info mt-12">
      <v-row no-gutters v-if="totalResultsLength > 0">   
        <v-col cols="12" style="vertical-align: middle;">
        <span class="results-count ml-6">Search Results({{ totalResultsLength }})</span>
        </v-col>           
    </v-row>
    </div>
    <div class="container pa-0 ">
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

.results-count{
  font-size: 1rem;
  font-weight: bold;
}
</style>
