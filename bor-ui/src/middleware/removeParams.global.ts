export default defineNuxtRouteMiddleware((to) => {
  // clean up url
  if (to.query) {
    const params = new URLSearchParams(to.fullPath.split('?')[1])
    params.delete('state')
    params.delete('session_state')
    params.delete('code')
    params.delete('error')
    params.delete('iss')
    // TODO: temporary until pulling in the connect header
    params.delete('accountid')
    to.fullPath = to.path + (params.size > 0 ? `?${params}` : '') + to.hash
  }
})
