/** Return the table headers for the entity table. */
export const getPersonHeadersLimited = (): BaseTableHeader[] => {
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
      width: '18%'
    },
    {
      col: 'entityAddresses',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string | undefined) => filterSearch(['query', 'entityAddresses'], filterVal),
        label: 'Address',
        type: 'text',
        value: undefined
      },
      hasFilter: true,
      hasSort: false,
      slotId: 'address',
      value: 'Address',
      width: '17%'
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
      itemColspan: 5,
      slotId: 'roles',
      value: 'Roles',
      width: '17%'
    },
    {
      col: 'roles',
      hasFilter: false,
      hasSort: false,
      itemColspan: 0,
      itemHidden: true,
      slotId: 'date',
      value: 'Effective Dates',
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
      itemColspan: 0,
      itemHidden: true,
      value: 'Business Details',
      width: '15%'
    },
    {
      col: 'roles',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string | undefined) => (
          filterSearch(['categories', 'roles', 'relatedState'], toRaw(filterVal))),
        label: 'All',
        itemValue: 'value',
        itemsFn: facetItems,
        itemsFnVal: 'relatedState',
        multiple: true,
        type: 'select',
        value: undefined
      },
      hasFilter: true,
      hasSort: false,
      itemColspan: 0,
      itemHidden: true,
      value: 'Business Status',
      width: '11%'
    },
    {
      col: 'roles',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string | undefined) => filterSearch(['query', 'roles', 'relatedEmail'], filterVal),
        label: 'Business Email',
        type: 'text',
        value: undefined
      },
      hasFilter: true,
      hasSort: false,
      itemColspan: 0,
      itemHidden: true,
      value: 'Business Email',
      width: '13%'
    }
  ]
}
