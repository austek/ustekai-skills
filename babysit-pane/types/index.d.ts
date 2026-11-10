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

export type Tab = 'open' | 'merged'

/** What the pane shows: one tab and one repo (`''` for all). */
export type View = { tab: Tab; repo: string }

declare module 'claude-code' {
  interface PluginState {
    'babysit-pane': { entries: Shaped<Entry[]>; isPaneShown: boolean; view: Shaped<View> }
  }
}
