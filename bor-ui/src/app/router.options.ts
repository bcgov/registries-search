import type { RouterConfig } from '@nuxt/schema'

export default <RouterConfig> {
  // https://router.vuejs.org/api/interfaces/routeroptions.html#routes
  // alternatively, could put this inside the setup for each page
  routes: _routes => [
    {
      name: RouteNameE.SEARCH,
      path: '/',
      component: () => import('~/pages/search.vue').then(r => r.default || r),
      meta: {
        layout: 'default',
        title: 'Person Search',
        breadcrumbs: [getBcrosHomeCrumb, getSearchCrumb]
      }
    }
  ]
}
