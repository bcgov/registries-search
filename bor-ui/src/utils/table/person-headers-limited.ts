/** Return the table headers for the entity table. */
export const getPersonHeadersLimited = (): BaseTableHeaderI[] => {
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
      width: '18%'
    },
    {
      col: 'entityAddresses',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string) => filterSearch(['query', 'entityAddresses'], filterVal),
        label: 'Address',
        type: 'text',
        value: ''
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
        filterApiFn: (filterVal: string) => filterSearch(['query', 'roles', 'value'], filterVal),
        label: 'Business Details',
        type: 'text',
        value: ''
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
        filterApiFn: (filterVal: string) => filterSearch(['categories', 'roles', 'relatedState'], filterVal),
        label: 'All',
        itemValue: 'value',
        itemsFn: facetItems,
        itemsFnVal: 'relatedState',
        multiple: true,
        type: 'select',
        value: []
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
        filterApiFn: (filterVal: string) => filterSearch(['query', 'roles', 'relatedEmail'], filterVal),
        label: 'Business Email',
        type: 'text',
        value: ''
      },
      hasFilter: true,
      hasSort: false,
      itemColspan: 0,
      itemHidden: true,
      value: 'Business Email',
      width: '13%'
    }
    // {
    //   col: '',
    //   hasFilter: false,
    //   hasSort: false,
    //   slotId: 'actions',
    //   value: '',
    //   width: '10%'
    // }
  ]
}
