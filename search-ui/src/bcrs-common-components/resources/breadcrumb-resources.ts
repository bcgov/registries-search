import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'


export const SearchHomeBreadCrumb: BreadcrumbIF = {
    text: 'BC Search and Online Services',
    href: sessionStorage.getItem('REGISTRY_URL')
}

export const SearchDashboardBreadcrumb: BreadcrumbIF = {
    text: 'BC Search Dashboard',
    href: '/dashboard'
}

export const SearchSIGNINBreadcrumb: BreadcrumbIF = {
    text: 'SIGN IN',
    href: ''
}