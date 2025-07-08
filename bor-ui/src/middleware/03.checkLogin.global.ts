export default defineNuxtRouteMiddleware(() => {
  const { requireLogin } = useRuntimeConfig().public
  if (requireLogin && !useBcrosKeycloak().kc.authenticated) {
    useBcrosNavigate().goToBcrosDashboard()
  }
})
