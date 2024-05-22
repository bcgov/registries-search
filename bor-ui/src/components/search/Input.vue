<template>
  <div class="rounded" data-cy="search-input">
    <v-text-field
      id="search-bar-field"
      v-model="searchVal"
      class="pt-2"
      :append-inner-icon="'mdi-magnify'"
      autocomplete="off"
      :error-messages="showErrors ? searchErrorMsg : ''"
      filled
      :label="searchLabel"
      :hint="searchHint"
      persistent-hint
      :rules="[v => (v || '' ).length <= 150 || 'Maximum 150 characters']"
      @keyup="submitSearch()"
      @keyup.enter="toggleErrorMsg()"
    />
    <v-row v-if="hasExtendedAccess" class="mt-5 search-radios" no-gutters>
      <v-col cols="auto">
        <v-radio
          v-model="facets.entityType.business"
          color="primary"
          density="compact"
          disabled
          label="Search Businesses"
        />
      </v-col>
      <v-col class="ml-3" cols="auto">
        <v-radio
          v-model="facets.entityType.person"
          color="primary"
          density="compact"
          label="Search People"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import _ from 'lodash'

const search = useBcrosSearch()
const { accessLevel, hasExtendedAccess } = storeToRefs(search)
const searchErrorMsg = ref('')
const searchHint = ref('')
const searchLabel = ref('')

const searchVal = ref('')

onMounted(() => {
  switch (accessLevel.value) {
    case SearchAccessE.EXTENDED:
      searchErrorMsg.value = 'Enter a name, address, SIN/TTN/ITN, and/or email address'
      searchHint.value = ('Example: "John Smith", "123 Main St", ' +
        '"V1V 1V1", "John Smith Victoria", "j.smith@123.aba", "000 000 000"')
      searchLabel.value = 'Person Name, Address, SIN/TTN/ITN, and/or Email Address'
      break
    case SearchAccessE.LIMITED:
      searchErrorMsg.value = 'Enter a name, address, and/or business email address'
      searchHint.value = 'Example: "John Smith", "123 Main St", "V1V 1V1", "John Smith Victoria", "j.smith@123.aba"'
      searchLabel.value = 'Person Name, Address, and/or Business Email Address'
      break
    default: // SearchAccessE.PUBLIC
      searchErrorMsg.value = 'Enter a name'
      searchHint.value = 'Example: "John Smith"'
      searchLabel.value = 'Person Name'
  }

  searchVal.value = search.searchValue
})

const submitSearch = _.debounce(async () => {
  await search.getSearchResults(searchVal.value)
}, 500)

// search error stuff
const showErrors = ref(false)
watch(() => searchVal.value, () => {
  if (searchVal.value.trim()) { showErrors.value = false }
})

const toggleErrorMsg = () => {
  if (!searchVal.value.trim()) { showErrors.value = true }
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
  if (searchVal.value) { showErrors.value = false }

  // not currently supporting searching both at once
  if (val.business) {
    search.filterSearch(['categories', 'entityType'], ['BUSINESS'])
    return
  }
  // if (val.person)
  search.filterSearch(['categories', 'entityType'], ['PERSON'])
}, { deep: true })
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.search-radios {
  height: 34px;
  width: 385px;

  :deep(.v-label) {
    color: $gray7 !important;
    font-size: 1rem;
    font-weight: normal;
    opacity: 1;
  }
}
</style>
