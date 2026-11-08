import { expect, test } from 'claude-code/testing'

const NOW = 1_800_000_000_000

const PANE = {
  plugin: 'babysit-pane',
  component: 'Pane',
  requestId: 'babysit-pane',
  props: {
    title: 'Babysit',
    isFocused: false,
    bodyColumns: 60,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 20 },
    view: {},
  },
} as const

const FILE = JSON.stringify({
  v: 1,
  repo: 'austek/dotfiles',
  pr: 97,
  state: 'BLOCKED',
  cycle: 2,
  cycles: 3,
  head: '594fe7f',
  pass: 8,
  fail: 1,
  pending: 0,
  openThreads: 3,
  next: 'approve the drafted fix',
  updatedAt: NOW - 60_000,
})

function seed(on: Parameters<Parameters<typeof test>[1]>[1], files: Record<string, string>, mtimeMs = NOW): void {
  on('env.get', () => ({ value: '/home/t' }))
  on('fs.exists', () => ({ value: true }))
  on('fs.list', () => ({
    value: Object.keys(files).map(name => ({ name, kind: 'file', size: 1, mtimeMs, isLink: false })),
  }))
  on('fs.read', (_, e) => ({ value: files[e.path.split('/').at(-1) ?? ''] ?? '' }))
  on('clock.now', () => ({ value: NOW }))
  on('clock.every', () => ({ value: { cancel: () => undefined } }))
  on('command.register', () => ({ value: { command: 'babysit' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.panes', () => ({ value: [] }))
  on('ui.status', () => ({ value: undefined }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
}

test('the pane lists a watched PR with its state and detail, on every surface', async ($, on) => {
  seed(on, { 'austek__dotfiles__97.json': FILE, 'junk.json': 'not json', 'note.txt': 'x' })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  for (const surface of ['terminal', 'desktop', 'vscode', 'mobile'] as const) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect((await ui.find({ type: 'Text', text: /dotfiles#97 BLOCKED 2\/3/ }))?.text).toBe('dotfiles#97 BLOCKED 2/3')
    expect(await ui.find({ type: 'Text', text: /next: approve the drafted fix/ })).toBeDefined()
    await ui.unmount()
  }
})

test('a future updatedAt is capped at the file mtime, so the pane shows the real age', async ($, on) => {
  const future = JSON.stringify({ ...JSON.parse(FILE), updatedAt: NOW + 92 * 3_600_000 })
  seed(on, { 'austek__dotfiles__97.json': future }, NOW - 3 * 3_600_000)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect(await ui.find({ type: 'Text', text: /updated 3h ago/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /clock skew/ })).toBeUndefined()
  await ui.unmount()
})

test('with no state files the pane says nothing is watched', async ($, on) => {
  seed(on, {})
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect((await ui.find({ type: 'Text' }))?.text).toBe('No PR is being watched.')
  await ui.unmount()
})
