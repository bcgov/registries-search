import { getCode, getNames } from 'country-list'

/** Return the table headers for the entity table. */
export const getPersonHeadersPublic = (): BaseTableHeaderI[] => {
  const { facetItems, filterSearch, highlightMatch } = useBcrosSearch()

  return [
    {
      col: 'legalName',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string) => filterSearch(['query', 'legalName'], filterVal),
        label: 'Name',
        type: 'text',
        value: ''
      },
      hasFilter: true,
      hasSort: false,
      itemFn: (val: SearchResultI) => highlightMatch(val.legalName),
      slotId: 'name',
      value: 'Name',
      width: '33%'
    },
    {
      col: 'nationalities',
      filter: {
        clearable: true,
        disabled: true,
        filterApiFn: (filterVal: string) => filterSearch(
          ['categories', 'nationalities'], filterVal ? [getCode(filterVal)] : null),
        hasSelectedSlot: true,
        itemValue: 'value',
        items: ['Canada', 'United States of America'].concat(
          (getNames()).filter(country => !['Canada', 'United States of America'].includes(country))),
        label: 'All',
        type: 'select',
        value: null
      },
      hasFilter: true,
      hasSort: false,
      value: 'Citizenship',
      slotId: 'citizenship',
      width: '15%'
    },
    {
      col: 'roles',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string) => filterSearch(['query', 'roles', 'value'], filterVal),
        label: 'Business Details',
        type: 'text',
        value: ''
      },
      hasFilter: true,
      hasSort: false,
      itemColspan: 2,
      itemHidden: false,
      slotId: 'details',
      value: 'Business Details',
      width: '32%'
    },
    {
      col: 'roles',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string[]) => {
          return filterSearch(['categories', 'roles', 'roleType'], filterVal)
        },
        label: 'All',
        itemValue: 'value',
        itemsFn: facetItems,
        itemsFnVal: 'roleType',
        multiple: true,
        type: 'select',
        value: []
      },
      hasFilter: true,
      hasSort: false,
      itemColspan: 0,
      itemHidden: true,
      value: 'Roles',
      width: '20%'
    }
  ]
}
