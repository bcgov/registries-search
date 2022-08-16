<template>
  <v-container no-gutters class="container pa-0 white-background soft-corners">    
    <v-text-field
      id="search-bar-field"
      class="pt-2"
      autocomplete="off"
      filled
      label="Business Name, Incorporation/Registration Number, CRA Business Number or Firm Owner Name"
      :hint="searchHint"
      persistent-hint
      v-model="searchVal"
      @keyup="submitSearch()"
      :rules="[v => (v || '' ).length <= 150 || 'Maximum 150 characters']"
    />
    <v-row no-gutters>
      <v-col cols="auto" style="padding-top: 2px;">
        <input type="radio" value="business" v-model="search.searchType">
      </v-col>
      <v-col class="ml-2" cols="auto">
        <label class="font-normal">Businesses</label>
      </v-col>
      <v-col class="ml-4" cols="auto" style="padding-top: 2px;">
        <input type="radio" value="partner" v-model="search.searchType">
      </v-col>
      <v-col class="ml-2" cols="auto">
        <label class="font-normal">Firm Owners</label>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import _ from 'lodash'
// local
import { useSearch } from '@/composables'

// Composables
const { search, getSearchResults } = useSearch()

const searchHint = 'Example: "Test Construction Inc.", "BC0000123", "987654321"'
const searchVal = ref('')

const submitSearch = _.debounce(async () => {
  await getSearchResults(searchVal.value)
}, 500)

onMounted(() => { searchVal.value = search._value })

watch(() => search.searchType, () => {
  if (searchVal.value) getSearchResults(searchVal.value)
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';

#search-btn,
#client-search {
  height: 2.85rem;
  min-width: 0 !important;
  width: 3rem;
}
</style>
