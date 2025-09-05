import { getCode, getNames } from 'country-list'

/** Return the table headers for the entity table. */
export const getPersonHeadersExtended = (): BaseTableHeader[] => {
  const { facetItems, filterSearch, highlightMatch } = useSearchStore()

  return [
    {
      col: 'legalName',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string | undefined) => filterSearch(['query', 'name'], filterVal),
        label: 'Name',
        type: 'text',
        value: undefined
      },
      hasFilter: true,
      hasSort: false,
      itemFn: (val: SearchResult) => highlightMatch(val.legalName),
      slotId: 'name',
      value: 'Name',
      width: '17%'
    },
    {
      col: 'entityAddresses',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string | undefined) => filterSearch(['query', 'info'], filterVal),
        label: 'Info',
        type: 'text',
        value: undefined
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
        filterApiFn: (filterVal: string | undefined) => filterSearch(
          ['categories', 'nationalities'], filterVal ? [getCode(filterVal)] : null),
        hasSelectedSlot: true,
        items: ['Canada', 'United States of America'].concat(
          (getNames()).filter(country => !['Canada', 'United States of America'].includes(country))),
        label: 'All',
        type: 'select',
        value: undefined
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
        filterApiFn: (filterVal: string | undefined) => filterSearch(['query', 'roles', 'value'], filterVal),
        label: 'Business Details',
        type: 'text',
        value: undefined
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
        filterApiFn: (filterVal: string[] | undefined) => {
          return filterSearch(['categories', 'roles', 'roleType'], toRaw(filterVal))
        },
        label: 'All',
        itemValue: 'value',
        itemsFn: facetItems,
        itemsFnVal: 'roleType',
        multiple: true,
        type: 'select',
        value: undefined
      },
      hasFilter: true,
      hasSort: false,
      itemColspan: 0,
      itemHidden: true,
      itemFn: (val: SearchResult) => {
        if (val.roles && val.roles[0]) {
          return capFirstLetter(`${val.roles[0].roleType}`)
        }
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
