export const useBcrosNavigate = () => {
  const config = useRuntimeConfig()
  const account = useBcrosAccount()

  /** Redirect to the given URL with necessary BCROS args */
  function redirect (url: string) {
    // get account id and set in params
    const redirectURL = new URL(url)
    const accountId = account.currentAccount.id
    if (accountId) {
      redirectURL.searchParams.append('accountid', accountId)
    }
    // assume URL is always reachable
    window.location.assign(redirectURL.href)
  }

  // common redirects
  function goToBcrosHome () { redirect(config.public.registryHomeURL) }
  function goToBcrosDashboard () { redirect(config.public.registryHomeURL + 'dashboard') }
  function goToBcrosLogin (idpHint: string) {
    /** Redirect to bcros login page given the login type. */
    window.location.assign(`${config.public.registryHomeURL}signin/${idpHint}`)
  }
  function goToEditProfile () { redirect(config.public.authWebURL + 'userprofile') }
  function goToAccountInfo () {
    redirect(config.public.authWebURL + `account/${account.currentAccount.id}/settings/account-info`)
  }
  function goToTeamMembers () {
    redirect(config.public.authWebURL + `account/${account.currentAccount.id}/settings/team-members`)
  }
  function goToTransactions () {
    redirect(config.public.authWebURL + `account/${account.currentAccount.id}/settings/transactions`)
  }
  function goToCreateAccount () {
    redirect(config.public.authWebURL + 'choose-authentication-method')
  }
  function goToSetupAccount () {
    redirect(config.public.authWebURL + 'setup-account')
  }

  return {
    redirect,
    goToBcrosDashboard,
    goToBcrosHome,
    goToBcrosLogin,
    goToAccountInfo,
    goToCreateAccount,
    goToEditProfile,
    goToSetupAccount,
    goToTeamMembers,
    goToTransactions
  }
}
