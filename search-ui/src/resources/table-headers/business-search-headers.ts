import { useEntity, useSearch } from '@/composables'
import { BaseTableHeaderI } from '@/interfaces/base-table'
import { SearchCorpTypes } from '@/resources'

const { getEntityCode, getEntityDescription } = useEntity()
const { filterSearch, highlightMatch } = useSearch()

export const BusinessSearchHeaders: BaseTableHeaderI[] = [
  {
    col: 'name',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('name', filterVal),
      label: 'Business Name',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    itemFn: highlightMatch,
    slotId: 'name',
    value: 'Business Name',
    width: '26%'
  },
  {
    col: 'identifier',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('identifier', filterVal),
      label: 'Number',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    itemFn: highlightMatch,
    value: 'Incorporation/<br />Registration Number',
    width: '15%'
  },
  {
    col: 'bn',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('bn', filterVal),
      label: 'CRA Business Number',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    itemFn: highlightMatch,
    value: 'CRA Business Number',
    width: '16%'
  },
  {
    col: 'legalType',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('legalType', getEntityCode(filterVal) || filterVal),
      items: SearchCorpTypes,
      label: 'Business Type',
      type: 'select',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    itemFn: getEntityDescription,
    value: 'Business Type',
    width: '18%'
  },
  {
    col: 'status',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('status', filterVal),
      items: ['Active', 'Historical'],
      label: 'Status',
      type: 'select',
      value: ''
    },
    itemFn: (val: string) => val.charAt(0) + val.slice(1).toLowerCase(),
    hasFilter: true,
    hasSort: true,
    value: 'Status',
    width: '12%'
  },
  {
    col: '',
    hasFilter: false,
    hasSort: false,
    slotId: 'action',
    value: 'Actions',
    width: '13%'
  }
]
