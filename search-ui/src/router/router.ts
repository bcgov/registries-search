import { nextTick } from 'vue'
import { RouteLocationNormalized } from 'vue-router'
// External
import { createRouter, createWebHistory, Router } from 'vue-router'
// BC registry
import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// Local
import { RouteNames } from '@/enums'
import { SearchBusinessInfoBreadcrumb } from '@/resources'
import { routes } from './routes'

export function createVueRouter (): Router {
  const router = createRouter({
    history: createWebHistory(sessionStorage.getItem('VUE_ROUTER_BASE') || ''),
    routes
  })
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  router.beforeEach(async (to, from, next) => {
    if (isLoginSuccess(to)) {
      // this route is to verify login
      next({
        name: RouteNames.SIGN_IN,
        query: { redirect: sessionStorage.getItem('REGISTRY_URL') },
      })
    } else {
      if (requiresAuth(to) && !isAuthenticated()) {
        // this route needs authentication, so re-route to login
        next({
          name: RouteNames.LOGIN,
          query: { redirect: sessionStorage.getItem('REGISTRY_URL') },
        })
      } else {
        if (isLogin(to) && isAuthenticated()) {
          // this route is to login
          next({ name: RouteNames.SEARCH })
        } else {
          if (isBusinessInfo(to) || isDocumentRequest(to)) {
            // update meta info
            const breadcrumb = to.meta.breadcrumb as Array<BreadcrumbIF>
            if (breadcrumb.length < 3) {
              // add business info breadcrumb
              breadcrumb.push({ text: to.params.identifier as string, to: SearchBusinessInfoBreadcrumb.to })
            } else {
              // update the text for the business info breadcrumb to the current identifier
              breadcrumb[2].text = to.params.identifier as string
            }
          }
          // proceed normally
          next()
        }
      }
    }
  })
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  router.afterEach((to, from) => {
    // Overrid the browser tab name
    nextTick(() => {
      if (to.meta.title) {
        document.title = to.meta.title as string
      }
    })
  })
  
  /** Returns True if route requires authentication, else False. */
  function requiresAuth(route: RouteLocationNormalized): boolean {
    return route.matched.some(r => r.meta?.requiresAuth)
  }
  
  /** Returns True if user is authenticated, else False. */
  function isAuthenticated(): boolean {
    // FUTURE: also check that token isn't expired!
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  }
  
  /** Returns True if route is Signin, else False. */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  function isSigninRoute(route: RouteLocationNormalized): boolean {
    return Boolean(route.name === RouteNames.SIGN_IN)
  }
  
  /** Returns True if route is Signout, else False. */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  function isSignoutRoute(route: RouteLocationNormalized): boolean {
    return Boolean(route.name === RouteNames.SIGN_OUT)
  }
  
  /** Returns True if route is Login success, else False. */
  function isLogin(route: RouteLocationNormalized): boolean {
    return Boolean(route.name === RouteNames.LOGIN)
  }
  
  /** Returns True if route is Login success, else False. */
  function isLoginSuccess(route: RouteLocationNormalized): boolean {
    return Boolean(route.name === RouteNames.LOGIN && route.hash)
  }

  /** Returns True if route is BusinessInfo, else False. */
  function isBusinessInfo(route: RouteLocationNormalized): boolean {
    return Boolean(route.name === RouteNames.BUSINESS_INFO)
  }

  /** Returns True if route is BusinessInfo, else False. */
  function isDocumentRequest(route: RouteLocationNormalized): boolean {
    return Boolean(route.name === RouteNames.DOCUMENT_REQUEST)
  }

  return router
}
