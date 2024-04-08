import { SearchIconsE } from '@/enums/search-icons-e'

export interface ControlColumnIconI {
  src: SearchIconsE
  alt: string
  tooltip: string
  displayName: string
}

export interface ControlColumnDetailsInfoBoxI {
  title: string,
  content: string
}
