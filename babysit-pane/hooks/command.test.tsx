import { expect, test } from 'claude-code/testing'

const NOW = 1_800_000_000_000

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

const calls = { open: 0, close: 0 }

function seed(on: Parameters<Parameters<typeof test>[1]>[1], files: Record<string, string>, isPlaced = true): void {
  on('env.get', () => ({ value: '/home/t' }))
  on('fs.exists', () => ({ value: true }))
  on('fs.list', () => ({
    value: Object.keys(files).map(name => ({ name, kind: 'file', size: 1, mtimeMs: NOW, isLink: false })),
  }))
  on('fs.read', (_, e) => ({ value: files[e.path.split('/').at(-1) ?? ''] ?? '' }))
  on('clock.now', () => ({ value: NOW }))
  on('clock.every', () => ({ value: { cancel: () => undefined } }))
  on('command.register', (_, e) => ({ value: { command: e.name } }))
  calls.open = 0
  calls.close = 0
  on('ui.open', () => {
    calls.open += 1
    return { value: { isPlaced } }
  })
  on('ui.close', () => {
    calls.close += 1
    return { value: undefined }
  })
  on('ui.status', () => ({ value: undefined }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
}

async function band($: Parameters<Parameters<typeof test>[1]>[0]) {
  return $.ui.mount({
    plugin: 'babysit-pane',
    component: 'AbovePrompt',
    surface: 'terminal',
    props: { hasSurvey: false },
  } as never)
}

test('babysit-pane only prints the state and leaves the pane alone', async ($, on) => {
  seed(on, { 'austek__dotfiles__97.json': FILE })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  const opensAtStart = calls.open
  const result = await $.command.run({ command: 'babysit-pane' })
  expect(calls.open).toBe(opensAtStart)
  expect(calls.close).toBe(0)
  expect(result.text).toContain('dotfiles#97 BLOCKED 2/3')
  expect(result.text).toContain('next: approve the drafted fix')
  expect(result.text).not.toContain('pane hidden')
  expect(result.text).not.toContain('pane shown')
})

test('babysit-panel hides an open pane, shows it again, and prints the state both times', async ($, on) => {
  seed(on, { 'austek__dotfiles__97.json': FILE })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  const hidden = await $.command.run({ command: 'babysit-panel' })
  expect(hidden.text).toContain('Babysit pane hidden')
  expect(hidden.text).toContain('dotfiles#97 BLOCKED 2/3')

  const shown = await $.command.run({ command: 'babysit-panel' })
  expect(shown.text).toContain('Babysit pane shown')
})

test('with nothing watched the state command says so', async ($, on) => {
  seed(on, {})
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  expect((await $.command.run({ command: 'babysit-pane' })).text).toContain('No PR is being watched.')
})

test('the band shows the status and a show-pane button only while the pane is hidden', async ($, on) => {
  seed(on, { 'austek__dotfiles__97.json': FILE })
  on('ui.render', { component: 'AbovePrompt' }, ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text>engine band</Text>
  })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  const whileShown = await band($)
  expect(await whileShown.find({ type: 'Text', text: /engine band/ })).toBeDefined()
  expect(await whileShown.find({ type: 'Text', text: /babysit dotfiles#97/ })).toBeUndefined()
  await whileShown.unmount()

  await $.command.run({ command: 'babysit-panel' })
  const whileHidden = await band($)
  expect(await whileHidden.find({ type: 'Text', text: /babysit dotfiles#97 BLOCKED 2\/3/ })).toBeDefined()
  expect(await whileHidden.find({ type: 'Button', text: /show pane/ })).toBeDefined()
  await whileHidden.unmount()
})

test('the band stays visible when the surface does not place the pane', async ($, on) => {
  seed(on, { 'austek__dotfiles__97.json': FILE }, false)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  const ui = await band($)
  expect(await ui.find({ type: 'Button', text: /show pane/ })).toBeDefined()
  await ui.unmount()
})
