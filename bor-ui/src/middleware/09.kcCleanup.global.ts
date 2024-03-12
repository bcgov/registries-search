export default defineNuxtRouteMiddleware((to) => {
  // remove query params in url added by keycloak
  if (to.query) {
    const params = new URLSearchParams(to.fullPath.split('?')[1])
    params.delete('state')
    params.delete('session_state')
    params.delete('code')
    params.delete('error')
    to.fullPath = to.path + (params.size > 0 ? `?${params}` : '') + to.hash
  }
})
