import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { BabysitState, Entry, Tab, View } from '../types'
import {
  clip,
  detailOf,
  isMerged,
  nextRepo,
  noteOf,
  pageSizeOf,
  parseEntry,
  repoName,
  select,
  STATE_DIR,
  statusOf,
  summaryOf,
  titleOf,
  visible,
} from './model'

const PANE = 'babysit-pane'
const STATUS_COMMAND = 'babysit-pane'
const TOGGLE_COMMAND = 'babysit-panel'
const POLL_MS = 10_000
// Change the tag when an Entry's fields change: it declines what an earlier version stored.
const entries = atom({ plugin: 'babysit-pane', key: 'entries' } as const, [], { shape: 'entries-1' })
const isPaneShown = atom({ plugin: 'babysit-pane', key: 'isPaneShown' } as const, false)
const view = atom({ plugin: 'babysit-pane', key: 'view' } as const, { tab: 'open', repo: '' }, { shape: 'view-2' })

const COLOR: Readonly<Record<BabysitState, string>> = {
  BLOCKED: 'error',
  EXHAUSTED: 'error',
  WAITING: 'warning',
  READY: 'success',
  CLOSED: 'inactive',
}

const chip = (label: string, isActive: boolean): string => (isActive ? `[${label}]` : label)

async function readEntries($: EngineInterface): Promise<Entry[]> {
  const home = await $.env.get('HOME')
  if (home === undefined) return []
  const dir = `${home}/${STATE_DIR}`
  if (!(await $.fs.exists(dir))) return []
  const names = (await $.fs.list(dir)).filter(f => f.kind === 'file' && f.name.endsWith('.json'))
  const parsed = await Promise.all(
    names.map(async f => {
      const raw = await $.fs.read(`${dir}/${f.name}`).catch(() => '')
      const entry = typeof raw === 'string' ? parseEntry(raw) : undefined
      if (entry === undefined) return undefined
      // Stat after the read: a file replaced in between can only make the mtime newer than the contents, which the cap tolerates.
      const stat = await $.fs.stat(`${dir}/${f.name}`).catch(() => undefined)
      return stat === undefined ? undefined : { ...entry, updatedAt: Math.min(entry.updatedAt, stat.mtimeMs) }
    }),
  )
  return parsed.filter(e => e !== undefined)
}

async function syncPane($: EngineInterface): Promise<void> {
  const pane = (await $.ui.panes()).find(p => p.id === PANE)
  await update($, isPaneShown, () => pane?.isPlaced === true)
}

async function refresh($: EngineInterface): Promise<number> {
  const now = await $.clock.now()
  const shown = visible(await readEntries($), now)
  await update($, entries, () => shown)
  await syncPane($)
  return shown.length
}

async function setPane($: EngineInterface, shown: boolean): Promise<void> {
  if (shown) await $.ui.open({ id: PANE, title: 'Babysit' })
  else await $.ui.close({ id: PANE })
  await syncPane($)
}

async function stateText($: EngineInterface): Promise<string> {
  await refresh($)
  const now = await $.clock.now()
  const list = await read($, entries)
  const rows = list.flatMap(entry => [titleOf(entry), ...detailOf(entry, now).map(row => `  ${row}`)])

  return (rows.length > 0 ? rows : ['No PR is being watched.']).join('\n')
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: STATUS_COMMAND, description: 'Print the state of the PRs babysit-pr-oss watches' })
    await $.command.register({ name: TOGGLE_COMMAND, description: 'Show or hide the babysit pane' })
    $.ui.status(undefined)
    $.clock.every(POLL_MS, () => void refresh($).catch(() => undefined))
    if ((await refresh($)) > 0) await setPane($, true)

    return next(e)
  })

  on('command.run', { command: STATUS_COMMAND }, async $ => ({ text: await stateText($) }))

  on('command.run', { command: TOGGLE_COMMAND }, async ($, e) => {
    const arg = e.args?.trim()
    await syncPane($)
    const closing = arg === 'close' || (arg !== 'open' && (await read($, isPaneShown)))
    await setPane($, !closing)

    return { text: `${closing ? 'Babysit pane hidden' : 'Babysit pane shown'}\n${await stateText($)}` }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const line = statusOf((await read($, entries)).filter(entry => entry.state !== 'CLOSED'))
    if (e.props.hasSurvey || line === undefined || (await read($, isPaneShown))) return next(e)
    const { Box, Button, Text } = $.ui.resolve(e)

    return (
      <Box justifyContent="space-between">
        <Text dimColor>{line}</Text>
        <Button key="show" label="show pane" onPress={() => void setPane($, true)} />
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Button, Text } = $.ui.resolve(e)
    const all = await read($, entries)
    const now = await $.clock.now()
    const current = await read($, view)
    const columns = Math.max(20, Math.floor(e.props.bodyColumns))
    const { items, more, repos, repo, at } = select(all, current, pageSizeOf(e.props.scroll.bodyRows))
    const go = (next: Partial<View>) => void update($, view, v => ({ ...v, ...next }))
    const openCount = all.filter(x => !isMerged(x)).length
    const tabs: readonly [Tab, string][] = [
      ['open', `open ${openCount}`],
      ['merged', `merged ${all.length - openCount}`],
    ]
    const repoLabel = `${repo === '' ? 'all' : repoName(repo)} ${at + 1}/${repos.length + 1}`

    return (
      <Box flexDirection="column">
        <Box justifyContent="space-between">
          <Box columnGap={1}>
            {tabs.map(([tab, label]) => (
              <Button key={tab} label={chip(label, tab === current.tab)} onPress={() => go({ tab, repo: '' })} />
            ))}
          </Box>
          <Box columnGap={1}>
            {repos.length > 1 && <Button key="repo" label={repoLabel} onPress={() => go({ repo: nextRepo(repos, repo) })} />}
            <Button key="hide" label="hide" onPress={() => void setPane($, false)} />
          </Box>
        </Box>
        {items.length === 0 && <Text dimColor>{current.tab === 'open' ? 'No PR is being watched.' : 'No merged PR yet.'}</Text>}
        {items.map(entry => (
          <Box key={`${entry.repo}#${entry.pr}`} flexDirection="column" marginBottom={1}>
            <Box justifyContent="space-between">
              <Text color={COLOR[entry.state]} weight="bold">
                {titleOf(entry)}
              </Text>
              <Text dimColor>{summaryOf(entry, now, columns - titleOf(entry).length - 1)}</Text>
            </Box>
            <Text dimColor>{clip(`  ${noteOf(entry, now)}`, columns)}</Text>
          </Box>
        ))}
        {more > 0 && <Text dimColor>{`  … ${more} more`}</Text>}
      </Box>
    )
  })
}
