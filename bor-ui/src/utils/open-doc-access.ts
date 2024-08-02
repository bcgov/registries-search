export const goToOpenDocAccess = (docAccessItem: DocAccessI) => {
  const { businessSearchURL } = useRuntimeConfig().public
  useBcrosNavigate().redirect(businessSearchURL, { docAccessId: String(docAccessItem.id) }, '_blank')
}
