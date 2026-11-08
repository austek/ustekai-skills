import type { BabysitState, Entry } from '../types'

export const SCHEMA_VERSION = 1
export const STATE_DIR = '.cache/babysit-pr'

const HOUR_MS = 3_600_000
const STALE_MS = 24 * HOUR_MS
const ORDER: readonly BabysitState[] = ['BLOCKED', 'EXHAUSTED', 'WAITING', 'READY', 'CLOSED']

const isState = (value: unknown): value is BabysitState =>
  typeof value === 'string' && (ORDER as readonly string[]).includes(value)

const whole = (value: unknown): number =>
  typeof value === 'number' && Number.isFinite(value) ? Math.max(0, Math.floor(value)) : 0

const words = (value: unknown): string => (typeof value === 'string' ? value : '')

const optionalWords = (value: unknown): string | undefined => (words(value) === '' ? undefined : words(value))

const optionalTime = (value: unknown): number | undefined => (whole(value) === 0 ? undefined : whole(value))

const jsonOrUndefined = (raw: string): unknown => {
  try {
    return JSON.parse(raw)
  } catch {
    return undefined
  }
}

const entryOf = (o: Record<string, unknown>, state: BabysitState): Entry => ({
  repo: words(o.repo),
  pr: whole(o.pr),
  state,
  cycle: whole(o.cycle),
  cycles: whole(o.cycles),
  head: words(o.head).slice(0, 7),
  pass: whole(o.pass),
  fail: whole(o.fail),
  pending: whole(o.pending),
  openThreads: whole(o.openThreads),
  nextReviewAt: optionalTime(o.nextReviewAt),
  next: optionalWords(o.next),
  updatedAt: whole(o.updatedAt),
})

/** Reads one state file; anything that is not a version-1 entry with a repo, a PR and a known state is dropped. */
export function parseEntry(raw: string): Entry | undefined {
  const json = jsonOrUndefined(raw)
  if (typeof json !== 'object' || json === null) return undefined
  const o = json as Record<string, unknown>
  const valid = o.v === SCHEMA_VERSION && isState(o.state) && whole(o.pr) > 0 && words(o.repo) !== ''
  return valid && isState(o.state) ? entryOf(o, o.state) : undefined
}

const isFresh = (e: Entry, now: number): boolean =>
  now - e.updatedAt < STALE_MS && (e.state !== 'CLOSED' || now - e.updatedAt < HOUR_MS)

const rank = (e: Entry): number => ORDER.indexOf(e.state)

/** Drops stale entries and orders the rest by what needs a person first. */
export function visible(entries: readonly Entry[], now: number): Entry[] {
  return entries
    .filter(e => isFresh(e, now))
    .toSorted((a, b) => rank(a) - rank(b) || a.repo.localeCompare(b.repo) || a.pr - b.pr)
}

export function untilText(at: number | undefined, now: number): string | undefined {
  if (at === undefined) return undefined
  const minutes = Math.ceil((at - now) / 60_000)
  return minutes <= 0 ? 'CodeRabbit window open' : `CodeRabbit in ${minutes}m`
}

const repoName = (repo: string): string => repo.split('/').at(-1) ?? repo

export const labelOf = (e: Entry): string => `${repoName(e.repo)}#${e.pr}`

const cycleText = (e: Entry): string => (e.cycles > 0 ? ` ${e.cycle}/${e.cycles}` : '')

/** Display text for the age of the state file; a future `updatedAt` yields `clock skew`. */
export function ageText(updatedAt: number, now: number): string {
  const minutes = Math.floor((now - updatedAt) / 60_000)
  if (minutes < 0) return 'clock skew'
  if (minutes < 1) return 'updated now'
  return minutes < 60 ? `updated ${minutes}m ago` : `updated ${Math.floor(minutes / 60)}h ago`
}

/** The title row of an entry. */
export const titleOf = (e: Entry): string => `${labelOf(e)} ${e.state}${cycleText(e)}`

/** The detail rows of an entry: checks and threads, the review window, the next step. */
export function detailOf(e: Entry, now: number): string[] {
  const checks = `checks ${e.pass} pass, ${e.fail} fail, ${e.pending} pending`
  const threads = `${e.openThreads} open thread${e.openThreads === 1 ? '' : 's'}`
  const window = untilText(e.nextReviewAt, now)
  const rows = [`${checks} · ${threads} · ${ageText(e.updatedAt, now)}`, ...(window === undefined ? [] : [window])]
  return e.next === undefined ? rows : [...rows, `next: ${e.next}`]
}

/** The one-line status entry: the entry that needs a person most, and how many more are watched. */
export function statusOf(entries: readonly Entry[]): string | undefined {
  const [first, ...rest] = entries
  if (first === undefined) return undefined
  const more = rest.length === 0 ? '' : ` +${rest.length}`
  return `babysit ${titleOf(first)}${more}`
}
