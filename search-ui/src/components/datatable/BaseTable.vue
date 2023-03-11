<template>
  <v-container class="container pa-0 ma-0" :style="[{ height: height || '540px' }, { overflow: overflow || 'scroll' }]">
    <table class="base-table">
      <thead class="base-table__header">
        <slot name="header" :headers="headers">
          <tr v-if="title || pagination" :style="{ 'background-color': titleBg }">
            <slot name="header-title" :headers="headers">
              <th v-if="title" class="base-table__title" :colspan="pagination ? headers.length / 2 : headers.length">
                <slot name="title">
                  <h2 class="ml-3 py-6">
                    {{ title }}
                    <span class="ml-1" v-if="loading">
                      <v-progress-circular color="primary" indeterminate size="22" />
                    </span>
                    <span v-else-if="totalItems && resultsDescription" style="font-weight: normal">
                      ({{ totalItems }} {{ resultsDescription }})
                    </span>
                    <span v-else-if="totalItems" style="font-weight: normal">({{ totalItems }})</span>
                  </h2>
                </slot>
                <slot name="subtitle">
                  <h4 class="ml-3 mb-6" v-if="subtitle">{{ subtitle }}</h4>
                </slot>
              </th>
              <th v-if="pagination" :colspan="title? headers.length / 2 : headers.length">
                <slot name="pagination">
                  <BasePagination />
                </slot>
              </th>
            </slot>
          </tr>
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
                    :style="!header.col ? 'pointer-events: none;': ''"
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
                :class="[header.class, 'base-table__header__item pb-5']"
                :width="header.width"
              >
                <slot :name="'header-filter-slot-' + header.slotId" :header="header">
                  <v-select
                    v-if="header.hasFilter && header.filter.type === 'select'"
                    :class="[filterClass, 'base-table__header__item__filter']"
                    density="compact"
                    hide-details
                    :items="header.filter.items"
                    :label="!header.filter.value ? header.filter.label || '' : ''"
                    :open-on-clear="true"
                    v-model="header.filter.value"
                    @update:modelValue="filter(header)"
                  />
                  <v-text-field
                    v-else-if="header.hasFilter && header.filter.type === 'text'"
                    :class="[filterClass, 'base-table__header__item__filter', header.filter.value ? 'active' : '']"
                    density="compact"
                    hide-details
                    :placeholder="!header.filter.value ? header.filter.label || '' : ''"
                    v-model="header.filter.value"
                    @update:modelValue="filter(header)"
                  />
                  <v-btn
                    v-if="header.hasFilter && header.filter.value && header.filter.clearable"
                    class="base-table__header__item__clear-btn"
                    :class="header.filter.type === 'text' ? 'header-text-field' : 'header-select'"
                    icon
                    @click="header.filter.value=''; filter(header)"
                  >
                    <v-icon color="primary" size="20">mdi-close</v-icon>
                  </v-btn>
                </slot>
              </th>
            </tr>
          </slot>
        </slot>
      </thead>
      <tbody v-if="loading && !filtering" class="base-table__body">
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
        <tr v-if="filtering">
          <td :colspan="headers.length">
            <v-progress-linear color="primary" indeterminate />
          </td>
        </tr>
        <slot name="body" :headers="headers" :items="sortedItems">
          <tr v-for="item, i in sortedItems" :key="item[itemKey] + i" class="base-table__body__row" :tabindex="i + 1">
            <slot name="body-row">
              <td
                v-for="header in headers" :key="'item-' + header.col"
                :class="[header.itemClass, 'base-table__body__item']"
              >
                <slot :header="header" :item="item" :name="'item-slot-' + header.slotId">
                  <span v-if="header.itemFn" v-html="header.itemFn(item[header.col])" />
                  <span v-else>{{ item[header.col] }}</span>
                </slot>
              </td>
            </slot>
          </tr>
          <tr v-if="setItems.length === 0" class="base-table__body__empty">
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
  </v-container>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import _ from 'lodash'
// local
import { BaseTableColorsI, BaseTableHeaderI } from '@/interfaces/base-table'
import { BaseSelectFilter, BaseTextFilter } from './resources'
import { BasePagination } from './slot-templates'

const props = defineProps<{
  colors?: BaseTableColorsI,
  filterClass?: string,
  height?: string,
  itemKey: string,
  loading?: boolean,
  noResultsText?: string,
  pagination?: boolean,
  overflow?: string,
  resetFilters?: boolean,
  resetOnItemChange?: boolean,
  resultsDescription?: string,
  setHeaders: BaseTableHeaderI[],
  setItems: any[],
  title?: string
  totalItems?: number
  subtitle?: string
}>()

const emit = defineEmits<{
  (e: 'filterActive', value: boolean): void
  (e: 'resetFilters', value: boolean): void
}>()

