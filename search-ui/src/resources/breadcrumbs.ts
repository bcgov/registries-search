import { BreadcrumbIF } from '@/interfaces'
import { RouteNames } from '@/enums'

export const SearchHomeBreadCrumb: BreadcrumbIF = {
    text: 'BC Registries Dashboard',
    href: sessionStorage.getItem('REGISTRY_URL')
}

export const SearchDashboardBreadcrumb: BreadcrumbIF = {
    text: 'Business Search',
    to: { name: RouteNames.SEARCH },
    href: '/dashboard'
}

export const SearchBreadcrumb: BreadcrumbIF = {
    text: 'Business and Person Search',
    href: sessionStorage.getItem('BP_SEARCH_URL')
}

export const SearchBusinessInfoBreadcrumb: BreadcrumbIF = {
    text: '',
    to: { name: RouteNames.BUSINESS_INFO },
    href: ''
}