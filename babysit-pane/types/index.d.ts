export type BabysitState = 'BLOCKED' | 'EXHAUSTED' | 'WAITING' | 'READY' | 'CLOSED'

export type Entry = {
  repo: string
  pr: number
  state: BabysitState
  cycle: number
  cycles: number
  head: string
  pass: number
  fail: number
  pending: number
  openThreads: number
  nextReviewAt?: number
  next?: string
  updatedAt: number
}

declare module 'claude-code' {
  interface PluginState {
    'babysit-pane': { entries: Shaped<Entry[]>; isPaneShown: boolean }
  }
}
