import { DialogOptionsI } from '@/interfaces'

export const PayBcolError: DialogOptionsI = {
  buttons: [{ onClickClose: true, text: 'OK' }],
  text: 'The payment could not be completed for the following reason:',
  title: 'Payment Incomplete'
}
