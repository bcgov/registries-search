<template>
  <v-container fluid no-gutters class="white-background mt-8 soft-corners-top soft-corners-bottom">    
    <v-row no-gutters class="pt-6">
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
          @hide-details="setHideDetails"/>
      </v-col>
      <v-col class="pl-3 pt-2">
        <v-row no-gutters>
          <v-btn :id="$style['search-btn']" class="search-bar-btn primary mr-2" @click="search()"
          :disabled="!isSearchBtnActive">
            <v-icon>mdi-magnify</v-icon>
          </v-btn>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useStore } from 'vuex'

import AutoComplete from './AutoComplete.vue'

// Store
const store = useStore()

// Emits
const emit = defineEmits(['isLoading'])

// Refs
const autoCompleteIsActive = ref(true)
const autoCompleteSearchValue = ref('')
const searchValue = ref('')
const hideDetails = ref(false)
const currentBusinessName = ref('')

const searchHint = 'Example: "Test Construction Inc.", "BC0000123", "987654321"'

const setHideDetails = (hideDetailsVal: boolean) => {
  hideDetails.value = hideDetailsVal
}

const setCloseAutoComplete = () => {
  autoCompleteIsActive.value = false
}

const setSearchValue = (selectedAutoCompleteValue: string) => {
  autoCompleteIsActive.value = false
  searchValue.value = selectedAutoCompleteValue
  currentBusinessName.value = selectedAutoCompleteValue
}

const isSearchBtnActive = computed(() => searchValue.value.trim().length > 0 )

const search = async () => {
   emit('isLoading', true)
   await store.dispatch('search', searchValue.value.trim() )
   emit('isLoading', false)
}

watch(() => searchValue.value,(val: string) => {
    if (autoCompleteIsActive.value) {
        autoCompleteSearchValue.value = val
      }
      // show autocomplete results when there is a searchValue and if no error messages
      autoCompleteIsActive.value = val !== ''
  })

watch(() => currentBusinessName.value, (val: string) => {
    search()
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
</style>
