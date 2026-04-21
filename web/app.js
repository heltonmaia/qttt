import { Terminal } from 'https://cdn.jsdelivr.net/npm/xterm@5.3.0/+esm';
import { FitAddon } from 'https://cdn.jsdelivr.net/npm/@xterm/addon-fit@0.10.0/+esm';

const boot = document.getElementById('boot');
const termEl = document.getElementById('term');

const describe = (e) => {
  if (e == null) return 'null';
  if (typeof e === 'string') return e;
  const bits = [];
  if (e.name) bits.push(e.name);
  if (e.message) bits.push(e.message);
  if (e.errno !== undefined) bits.push(`errno=${e.errno}`);
  if (e.stack) bits.push(String(e.stack).split('\n').slice(0, 3).join(' | '));
  if (bits.length) return bits.join(' · ');
  try { return JSON.stringify(e); } catch { /* ignore */ }
  try { return String(e); } catch { return '(unknown)'; }
};

const fail = (prefix, e) => {
  boot.style.display = '';
  boot.style.color = '#ff6b6b';
  boot.textContent = `${prefix}: ${describe(e)}`;
  if (e) console.error(e);
};

window.addEventListener('unhandledrejection', (ev) => fail('rejection', ev.reason));
window.addEventListener('error', (ev) => fail('error', ev.error || ev.message));

const term = new Terminal({
  cursorBlink: true,
  fontFamily: 'ui-monospace, Menlo, Consolas, monospace',
  fontSize: 14,
  theme: {
    background: '#0d1117',
    foreground: '#c9d1d9',
    cursor: '#5cff5c',
  },
});

const fit = new FitAddon();
term.loadAddon(fit);
term.open(termEl);
fit.fit();
window.addEventListener('resize', () => fit.fit());

let buffer = '';
let waiter = null;

window.__qttt_request_line = () =>
  new Promise((resolve) => {
    // Drop anything that was in the buffer before python asked for input —
    // stray keystrokes during auto-play shouldn't be consumed as a reply.
    buffer = '';
    waiter = resolve;
  });

term.onData((data) => {
  for (const ch of data) {
    const code = ch.charCodeAt(0);
    if (code === 13) {
      const line = buffer;
      buffer = '';
      term.write('\r\n');
      if (waiter) {
        const r = waiter;
        waiter = null;
        r(line);
      }
    } else if (code === 127 || code === 8) {
      if (waiter && buffer.length) {
        buffer = buffer.slice(0, -1);
        term.write('\b \b');
      }
    } else if (code >= 32 && code < 127) {
      if (waiter) {
        buffer += ch;
        term.write(ch);
      }
    }
  }
});

const bust = `?cb=${Date.now()}`;
const grab = async (url, asBytes = false) => {
  const res = await fetch(url + bust, { cache: 'no-store' });
  if (!res.ok) throw new Error(`failed to fetch ${url}: HTTP ${res.status}`);
  return asBytes ? new Uint8Array(await res.arrayBuffer()) : await res.text();
};

try {
  boot.textContent = 'loading pyodide (~6 MB, first visit only)…';
  const { loadPyodide } = await import('https://cdn.jsdelivr.net/pyodide/v0.26.1/full/pyodide.mjs');
  const pyodide = await loadPyodide({
    indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.1/full/',
  });

  const writeOut = (s) => term.write(s.replace(/\r?\n/g, '\r\n') + '\r\n');
  pyodide.setStdout({ batched: writeOut });
  pyodide.setStderr({ batched: writeOut });

  const ROOT = '/home/pyodide';
  try { pyodide.FS.mkdirTree(ROOT); } catch (_) { /* already exists */ }
  try { pyodide.FS.chdir(ROOT); } catch (_) { /* fallback to root */ }

  const writeAt = (path, data) => {
    const full = `${ROOT}/${path}`;
    const dir = full.slice(0, full.lastIndexOf('/'));
    try { pyodide.FS.mkdirTree(dir); } catch (_) { /* already exists */ }
    pyodide.FS.writeFile(full, data);
  };

  const sources = [
    'agent/__init__.py',
    'game/__init__.py',
    'utils/__init__.py',
    'agent/qlearning.py',
    'game/board.py',
    'utils/clear_screen.py',
    'utils/style.py',
  ];
  for (const path of sources) {
    boot.textContent = `fetching ${path}…`;
    if (path.endsWith('__init__.py')) {
      writeAt(path, '');
      continue;
    }
    const text = await grab('../' + path);
    writeAt(path, text);
  }

  boot.textContent = 'fetching pre-trained model…';
  const modelBytes = await grab('../models/qlearning_model.pkl', true);
  writeAt('models/qlearning_model.pkl', modelBytes);

  boot.textContent = 'fetching play.py…';
  const playSrc = await grab('play.py');

  boot.textContent = 'starting…';
  term.focus();

  await pyodide.runPythonAsync(`
import os, sys
os.environ['FORCE_COLOR'] = '1'
if '${ROOT}' not in sys.path:
    sys.path.insert(0, '${ROOT}')
os.chdir('${ROOT}')
`);

  boot.textContent = '';
  boot.style.display = 'none';
  await pyodide.runPythonAsync(playSrc);
} catch (e) {
  fail('fatal', e);
  term.write(`\r\n\x1b[38;5;196m${describe(e)}\x1b[0m\r\n`);
}
