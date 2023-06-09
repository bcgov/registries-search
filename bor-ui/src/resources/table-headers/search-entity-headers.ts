import { useSearch } from '@/composables'
import { RoleType } from '@/enums'
import { SearchResultI } from '@/interfaces'
import { BaseTableHeaderI } from '@/interfaces/base-table'
import { toDateStr } from '@/utils'

const { facetItems, filterSearch, highlightMatch } = useSearch()

const capFirstLetter = (val: string) => val.charAt(0).toUpperCase() + val.toLocaleLowerCase().slice(1)

export const SearchEntityHeaders: BaseTableHeaderI[] = [
  {
    col: 'legalName',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch(['query','legalName'], filterVal),
      label: 'Name',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: false,
    itemFn: (val: SearchResultI) => highlightMatch(val.legalName),
    slotId: 'name',
    value: 'Name',
    width: '20%'
  },
  {
    col: 'entityAddresses',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch(['query','entityAddresses'], filterVal),
      label: 'Address',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: false,
    itemFn: (val: SearchResultI) => {
      if (!val.entityAddresses) return 'N/A'
      return `${val.entityAddresses[0].streetAddress}<br>${val.entityAddresses[0].addressCity} ` +
        `${val.entityAddresses[0].addressRegion} ${val.entityAddresses[0].postalCode}` +
        `<br>${val.entityAddresses[0].addressCountry}`
    },
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
      if (val.roles) return capFirstLetter(`${val.roles[0].roleType}`)
      return 'N/A'
    },
    value: 'Roles',
    width: '10%'
  },
  {
    col: 'roles',
    hasFilter: false,
    hasSort: false,
    itemFn: (val: SearchResultI) => {
      if (val.roles && val.roles.length > 0) {
        // only 1 role per item for now
        const roleType = val.roles[0].roleType
        let dates = ''
        for (const i in val.roles[0].roleDates) {
          if (i !== '0') dates += '<br>'
          const start = toDateStr(val.roles[0].roleDates[i].start)
          const end = toDateStr(val.roles[0].roleDates[i].end)
  
          if (roleType === RoleType.INCORPORATOR) {
            dates += start
          } else {
            dates += `${start} To ${end || 'Current'}`  
          }
        }
        return dates
      }
      return 'N/A'
    },
    slotId: 'date',
    value: 'Effective Dates',
    width: '15%'
  },
  {
    col: 'roles',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch(['query','roles', 'value'], filterVal),
      label: 'Business Details',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: false,
    slotId: 'details',
    value: 'Business Details',
    width: '15%'
  },
  {
    col: 'roles',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch(['categories', 'roles', 'relatedState'], filterVal),
      label: 'Business State',
      itemValue: 'value',
      itemsFn: facetItems,
      itemsFnVal: 'relatedState',
      multiple: true,
      type: 'select',
      value: null
    },
    hasFilter: true,
    hasSort: false,
    itemFn: (val: SearchResultI) => {
      if (val.roles) return capFirstLetter(`${val.roles[0].relatedState}`)
      return 'N/A'
    },
    value: 'Business State',
    width: '13%'
  },
  {
    col: '',
    hasFilter: false,
    hasSort: false,
    slotId: 'action',
    value: 'Actions',
    width: '10%'
  }
]
