import { BaseSelectFilter } from '@/components/datatable/resources'
import { useEntity } from '@/composables'
import { ColinStateTypes } from '@/enums'
import { BaseTableHeaderI } from '@/interfaces/base-table'

const { corpStatusTypes } = useEntity()

export const PartySearchHeaders: BaseTableHeaderI[] = [
  {
    col: '',
    customItemSlot: 'icon',
    hasFilter: false,
    hasSort: false,
    value: '',
    width: '1%'
  },
  {
    col: 'partyName',
    filter: { clearable: true, type: 'text', value: '' },
    hasFilter: true,
    hasSort: true,
    value: 'Owner Name',
    width: '19%'
  },
  {
    col: 'partyRoles',
    customItemSlot: 'roles',
    filter: {
      clearable: true,
      filterFn: (colVal: any[], filterVal: string) => {
        if (filterVal === '') return true
        return (colVal.map((role) => role.toUpperCase()).includes(filterVal.toUpperCase()))
      },
      items: ['Partner', 'Proprietor'],
      type: 'select',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    value: 'Role',
    width: '10%'
  },
  {
    col: 'parentIdentifier',
    filter: { clearable: true, type: 'text', value: '' },
    hasFilter: true,
    hasSort: true,
    value: 'Firm Number',
    width: '10%'
  },
  {
    col: 'parentName',
    filter: { clearable: true, type: 'text', value: '' },
    hasFilter: true,
    hasSort: true,
    value: 'Firm Name',
    width: '10%'
  },
  {
    col: 'parentBN',
    filter: { clearable: true, type: 'text', value: '' },
    hasFilter: true,
    hasSort: true,
    value: 'CRA Business Number',
    width: '10%'
  },
  {
    col: 'parentStatus',
    filter: {
      clearable: true,
      filterFn: (colVal: string, filterVal: string) => {
        if (['ACTIVE','HISTORICAL','LIQUIDATION'].includes(colVal)) return BaseSelectFilter(colVal, filterVal)
        return BaseSelectFilter(ColinStateTypes[colVal], filterVal)
      },
      items: corpStatusTypes.value.sort(),
      type: 'select',
      value: ''
    },
    itemFn: (val: string) => {
      if (['ACTIVE','HISTORICAL','LIQUIDATION'].includes(val)) return val.charAt(0) + val.slice(1).toLowerCase()
      return ColinStateTypes[val]
    },
    hasFilter: true,
    hasSort: true,
    value: 'Status',
    width: '15%'
  },
  {
    col: '',
    customHeaderSlot: 'button',
    customItemSlot: 'button',
    hasFilter: false,
    hasSort: false,
    value: '',
    width: '15%'
  }
]