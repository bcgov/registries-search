import { ApiFiling } from "@/types"

export interface BaseStateI {
  authorization: { authRoles: string[] }
  searchResults: []
  filings: ApiFiling[]
}
