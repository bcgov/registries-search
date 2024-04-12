<template>
  <div class="container" :style="[{ height: height || '540px' }, { overflow: overflow || 'scroll' }]">
    <div v-if="title" class="table-title" :style="{ 'background-color': titleBg }">
      <slot name="table-title" :headers="headers">
        <v-row no-gutters>
          <v-col v-if="title" cols="auto">
            <slot name="title">
              <h2 class="ml-3 py-6">
                {{ title }}
                <span v-if="loading" class="ml-1">
                  <v-progress-circular color="primary" indeterminate size="22" />
                </span>
                <span v-else-if="resultsDescription" style="font-weight: normal">
                  ({{ resultsDescription }})
                </span>
                <span v-else-if="totalItems" style="font-weight: normal">({{ totalItems }})</span>
              </h2>
            </slot>
            <slot name="subtitle">
              <h4 v-if="subtitle" class="ml-3 mb-6">
                {{ subtitle }}
              </h4>
            </slot>
          </v-col>
          <v-col v-if="titleExtras">
            <slot name="title-extras" />
          </v-col>
        </v-row>
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
                :class="[header.class, 'base-table__header__item']"
                :style="!header.col ? 'text-align: center;' : ''"
                :width="header.width"
              >
                <slot :name="'header-item-slot-' + header.slotId" :header="header">
                  <v-btn
                    v-if="header.value"
                    class="base-table__header__item__title mb-5"
                    :class="!header.col ? 'mx-auto': ''"
                    :ripple="false"
                    :style="!header.hasSort || !header.col ? 'pointer-events: none;': ''"
                    @click="toggleSort(header)"
                  >
                    <span v-html="header.value" />
                    <v-icon v-if="sortBy && sortBy === header.col" class="ml-1">
                      {{ sortIcon }}
                    </v-icon>
                  </v-btn>
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
                :width="header.width"
              >
                <slot :name="'header-filter-slot-' + header.slotId" :header="header">
                  <div class="pb-5">
                    <v-select
                      v-if="header.hasFilter && header.filter.type === 'select'"
                      v-model="header.filter.value"
                      :class="[filterClass, 'base-table__header__item__filter']"
                      clear-icon="mdi-close"
                      density="compact"
                      hide-details
                      hide-no-data
                      :items="header.filter.items || header.filter.itemsFn(header.filter.itemsFnVal)"
                      :item-title="header.filter.itemValue || ''"
                      :item-value="header.filter.itemValue || ''"
                      :label="!header.filter.value ? header.filter.label || '' : ''"
                      :multiple="(header.filter.multiple as any)"
                      :open-on-clear="true"
                      @update:model-value="filter(header)"
                    >
                      <template v-if="header.filter.hasSelectedSlot" #selection="{ item }">
                        <slot :name="'header-filter-selected-slot-' + header.slotId" :item="item" />
                      </template>
                      <template v-else #selection="{ item, index }">
                        <span v-if="index == 0" style="font-size: 0.825rem;">
                          <span v-if="header.filter.value.length == 1">
                            {{ capFirstLetter(item.title) }}
                          </span>
                          <span v-else>
                            Multiple
                          </span>
                        </span>
                      </template>
                      <template v-if="header.filter.hasItemSlot" #item="{ props, item }">
                        <slot :name="'header-filter-item-slot-' + header.slotId" :item="item" :props="props" />
                      </template>
                    </v-select>
                    <v-text-field
                      v-else-if="header.hasFilter && header.filter.type === 'text'"
                      v-model="header.filter.value"
                      :class="[filterClass, 'base-table__header__item__filter', header.filter.value ? 'active' : '']"
                      density="compact"
                      hide-details
                      :placeholder="!header.filter.value ? header.filter.label || '' : ''"
                      @update:model-value="filter(header)"
                    />
                    <BaseTableFilterClearButton
                      v-if="header.hasFilter && header.filter.value && header.filter.clearable"
                      :right="header.filter.type === 'text' ? '10px' : '25px'"
                      @click="header.filter.value=header.filter.type === 'text' ? '' : null; filter(header)"
                    />
                  </div>
                </slot>
              </th>
            </tr>
          </slot>
        </slot>
      </thead>
      <tbody v-if="loading && !isFilteringActive" class="base-table__body">
        <tr class="base-table__body__loader">
          <td :colspan="headers.length">
            <v-row class="my-15" justify="center" no-gutters>
              <v-col cols="auto">
                <v-progress-circular color="primary" size="50" indeterminate />
              </v-col>
            </v-row>
          </td>
        </tr>
      </tbody>
      <tbody v-else class="base-table__body">
        <tr v-if="isFilteringActive">
          <td :colspan="headers.length">
            <v-progress-linear color="primary" indeterminate />
          </td>
        </tr>
        <slot name="body" :headers="headers" :items="sortedItems">
          <tr v-for="item, i in sortedItems" :key="item[itemKey] + i" class="base-table__body__row" :tabindex="i + 1">
            <slot name="body-row">
              <td
                v-for="header in headers"
                :key="'item-' + header.col"
                :class="[header.itemClass, 'base-table__body__row__item']"
              >
                <slot :header="header" :item="item" :name="'item-slot-' + header.slotId">
                  <span v-if="header.itemFn" v-html="header.itemFn(item)" />
                  <span v-else>{{ item[header.col] }}</span>
                </slot>
              </td>
            </slot>
          </tr>
          <tr v-if="sortedItems.length === 0" class="base-table__body__empty">
            <td colspan="12">
              <slot name="body-empty">
                <v-row class="my-15" justify="center" no-gutters>
                  <v-col cols="auto">
                    <p class="ma-0" v-html="emptyText" />
                  </v-col>
                </v-row>
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

