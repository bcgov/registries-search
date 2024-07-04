export function getSearchCrumb (): BreadcrumbI {
  return {
    text: ref('Business and Person Search'),
    to: { name: RouteNameE.SEARCH },
    href: '/'
  }
}
