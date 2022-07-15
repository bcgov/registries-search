// External
import { RouteRecordRaw } from 'vue-router'
// Local
import {
  BusinessInfoView,
  DashboardView,
  DocumentRequestView,
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
    component: DashboardView,
    meta: {
      requiresAuth: false, // landing page so needs chance to load without auth
      breadcrumb:[SearchHomeBreadCrumb, SearchDashboardBreadcrumb]
    },
  },
  {
    path: '/open/:identifier',
    name: RouteNames.BUSINESS_INFO,
    component: BusinessInfoView,
    props: true,
    meta: {
      requiresAuth: true,
      breadcrumb:[SearchHomeBreadCrumb, SearchDashboardBreadcrumb]
    },
  },
  {
    path: '/open/request',
    name: RouteNames.DOCUMENT_REQUEST,
    component: DocumentRequestView,    
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
