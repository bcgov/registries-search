/** Return the table headers for the business search table. */
export const getBusinessHeaders = (): BaseTableHeaderI[] => {
  const { filterSearch, highlightMatch } = useBcrosSearch()
  const { t } = useNuxtApp().$i18n

  return [
    {
      col: 'name',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string) => filterSearch(['name'], filterVal),
        label: t('label.table.businessName'),
        type: 'text',
        value: ''
      },
      hasFilter: true,
      hasSort: false,
      slotId: 'name',
      value: t('label.table.businessName'),
      width: '26%'
    },
    {
      col: 'identifier',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string) => filterSearch(['identifier'], filterVal),
        label: t('label.table.businessIdentifier'),
        type: 'text',
        value: ''
      },
      hasFilter: true,
      hasSort: false,
      itemFn: (val: RegSearchResultI) => highlightMatch(val.identifier),
      value: t('label.table.incorpRegNum'),
      width: '15%'
    },
    {
      col: 'bn',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string) => filterSearch(['bn'], filterVal),
        label: t('label.table.bn'),
        type: 'text',
        value: ''
      },
      hasFilter: true,
      hasSort: false,
      itemFn: (val: RegSearchResultI) => highlightMatch(val.bn),
      value: t('label.table.bn'),
      width: '16%'
    },
    {
      col: 'legalType',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string) => filterSearch(['legalType'], getCorpCode(filterVal) || filterVal),
        items: SearchCorpTypes,
        label: t('label.table.businessType'),
        type: 'select',
        value: ''
      },
      hasFilter: true,
      hasSort: false,
      itemFn: (val: RegSearchResultI) => getCorpDescription(val.legalType),
      value: t('label.table.businessType'),
      width: '18%'
    },
    {
      col: 'status',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string) => filterSearch(['status'], filterVal),
        items: [t('label.business.status.active'), t('label.business.status.historical')],
        label: t('label.table.status'),
        type: 'select',
        value: ''
      },
      itemFn: (val: RegSearchResultI) => t(`label.business.status.${val.status.toLowerCase()}`),
      hasFilter: true,
      hasSort: false,
      value: t('label.table.status'),
      width: '12%'
    },
    {
      col: '',
      hasFilter: false,
      hasSort: false,
      slotId: 'action',
      value: t('label.table.actions'),
      width: '13%'
    }
  ]
}
