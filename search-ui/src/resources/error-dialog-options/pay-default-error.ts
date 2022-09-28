import { DialogOptionsI } from '@/interfaces'

export const PayDefaultError: DialogOptionsI = {
  buttons: [{ onClickClose: true, text: 'OK' }],
  text: 'Payment could not be completed.',
  title: 'Payment Incomplete'
}
