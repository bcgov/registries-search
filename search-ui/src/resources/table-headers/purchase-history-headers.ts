import { BaseTextFilter } from '@/components/datatable/resources'
import { useDatetime } from '@/composables'
import { BaseTableHeaderI } from '@/interfaces/base-table'
import { DocumentTypeDescriptions } from '@/resources'

const { dateTimeString } = useDatetime()

export const PurchaseHistoryHeaders: BaseTableHeaderI[] = [
  {
    col: 'businessName',
    filter: { clearable: true, label: 'Business Name', type: 'text', value: '' },
    hasFilter: true,
    hasSort: true,
    slotId: 'name',
    value: 'Business Name',
    width: '20%'
  },
  {
    class: 'pl-7',
    col: 'businessIdentifier',
    filter: { clearable: true, label: 'Number', type: 'text', value: '' },
    hasFilter: true,
    hasSort: true,
    itemClass: 'pl-7 small-cell',
    value: 'Incorporation/<br />Registration Number',
    width: '14%'
  },
  {
    col: 'documents',
    filter: {
      clearable: true,
      filterFn: (colVal: any[], filterVal: string) => {
        if (filterVal === '') return true
        return colVal.map((item) => DocumentTypeDescriptions[item.documentType]).includes(filterVal)
      },
      items: Object.values(DocumentTypeDescriptions),
      label: 'Document Type',
      type: 'select',
      value: ''
    },
    hasFilter: true,
    hasSort: false,
    slotId: 'documents',
    value: 'Purchased Items',
    width: '15%'
  },
  {
    col: 'submissionDate',
    filter: {
      clearable: true,
      filterFn: (colVal: string, filterVal: string) => BaseTextFilter(dateTimeString(colVal), filterVal),
      label: 'Date/Time',
      type: 'text',
      value: ''
    },
    hasFilter: true,
    hasSort: true,
    itemFn: dateTimeString,
    value: 'Search Date/Time<br />(Pacific time)',
    width: '17%'
  },
  // {
  //   col: 'expiryDate',
  //   filter: {
  //     clearable: true,
  //     filterFn: (colVal: string, filterVal: string) => BaseTextFilter(dateTimeString(colVal), filterVal),
  //     type: 'text',
  //     value: ''
  //   },
  //   hasFilter: true,
  //   hasSort: true,
  //   itemFn: dateTimeString,
  //   value: 'Expiry Date/Time<br />(Pacific time)',
  //   width: '17%'
  // },
  {
    col: 'submitter',
    filter: { clearable: true, label: 'User Name', type: 'text', value: '' },
    hasFilter: true,
    hasSort: true,
    value: 'User Name',
    width: '12%'
  },
  {
    col: '',
    itemClass: 'large-cell',
    hasFilter: false,
    hasSort: false,
    slotId: 'action',
    value: 'Actions',
    width: '12%'
  }
]