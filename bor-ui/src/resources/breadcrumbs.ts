import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
import { RouteName } from '@/enums'

export const SearchHomeBreadCrumb: BreadcrumbIF = {
    text: 'BC Registries Dashboard',
    href: sessionStorage.getItem('REGISTRY_URL')
}

export const SearchDashboardBreadcrumb: BreadcrumbIF = {
    text: 'Business and Person Search',
    to: { name: RouteName.SEARCH },
    href: '/search'
}