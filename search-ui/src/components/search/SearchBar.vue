<template>
  <v-container no-gutters class="container pa-0 white-background soft-corners">    
    <v-row no-gutters class="pt-2">
      <v-col class="ml-n6 pl-6" cols="11">
        <v-text-field
          id="search-bar-field"
          autocomplete="off"
          filled
          label="Business Name, Incorporation/Registration Number, CRA Business Number or Firm Owner Name"
          :hint="searchHint"
          persistent-hint
          :hide-details="suggestActive"
          v-model="suggest.query"
          @blur="handleFocusChange()"
          @click="suggest.disabled=false"
          @keypress="suggest.disabled=false"
          @keydown="suggest.disabled=false"
          @keyup.enter="submitSearch()"
        />
          <suggest-list v-if="suggestActive" />
      </v-col>
      <v-col class="pl-3 pt-2">
        <v-row no-gutters>
          <v-btn
            :id="$style['search-btn']"
            class="primary mr-2"
            :disabled="!isSearchBtnActive"
            @click="submitSearch()"
          >
            <v-icon>mdi-magnify</v-icon>
          </v-btn>
        </v-row>
      </v-col>
    </v-row>
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
import { computed, watch } from 'vue'
// local
import { useSearch, useSuggest } from '@/composables';
import { SuggestList } from '.'

// Composables
const { suggest, suggestActive } = useSuggest()
const { search, getSearchResults } = useSearch()

const searchHint = 'Example: "Test Construction Inc.", "BC0000123", "987654321"'

const isSearchBtnActive = computed(() => suggest.query.trim().length > 0)

const handleFocusChange = () => {
  // delay until click fires (in case clicking a suggest list item)
  setTimeout( () => suggest.disabled = true, 100)
}

const submitSearch = () => {
  suggest.disabled = true
  getSearchResults(suggest.query)
}

watch(() => search.searchType, () => {
  if (search._value) {
    getSearchResults(search._value)
  }
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
