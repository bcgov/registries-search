/** Return the table headers for the business search table. */
export const getBusinessHeaders = (): BaseTableHeader[] => {
  const { filterSearch, highlightMatch } = useSearchStore()
  const { t } = useNuxtApp().$i18n
  const ldarkly = useConnectLaunchDarkly()
  const columns: BaseTableHeader[] = [
    {
      col: 'name',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string | undefined) => filterSearch(['query', 'name'], filterVal),
        label: t('label.businessName'),
        type: 'text',
        value: undefined
      },
      hasFilter: true,
      hasSort: false,
      slotId: 'name',
      value: t('label.businessName'),
      width: '26%'
    },
    {
      col: 'identifier',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string | undefined) => filterSearch(['query', 'identifier'], filterVal),
        label: t('label.number'),
        type: 'text',
        value: undefined
      },
      hasFilter: true,
      hasSort: false,
      itemFn: (val: BusinessSearchResult) => highlightMatch(val.identifier),
      value: t('label.incorpRegNum'),
      width: '15%'
    },
    {
      col: 'bn',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string | undefined) => filterSearch(['query', 'bn'], filterVal),
        label: t('label.businessNum'),
        type: 'text',
        value: undefined
      },
      hasFilter: true,
      hasSort: false,
      itemFn: (val: BusinessSearchResult) => highlightMatch(val.bn),
      value: t('label.businessNum'),
      width: '16%'
    },
    {
      col: 'legalType',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string | undefined) => (
          filterSearch(['categories', 'legalType'], filterVal ? [filterVal] : [])),
        items: SearchCorpTypes,
        label: t('label.businessType'),
        type: 'select',
        value: undefined
      },
      hasFilter: true,
      hasSort: false,
      itemFn: (val: BusinessSearchResult) => getCorpDescription(val.legalType),
      value: t('label.businessType'),
      width: '18%'
    },
    {
      col: 'status',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string | undefined) => filterSearch(
          ['categories', 'status'], filterVal ? [filterVal.toUpperCase()] : []),
        items: [t('status.active'), t('status.historical')],
        label: t('label.status'),
        type: 'select',
        value: undefined
      },
      itemFn: (val: BusinessSearchResult) => t(`status.${val.status.toLowerCase()}`),
      hasFilter: true,
      hasSort: false,
      value: t('label.status'),
      width: '12%'
    }
  ]

  if (ldarkly.getStoredFlag('enable-business-si-column')) {
    columns.push({
      col: 'Significant Individuals',
      filter: {
        clearable: true,
        filterApiFn: (filterVal: string | undefined) => filterSearch(['query', 'parties', 'partyName'], filterVal),
        label: t('label.significantIndividuals'),
        type: 'text',
        value: undefined
      },
      hasFilter: true,
      hasSort: false,
      slotId: 'significant-individuals',
      value: t('label.significantIndividuals'),
      width: '15%'
    })
  }

  columns.push({
    col: '',
    filter: undefined,
    hasFilter: false,
    hasSort: false,
    slotId: 'action',
    value: t('label.actions'),
    width: '13%'
  })

  return columns
}
