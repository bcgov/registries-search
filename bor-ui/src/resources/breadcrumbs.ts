import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
import { RouteNames } from '@/enums'

export const SearchHomeBreadCrumb: BreadcrumbIF = {
    text: 'BC Registries Dashboard',
    href: sessionStorage.getItem('REGISTRY_URL')
}

export const SearchDashboardBreadcrumb: BreadcrumbIF = {
    text: 'Business and Person Search',
    to: { name: RouteNames.SEARCH },
    href: '/search'
}