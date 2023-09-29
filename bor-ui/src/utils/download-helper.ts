/** Download the file as the given filename. */
export const downloadFile = (data: any, fileName: string) => {
  const blob = new Blob([data])
  if (window.navigator && window.navigator['msSaveOrOpenBlob']) {
    window.navigator['msSaveOrOpenBlob'](blob, fileName)
  } else {
    // for other browsers, create a link pointing to the ObjectURL containing the blob
    const url = window.URL.createObjectURL(blob)
    const a = window.document.createElement('a')
    window.document.body.appendChild(a)
    a.setAttribute('style', 'display: none')
    a.href = url
    a.download = fileName
    a.click()
    window.URL.revokeObjectURL(url)
    a.remove()
  }
}

export const downloadFileURL = (url: string, filename: string) => {
  const xhr = new XMLHttpRequest()
  xhr.responseType = 'blob'
  xhr.onload = () => {
    const a = window.document.createElement('a')
    window.document.body.appendChild(a)
    a.setAttribute('style', 'display: none')
    a.href = window.URL.createObjectURL(xhr.response)
    a.download = filename
    a.click()
  }
  xhr.open('GET', url)
  xhr.send()
}
