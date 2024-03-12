export function getDefaultError (): DialogOptionsI {
  return {
    buttons: [
      {
        onClick: useBcrosNavigate().goToBcrosDashboard,
        onClickClose: true,
        text: 'OK'
      }
    ],
    onClose: useBcrosNavigate().goToBcrosDashboard,
    text: 'The Director Search application is currently unavailable. Please try again later.',
    title: 'Director Search Unavailable'
  }
}
