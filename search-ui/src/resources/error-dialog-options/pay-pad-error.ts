import { DialogOptionsI } from '@/interfaces'

export const PayPadError: DialogOptionsI = {
  buttons: [{ onClickClose: true, text: 'OK' }],
  text: 'The payment could not be completed for the following reason:',
  textExtra: [
    'Your account is in the 3-day PAD confirmation period. You ' +
    'will be able to do transactions only after the period is over.'],
  title: 'Payment Incomplete'
}
