import { DialogOptionsI } from '@/interfaces'

export const DownloadFileError: DialogOptionsI = {
  buttons: [{ onClickClose: true, text: 'OK' }],
  text: 'File cannot be downloaded due to an application error. Please try again later.',
  title: 'Unable to download file'
}
