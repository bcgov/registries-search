<template>
  <div class="rounded" data-cy="search-input">
    <UFormGroup :error="showErrors && searchErrorMsg" :help="searchHint">
      <UInput
        v-model="searchVal"
        class="border-b-[1px]"
        autocomplete="off"
        :color="searchVal ? 'primary' : 'gray'"
        :placeholder="searchPlaceholder"
        trailing
        trailing-icon="i-mdi-magnify"
        data-cy="search-textfield"
        size="lg"
        @keyup="submitSearch()"
        @keyup.enter="toggleErrorMsg()"
      />
    </UFormGroup>
    <URadioGroup
      v-model="searchType"
      class="mt-5 flex"
      :options="searchTypeOptions"
      :ui="{ fieldset: 'flex space-x-4' }"
      data-cy="search-radios"
    />
  </div>
</template>

<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'

const search = useBcrosSearch()
const { searchType, activeSearch } = storeToRefs(search)
const { accessLevel, hasExtendedAccess, hasLimitedAccess } = storeToRefs(useBcrosSearchAccess())

const searchVal = ref('')
watch(() => searchType.value, () => { searchVal.value = activeSearch.value.val })

const { t } = useNuxtApp().$i18n

const searchErrorMsg = computed(() => t(`text.search.${searchType.value}.${accessLevel.value}.error`))
const searchHint = computed(() => t(`text.search.${searchType.value}.${accessLevel.value}.hint`))
const searchPlaceholder = computed(() => t(`text.search.${searchType.value}.${accessLevel.value}.placeholder`))

const searchTypeOptions = ref([
  { value: SearchTypeE.BUSINESS, label: t('label.search.searchBusinesses') },
  {
    value: SearchTypeE.PERSON,
    label: hasExtendedAccess.value ? t('label.search.searchPeople') : t('label.search.searchOwners')
  }
])

onMounted(() => {
  if (hasExtendedAccess.value || hasLimitedAccess.value) {
    searchTypeOptions.value.push({
      value: SearchTypeE.DIRECTOR,
      label: t('label.search.searchDirectors')
    })
  }
})

const submitSearch = useDebounceFn(async () => {
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
