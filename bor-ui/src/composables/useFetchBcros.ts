export const useFetchBcros = <T>(request, opts?) => {
  if (!opts?.headers?.Authorization) {
    const token = useBcrosKeycloak().kc.token

    opts = opts || {}
    Object.assign(opts, { headers: { Authorization: `Bearer ${token}` } })
  }
  if (!opts.headers['Account-Id']) {
    opts.headers['Account-Id'] = (useBcrosAccount()).currentAccount?.id
  }

  return useFetch<T>(request, opts)
}