const headers = reactive(_.cloneDeep(props.setHeaders) as BaseTableHeaderI[])
const sortedItems = ref([...props.setItems])

const emptyText = computed(() => props.noResultsText || 'No results found')
const filtering = ref(false)
const filterActive = computed(() => {
  for (const i in headers) if (headers[i].filter?.value) return true
  return false
})
const headerBg = computed(() => props.colors?.backgrounds?.header || 'white')
const titleBg = computed(() => props.colors?.backgrounds?.title || '#e0e7ed')

const sortBy = ref('')
const sortDirection = ref('desc')
const sortIcon = computed(() => {
  if (sortDirection.value === 'desc') return 'mdi-chevron-down'
  return 'mdi-chevron-up'
})

const resetAll = () => {
  // reset sort
  sortBy.value = ''
  sortDirection.value = 'desc'
  // reset filters
  for (const i in headers) {
    if (headers[i]?.filter?.value) headers[i].filter.value = ''
  }
}

const sort = (itemFn: (val: any) => string) => {
  const compareFn = (item1: object, item2: object) => {
    let val1 = item1[sortBy.value] || ''
    let val2 = item2[sortBy.value] || ''
    if (itemFn) {
      val1 = itemFn(val1)
      val2 = itemFn(val2)
    }
    if (sortDirection.value === 'asc') return val1.localeCompare(val2)
    return val2.localeCompare(val1)
  }
  sortedItems.value = sortedItems.value.sort(compareFn)
}

const toggleSort = (header: BaseTableHeaderI) => {
  if (!header.hasSort) return
  if (sortBy.value === header.col) sortDirection.value = sortDirection.value === 'desc' ? 'asc' : 'desc'
  else {
    sortBy.value = header.col
    sortDirection.value = 'desc'
  }
  sort(header.itemFn)
}

const filter = _.debounce(async (header: BaseTableHeaderI) => {
  // rely on custom filterApiFn to alter result set if given (meant for server side filtering)
  if (header.filter.filterApiFn) {
    filtering.value = true
    await header.filter.filterApiFn(header.filter.value)
    filtering.value = false
  } else {
    // client side custom or base filter
    sortedItems.value = props.setItems.filter((item) => {
      if (header.filter.filterFn) return header.filter.filterFn(item[header.col], header.filter.value)
      else {
        if (header.filter.type === 'select') return BaseSelectFilter(item[header.col], header.filter.value)
        else return BaseTextFilter(item[header.col], header.filter.value)
      }
    })
  }
  // clear sort
  sortBy.value = ''
  sortDirection.value = 'desc'
}, 500)

watch(() => filterActive.value, (val) => {
  emit('filterActive', val)
})

watch(() => props.resetFilters, (val) => {
  if (val) {
    let usedFilter = null
    for (const i in headers) {
      if (headers[i]?.filter?.value) {
        usedFilter = i
        headers[i].filter.value = ''
      }
    }
    if (usedFilter !== null) filter(headers[usedFilter])
    emit('resetFilters', true)
  }
})

watch(() => props.setItems, () => {
  sortedItems.value = [...props.setItems]
  if (props.resetOnItemChange) resetAll()
}, { deep: true })
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
td,
th {
  min-width: 40px;
  max-width: 40px;
  text-align: inherit;
  white-space: normal;
}
.base-table {
  border-spacing: 0px;
  width: calc(100%);
  table-layout: auto;

  &__title {
    text-align: start;
  }

  &__pagination {

    &__btn {
      background-color: transparent;
      box-shadow: none;
    }
  }

  &__header {
    position: sticky;
    top: 0;
    z-index: 1000;

    &__item {
      border-bottom: 1px solid $gray4;
      padding: 20px 0 0 12px;
      position: relative;

      &__clear-btn {
        background-color: transparent;
        bottom: 37%;
        box-shadow: none;
        height: 25px;
        position: absolute;
        width: 25px;
      }
      &__clear-btn.header-select {
        right: 25px;
      }
      &__clear-btn.header-text-field {
        right: 10px;
      }

      &__filter {
        :deep(.v-input__control .v-field .v-field__field .v-label.v-field-label) {
          font-size: 14px;
          margin: 11px 0 0 8px;
          max-width: none;
        }
        :deep(.v-input__control .v-field .v-field__field .v-label.v-field-label.v-field-label--floating) {
          color: $gray7;
          font-size: 14px;
          top: 0 !important;
        }
      }

      &__filter.v-input--dirty {
        :deep(.v-input__control .v-field--active.v-field--dirty .v-field__overlay) {
          background-color: $blueSelected;
          opacity: 1;
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
        font-size: 0.875rem;
        font-weight: 700;
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
    }

    &__row:focus-visible {
      background-color: #EBEEF0;
      outline: none;
    }

    &__row:hover {
      background-color: $blueSelected !important;
      transition: linear 0.5s;
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
