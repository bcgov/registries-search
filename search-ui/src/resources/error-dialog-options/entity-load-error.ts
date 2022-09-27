// external
import { useRouter } from 'vue-router'
// local
import { DialogOptionsI } from '@/interfaces'
import { RouteNames } from '@/enums'

const redirectToSearch = () => {
  const router = useRouter()
  router.push({ name: RouteNames.SEARCH })
}

export const EntityLoadError: DialogOptionsI = {
  buttons: [{ onClick: redirectToSearch, onClickClose: true, text: 'OK' }],
  onClose: redirectToSearch,
  text: 'The Business Search application is currently unable to ' +
    'load the dashboard for this business. Please try again later.',
  title: 'Business Dashboard unavailable'
}
