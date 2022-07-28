export interface BaseTableFilterI {
  clearable: boolean
  items?: string[]
  filterApiFn?: (val: string) => Promise<void>
  filterFn?: (colVal: any, filterVal: string) => boolean
  type: 'select' | 'text'
  value: string
}