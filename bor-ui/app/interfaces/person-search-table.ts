export interface ControlColumnIcon {
  src: string
  alt: string
  tooltip: string
  displayName: string
}

export interface ControlColumnDetailsInfoBox {
  title: string
  icons: ControlColumnIcon[]
  content?: string
  actingJointlyNames?: string[]
  inConcertNames?: string[]
}
