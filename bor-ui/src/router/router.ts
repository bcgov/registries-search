import { nextTick } from 'vue'
import { RouteLocationNormalized } from 'vue-router'
// External
import { createRouter, createWebHistory, Router } from 'vue-router'
// BC registry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// Local
import { RouteName } from '@/enums'
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
        name: RouteName.SIGN_IN,
        query: { redirect: sessionStorage.getItem('REGISTRY_URL') },
      })
    } else {
      if (requiresAuth(to) && !isAuthenticated()) {
        // this route needs authentication, so re-route to login
        next({
          name: RouteName.LOGIN,
          query: { redirect: sessionStorage.getItem('REGISTRY_URL') },
        })
      } else {
        if (isLogin(to) && isAuthenticated()) {
          // this route is to login
          next({ name: RouteName.SEARCH })
        } else {
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
  
  /** Returns True if route is Login success, else False. */
  function isLogin(route: RouteLocationNormalized): boolean {
    return Boolean(route.name === RouteName.LOGIN)
  }
  
  /** Returns True if route is Login success, else False. */
  function isLoginSuccess(route: RouteLocationNormalized): boolean {
    return Boolean(route.name === RouteName.LOGIN && route.hash)
  }

  return router
}
