/**
 * Fetches documents object.
 * @param url the full URL to fetch the documents
 * @returns the fetch documents object
 */
export const fetchDocuments = async (url: string): Promise<Blob> => {
  return await useBcrosFetch<Blob>(url,
    { method: 'GET', headers: { Accept: 'application/pdf' }, responseType: 'blob' })
    .then(({ data, error }) => {
      if (error.value || !data.value) {
        console.warn('fetchDocuments() error - invalid response =', error?.value)
        throw new Error('Invalid documents')
      }
      return data?.value
    })
}

/** save data blob to computer */
export const saveBlob = (blob: any, fileName: string) => {
  if (window.navigator && window.navigator.msSaveOrOpenBlob) {
    window.navigator.msSaveOrOpenBlob(blob, fileName)
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

/** Download the file as the given filename. */
export const downloadFile = (data: any, fileName: string) => {
  const blob = new Blob([data])
  saveBlob(blob, fileName)
}
