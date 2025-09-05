export const useBcrosNavigate = () => {
  const account = useConnectAccountStore()

  /** Redirect to the given URL with necessary BCROS args */
  function redirect(url: string, params?: { [key: string]: string }, target = '_self') {
    // get account id and set in params
    const redirectURL = new URL(url)
    const accountId = account.currentAccount.id
    if (accountId) {
      redirectURL.searchParams.append('accountid', accountId.toString())
    }
    for (const [key, value] of Object.entries(params ?? {})) {
      redirectURL.searchParams.append(key, value)
    }
    // assume URL is always reachable
    window.open(redirectURL, target)
  }

  return {
    redirect
  }
}
