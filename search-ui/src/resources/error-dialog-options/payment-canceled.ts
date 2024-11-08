import { DialogOptionsI } from '@/interfaces'

export const PaymentCancelledError: DialogOptionsI = {
  buttons: [{ onClickClose: true, text: 'OK' }],
  text: 'Your payment has been cancelled. No charges have been applied to your credit card.',
  title: 'Payment Cancelled'
}
