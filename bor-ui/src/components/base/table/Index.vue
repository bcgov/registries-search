<template>
  <div :style="[{ height: height || '540px' }, { overflow: overflow || 'scroll' }]">
    <div v-if="title" class="table-title" :style="{ 'background-color': titleBg }">
      <slot name="table-title" :headers="headers">
        <div class="flex">
          <CommonTitle
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
    <table class="base-table" :style="{ width: tableWidth ? tableWidth : '100%'}">
      <thead class="base-table__header">
        <slot name="header" :headers="headers">
          <slot name="header-item-titles" :headers="headers">
            <tr :style="{ 'background-color': headerBg }">
              <th
                v-for="header, i in headers"
                :key="header.col + i"
                :class="[header.class, 'base-table__header__item', 'align-bottom']"
                :style="[!header.col ? 'text-align: center;' : '', `width: ${header.width}`]"
              >
                <slot :name="'header-item-slot-' + header.slotId" :header="header">
                  <UButton
                    v-if="header.value"
                    class="base-table__header__item__title mb-5 font-bold text-justify"
                    color="gray"
                    :class="!header.col ? 'mx-auto': ''"
                    :label="header.value"
                    :style="!header.hasSort || !header.col ? 'pointer-events: none;': ''"
                    variant="ghost"
                    @click="toggleSort(header)"
                  />
                </slot>
              </th>
            </tr>
          </slot>
          <slot name="header-item-filters" :headers="headers">
            <tr :style="{ 'background-color': headerBg }">
              <th
                v-for="header, i in headers"
                :key="header.col + i"
                :class="[header.class, 'base-table__header__item']"
                :style="{ width: header.width }"
              >
                <slot :name="'header-filter-slot-' + header.slotId" :header="header">
                  <div class="pb-5 font-normal">
                    <USelectMenu
                      v-if="header.hasFilter && header.filter.type === 'select'"
                      v-model="header.filter.value"
                      :class="[filterClass, 'base-table__header__item__filter']"
                      :options="(header.filter.items || header.filter.itemsFn(header.filter.itemsFnVal))"
                      :option-attribute="header.filter.itemValue || ''"
                      :value-attribute="header.filter.itemValue || ''"
                      :color="header.filter.value?.length ? 'primary' : 'gray'"
                      :placeholder="header.filter.label"
                      :popper="{placement: 'bottom-start'}"
                      :disabled="header.filter.disabled"
                      :multiple="!!header.filter.multiple"
                      size="sm"
                      @update:model-value="filter(header)"
                    >
                      <template #label>
                        <div class="flex text-sm">
                          <div class="grow">
                            <slot
                              :name="'header-filter-selected-slot-' + header.slotId"
                              :selected="header.filter.value"
                            >
                              <span v-if="!header.filter.value || header.filter?.value.length === 0">
                                {{ header.filter.label }}
                              </span>
                              <span v-else-if="header.filter?.value.length == 1">
                                {{ capFirstLetter(header.filter.value[0]) }}
                              </span>
                              <span v-else>
                                Multiple
                              </span>
                            </slot>
                          </div>
                          <UButton
                            v-show="header.filter.value?.length"
                            color="primary"
                            variant="link"
                            icon="i-heroicons-x-mark-20-solid"
                            :padded="false"
                            @click="clearFilter(header)"
                          />
                        </div>
                      </template>
                      <template v-if="header.filter.hasItemSlot" #option="{ option, selected }">
                        <slot :name="'header-filter-item-slot-' + header.slotId" :item="option" :selected="selected" />
                      </template>
                    </USelectMenu>
                    <UInput
                      v-else-if="header.hasFilter && header.filter.type === 'text'"
                      v-model="header.filter.value"
                      :class="[filterClass, 'base-table__header__item__filter']"
                      autocomplete="off"
                      :color="header.filter.value ? 'primary' : 'gray'"
                      :disabled="header.filter.disabled"
                      :placeholder="!header.filter.value ? header.filter.label || '' : ''"
                      size="sm"
                      :ui="{ icon: { trailing: { pointer: '' }}}"
                      @update:model-value="filter(header)"
                    >
                      <template #trailing>
                        <UButton
                          v-show="header.filter.value !== ''"
                          color="primary"
                          variant="link"
                          icon="i-heroicons-x-mark-20-solid"
                          :padded="false"
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
      <tbody v-if="loading" class="base-table__body">
        <slot name="loading" :headers="headers">
          <tr v-for="index in 4" :key="index" class="base-table__body__row animate-pulse">
            <td
              v-for="header, i in headers"
              :key="header.col + i"
              :class="[header.itemLoadingClass, 'base-table__body__row__item']"
            >
              <slot :header="header" :name="'item-loading-slot-' + header.slotId">
                <div class="h-10 bg-gray-300 rounded" />
              </slot>
            </td>
          </tr>
        </slot>
      </tbody>
      <tbody v-else class="base-table__body">
        <slot name="body" :headers="headers" :items="sortedItems">
          <tr v-for="item, i in sortedItems" :key="item[itemKey] + i" class="base-table__body__row" :tabindex="i + 1">
            <slot name="body-row">
              <td
                v-for="header in displayItemHeaders"
                :key="'item-' + header.col"
                :class="[
                  header.itemClass,
                  'base-table__body__row__item',
                  (header.itemColspan && header.itemColspan > 1) ? 'pl-0' : ''
                ]"
                :colspan="header.itemColspan || 1"
              >
                <slot :header="header" :item="item" :name="'item-slot-' + header.slotId">
                  <div v-if="!header.itemHidden">
                    <span v-if="header.itemFn" v-html="header.itemFn(item)" />
                    <span v-else>{{ item[header.col] }}</span>
                  </div>
                </slot>
              </td>
            </slot>
          </tr>
          <tr v-if="sortedItems?.length === 0" class="base-table__body__empty">
            <td colspan="12">
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

