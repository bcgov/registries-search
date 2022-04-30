<template>
  <v-container fluid no-gutters class="white-background">
    <v-row no-gutters class="pt-4">
      <v-col class="search-info select-search-text">
        <span>
          Search for businesses registered in B.C. and access business documents
          (for a fee).
        </span>
      </v-col>
    </v-row>
    <v-row no-gutters class="pt-8">
      <v-col class="ml-n6 pl-6" cols="11">
        <v-text-field
          id="search-bar-field"
          class="search-bar-text-field"
          autocomplete="off"
          filled
          label="Business Name, Registration Number or CRA Business Number"
          :hint="searchHint"
          persistent-hint
          :hide-details="hideDetails"
          v-model="searchValue"/>
        <auto-complete
          :searchValue="autoCompleteSearchValue"
          :setAutoCompleteIsActive="autoCompleteIsActive"
          v-click-outside="setCloseAutoComplete"
          @search-value="setSearchValue"
          @hide-details="setHideDetails"
        />
      </v-col>
      <v-col class="pl-3 pt-2">
        <v-row no-gutters>
          <v-btn :id="$style['search-btn']" class="search-bar-btn primary mr-2">
            <v-icon>mdi-magnify</v-icon>
          </v-btn>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import _ from 'lodash'

import AutoComplete from './AutoComplete.vue'

const autoCompleteIsActive = ref(true)
const autoCompleteSearchValue = ref('')
const searchValue = ref('')
const hideDetails = ref(false)
const currentBusinessName = ref('')

const searchHint =
  'Example: "Test Construction Inc.", "BC0000123", "987654321"'

const setHideDetails = (hideDetailsVal: boolean) => {
  hideDetails.value = hideDetailsVal
}

const setCloseAutoComplete = () => {
  autoCompleteIsActive.value = false
}

const setSearchValue = (searchValueTyped: string) => {
  autoCompleteIsActive.value = false
  searchValue.value = searchValueTyped
  currentBusinessName.value = searchValueTyped
}

watch(
  () => searchValue.value,
  (val: string) => {
    if (autoCompleteIsActive.value) {
        autoCompleteSearchValue.value = val
      }
      // show autocomplete results when there is a searchValue and if no error messages
      autoCompleteIsActive.value = val !== ''
  }
)
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';

#search-btn,
#client-search {
  height: 2.85rem;
  min-width: 0 !important;
  width: 3rem;
}
#search-btn-info {
  color: $gray8;
  font-size: 0.725rem;
}
.search-info {
  color: $gray8;
  font-size: 1rem;
}
.search-title {
  color: $gray9;
  font-size: 1rem;
}
.fee-info {
  border-bottom: 1px dotted $gray9;
}
.folio-btn {
  background-color: transparent !important;
  color: $primary-blue !important;
  font-size: 0.825rem !important;
}
.folio-btn::before {
  background-color: transparent !important;
  color: $primary-blue !important;
}
.folio-close-btn {
  background-color: transparent !important;
  color: $primary-blue !important;
  position: absolute;
}
.folio-close-btn::before {
  background-color: transparent !important;
  color: $primary-blue !important;
}
.folio-edit-card {
  width: 15rem;
  position: absolute;
  z-index: 3;
}
.folio-header {
  color: $gray9;
}
.folio-info {
  color: $gray7;
  font-size: 0.875rem;
}
</style>
