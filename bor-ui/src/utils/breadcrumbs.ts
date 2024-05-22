export function getBcrosHomeBreadCrumb (): BreadcrumbI {
  return {
    text: ref('BC Registries Dashboard'),
    href: useRuntimeConfig().public.registryHomeURL + 'dashboard'
  }
}

export function getPersonSearchBreadcrumb (): BreadcrumbI {
  const { hasLimitedAccess } = storeToRefs(useBcrosSearch())
  return {
    text: computed(() => hasLimitedAccess.value ? 'Director Search' : 'Business and Person Search'),
    to: { name: RouteNameE.SEARCH },
    href: '/'
  }
}
