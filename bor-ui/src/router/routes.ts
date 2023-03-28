// External
import { RouteRecordRaw } from 'vue-router'
// Local
import {
  DashboardView,
  LogIn,
  SignIn,
  SignOut
 } from '@/views'
import { RouteName } from '@/enums'
import { SearchDashboardBreadcrumb, SearchHomeBreadCrumb } from '@/resources'

export const routes: RouteRecordRaw[] = [
  {
    // router.beforeEach() routes here:
    path: '/login',
    name: RouteName.LOGIN,
    component: LogIn,
    props: true,
    meta: {
      requiresAuth: false,
      title: 'BC Registries Account Login'
    }
  },
  {
    // router.beforeEach() routes here:
    path: '/signin',
    name: RouteName.SIGN_IN,
    component: SignIn,
    props: true,
    meta: {
      requiresAuth: false
    }
  },
  {
    // SbcHeader.logout() redirects here:
    path: '/signout',
    name: RouteName.SIGN_OUT,
    component: SignOut,
    props: true,
    meta: {
      requiresAuth: false
    }
  },
  {
    path: '/',
    name: RouteName.SEARCH,
    component: DashboardView,
    meta: {
      requiresAuth: false, // landing page so needs chance to load without auth
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
