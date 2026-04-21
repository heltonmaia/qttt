import { Terminal } from 'https://cdn.jsdelivr.net/npm/xterm@5.3.0/+esm';
import { FitAddon } from 'https://cdn.jsdelivr.net/npm/@xterm/addon-fit@0.10.0/+esm';

const boot = document.getElementById('boot');
const termEl = document.getElementById('term');

const fail = (msg, e) => {
  boot.style.display = '';
  boot.style.color = '#ff6b6b';
  boot.textContent = msg;
  if (e) console.error(e);
};

window.addEventListener('unhandledrejection', (ev) => {
  fail(`error: ${ev.reason && ev.reason.message || ev.reason}`, ev.reason);
});
window.addEventListener('error', (ev) => {
  fail(`error: ${ev.message}`, ev.error);
});

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
let resolver = null;

term.onData((data) => {
  for (const ch of data) {
    const code = ch.charCodeAt(0);
    if (code === 13) {
      const line = buffer;
      buffer = '';
      term.write('\r\n');
      if (resolver) {
        const r = resolver;
        resolver = null;
        r(line);
      }
    } else if (code === 127 || code === 8) {
      if (buffer.length) {
        buffer = buffer.slice(0, -1);
        term.write('\b \b');
      }
    } else if (code >= 32 && code < 127) {
      buffer += ch;
      term.write(ch);
    }
  }
});

window.__qttt_read_line = () =>
  new Promise((resolve) => {
    resolver = resolve;
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

  pyodide.setStdout({ batched: (s) => term.write(s.replace(/\n/g, '\r\n')) });
  pyodide.setStderr({ batched: (s) => term.write(s.replace(/\n/g, '\r\n')) });

  const sources = [
    'agent/qlearning.py',
    'game/board.py',
    'utils/clear_screen.py',
    'utils/style.py',
  ];
  for (const path of sources) {
    boot.textContent = `fetching ${path}…`;
    const text = await grab('../' + path);
    const dir = path.slice(0, path.lastIndexOf('/'));
    if (dir) pyodide.FS.mkdirTree(dir);
    pyodide.FS.writeFile(path, text);
  }

  boot.textContent = 'fetching pre-trained model…';
  const modelBytes = await grab('../models/qlearning_model.pkl', true);
  pyodide.FS.mkdirTree('models');
  pyodide.FS.writeFile('models/qlearning_model.pkl', modelBytes);

  boot.textContent = 'fetching play.py…';
  const playSrc = await grab('play.py');

  boot.textContent = 'starting…';
  term.focus();

  await pyodide.runPythonAsync(`
import os
os.environ['FORCE_COLOR'] = '1'
`);

  boot.textContent = '';
  boot.style.display = 'none';
  await pyodide.runPythonAsync(playSrc);
} catch (e) {
  fail(`fatal: ${e.message}`, e);
  term.write(`\r\n\x1b[38;5;196m${e.message}\x1b[0m\r\n`);
}
