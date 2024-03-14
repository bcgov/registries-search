export function getBcrosHomeBreadCrumb (): BreadcrumbI {
  return {
    text: ref('BC Registries Dashboard'),
    href: useRuntimeConfig().public.registryHomeURL + 'dashboard'
  }
}

export function getPersonSearchBreadcrumb (): BreadcrumbI {
  const { isExtended } = storeToRefs(useBcrosSearch())
  return {
    text: computed(() => isExtended.value ? 'Business and Person Search' : 'Director Search'),
    to: { name: RouteNameE.SEARCH },
    href: '/'
  }
}
