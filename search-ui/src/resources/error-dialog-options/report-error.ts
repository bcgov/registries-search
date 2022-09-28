import { DialogOptionsI } from '@/interfaces'

export const ReportError: DialogOptionsI = {
  buttons: [{ onClickClose: true, text: 'OK' }],
  text: 'We are currently unable to download this document. Please try again later. ',
  title: 'Unable to download document'
}
