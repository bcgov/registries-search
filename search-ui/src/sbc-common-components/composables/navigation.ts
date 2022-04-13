// External
import { useRouter } from 'vue-router'
// BC Registry
import ConfigHelper from 'sbc-common-components/src/util/config-helper'

export const useNavigation = () => {
  const redirectToPath = (inAuth: boolean, routePath: string) => {
    if (inAuth) {
      redirectInTriggeredApp(routePath)
    } else {
      window.location.assign(`${ConfigHelper.getAuthContextPath()}/${routePath}`)
    }
  }

  const redirectInTriggeredApp = (routePath: string) => {
    const router = useRouter()
    const resolvedRoutes = router.resolve({ path: `/${routePath}` })
    if (resolvedRoutes.matched.length > 0) {
      router.push(`/${routePath}`)
    } else {
      // navigate to auth app if route is not found in the triggered app
      window.location.assign(`${ConfigHelper.getAuthContextPath()}/${routePath}`)
    }
  }
  return {
    redirectToPath
  }
}
