export const goToOpenDocAccess = (docAccessItem: DocAccess) => {
  const { registriesSearchUrl } = useRuntimeConfig().public
  useBcrosNavigate().redirect(registriesSearchUrl, { documentAccessRequestId: String(docAccessItem.id) }, '_blank')
}
