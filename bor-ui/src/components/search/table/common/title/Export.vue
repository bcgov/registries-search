<template>
  <v-row class="mt-3" no-gutters justify="end">
    <v-col align-self="center" cols="auto">
      <v-select
        v-model="exportRows"
        class="search-table__export-select pt-1 rounded-top"
        density="default"
        hide-details
        :items="[50,100,250,500,1000,2000]"
        label="Maximum results to export"
        style="width: 225px;"
        variant="underlined"
      />
    </v-col>
    <v-col align-self="center" cols="auto">
      <v-btn
        class="search-table__export-rows-btn"
        color="primary"
        density="compact"
        :loading="exportLoading"
        prepend-icon="mdi-table-arrow-down"
        :ripple="false"
        variant="text"
        @click="exportToXlsx()"
      >
        Export to .xlsx
      </v-btn>
    </v-col>
  </v-row>
  <v-snackbar :model-value="showExportSnack">
    Search results successfully exported in the order displayed in the table.
    <template #actions>
      <v-btn icon="mdi-window-close" @click="showExportSnack = false" />
    </template>
  </v-snackbar>
</template>
<script setup lang="ts">
import _ from 'lodash'

const search = useBcrosSearch()
const { exportRows, searchError } = storeToRefs(search)

const exportLoading = ref(false)
const showExportSnack = ref(false)

/** Export search results into an .xlsx download file. */
const exportToXlsx = _.debounce(async () => {
  exportLoading.value = true
  await search.exportSearch()
  exportLoading.value = false
  if (!searchError.value) { showExportSnack.value = true }
}, 50, { leading: true, trailing: false })
</script>
