// External
import { RouteRecordRaw } from 'vue-router'
// Local
import {
  BusinessInfoView,
  SearchView,
  Login,
  Signin,
  Signout
 } from '@/views'
import { RouteNames } from '@/enums'
import { SearchDashboardBreadcrumb, SearchHomeBreadCrumb } from '@/resources'

export const routes: RouteRecordRaw[] = [
  {
    // router.beforeEach() routes here:
    path: '/login',
    name: RouteNames.LOGIN,
    component: Login,
    props: true,
    meta: {
      requiresAuth: false,
      title: 'BC Registries Account Login'
    }
  },
  {
    // router.beforeEach() routes here:
    path: '/signin',
    name: RouteNames.SIGN_IN,
    component: Signin,
    props: true,
    meta: {
      requiresAuth: false
    }
  },
  {
    // SbcHeader.logout() redirects here:
    path: '/signout',
    name: RouteNames.SIGN_OUT,
    component: Signout,
    props: true,
    meta: {
      requiresAuth: false
    }
  },
  {
    path: '/',
    name: RouteNames.SEARCH,
    component: SearchView,
    meta: {
      requiresAuth: true,
      breadcrumb:[SearchHomeBreadCrumb, SearchDashboardBreadcrumb]
    },
  },
  {
    path: '/:identifier',
    name: RouteNames.BUSINESS_INFO,
    component: BusinessInfoView,
    props: true,
    meta: {
      requiresAuth: true,
      breadcrumb:[SearchHomeBreadCrumb, SearchDashboardBreadcrumb]
    },
  },
  {
    // default/fallback route
    // must be last
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]
