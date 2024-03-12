export default defineNuxtRouteMiddleware(() => {
  if (!useBcrosKeycloak().kc.authenticated) {
    const { goToBcrosDashboard } = useBcrosNavigate()
    goToBcrosDashboard()
  }
})
