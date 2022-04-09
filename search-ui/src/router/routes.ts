// External
import { RouteRecordRaw } from 'vue-router'
// Local
import { DashboardView } from '@/views'
import { RouteNames } from '@/enums'

export const routes: RouteRecordRaw[] = [
  {
    path: '/dashboard',
    name: RouteNames.DASHBOARD,
    component: DashboardView,
    meta: {
      requiresAuth: false,
    },
  },
  {
    // default/fallback route
    // must be last
    path: '/',
    redirect: '/dashboard',
  },
]
