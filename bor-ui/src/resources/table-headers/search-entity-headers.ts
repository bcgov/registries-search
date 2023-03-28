import { useSearch } from '@/composables'
import { SearchResultI } from '@/interfaces'
import { BaseTableHeaderI } from '@/interfaces/base-table'

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
    itemFn: highlightMatch,
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
      return `${val.entityAddresses[0].streetAddress}<br/>${val.entityAddresses[0].addressCity} ` +
        `${val.entityAddresses[0].addressRegion} ${val.entityAddresses[0].postalCode}` +
        `<br/>${val.entityAddresses[0].addressCountry}`
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
      if (val.roles) {
        let dates = ''
        for (const i in val.roles[0].roleDates) {
          if (i !== '0') dates += '<br/>'
          dates += `${val.roles[0].roleDates[i].start} To ${val.roles[0].roleDates[i].end || 'Current'}`  
        }
        return dates
      }
      return 'N/A'
    },
    value: 'Effective Dates',
    width: '15%'
  },
  {
    col: 'roles',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch(['query','roles', 'relatedName'], filterVal),
      label: 'Business Name',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: false,
    itemFn: (val: SearchResultI) => {
      if (val.roles) return `<u>${val.roles[0].relatedName}</u>` +
        `<br/>${val.roles[0].relatedIdentifier}<br/>${val.roles[0].relatedBN || ''}`
      return 'N/A'
    },
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
      value: ''
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
