<script setup lang="ts">
const { accessLevel } = storeToRefs(useSearchAccessStore())
const { searchType, activeSearch } = storeToRefs(useSearchStore())
const { t } = useNuxtApp().$i18n

const searchInfoText = computed(() => t(`search.${searchType.value}.${accessLevel.value}.info`))
const componentReady = ref(false)
onBeforeMount(() => {
  componentReady.value = false
})
onMounted(() => {
  componentReady.value = true
})
</script>

<template>
  <div class="px-[30px] py-12 bg-white rounded" data-testid="search-container">
    <p class="mb-7" data-testid="search-input-info-text">
      {{ searchInfoText }}
    </p>
    <search-input v-model:search-type="searchType" />
    <!-- NOTE: below is what the date picker teleport attaches to -->
    <div id="date-range-filter-dest" />
    <!-- Only render after this is mounted so that ^ div exists for the teleporter -->
    <search-table-results
      v-if="componentReady && (activeSearch.resultsTotal !== undefined || activeSearch.loading || activeSearch.error)"
      class="mt-[30px]"
    />
  </div>
</template>
