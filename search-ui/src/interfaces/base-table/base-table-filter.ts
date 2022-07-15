export interface BaseTableFilterI {
  clearable: boolean
  items?: string[]
  filterFn?: (colVal: any, filterVal: string) => boolean
  type: 'select' | 'text'
  value: string
}