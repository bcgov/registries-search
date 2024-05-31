<template>
  <div class="rounded" data-cy="search-input">
    <UFormGroup :error="showErrors && searchErrorMsg" :help="searchHint">
      <UInput
        v-model="searchVal"
        class="border-b-[1px]"
        autocomplete="off"
        :color="searchVal ? 'primary' : 'gray'"
        :placeholder="searchLabel"
        trailing
        trailing-icon="i-mdi-magnify"
        data-cy="search-textfield"
        @keyup="submitSearch()"
        @keyup.enter="toggleErrorMsg()"
      />
    </UFormGroup>
    <URadioGroup
      v-if="hasExtendedAccess || hasPublicAccess"
      v-model="searchType"
      class="mt-5 flex"
      :options="searchTypeOptions"
      :ui="{ fieldset: 'flex space-x-3' }"
      data-cy="search-radios"
    />
  </div>
</template>

<script setup lang="ts">
import _ from 'lodash'

const search = useBcrosSearch()
const { accessLevel, hasExtendedAccess, hasPublicAccess, searchType } = storeToRefs(search)
const searchErrorMsg = ref('')
const searchHint = ref('')
const searchLabel = ref('')
const searchTypeOptions = [
  { value: SearchTypeE.BUSINESS, label: 'Search Businesses' },
  { value: SearchTypeE.PERSON, label: 'Search People' }
]

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
</script>
