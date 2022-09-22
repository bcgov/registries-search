<template>
  <v-container no-gutters class="container pa-0 white-background soft-corners">    
    <v-text-field
      id="search-bar-field"
      class="pt-2"
      :append-inner-icon="'mdi-magnify'"
      autocomplete="off"
      :error-messages="showErrors ? searchErrorMsg : ''"
      filled
      :label="searchLabel"
      :hint="searchHint"
      persistent-hint
      v-model="searchVal"
      @keyup="submitSearch()"
      @keyup.enter="toggleErrorMsg()"
      :rules="[v => (v || '' ).length <= 150 || 'Maximum 150 characters']"
    />
    <v-radio-group class="search-radios pt-1" :direction="'horizontal'" hide-details v-model="search.searchType">
      <v-radio class="search-radios__btn" color="primary" key="business" label="Search Businesses" value="business" />
      <v-radio class="search-radios__btn" color="primary" key="partner" label="Search Firm Owners" value="partner" />
    </v-radio-group>
    <!-- <v-row class="mt-3" no-gutters style="height: 22px;">
      <v-col cols="auto" style="padding-top: 3px;">
      </v-col>
      <v-col class="ml-6" cols="auto" style="padding-top: 3px;">
        <input class="search-radio-btn" type="radio" value="partner" v-model="search.searchType">
      </v-col>
      <v-col class="ml-2" cols="auto">
        <label class="font-normal font-16">Search Firm Owners</label>
      </v-col>
    </v-row> -->
  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import _ from 'lodash'
// local
import { useSearch } from '@/composables'

// Composables
const { search, getSearchResults } = useSearch()

const searchErrorMsg = computed(() => {
  if (search.searchType === 'partner') return 'Enter an owner name'
  return 'Enter a business name or number'
})

const searchHint = computed(() => {
  if (search.searchType === 'partner') return 'Example: "John Smith"'
  return 'Example: "Test Construction Inc.", "BC0000123", "987654321"'
})

const searchLabel = computed(() => {
  if (search.searchType === 'partner') return 'Firm Owner Name'
  return 'Business Name or Incorporation/Registration Number or CRA Business Number'
})

const searchVal = ref('')

const showErrors = ref(false)

const submitSearch = _.debounce(async () => {
  await getSearchResults(searchVal.value)
}, 500)

const toggleErrorMsg = () => {
  if (!searchVal.value) showErrors.value = true
}

onMounted(() => { searchVal.value = search._value })

watch(() => searchVal.value, () => { showErrors.value = false })

watch(() => search.searchType, () => {
  showErrors.value = false
  if (searchVal.value) getSearchResults(searchVal.value)
})

watch(() => search.unavailable, async (val) => {
  if (val) {
    // retry every 30s until search is available again
    let count = 0
    while (search.unavailable === true && count < 1000) {
      await new Promise(resolve => setTimeout(resolve, 30000))
      await getSearchResults(searchVal.value)
      count++
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.search-radios {
  height: 34px;
  width: 385px;

  &__btn {

    :deep(.v-label) {
      color: $gray7 !important;
      font-size: 1rem;
      font-weight: normal;
      opacity: 1;
    }
  }

  &__btn:last-child {
    display: flex;
    margin-top: -40px;
    margin-left: 190px;
  }
}
</style>
