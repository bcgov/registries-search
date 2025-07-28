export const goToOpenBusiness = (identifier: string, modernized = false) => {
  const { accessLevel } = useBcrosSearchAccess()
  const { bcolURL, businessDashURL, businessSearchURL } = useRuntimeConfig().public

  if (modernized) {
    if (accessLevel !== SearchAccessE.EXTENDED) {
      // will redirect to business search document purchase page for given identifier
      useBcrosNavigate().redirect(businessSearchURL, { identifier }, '_blank')
    } else {
      // will redirect to business dashboard for given identifier
      useBcrosNavigate().redirect(businessDashURL + identifier, {}, '_blank')
    }
  } else {
    useBcrosNavigate().redirect(bcolURL, {}, '_blank')
  }
}
