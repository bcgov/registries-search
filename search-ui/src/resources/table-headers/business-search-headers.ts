import { useEntity, useSearch } from '@/composables'
import { CorpTypeCd } from '@/enums'
import { BaseTableHeaderI } from '@/interfaces/base-table'

const { corpTypes, getEntityDescription } = useEntity()
const { highlightMatch } = useSearch()

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
    filter: { clearable: true, type: 'text', value: '' },
    hasFilter: true,
    hasSort: true,
    itemFn: highlightMatch,
    value: 'Business Name',
    width: '25%'
  },
  {
    col: 'identifier',
    filter: { clearable: true, type: 'text', value: '' },
    hasFilter: true,
    hasSort: true,
    itemFn: highlightMatch,
    value: 'Incorporation/<br />Registration',
    width: '10%'
  },
  {
    col: 'bn',
    filter: { clearable: true, type: 'text', value: '' },
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
      filterFn: (val: CorpTypeCd, filter: string) => {
        return getEntityDescription(val).toUpperCase() === filter.toUpperCase() || filter === ''
      },
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
