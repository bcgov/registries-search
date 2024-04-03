/** Return the table headers for the entity table. */
export const getPersonHeadersExtended = (): BaseTableHeaderI[] => {
  const { facetItems, filterSearch, highlightMatch } = useBcrosSearch()
  const capFirstLetter = (val: string) => val.charAt(0).toUpperCase() + val.toLocaleLowerCase().slice(1)

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
      width: '17%'
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
      value: 'Information',
      slotId: 'information',
      width: '18%'
    },
    {
      col: 'nationalities',
      hasFilter: false,
      hasSort: false,
      value: 'Citizenship',
      slotId: 'citizenship',
      width: '7%'
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
      itemFn: (val: SearchResultI) => {
        if (val.roles) { return capFirstLetter(`${val.roles[0].roleType}`) }
        return 'N/A'
      },
      value: 'Roles',
      width: '11%'
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
      slotId: 'details',
      value: 'Business Details',
      width: '17%'
    },
    {
      col: 'roles',
      hasFilter: false,
      hasSort: false,
      // eslint-disable-next-line
      itemFn: (val: SearchResultI) => 'TBD dd',
      slotId: 'personControl',
      value: 'Details',
      width: '17%'
    },
    {
      class: 'effective-date-header',
      col: 'roles',
      hasFilter: false,
      hasSort: false,
      itemFn: (val: SearchResultI) => {
        if (val.roles && val.roles.length > 0) {
          // only 1 role per item for now
          const roleType = val.roles[0].roleType
          let dates = ''
          for (const i in val.roles[0].roleDates) {
            if (i !== '0') { dates += '<br>' }
            const start = toDateStr(val.roles[0].roleDates[i].start)
            const end = toDateStr(val.roles[0].roleDates[i].end as Date)

            if (roleType === RoleTypeE.INCORPORATOR) {
              dates += start
            } else {
              dates += `${start || 'Unknown'} To ${end || 'Current'}`
            }
          }
          return dates
        }
        return 'N/A'
      },
      slotId: 'date',
      value: 'Effective Dates',
      width: '14%'
    },
    {
      class: 'actions-col',
      col: '',
      hasFilter: false,
      hasSort: false,
      itemClass: 'actions-col',
      slotId: 'actions',
      value: 'Actions'
    }
  ]
}
