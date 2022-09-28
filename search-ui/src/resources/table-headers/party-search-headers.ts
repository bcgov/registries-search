import { useSearch } from '@/composables'
import { BaseTableHeaderI } from '@/interfaces/base-table'

const { filterSearch, highlightMatch } = useSearch()

export const PartySearchHeaders: BaseTableHeaderI[] = [
  {
    col: 'partyName',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('partyName', filterVal),
      label: 'Owner Name',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    itemFn: highlightMatch,
    slotId: 'name',
    value: 'Owner Name',
    width: '20%'
  },
  {
    col: 'partyRoles',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('partyRoles', filterVal),
      items: ['Partner', 'Proprietor'],
      label: 'Role',
      type: 'select',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    slotId: 'roles',
    value: 'Role',
    width: '10%'
  },
  {
    col: 'parentName',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('parentName', filterVal),
      label: 'Firm Name',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    value: 'Firm Name',
    width: '14%'
  },
  {
    col: 'parentIdentifier',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('parentIdentifier', filterVal),
      label: 'Firm Number',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    value: 'Firm Registration Number',
    width: '10%'
  },
  {
    col: 'parentBN',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('parentBN', filterVal),
      label: 'CRA Business Number',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    value: 'CRA Business Number',
    width: '14%'
  },
  {
    col: 'parentStatus',
    filter: {
      clearable: true,
      filterApiFn: (filterVal: string) => filterSearch('parentStatus', filterVal),
      items: ['Active', 'Historical'],
      label: 'Status',
      type: 'select',
      value: ''
    },
    itemFn: (val: string) => val.charAt(0) + val.slice(1).toLowerCase(),
    hasFilter: true,
    hasSort: true,
    value: 'Status',
    width: '10%'
  },
  {
    col: '',
    hasFilter: false,
    hasSort: false,
    slotId: 'action',
    value: 'Actions',
    width: '12%'
  }
]