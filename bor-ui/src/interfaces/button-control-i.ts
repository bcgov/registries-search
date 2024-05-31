export interface ButtonControlI {
  action: () => any
  label: string
  class?: string
  color?: string
  icon?: string
  loading?: boolean
  variant?: string
  trailing?: boolean
}
