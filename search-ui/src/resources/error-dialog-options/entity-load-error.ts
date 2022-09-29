// local
import { DialogOptionsI } from '@/interfaces'
import { navigate } from '@/utils'

export const EntityLoadError: DialogOptionsI = {
  buttons: [{
    onClick: navigate, onClickArgs: [sessionStorage.getItem('BASE_URL')],
    onClickClose: true, text: 'Return to Business Search'
  }],
  hideClose: true,
  text: 'The Business Search application is currently unable to ' +
    'load the information for this business. Please try again later.',
  title: 'Business Information Unavailable'
}
