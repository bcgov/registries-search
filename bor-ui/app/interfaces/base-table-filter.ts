export interface BaseTableFilter {
  clearable: boolean
  disabled?: boolean
  hasItemSlot?: boolean
  hasSelectedSlot?: boolean
  itemValue?: string
  items?: any[]
  itemsFn?: (val: string | undefined) => any
  itemsFnVal?: string
  filterApiFn?: (val: any) => Promise<void>
  filterFn?: (colVal: any, filterVal: any) => boolean
  label?: string
  multiple?: boolean
  type: 'select' | 'text'
  value: string | undefined
}
