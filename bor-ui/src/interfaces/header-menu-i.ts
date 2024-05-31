export interface HeaderMenuItemI {
  label: string,
  action?: () => any
  args?: any
  icon?: string
  setActive?: boolean
}

export interface HeaderMenuOptionsI {
  header?: string,
  items?: HeaderMenuItemI[]
}