<script setup lang="ts">
import _ from 'lodash'
// local
import { CommonTitle } from './common'
import { BaseSelectFilter, BaseTextFilter } from './resources'

const localProps = defineProps<{
  colors?: BaseTableColorsI,
  filterClass?: string,
  height?: string,
  itemKey: string,
  loading?: boolean,
  noResultsText?: string,
  pagination?: boolean,
  overflow?: string,
  resetFiltersTrigger?: boolean,
  resetOnItemChange?: boolean,
  resultsDescription?: string,
  setHeaders: BaseTableHeaderI[],
  setItems: any[],
  tableWidth?: string,
  title?: string
  titleExtras?: boolean
  totalItems?: number
  subtitle?: string
}>()

const emit = defineEmits<{(e: 'filterActive', value: boolean): void }>()

const headers = reactive(_.cloneDeep(localProps.setHeaders) as BaseTableHeaderI[])
const displayItemHeaders = headers?.filter(header => !header.itemHidden)
const sortedItems = ref([...localProps.setItems])

const emptyText = computed(() => localProps.noResultsText || 'No results found')
const isFilteringActive = ref(false)

const headerBg = computed(() => localProps.colors?.backgrounds?.header || 'white')
const titleBg = computed(() => localProps.colors?.backgrounds?.title || '#e0e7ed')

const sortBy = ref('')
const sortDirection = ref('desc')
// TODO: ticket TBD - will be used when bringing in business search history table
// const sortIcon = computed(() => {
//   if (sortDirection.value === 'desc') { return 'mdi-chevron-down' }
//   return 'mdi-chevron-up'
// })

const resettingFilters = ref(false)
const resetAll = () => {
  resettingFilters.value = true
  // reset sort
  sortBy.value = ''
  sortDirection.value = 'desc'
  // reset filters
  for (const i in headers) {
    if (headers[i]?.filter?.value) {
      headers[i].filter.value = null
    }
  }
  resettingFilters.value = false
}
watch(() => localProps.resetFiltersTrigger, () => { resetAll() })

const sort = (itemFn: (val: any) => string) => {
  const compareFn = (item1: object, item2: object) => {
    let val1 = item1[sortBy.value] || ''
    let val2 = item2[sortBy.value] || ''
    if (itemFn) {
      val1 = itemFn(val1)
      val2 = itemFn(val2)
    }
    if (sortDirection.value === 'asc') { return val1.localeCompare(val2) }
    return val2.localeCompare(val1)
  }
  sortedItems.value = sortedItems.value.sort(compareFn)
}

