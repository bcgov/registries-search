import { DialogButtonI } from './dialog-button'

export interface DialogOptionsI {
  buttons: DialogButtonI[]
  onClose?: (...args: any[]) => any
  onCloseArgs?: any[]
  text: string
  textExtra?: string[]
  title: string
}
