export interface BaseTableFilterI {
  clearable: boolean
  itemValue?: string
  items?: any[]
  itemsFn?: (val: string) => any
  itemsFnVal?: string
  filterApiFn?: (val: any) => Promise<void>
  filterFn?: (colVal: any, filterVal: any) => boolean
  label?: string
  multiple?: boolean
  type: 'select' | 'text'
  value: string
}