const toggleSort = (header: BaseTableHeaderI) => {
  if (!header.hasSort) { return }
  if (sortBy.value === header.col) { sortDirection.value = sortDirection.value === 'desc' ? 'asc' : 'desc' } else {
    sortBy.value = header.col
    sortDirection.value = 'desc'
  }
  sort(header.itemFn)
}

const filterActive = computed(() => {
  for (const i in headers) { if (headers[i].filter?.value) { return true } }
  return false
})
watch(() => filterActive.value, (val) => { emit('filterActive', val) })

const clearFilter = (header: BaseTableHeaderI) => {
  if (header.filter?.multiple) {
    header.filter.value = []
  } else if (header.filter.type === 'select') {
    header.filter.value = null
  } else {
    header.filter.value = ''
  }
  filter(header)
}
const filter = _.debounce(async (header: BaseTableHeaderI) => {
  if (resettingFilters.value) { return }
  // rely on custom filterApiFn to alter result set if given (meant for server side isFilteringActive)
  if (!header.filter.value || header.filter.value.length === 0) {
    header.filter.value = header.filter.multiple ? [] : header.filter.type === 'select' ? null : ''
  }
  if (header.filter.filterApiFn) {
    isFilteringActive.value = true
    await header.filter.filterApiFn(header.filter.value)
    isFilteringActive.value = false
  } else {
    // client side custom or base filter
    sortedItems.value = localProps.setItems.filter((item) => {
      if (header.filter.filterFn) {
        return header.filter.filterFn(item[header.col], header.filter.value)
      } else if (header.filter.type === 'select') {
        return BaseSelectFilter(item[header.col], header.filter.value)
      } else {
        return BaseTextFilter(item[header.col], header.filter.value)
      }
    })
  }
  // clear sort
  sortBy.value = ''
  sortDirection.value = 'desc'
}, 500)

watch(() => localProps.setItems, (val) => {
  if (val) { sortedItems.value = [...val] } else { sortedItems.value = [] }

  if (localProps.resetOnItemChange) { resetAll() }
}, { deep: true })
</script>

<style lang="scss" scoped>
td,
th {
  min-width: 40px;
  text-align: inherit;
  white-space: normal;
  overflow-wrap: break-word;
}
.table-title {
  text-align: start;
  position: sticky;
  z-index: 99;
  left: 0;
}
.base-table {
  border-spacing: 0px;
  table-layout: fixed;

  &__header {
    position: sticky;
    top: 0;
    z-index: 98;

    &__item {
      background-color: white;
      border-bottom: 1px solid theme('colors.bcGovGray.400');
      padding: 20px 0 0 12px;
      position: relative;

      &___title,
      &___title::after,
      &___title::before,
      &___title:hover {
        background-color: transparent;
        box-shadow: none;
        color: theme('colors.bcGovGray.900');
        font-size: 0.875rem !important;
        font-weight: 700 !important;
        justify-content: start;
        padding: 0;
        text-align: start;
      }
    }
  }

  &__body {

    &__empty {

      td {
        color: theme('colors.bcGovGray.700');
      }
    }

    &__row {
      background-color: white;
      transition: linear 0.5s;

      &:focus-visible {
        background-color: #EBEEF0;
        outline: none;
      }

      &:hover {

        .base-table__body__row__item {
          background-color: theme('colors.blue.50') !important;
          transition: linear 0.5s;
        }
      }

      &:not(:hover) {

        .base-table__body__row__item {
          background-color: white;
          transition: linear 0.5s;
        }
      }

      &__item {
        border-bottom: 1px solid theme('colors.bcGovGray.300');
        color: theme('colors.bcGovGray.700') !important;
        font-size: 0.875rem !important;
        height: 40px;
        margin: 8px 0 0 0;
        padding: 26px 0 16px 12px;
        position: relative;
        vertical-align: top;
      }
    }

    &__row:focus-visible {
      background-color: #EBEEF0;
      outline: none;
    }

    &__row:hover {
      background-color: theme('colors.blue.50') !important;
      transition: linear 0.5s;
    }
  }
}
// preset optional itemClasses
.small-cell {
  min-width: 115px !important;
}
.large-cell {
  min-width: 156px !important;
}
</style>
