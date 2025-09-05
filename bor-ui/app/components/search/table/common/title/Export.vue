<script setup lang="ts">
import { useThrottleFn } from '@vueuse/core'

const exportRows = defineModel('exportRows', { required: true, type: String, default: '1000' })

const search = useSearchStore()
const { activeSearch } = storeToRefs(search)

const { t } = useI18n()

const exportLoading = ref(false)
const toast = useToast()

/** Export search results into an .xlsx download file. */
const exportToXlsx = useThrottleFn(async () => {
  exportLoading.value = true
  await search.exportSearch()
  exportLoading.value = false
  if (!activeSearch.value.error) {
    toast.add({
      progress: false,
      title: t('text.exportedSearchResults')
    })
  }
}, 1000)
</script>

<template>
  <div class="flex mt-3">
    <USelectMenu
      v-model="exportRows"
      color="primary"
      :content="{ align: 'start' }"
      :items="['50', '100', '250', '500', '1000', '2000']"
      placeholder="Maximum results to export"
      :search-input="false"
      style="width: 225px;"
      data-testid="table-export-select"
    />
    <UButton
      class="px-4 hover:bg-inherit"
      icon="i-mdi-table-arrow-down"
      label="Export to .xlsx"
      :loading="exportLoading"
      loading-icon="i-mdi-loading"
      variant="ghost"
      data-testid="table-export-btn"
      @click="exportToXlsx()"
    />
  </div>
</template>
