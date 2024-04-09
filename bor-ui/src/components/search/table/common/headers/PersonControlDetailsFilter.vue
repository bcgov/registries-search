<template>
  <v-menu
    :close-on-content-click="false"
  >
    <template #activator="{ isActive, props }">
      <div class="pb-5 cursor-pointer" data-cy="details-filter">
        <v-text-field
          v-model="detailsFilterDisplay"
          density="compact"
          hide-details
          v-bind="props"
          :append-inner-icon="isActive ? 'mdi-menu-up' : 'mdi-menu-down' "
          placeholder="Details"
          data-cy="details-filter-textbox"
          :class="['filterClass', 'base-table__header__item__filter', detailsFilterDisplay!='' ? 'active' : '']"
        />
        <v-btn
          v-if="detailsFilterDisplay!=''"
          class="base-table__header__item__clear-btn header-select"
          icon
          @click="selectedDetailsFilters=[]"
        >
          <v-icon color="primary" size="20">
            mdi-close
          </v-icon>
        </v-btn>
      </div>
    </template>
    <v-expansion-panels
      variant="accordion"
      multiple

    >
      <v-expansion-panel data-cy="details-filter-shares-votes" class="w-52 max-w-52">
        <v-expansion-panel-title class="font-bold">
          Control of Shares/Votes
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Registered Owner"
            :value="PersonControlTypeE.SharesOrVotesRegisteredOwner"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-200 hover:text-blue-700"
            data-cy="details-filter-shares-votes-registered-owner"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Beneficial Owner"
            :value="PersonControlTypeE.SharesOrVotesBeneficialOwner"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-700"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Indirect Control"
            :value="PersonControlTypeE.SharesOrVotesIndirectControl"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-700"
          />
        </v-expansion-panel-text>
      </v-expansion-panel>

      <v-expansion-panel data-cy="details-filter-directors" class="w-52 max-w-52">
        <v-expansion-panel-title class="font-bold">
          Control of Directors
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Indirect Control of directors"
            :value="PersonControlTypeE.DirectorsIndirectControl"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-700"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Direct Control"
            :value="PersonControlTypeE.DirectorsDirectControl"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-700"
            data-cy="details-filter-directors-direct-control"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Control Majority of Directors"
            :value="PersonControlTypeE.DirectorsInConcertControl"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-700"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Significant Influence Control"
            :value="PersonControlTypeE.DirectorsSignificantInfluence"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-700"
          />
        </v-expansion-panel-text>
      </v-expansion-panel>
      <v-expansion-panel data-cy="details-filter-other" class="w-52 max-w-52">
        <v-expansion-panel-title class="font-bold">
          Other
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Other"
            value="other"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-700"
            data-cy="details-filter-other-other"
          />
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-menu>
</template>

<script setup lang="ts">
const search = useBcrosSearch()
const selectedDetailsFilters: Ref<string[]> = ref([])

// for clear filters
const localProps = defineProps<{ clearFilter?: boolean }>()
watch(() => localProps.clearFilter, () => {
  selectedDetailsFilters.value = []
})

const detailsFilterDisplay = computed(() => {
  if (selectedDetailsFilters.value.length === 0) {
    return ''
  }

  if (selectedDetailsFilters.value.length === 1) {
    let icon = convertDetailsToIcon(selectedDetailsFilters.value[0])
    if (!icon) {
      icon = OtherControlIcon
    }
    return icon.displayName
  }

  return 'Multiple'
})

watch(selectedDetailsFilters, (newList: string[], oldList: string[]) => {
  if (oldList.length === 0 && newList.length === 0) {
    return
  }
  search.filterSearch(['query', 'roles', 'relatedInterests'], selectedDetailsFilters.value)
})

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
:deep .v-expansion-panel-text__wrapper {
  padding: 0;
}
</style>
