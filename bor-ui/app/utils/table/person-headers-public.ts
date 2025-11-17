// import { getCode, getNames } from 'country-list'

/** Return the table headers for the entity table. */
export const getPersonHeadersPublic = (): BaseTableHeader[] => {
  const { facetItems, filterSearch, highlightMatch } = useSearchStore()

  return [
    {
      col: 'legalName',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string | undefined) => filterSearch(['query', 'legalName'], filterVal),
        label: 'Name',
        type: 'text',
        value: undefined
      },
      hasFilter: true,
      hasSort: false,
      itemFn: (val: SearchResult) => highlightMatch(val.legalName),
      slotId: 'name',
      value: 'Name',
      width: '34%'
    },
    // will be added back in once SIs are added
    // {
    //   col: 'nationalities',
    //   filter: {
    //     clearable: true,
    //     disabled: true,
    //     filterApiFn: (filterVal: string | undefined) => filterSearch(
    //       ['categories', 'nationalities'], filterVal ? [getCode(filterVal)] : null),
    //     hasSelectedSlot: true,
    //     itemValue: 'value',
    //     items: ['Canada', 'United States of America'].concat(
    //       (getNames()).filter(country => !['Canada', 'United States of America'].includes(country))),
    //     label: 'All',
    //     type: 'select',
    //     value: null
    //   },
    //   hasFilter: true,
    //   hasSort: false,
    //   value: 'Citizenship',
    //   slotId: 'citizenship',
    //   width: '15%'
    // },
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
      itemColspan: 2,
      itemHidden: false,
      slotId: 'details',
      subCol: 'value',
      value: 'Business Details',
      width: '33%'
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
      value: 'Roles',
      width: '33%'
    }
  ]
}
