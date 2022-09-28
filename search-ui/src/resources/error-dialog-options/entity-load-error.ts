// local
import { DialogOptionsI } from '@/interfaces'
import { navigate } from '@/utils'

export const EntityLoadError: DialogOptionsI = {
  buttons: [{ onClick: navigate, onClickArgs: [sessionStorage.getItem('BASE_URL')], onClickClose: true, text: 'OK' }],
  onClose: navigate,
  onCloseArgs: [sessionStorage.getItem('BASE_URL')],
  text: 'The Business Search application is currently unable to ' +
    'load the dashboard for this business. Please try again later.',
  title: 'Business Dashboard unavailable'
}
