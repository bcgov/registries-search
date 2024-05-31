<template>
  <div class="flex mt-3">
    <USelectMenu
      v-model="exportRows"
      color="primary"
      :options="['50','100','250','500','1000','2000']"
      place-holder="Maximum results to export"
      :popper="{ offsetDistance: 0 }"
      style="width: 225px;"
      variant="none"
      data-cy="table-export-select"
    />
    <UButton
      class="px-4 hover:bg-inherit"
      icon="i-mdi-table-arrow-down"
      label="Export to .xlsx"
      :loading="exportLoading"
      loading-icon="i-mdi-loading"
      variant="ghost"
      data-cy="table-export-btn"
      @click="exportToXlsx()"
    />
  </div>
</template>
<script setup lang="ts">
import _ from 'lodash'

const search = useBcrosSearch()
const { exportRows, searchError } = storeToRefs(search)

const exportLoading = ref(false)
const toast = useToast()

/** Export search results into an .xlsx download file. */
const exportToXlsx = _.debounce(async () => {
  exportLoading.value = true
  await search.exportSearch()
  exportLoading.value = false
  if (!searchError.value) {
    toast.add({
      title: 'Search results successfully exported in the order displayed in the table.'
    })
  }
}, 50, { leading: true, trailing: false })
</script>
