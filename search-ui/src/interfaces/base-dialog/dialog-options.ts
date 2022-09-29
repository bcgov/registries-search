import { DialogButtonI } from './dialog-button'

export interface DialogOptionsI {
  buttons: DialogButtonI[]
  hideClose?: boolean
  onClose?: (...args: any[]) => any
  onCloseArgs?: any[]
  text: string
  textExtra?: string[]
  title: string
}
