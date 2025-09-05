import { BaseTextFilter } from '~/utils/table/base-filters'

/** Return the table headers for the document history table. */
export const getDocHistoryHeaders = (): BaseTableHeader[] => {
  const { t } = useNuxtApp().$i18n

  return [
    {
      col: 'businessName',
      filter: { clearable: true, label: t('label.businessName'), type: 'text', value: undefined },
      hasFilter: true,
      hasSort: false,
      slotId: 'name',
      value: t('label.businessName'),
      width: '25%'
    },
    {
      class: 'pl-7',
      col: 'businessIdentifier',
      filter: { clearable: true, label: t('label.number'), type: 'text', value: undefined },
      hasFilter: true,
      hasSort: false,
      itemClass: 'pl-7 small-cell',
      value: t('label.number'),
      width: '14%'
    },
    {
      col: 'documents',
      filter: {
        clearable: true,
        filterFn: (colVal: Doc[], filterVal: string) => {
          if (filterVal === '') {
            return true
          }
          return colVal.map(item => t(`docAccess.${item.documentType}`)).includes(filterVal)
        },
        items: Object.keys(DocAccessType).map(item => t(`docAccess.${item}`)),
        label: t('label.documentType'),
        type: 'select',
        value: undefined
      },
      hasFilter: true,
      hasSort: false,
      slotId: 'documents',
      value: t('label.purchasedItems'),
      width: '17%'
    },
    {
      col: 'submissionDate',
      filter: {
        clearable: true,
        filterFn: (colVal: string, filterVal: string) => BaseTextFilter(apiToPacificDateTime(colVal), filterVal),
        label: t('label.dateTime'),
        type: 'text',
        value: undefined
      },
      hasFilter: true,
      hasSort: false,
      itemFn: (val: DocAccess) => apiToPacificDateTime(val.submissionDate) || '',
      value: t('label.purchasedDate'),
      width: '17%'
    },
    {
      col: 'submitter',
      filter: { clearable: true, label: t('label.userName'), type: 'text', value: undefined },
      hasFilter: true,
      hasSort: false,
      value: t('label.userName'),
      width: '14%'
    },
    {
      col: '',
      hasFilter: false,
      hasSort: false,
      slotId: 'action',
      value: t('label.actions'),
      width: '15%'
    }
  ]
}
