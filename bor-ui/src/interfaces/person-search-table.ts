export interface ControlColumnIconI {
  src: string
  alt: string
  tooltip: string
  displayName: string
}

export interface ControlColumnDetailsInfoBoxI {
  title: string
  icons: ControlColumnIconI[]
  content?: string
  actingJointlyNames?: string[]
  inConcertNames?: string[]
}
