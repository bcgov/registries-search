export interface BaseTableFilterI {
  clearable: boolean
  items?: string[]
  filterApiFn?: (val: string) => Promise<void>
  filterFn?: (colVal: any, filterVal: string) => boolean
  label?: string
  type: 'select' | 'text'
  value: string
}