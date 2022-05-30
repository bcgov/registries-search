<template>
  <v-container fluid no-gutters class="white-background mt-8 soft-corners">    
    <v-row no-gutters class="pt-6">
      <v-col class="ml-n6 pl-6" cols="11">
        <v-text-field
          id="search-bar-field"
          autocomplete="off"
          filled
          label="Business Name, Registration Number or CRA Business Number"
          :hint="searchHint"
          persistent-hint
          :hide-details="suggestActive"
          v-model="suggest.query"
          @blur="suggest.disabled=true"
          @click="suggest.disabled=false"
          @keypress="suggest.disabled=false"
          @keydown="suggest.disabled=false"
          @keyup.enter="submitSearch()"
        />
          <auto-complete v-if="suggestActive" />
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
  </v-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
// local
import { useSearch, useSuggest } from '@/composables';
import { AutoComplete } from '.'

// Composables
const { suggest, suggestActive } = useSuggest()
const { getSearchResults } = useSearch()

const searchHint = 'Example: "Test Construction Inc.", "BC0000123", "987654321"'

const isSearchBtnActive = computed(() => suggest.query.trim().length > 0)

const submitSearch = () => {
  suggest.disabled = true
  getSearchResults(suggest.query)
}
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
