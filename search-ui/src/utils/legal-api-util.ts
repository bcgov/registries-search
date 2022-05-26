import { CommentIF } from '@/interfaces'

/**
   * Flattens and sorts an array of comments.
   * @param comments the array of comments to sort and deconstruct
   * @returns the sorted and flattened array of comments
   */
export const flattenAndSortComments = (comments: Array<CommentIF>): Array<CommentIF> => {
    if (comments && comments.length > 0) {
        // first use map to change comment.comment to comment
        const temp: Array<any> = comments.map(c => c.comment)
        // then sort newest to oldest
        temp.sort((a, b) => new Date(a.timestamp) < new Date(b.timestamp) ? 1 : -1)
        return temp
    }
    return []
}