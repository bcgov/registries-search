import { DialogOptionsI } from '@/interfaces'
import { navigate } from '@/utils'

export const AuthAccessError: DialogOptionsI = {
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
  text: '',
  title: 'Business Search Access Denied'
}
