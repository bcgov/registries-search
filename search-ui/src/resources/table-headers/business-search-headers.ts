import { useEntity, useSearch } from '@/composables'
import { BaseTableHeaderI } from '@/interfaces/base-table'

const { corpTypes, getEntityCode, getEntityDescription } = useEntity()
const { filterSearch, highlightMatch } = useSearch()

export const BusinessSearchHeaders: BaseTableHeaderI[] = [
  {
    col: '',
    customItemSlot: 'icon',
    hasFilter: false,
    hasSort: false,
    value: '',
    width: '1%'
  },
  {
    col: 'name',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('name', filterVal),
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    itemFn: highlightMatch,
    value: 'Business Name',
    width: '25%'
  },
  {
    col: 'identifier',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('identifier', filterVal),
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    itemFn: highlightMatch,
    value: 'Incorporation/<br />Registration',
    width: '10%'
  },
  {
    col: 'bn',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('bn', filterVal),
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    itemFn: highlightMatch,
    value: 'CRA Business Number',
    width: '15%'
  },
  {
    col: 'legalType',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('legalType', getEntityCode(filterVal)),
      items: corpTypes.value.sort(),
      type: 'select',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    itemFn: getEntityDescription,
    value: 'Type',
    width: '20%'
  },
  {
    col: 'status',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('status', filterVal),
      items: ['Active', 'Historical'],
      type: 'select',
      value: ''
    },
    itemFn: (val: string) => val.charAt(0) + val.slice(1).toLowerCase(),
    hasFilter: true,
    hasSort: true,
    value: 'Status',
    width: '17%'
  },
  {
    col: '',
    customHeaderSlot: 'button',
    customItemSlot: 'button',
    hasFilter: false,
    hasSort: false,
    value: '',
    width: '12%'
  }
]
