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
  text: 'The Business Search application is currently unavailable. Please try again later.',
  title: 'Business Search Unavailable'
}
