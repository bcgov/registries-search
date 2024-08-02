import { BaseTextFilter } from '@/components/base/table/resources/base-filters'

/** Return the table headers for the document history table. */
export const getDocHistoryHeaders = (): BaseTableHeaderI[] => {
  const { t } = useNuxtApp().$i18n

  return [
    {
      col: 'businessName',
      filter: { clearable: true, label: t('label.table.businessName'), type: 'text', value: '' },
      hasFilter: true,
      hasSort: false,
      slotId: 'name',
      value: t('label.table.businessName'),
      width: '25%'
    },
    {
      class: 'pl-7',
      col: 'businessIdentifier',
      filter: { clearable: true, label: t('label.table.businessIdentifier'), type: 'text', value: '' },
      hasFilter: true,
      hasSort: false,
      itemClass: 'pl-7 small-cell',
      value: t('label.table.businessIdentifier'),
      width: '14%'
    },
    {
      col: 'documents',
      filter: {
        clearable: true,
        filterFn: (colVal: DocI[], filterVal: string) => {
          if (filterVal === '') {
            return true
          }
          return colVal.map(item => t(`label.docAccess.${item.documentType}`)).includes(filterVal)
        },
        items: Object.keys(DocAccessTypeE).map(item => t(`label.docAccess.${item}`)),
        label: t('label.table.documentType'),
        type: 'select',
        value: ''
      },
      hasFilter: true,
      hasSort: false,
      slotId: 'documents',
      value: t('label.table.purchasedItems'),
      width: '17%'
    },
    {
      col: 'submissionDate',
      filter: {
        clearable: true,
        filterFn: (colVal: string, filterVal: string) => BaseTextFilter(apiToPacificDateTime(colVal), filterVal),
        label: t('label.table.dateTime'),
        type: 'text',
        value: ''
      },
      hasFilter: true,
      hasSort: false,
      itemFn: (val: DocAccessI) => apiToPacificDateTime(val.submissionDate),
      value: t('label.table.purchasedDate'),
      width: '17%'
    },
    {
      col: 'submitter',
      filter: { clearable: true, label: t('label.table.userName'), type: 'text', value: '' },
      hasFilter: true,
      hasSort: false,
      value: t('label.table.userName'),
      width: '14%'
    },
    {
      col: '',
      hasFilter: false,
      hasSort: false,
      slotId: 'action',
      value: t('label.table.actions'),
      width: '15%'
    }
  ]
}
