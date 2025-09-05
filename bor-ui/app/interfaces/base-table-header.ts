export interface BaseTableHeader {
  class?: string // must be accessible in base table (i.e. large-cell pt-3)
  col: string // item value
  filter?: BaseTableFilter
  hasFilter: boolean
  hasSort: boolean
  itemClass?: string
  itemColspan?: number
  itemHidden?: boolean
  itemLoadingClass?: string
  itemFn?: (val: any) => string
  slotId?: string
  value: string // display text (v-html)
  width?: string
}
