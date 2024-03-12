export function getBcrosHomeBreadCrumb (): BreadcrumbI {
  return {
    text: 'BC Registries Dashboard',
    href: useRuntimeConfig().public.registryHomeURL + 'dashboard'
  }
}

export function getPersonSearchBreadcrumb (): BreadcrumbI {
  return {
    text: 'Director Search',
    to: { name: RouteNameE.SEARCH },
    href: '/'
  }
}
