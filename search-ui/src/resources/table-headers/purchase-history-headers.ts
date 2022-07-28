import { BaseTextFilter } from '@/components/datatable/resources'
import { useDatetime } from '@/composables'
import { BaseTableHeaderI } from '@/interfaces/base-table'
import { DocumentTypeDescriptions } from '@/resources'

const { dateTimeString } = useDatetime()

export const PurchaseHistoryHeaders: BaseTableHeaderI[] = [
  {
    class: 'pl-7',
    col: 'businessIdentifier',
    filter: { clearable: true, type: 'text', value: '' },
    hasFilter: true,
    hasSort: true,
    itemClass: 'pl-7 small-cell',
    value: 'Incorporation/<br />Registration Number',
    width: '10%'
  },
  {
    col: 'businessName',
    filter: { clearable: true, type: 'text', value: '' },
    hasFilter: true,
    hasSort: true,
    value: 'Business Name',
    width: '15%'
  },
  {
    col: 'documents',
    customItemSlot: 'documents',
    filter: {
      clearable: true,
      filterFn: (colVal: any[], filterVal: string) => {
        if (filterVal === '') return true
        return colVal.map((item) => DocumentTypeDescriptions[item.documentType]).includes(filterVal)
      },
      items:['Business Summary', 'Certificate of Good Standing'],
      type: 'select',
      value: ''
    },
    hasFilter: true,
    hasSort: false,
    value: 'Purchased Items',
    width: '19%'
  },
  {
    col: 'submissionDate',
    filter: {
      clearable: true,
      filterFn: (colVal: string, filterVal: string) => BaseTextFilter(dateTimeString(colVal), filterVal),
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    itemFn: dateTimeString,
    value: 'Search Date/Time<br />(Pacific time)',
    width: '17%'
  },
  {
    col: 'expiryDate',
    filter: {
      clearable: true,
      filterFn: (colVal: string, filterVal: string) => BaseTextFilter(dateTimeString(colVal), filterVal),
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    itemFn: dateTimeString,
    value: 'Expiry Date/Time<br />(Pacific time)',
    width: '17%'
  },
  {
    col: 'submitter',
    customHeaderSlot: '',
    customItemSlot: '',
    filter: { clearable: true, type: 'text', value: '' },
    hasFilter: true,
    hasSort: true,
    value: 'User Name',
    width: '10%'
  },
  {
    col: '',
    customItemSlot: 'button',
    itemClass: 'large-cell',
    hasFilter: false,
    hasSort: false,
    value: '',
    width: '12%'
  }
]