const sortedItems = ref([...localProps.setItems])

const emptyText = computed(() => localProps.noResultsText || 'No results found')
const isFilteringActive = ref(false)

const headerBg = computed(() => localProps.colors?.backgrounds?.header || 'white')
const titleBg = computed(() => localProps.colors?.backgrounds?.title || '#e0e7ed')

const sortBy = ref('')
const sortDirection = ref('desc')
const sortIcon = computed(() => {
  if (sortDirection.value === 'desc') { return 'mdi-chevron-down' }
  return 'mdi-chevron-up'
})

const capFirstLetter = (val: string) => val.charAt(0).toUpperCase() + val.toLocaleLowerCase().slice(1)

const resettingFilters = ref(false)
const resetAll = () => {
  resettingFilters.value = true
  // reset sort
  sortBy.value = ''
  sortDirection.value = 'desc'
  // reset filters
  for (const i in headers) {
    if (headers[i]?.filter?.value) { headers[i].filter.value = null }
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

const filter = _.debounce(async (header: BaseTableHeaderI) => {
  if (resettingFilters.value) { return }
  // rely on custom filterApiFn to alter result set if given (meant for server side isFilteringActive)
  if (header.filter.value?.length === 0) {
    header.filter.value = null
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
@import '@/assets/styles/theme.scss';
td,
th {
  min-width: 40px;
  text-align: inherit;
  white-space: normal;
}
.table-title {
  text-align: start;
  position: sticky;
  left: 0;
}
.base-table {
  border-spacing: 0px;
  table-layout: auto;

  &__header {
    position: sticky;
    top: 0;
    z-index: 1000;

    &__item {
      background-color: white;
      border-bottom: 1px solid $gray4;
      padding: 20px 0 0 12px;
      position: relative;

      &__filter {
        :deep(.v-input__control .v-field .v-field__field .v-label.v-field-label) {
          font-size: 14px;
          margin: 3px 0 0 8px;
          max-width: none;
        }
        :deep(.v-input__control .v-field .v-field__field .v-label.v-field-label.v-field-label--floating) {
          color: $gray7;
          font-size: 14px;
          margin: 11px 0 0 8px;
          top: 0 !important;
          --v-field-label-scale: 1;
        }
        :deep(.v-label.v-field-label) {
          transform: none;
          transform-origin: none;
          transition: none;
        }
      }

      &__filter.v-input--dirty {
        :deep(.v-input__control .v-field--active.v-field--dirty .v-field__overlay) {
          background-color: $blueSelected !important;
        }
        :deep(.v-input__control .v-field--active.v-field--dirty .v-field__input .v-select__selection) {
          margin-bottom: 10px;
        }
      }

      &__title,
      &__title::after,
      &__title::before,
      &__title:hover {
        background-color: transparent;
        box-shadow: none;
        color: $gray9;
        font-size: 0.875rem !important;
        font-weight: 700 !important;
        justify-content: start;
        padding: 0;
        text-align: start;
      }

      &__title :deep(.v-btn__content) {
        align-self: end;
      }
    }
  }

  &__body {

    &__empty {

      td {
        color: $gray7;
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
          background-color: $blueSelected !important;
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
        border-bottom: 1px solid $gray3;
        color: $gray7 !important;
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
      background-color: $blueSelected !important;
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
:deep(.v-btn__content) {
  display: block;
  white-space: normal;
}
:deep(.v-btn__overlay),
:deep(.v-btn__overlay::before),
:deep(.v-btn__overlay::after) {
  background-color: transparent !important;
}
:deep(.v-field__input) {
  align-items: end;
  flex-wrap: nowrap;
  font-size: 0.875rem;
}
:deep(.v-text-field .v-field__input) {
  padding: 0 0 0 8px;
}
:deep(.v-field__append-inner) {
  margin: auto;
  padding: 0;
}
:deep(.v-list-item-header) {
  background-color: black !important;
  padding: 20px;
}
</style>
