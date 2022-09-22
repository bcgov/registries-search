import { DialogButtonI } from './dialog-button'

export interface DialogOptionsI {
  buttons: DialogButtonI[]
  text: string
  textExtra?: string[]
  title: string
}
