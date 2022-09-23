import { BaseTableFilterI } from './base-table-filter'

export interface BaseTableHeaderI {
  class?: string  // must be accessible in base table (i.e. large-cell pt-3)
  col: string  // item value
  filter?: BaseTableFilterI
  hasFilter: boolean
  hasSort: boolean
  itemClass?: string
  itemFn?: (val: any) => string
  slotId?: string
  value: string  // display text (v-html)
  width?: string
}