export interface DialogButtonI {
  // define other colours in vuetify plugin bcgov theme if needed
  class?: string
  color?: 'primary' | 'error' | 'success' | 'darkBlue'
  onClick?: (...args: any[]) => any
  onClickArgs?: any[]
  onClickClose: boolean
  outlined?: boolean
  slotId?: string
  text: string
}