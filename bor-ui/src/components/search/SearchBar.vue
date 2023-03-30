<template>
  <v-container no-gutters class="container pa-0 white-background rounded">    
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
    <v-row class="mt-3" no-gutters>
      <v-col cols="auto">
        <v-checkbox color="primary" density="compact" label="Person" v-model="facets.entityType.person" />
      </v-col>
      <v-col class="ml-3" cols="auto">
        <v-checkbox color="primary" density="compact" label="Business" v-model="facets.entityType.business" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import _ from 'lodash'
// local
import { useSearch } from '@/composables'

// Composables
const { search, filterSearch, getSearchResults } = useSearch()

// search field stuff
const searchErrorMsg = 'Enter a name or number'
const searchHint = 'Example: "John Smith, Test Construction Inc.", "BC0000123", "987654321"'
const searchLabel = 'Entity Name or Incorporation/Registration Number or CRA Business Number'

// search value stuff
const searchVal = ref('')

onMounted(() => { searchVal.value = search._value })

const submitSearch = _.debounce(async () => {
  await getSearchResults(searchVal.value)
}, 500)

// search error stuff
const showErrors = ref(false)
watch(() => searchVal.value, () => {
  if (searchVal.value.trim()) showErrors.value = false
})

const toggleErrorMsg = () => {
  if (!searchVal.value.trim()) showErrors.value = true
}

// facets / checkbox stuff
const facets = reactive({
  entityType: {
    business: false,
    person: true
  }
})

// use below if facet counts move to checkboxes
// const checkboxLabelBusiness = computed(() => {
//   if ((facets.entityType.business || !facets.entityType.person)) {
//     return `Business (${facetCount('entityType', 'BUSINESS')})`
//   }
//   return 'Business'
// })

// const checkboxLabelPerson = computed(() => {
//   if ((facets.entityType.person || !facets.entityType.business)) {
//     return `Person (${facetCount('entityType', 'PERSON')})`
//   }
//   return 'Person'
// })

watch(() => facets.entityType, (val) => {
  if (searchVal.value) showErrors.value = false

  const entityTypes = []
  if (val.business) entityTypes.push('BUSINESS')
  if (val.person) entityTypes.push('PERSON')
  filterSearch(['categories','entityType'], entityTypes)
}, { deep: true })

// unavailable scenario (when search is reindexing / reimporting)
watch(() => search.unavailable, async (val) => {
  if (val) {
    // retry every 10s until search is available again
    let count = 0
    while (search.unavailable === true && count < 1000) {
      await new Promise(resolve => setTimeout(resolve, 10000))
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
