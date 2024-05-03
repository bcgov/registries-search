import { getCode, getNames } from 'country-list'

/** Return the table headers for the entity table. */
export const getPersonHeadersExtended = (): BaseTableHeaderI[] => {
  const { facetItems, filterSearch, highlightMatch } = useBcrosSearch()

  return [
    {
      col: 'legalName',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string) => filterSearch(['query', 'name'], filterVal),
        label: 'Name',
        type: 'text',
        value: ''
      },
      hasFilter: true,
      hasSort: false,
      itemFn: (val: SearchResultI) => highlightMatch(val.legalName),
      slotId: 'name',
      value: 'Name',
      width: '17%'
    },
    {
      col: 'entityAddresses',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string) => filterSearch(['query', 'info'], filterVal),
        label: 'Info',
        type: 'text',
        value: ''
      },
      hasFilter: true,
      hasSort: false,
      value: 'Information',
      slotId: 'information',
      width: '16%'
    },
    {
      col: 'nationalities',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string) => filterSearch(
          ['categories', 'nationalities'], filterVal ? [getCode(filterVal)] : null),
        hasSelectedSlot: true,
        itemValue: 'value',
        items: ['Canada', 'United States of America'].concat(
          (getNames()).filter(country => !['Canada', 'United States of America'].includes(country))),
        label: 'Country',
        type: 'select',
        value: null
      },
      hasFilter: true,
      hasSort: false,
      value: 'Citizenship',
      slotId: 'citizenship',
      width: '9%'
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
      itemColspan: 4,
      itemHidden: false,
      slotId: 'details',
      value: 'Business Details',
      width: '14%'
    },
    {
      col: 'roles',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string[]) => {
          return filterSearch(['categories', 'roles', 'roleType'], filterVal)
        },
        label: 'Roles',
        itemValue: 'value',
        itemsFn: facetItems,
        itemsFnVal: 'roleType',
        multiple: true,
        type: 'select',
        value: null
      },
      hasFilter: true,
      hasSort: false,
      itemColspan: 0,
      itemHidden: true,
      itemFn: (val: SearchResultI) => {
        if (val.roles) { return capFirstLetter(`${val.roles[0].roleType}`) }
        return 'N/A'
      },
      slotId: 'roles',
      value: 'Roles',
      width: '16%'
    },
    {
      col: 'roles',
      hasFilter: false,
      hasSort: false,
      itemColspan: 0,
      itemHidden: true,
      slotId: 'personControl',
      value: 'Details',
      width: '16%'
    },
    {
      class: 'effective-date-header',
      col: 'roles',
      hasFilter: false,
      hasSort: false,
      itemColspan: 0,
      itemHidden: true,
      slotId: 'date',
      value: 'Effective Dates',
      width: '11%'
    }
    // NOTE: to be added back in after details page flow is figured out
    // {
    //   class: 'actions-col',
    //   col: '',
    //   hasFilter: false,
    //   hasSort: false,
    //   itemClass: 'actions-col',
    //   itemLoadingClass: 'actions-col',
    //   slotId: 'actions',
    //   value: 'Actions'
    // }
  ]
}

export const capFirstLetter = (val: string) => {
  return val.charAt(0).toUpperCase() + val.toLocaleLowerCase().slice(1)
}
