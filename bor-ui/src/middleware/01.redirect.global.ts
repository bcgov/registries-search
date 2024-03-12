import { RouteNameE } from '@/enums/route-name-e'

export default defineNuxtRouteMiddleware((to) => {
  const expectedRoutes = [RouteNameE.SEARCH]
  // temporary until there is a launch point for this app
  if (!expectedRoutes.includes(to.name as RouteNameE)) {
    return navigateTo({ name: RouteNameE.SEARCH })
  }
})
