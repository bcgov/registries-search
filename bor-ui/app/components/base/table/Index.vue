<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'

const localProps = defineProps<{
  colors?: BaseTableColors
  filterClass?: string
  height?: string
  itemKey: string
  loading?: boolean
  noResultsText?: string
  pagination?: boolean
  overflow?: string
  resetFiltersTrigger?: boolean
  resetOnItemChange?: boolean
  resultsDescription?: string
  setHeaders: BaseTableHeader[]
  setItems: any[]
  tableWidth?: string
  title?: string
  titleExtras?: boolean
  totalItems?: number
  subtitle?: string
}>()

const emit = defineEmits<{ (e: 'filterActive', value: boolean): void }>()

const headers = reactive(([...localProps.setHeaders]) as BaseTableHeader[])
const displayItemHeaders = headers?.filter(header => !header.itemHidden)
const sortedItems = ref([...localProps.setItems])

const emptyText = computed(() => localProps.noResultsText || 'No results found')
const isFilteringActive = ref(false)

const headerBg = computed(() => localProps.colors?.backgrounds?.header || 'white')
const titleBg = computed(() => localProps.colors?.backgrounds?.title || '#e0e7ed')

const resettingFilters = ref(false)
const resetAll = () => {
  if (headers.length > 0 && headers[0]) {
    resettingFilters.value = true
    // reset filters
    for (const header of headers) {
      if (header.filter?.value) {
        header.filter.value = undefined
      }
    }
    resettingFilters.value = false
  }
}
watch(() => localProps.resetFiltersTrigger, () => {
  resetAll()
})

const filterActive = computed(() => {
  for (const header of headers) {
    if (header.filter?.value) {
      return true
    }
  }
  return false
})
watch(() => filterActive.value, (val) => {
  emit('filterActive', val)
})

const clearFilter = (header: BaseTableHeader) => {
  if (header.filter) {
    header.filter.value = undefined
    filter(header)
  }
}
const filter = useDebounceFn(async (header: BaseTableHeader) => {
  if (resettingFilters.value) {
    return
  }
  if (header.filter) {
    // rely on custom filterApiFn to alter result set if given (meant for server side isFilteringActive)
    if (!header.filter?.value || header.filter.value.length === 0) {
      header.filter.value = undefined
    }
    if (header.filter.filterApiFn) {
      isFilteringActive.value = true
      await header.filter.filterApiFn(header.filter.value)
      isFilteringActive.value = false
    } else {
      // client side custom or base filter
      sortedItems.value = [...localProps.setItems]
      for (const header of headers) {
        const filterValue = header.filter?.value
        if (filterValue) {
          sortedItems.value = sortedItems.value.filter((item) => {
            if (header.filter?.filterFn) {
              return header.filter.filterFn(item[header.col], filterValue)
            } else if (header.filter?.type === 'select') {
              return BaseSelectFilter(item[header.col], filterValue)
            } else if (header.col && item[header.col]) {
              return BaseTextFilter(item[header.col], filterValue)
            }
          })
        }
      }
    }
  }
}, 500)

watch(() => localProps.setItems, (val) => {
  if (val) {
    sortedItems.value = [...val]
  } else {
    sortedItems.value = []
  }

  if (localProps.resetOnItemChange) {
    resetAll()
  }
}, { deep: true })
</script>

