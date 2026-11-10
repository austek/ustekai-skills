import { expect, test } from 'claude-code/testing'

import type { Entry } from '../types'
import {
  ageText,
  clip,
  detailOf,
  nextRepo,
  noteOf,
  pageSizeOf,
  parseEntry,
  select,
  statusOf,
  summaryOf,
  untilText,
  visible,
} from './model'

const NOW = 1_800_000_000_000
const MIN = 60_000

const raw = (over: Record<string, unknown> = {}): string =>
  JSON.stringify({
    v: 1,
    repo: 'austek/dotfiles',
    pr: 97,
    state: 'WAITING',
    cycle: 1,
    cycles: 3,
    head: '594fe7f0abc',
    pass: 8,
    fail: 0,
    pending: 1,
    openThreads: 3,
    nextReviewAt: NOW + 12 * MIN,
    next: 'wait for the homelab install',
    updatedAt: NOW - MIN,
    ...over,
  })

const entry = (over: Partial<Entry> = {}): Entry => ({ ...(parseEntry(raw()) as Entry), ...over })

test('a version-1 file parses and the head is cut to seven characters', () => {
  const parsed = parseEntry(raw())
  expect(parsed?.repo).toBe('austek/dotfiles')
  expect(parsed?.head).toBe('594fe7f')
  expect(parsed?.openThreads).toBe(3)
})

test('files that are not a version-1 entry are dropped', () => {
  for (const bad of ['not json', '[]', 'null', raw({ v: 2 }), raw({ state: 'DONE' }), raw({ pr: 0 }), raw({ repo: '' })]) {
    expect(parseEntry(bad)).toBeUndefined()
  }
})

test('a missing or odd number reads as zero and a missing window as unset', () => {
  const parsed = parseEntry(raw({ pass: 'x', fail: -4, nextReviewAt: null, next: '' }))
  expect(parsed?.pass).toBe(0)
  expect(parsed?.fail).toBe(0)
  expect(parsed?.nextReviewAt).toBeUndefined()
  expect(parsed?.next).toBeUndefined()
})

test('stale entries and old closed ones are dropped, and what needs a person comes first', () => {
  const list = [
    entry({ pr: 1, state: 'READY' }),
    entry({ pr: 2, state: 'BLOCKED' }),
    entry({ pr: 3, state: 'WAITING', updatedAt: NOW - 25 * 60 * MIN }),
    entry({ pr: 4, state: 'CLOSED', updatedAt: NOW - 2 * 60 * MIN }),
    entry({ pr: 5, state: 'CLOSED', updatedAt: NOW - 5 * MIN }),
  ]
  expect(visible(list, NOW).map(e => e.pr)).toEqual([2, 1, 5])
})

test('the input list is left unchanged by ordering', () => {
  const list = [entry({ pr: 1, state: 'READY' }), entry({ pr: 2, state: 'BLOCKED' })]
  visible(list, NOW)
  expect(list.map(e => e.pr)).toEqual([1, 2])
})

test('the review window reads in minutes and says when it is open', () => {
  expect(untilText(NOW + 12 * MIN, NOW)).toBe('CodeRabbit in 12m')
  expect(untilText(NOW - MIN, NOW)).toBe('CodeRabbit window open')
  expect(untilText(undefined, NOW)).toBeUndefined()
})

test('the detail rows carry checks, threads, the window and the next step', () => {
  expect(detailOf(entry(), NOW)).toEqual([
    'checks 8 pass, 0 fail, 1 pending · 3 open threads · updated 1m ago',
    'CodeRabbit in 12m',
    'next: wait for the homelab install',
  ])
  expect(detailOf(entry({ openThreads: 1, nextReviewAt: undefined, next: undefined }), NOW)).toEqual([
    'checks 8 pass, 0 fail, 1 pending · 1 open thread · updated 1m ago',
  ])
})

test('a WAITING entry nobody has written for two hours has a dead watcher and is dropped', () => {
  const list = [
    entry({ pr: 1, state: 'WAITING', updatedAt: NOW - 119 * MIN }),
    entry({ pr: 2, state: 'WAITING', updatedAt: NOW - 120 * MIN }),
    entry({ pr: 3, state: 'BLOCKED', updatedAt: NOW - 600 * MIN }),
    entry({ pr: 4, state: 'READY', updatedAt: NOW - 600 * MIN }),
  ]
  expect(visible(list, NOW).map(e => e.pr)).toEqual([3, 1, 4])
})

