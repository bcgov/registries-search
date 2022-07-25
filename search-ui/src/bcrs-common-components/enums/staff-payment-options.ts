export enum StaffPaymentOptions {
  // NB: cannot use 0 as it gets passed as a boolean false by vuetify
  NONE = -1,
  FAS = 1,
  BCOL = 2,
  NO_FEE = 3,
}