<template>
  <div :style="[{ height: height || '540px' }, { overflow: overflow || 'scroll' }]">
    <div
      v-if="title"
      class="table-title"
      :style="{ 'background-color': titleBg }"
    >
      <slot name="table-title" :headers="headers">
        <div class="flex">
          <BaseTableTitle
            :loading="loading"
            :results-description="resultsDescription"
            :subtitle="subtitle"
            :title="title"
            :title-extras="titleExtras"
            :total-items="totalItems"
          />
          <div v-if="titleExtras">
            <slot name="title-extras" />
          </div>
        </div>
      </slot>
    </div>
    <table class="base-table border border-line-muted" :style="{ width: tableWidth ? tableWidth : '100%' }">
      <thead>
        <slot name="header" :headers="headers">
          <slot name="header-item-titles" :headers="headers">
            <tr :style="{ 'background-color': headerBg }">
              <th
                v-for="header, i in headers"
                :key="header.col + i"
                :class="[header.class, 'align-bottom text-start pb-5 pt-2 px-1 first:pl-3']"
                :style="[!header.col ? 'text-align: center;' : '', `width: ${header.width}`]"
                data-testid="base-table-header"
              >
                {{ header.value }}
              </th>
            </tr>
          </slot>
          <slot name="header-item-filters" :headers="headers">
            <tr class="border-y border-line-muted" :style="{ 'background-color': headerBg }">
              <th
                v-for="header, i in headers"
                :key="header.col + i"
                :class="[header.class, 'first:pl-3 p-1']"
                :style="{ width: header.width }"
              >
                <slot :name="'header-filter-slot-' + header.slotId" :header="header">
                  <div class="py-5 font-normal">
                    <USelectMenu
                      v-if="header.hasFilter && header.filter && header.filter?.type === 'select'"
                      v-model="header.filter.value"
                      :class="[filterClass, 'text-sm w-full h-9', header.filter.value ? 'bg-shade-highlighted' : '']"
                      :content="{ align: 'start' }"
                      :items="(
                        header.filter.items
                        || (header.filter.itemsFn
                          ? header.filter.itemsFn(header.filter.itemsFnVal)
                          : undefined)
                      )"
                      :label-key="header.filter.itemValue"
                      :value-key="header.filter.itemValue"
                      :placeholder="header.filter.label"
                      :disabled="header.filter.disabled"
                      :multiple="!!header.filter.multiple"
                      :search-input="false"
                      :ui="{ content: 'w-full', placeholder: 'text-neutral' }"
                      data-testid="base-table-header-filter"
                      @update:model-value="filter(header)"
                    >
                      <template #default>
                        <div class="overflow-hidden whitespace-nowrap text-ellipsis">
                          <slot
                            :name="'header-filter-selected-slot-' + header.slotId"
                            :selected="header.filter.value"
                          >
                            <span
                              v-if="!header.filter.value || header.filter?.value.length === 0"
                              class="text-neutral"
                            >
                              {{ header.filter.label }}
                            </span>
                            <span v-else-if="!header.filter.multiple" class="text-start">
                              {{ capFirstLetterAll(header.filter.value) }}
                            </span>
                            <span v-else class="text-start">
                              <span v-for="val, filterIndex in header.filter.value" :key="`filter-${val}`">
                                {{ (filterIndex !== 0 ? ', ' : '') + capFirstLetterAll(val) }}
                              </span>
                            </span>
                          </slot>
                        </div>
                      </template>
                      <template #trailing>
                        <div class="text-sm">
                          <UButton
                            v-if="header.filter.value?.length"
                            class="-me-1 p-0"
                            color="primary"
                            variant="link"
                            icon="i-heroicons-x-mark-20-solid"
                            data-testid="base-table-header-filter-clear"
                            @click="clearFilter(header)"
                          />
                          <UIcon name="i-mdi-arrow-drop-down" class="size-5 text-neutral" />
                        </div>
                      </template>
                      <template
                        v-if="header.filter.multiple || header.filter.hasItemSlot"
                        #item="{ item }"
                      >
                        <slot :name="'header-filter-item-slot-' + header.slotId" :item="item">
                          <div class="hover:cursor-pointer">
                            <UCheckbox
                              class="pointer-events-none"
                              :label="capFirstLetterAll(
                                header.filter.itemValue ? item[header.filter.itemValue] : item)"
                              :model-value="header.filter.value?.includes(item.value)"
                            />
                          </div>
                        </slot>
                      </template>
                    </USelectMenu>
                    <UInput
                      v-else-if="header.filter && header.hasFilter && header.filter?.type === 'text'"
                      v-model="header.filter.value"
                      :class="[filterClass, 'w-full', header.filter.value ? '*:bg-shade-highlighted' : '']"
                      :disabled="header.filter.disabled"
                      :placeholder="!header.filter.value ? header.filter.label || '' : ''"
                      size="lg"
                      :ui="{ base: 'placeholder:text-neutral', trailing: 'size-8' }"
                      data-testid="base-table-header-filter"
                      @update:model-value="filter(header)"
                    >
                      <template #trailing>
                        <UButton
                          v-if="!!header.filter.value"
                          color="primary"
                          variant="link"
                          icon="i-heroicons-x-mark-20-solid"
                          :padded="false"
                          data-testid="base-table-header-filter-clear"
                          @click="clearFilter(header)"
                        />
                      </template>
                    </UInput>
                  </div>
                </slot>
              </th>
            </tr>
          </slot>
        </slot>
      </thead>
      <tbody v-if="loading">
        <slot name="loading" :headers="headers">
          <tr
            v-for="index in 4"
            :key="index"
            class="animate-pulse"
          >
            <td
              v-for="header, i in headers"
              :key="header.col + i"
              :class="[header.itemLoadingClass, 'p-1']"
            >
              <slot :header="header" :name="'item-loading-slot-' + header.slotId">
                <div class="h-10 bg-gray-300 rounded" />
              </slot>
            </td>
          </tr>
        </slot>
      </tbody>
      <tbody v-else>
        <slot
          name="body"
          :headers="headers"
          :items="sortedItems"
        >
          <tr
            v-for="item, i in sortedItems"
            :key="item[itemKey] + i"
            :class="[
              'border-b border-line-muted hover:bg-shade-highlighted',
              'focus-visible:bg-shade-highlighted focus-visible:ring-primary focus-visible:ring-1',
            ]"
            tabindex="0"
            data-testid="base-table-result-row"
          >
            <slot name="body-row">
              <td
                v-for="header in displayItemHeaders"
                :key="'item-' + header.col"
                :class="[
                  header.itemClass,
                  'align-top text-neutral pt-5 pb-4 pl-2 first:pl-3',
                  (header.itemColspan && header.itemColspan > 1) ? 'pl-0' : '',
                ]"
                :colspan="header.itemColspan || 1"
                data-testid="base-table-result-row-item"
              >
                <slot
                  :header="header"
                  :item="item"
                  :name="'item-slot-' + header.slotId"
                >
                  <div v-if="!header.itemHidden">
                    <!-- eslint-disable-next-line vue/no-v-html ; Not a user input field -->
                    <span v-if="header.itemFn" v-html="header.itemFn(item)" />
                    <span v-else>{{ item[header.col] }}</span>
                  </div>
                </slot>
              </td>
            </slot>
          </tr>
          <tr v-if="sortedItems?.length === 0">
            <td colspan="12" data-testid="base-table-item-empty">
              <slot name="body-empty">
                <p class="my-[100px] text-center">
                  {{ emptyText }}
                </p>
              </slot>
            </td>
          </tr>
        </slot>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
td,
th {
  min-width: 40px;
  text-align: inherit;
  white-space: normal;
  overflow-wrap: break-word;
}
.table-title {
  text-align: start;
}
.base-table {
  border-spacing: 0px;
  table-layout: fixed;
}
.small-cell {
  min-width: 115px !important;
}
.large-cell {
  min-width: 156px !important;
}
</style>
