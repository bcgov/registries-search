import { DialogOptionsI } from '@/interfaces'
import { navigate } from '@/utils'

export const DefaultError: DialogOptionsI = {
  buttons: [
    {
      onClick: navigate,
      onClickArgs: [sessionStorage.getItem('REGISTRY_URL')],
      onClickClose: true,
      text: 'OK'
    }
  ],
  onClose: navigate,
  onCloseArgs: [sessionStorage.getItem('REGISTRY_URL')],
  text: 'The Director Search application is currently unavailable. Please try again later.',
  title: 'Director Search Unavailable'
}
