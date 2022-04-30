export interface AutoCompleteResponseIF {
    total: number,
    results: Array<AutoCompleteResultIF>
}
 
export interface AutoCompleteResultIF {
    type: string
    value: string
    score: number
}