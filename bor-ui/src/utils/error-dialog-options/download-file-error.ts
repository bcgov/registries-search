export function getDownloadFileError (): DialogOptionsI {
  return {
    buttons: [{ onClickClose: true, text: 'OK' }],
    text: 'File cannot be downloaded due to an application error. Please try again later.',
    title: 'Unable to download file'
  }
}