test('the age reads in minutes then hours, and a future timestamp reads as clock skew', () => {
  expect(ageText(NOW, NOW)).toBe('updated now')
  expect(ageText(NOW - 59 * MIN, NOW)).toBe('updated 59m ago')
  expect(ageText(NOW - 135 * MIN, NOW)).toBe('updated 2h ago')
  expect(ageText(NOW + 4 * 24 * 60 * MIN, NOW)).toBe('clock skew')
})

test('the status entry names the first entry and counts the rest', () => {
  expect(statusOf([])).toBeUndefined()
  expect(statusOf([entry({ state: 'BLOCKED' })])).toBe('babysit dotfiles#97 BLOCKED 1/3')
  expect(statusOf([entry(), entry({ pr: 98 }), entry({ pr: 99 })])).toBe('babysit dotfiles#97 WAITING 1/3 +2')
})

const OPEN = { tab: 'open', repo: '' } as const
const paged = (entries: readonly Entry[], view: Parameters<typeof select>[1]) => select(entries, view, 3)

test('the page size follows the pane height and never drops below one', () => {
  expect(pageSizeOf(12)).toBe(3)
  expect(pageSizeOf(38)).toBe(12)
  expect(pageSizeOf(0)).toBe(1)
  expect(pageSizeOf(Number.NaN)).toBe(1)
})

test('long text is cut to the width with an ellipsis and short text is left alone', () => {
  expect(clip('abcdef', 4)).toBe('abc…')
  expect(clip('abcd', 4)).toBe('abcd')
  expect(clip('abcdef', 0)).toBe('abcdef')
})

test('an entry reads as a summary row and a note row', () => {
  const e = entry({ pass: 7, fail: 1, pending: 0, openThreads: 1, updatedAt: NOW - 29 * MIN, nextReviewAt: NOW - MIN })

  expect(summaryOf(e, NOW, 80)).toBe('7✓ 1✗ 0… · 1 thread · updated 29m ago')
  expect(summaryOf(e, NOW, 30)).toBe('7✓ 1✗ 0… · 1 thread')
  expect(summaryOf(e, NOW, 10)).toBe('7✓ 1✗ 0… …')
  expect(noteOf(e, NOW)).toBe('CodeRabbit window open · next: wait for the homelab install')
  expect(noteOf(entry({ next: undefined, nextReviewAt: undefined }), NOW)).toBe('')
})
const many = [1, 2, 3, 4, 5].map(pr => entry({ pr }))

test('a tab holds only its own entries and what does not fit is counted', () => {
  const all = [...many, entry({ pr: 90, state: 'CLOSED' })]

  expect(paged(all, OPEN).items.map(e => e.pr)).toEqual([1, 2, 3])
  expect(paged(all, OPEN).more).toBe(2)
  expect(paged(all, { ...OPEN, tab: 'merged' }).items.map(e => e.pr)).toEqual([90])
  expect(paged(all, { ...OPEN, tab: 'merged' }).more).toBe(0)
})

test('a repo narrows the view and the repo list keeps every repo of the tab', () => {
  const all = [...many, entry({ pr: 7, repo: 'austek/ebbwise' })]
  const result = paged(all, { ...OPEN, repo: 'austek/ebbwise' })

  expect(result.items.map(e => e.pr)).toEqual([7])
  expect(result.repos).toEqual(['austek/dotfiles', 'austek/ebbwise'])
  expect(result.at).toBe(2)
  expect(paged(all, OPEN).at).toBe(0)
})

test('a repo that vanished falls back to all repos instead of showing nothing', () => {
  const result = paged(many, { tab: 'open', repo: 'austek/gone' })

  expect(result.repo).toBe('')
  expect(result.items.map(e => e.pr)).toEqual([1, 2, 3])
  expect(paged([], OPEN)).toMatchObject({ items: [], more: 0, repos: [], at: 0 })
})

test('the repo button cycles all, each repo, then back to all', () => {
  const repos = ['austek/dotfiles', 'austek/ebbwise']

  expect(nextRepo(repos, '')).toBe('austek/dotfiles')
  expect(nextRepo(repos, 'austek/dotfiles')).toBe('austek/ebbwise')
  expect(nextRepo(repos, 'austek/ebbwise')).toBe('')
  expect(nextRepo([], '')).toBe('')
  expect(nextRepo(repos, 'austek/gone')).toBe('')
})
