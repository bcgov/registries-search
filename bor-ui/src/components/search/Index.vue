<template>
  <div class="px-[30px] py-12 bg-white rounded" data-cy="search-container">
    <p class="mb-7" data-cy="search-input-info-text">
      {{ searchInfoText }}
    </p>
    <search-input v-model:searchType="searchType" />
    <!-- NOTE: below is what the date picker teleport attaches to -->
    <div id="date-range-filter-dest" />
    <search-table-results
      v-if="activeSearch.resultsTotal !== undefined || activeSearch.loading || activeSearch.error"
      class="mt-[30px]"
    />
  </div>
</template>

<script setup lang="ts">
const { accessLevel } = storeToRefs(useBcrosSearchAccess())
const { searchType, activeSearch } = storeToRefs(useBcrosSearch())
const { t } = useNuxtApp().$i18n

const searchInfoText = computed(() => t(`text.search.${searchType.value}.${accessLevel.value}.info`))

</script>
