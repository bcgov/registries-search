<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'

const search = useSearchStore()
const { searchType, activeSearch } = storeToRefs(search)
const searchAccess = useSearchAccessStore()
const { accessLevel, hasExtendedAccess, hasLimitedAccess } = storeToRefs(searchAccess)

const searchVal = ref('')
watch(() => searchType.value, () => {
  searchVal.value = activeSearch.value.val
})

const { t } = useNuxtApp().$i18n

const searchErrorMsg = computed(() => t(`search.${searchType.value}.${accessLevel.value}.error`))
const searchHint = computed(() => t(`search.${searchType.value}.${accessLevel.value}.hint`))
const searchPlaceholder = computed(() => t(`search.${searchType.value}.${accessLevel.value}.placeholder`))

const searchTypeOptions = ref([
  { value: SearchType.BUSINESS, label: t('label.searchBusinesses'), disabled: false },
  {
    value: SearchType.PERSON,
    label: t('label.searchPeople'),
    disabled: false
  }
])

onMounted(async () => {
  if (activeSearch.value.val) {
    searchVal.value = activeSearch.value.val
  }
  const { getStoredFlag } = useConnectLaunchDarkly()
  await searchAccess.init()
  if (hasExtendedAccess.value || hasLimitedAccess.value) {
    searchTypeOptions.value.push({
      value: SearchType.DIRECTOR,
      label: t('label.searchDirectors'),
      disabled: false
    })
  }

  const disabledOptions = (getStoredFlag<string>('disabled-search-types').value || '').split(',')
  for (const option of searchTypeOptions.value) {
    if (disabledOptions.includes(option.value)) {
      option.disabled = true
      option.label = option.label + ' (disabled)'
    }
  }
})

const submitSearch = useDebounceFn(async () => {
  await search.getSearchResults(searchVal.value)
}, 500)

// search error stuff
const showErrors = ref(false)
watch(() => searchVal.value, () => {
  if (searchVal.value.trim()) {
    showErrors.value = false
  }
})

const toggleErrorMsg = () => {
  if (!searchVal.value.trim()) {
    showErrors.value = true
  }
}
</script>

<template>
  <div class="rounded" data-testid="search-input">
    <UFormField :error="showErrors && searchErrorMsg" :help="searchHint">
      <ConnectInput
        id="search-input"
        v-model="searchVal"
        class="border-b-[1px]"
        :label="searchPlaceholder"
        trailing
        trailing-icon="i-mdi-magnify"
        data-testid="search-textfield"
        @keyup="submitSearch()"
        @keyup.enter="toggleErrorMsg()"
      />
    </UFormField>
    <URadioGroup
      v-model="searchType"
      class="mt-5"
      orientation="horizontal"
      :items="searchTypeOptions"
      :ui="{ fieldset: 'flex space-x-4' }"
      data-testid="search-radios"
    />
  </div>
</template>
