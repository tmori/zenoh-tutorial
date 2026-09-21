#!/usr/bin/env node

import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, resolve } from 'node:path';
import { mkdir } from 'node:fs/promises';

function parseArgs(argv) {
  const defaultChromium = [
    process.env.CHROMIUM_BIN,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/chromium',
    '/usr/bin/google-chrome'
  ].find((candidate) => candidate && existsSync(candidate));
  const result = {
    url: 'http://localhost:5173/',
    output: '',
    expectedNodes: null,
    expectedLinks: null,
    zoomOut: 0,
    panY: 0,
    timeoutMs: 15000,
    width: 1500,
    height: 950,
    chromium: defaultChromium || 'chromium'
  };

  for (let i = 0; i < argv.length; i += 1) {
    const value = argv[i];
    const next = () => {
      i += 1;
      if (i >= argv.length) throw new Error(`Missing value for ${value}`);
      return argv[i];
    };
    if (value === '--url') result.url = next();
    else if (value === '--output') result.output = next();
    else if (value === '--expected-nodes') result.expectedNodes = Number(next());
    else if (value === '--expected-links') result.expectedLinks = Number(next());
    else if (value === '--zoom-out') result.zoomOut = Number(next());
    else if (value === '--pan-y') result.panY = Number(next());
    else if (value === '--timeout-ms') result.timeoutMs = Number(next());
    else if (value === '--width') result.width = Number(next());
    else if (value === '--height') result.height = Number(next());
    else if (value === '--chromium') result.chromium = next();
    else throw new Error(`Unknown option: ${value}`);
  }

  if (!result.output) throw new Error('--output is required');
  return result;
}

const sleep = (ms) => new Promise((resolvePromise) => setTimeout(resolvePromise, ms));

async function waitFor(getter, predicate, timeoutMs, description) {
  const deadline = Date.now() + timeoutMs;
  let latest;
  while (Date.now() < deadline) {
    latest = await getter();
    if (predicate(latest)) return latest;
    await sleep(200);
  }
  throw new Error(`Timed out waiting for ${description}; latest=${JSON.stringify(latest)}`);
}

function createCdpClient(webSocketUrl) {
  const socket = new WebSocket(webSocketUrl);
  const pending = new Map();
  let sequence = 0;

  socket.addEventListener('message', (event) => {
    const message = JSON.parse(event.data);
    if (!message.id) return;
    const waiter = pending.get(message.id);
    if (!waiter) return;
    pending.delete(message.id);
    if (message.error) waiter.reject(new Error(message.error.message));
    else waiter.resolve(message.result);
  });

  return {
    ready: new Promise((resolvePromise, reject) => {
      socket.addEventListener('open', resolvePromise, { once: true });
      socket.addEventListener('error', reject, { once: true });
    }),
    send(method, params = {}) {
      sequence += 1;
      const id = sequence;
      return new Promise((resolvePromise, reject) => {
        pending.set(id, { resolve: resolvePromise, reject });
        socket.send(JSON.stringify({ id, method, params }));
      });
    },
    close() {
      socket.close();
    }
  };
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const profile = mkdtempSync(resolve(tmpdir(), 'hako-topology-shot-'));
  const activePortFile = resolve(profile, 'DevToolsActivePort');
  const browser = spawn(options.chromium, [
    '--headless=new',
    '--disable-gpu',
    '--hide-scrollbars',
    '--no-first-run',
    '--no-default-browser-check',
    '--remote-debugging-port=0',
    `--user-data-dir=${profile}`,
    `--window-size=${options.width},${options.height}`,
    options.url
  ], { stdio: 'ignore' });

  let cdp;
  try {
    await waitFor(
      async () => existsSync(activePortFile),
      Boolean,
      options.timeoutMs,
      'Chromium DevTools port'
    );
    const [port] = readFileSync(activePortFile, 'utf8').trim().split('\n');
    const targets = await waitFor(
      async () => fetch(`http://127.0.0.1:${port}/json/list`).then((response) => response.json()),
      (items) => items.some((item) => item.type === 'page'),
      options.timeoutMs,
      'Viewer page target'
    );
    const target = targets.find((item) => item.type === 'page');
    cdp = createCdpClient(target.webSocketDebuggerUrl);
    await cdp.ready;
    await cdp.send('Runtime.enable');
    await cdp.send('Page.enable');

    await waitFor(
      async () => cdp.send('Runtime.evaluate', {
        expression: "Boolean(document.querySelector('#connect-button'))",
        returnByValue: true
      }).then((result) => result.result.value),
      Boolean,
      options.timeoutMs,
      'Viewer controls'
    );
    await sleep(500);
    await cdp.send('Runtime.evaluate', {
      expression: "document.querySelector('#connect-button').click()"
    });

    const summary = await waitFor(
      async () => cdp.send('Runtime.evaluate', {
        expression: `JSON.stringify({
          status: document.querySelector('#status').textContent,
          nodes: Number(document.querySelector('#node-count').textContent),
          links: Number(document.querySelector('#link-count').textContent)
        })`,
        returnByValue: true
      }).then((result) => JSON.parse(result.result.value)),
      (value) => {
        const nodesMatch = options.expectedNodes === null || value.nodes === options.expectedNodes;
        const linksMatch = options.expectedLinks === null || value.links === options.expectedLinks;
        const snapshotReceived = value.status === 'connected' || value.status.startsWith('partial');
        return nodesMatch && linksMatch && snapshotReceived;
      },
      options.timeoutMs,
      'expected topology'
    );

    await cdp.send('Runtime.evaluate', {
      expression: "document.querySelector('#fit-button').click()"
    });
    if (options.zoomOut > 0) {
      await cdp.send('Input.dispatchMouseEvent', {
        type: 'mouseWheel',
        x: 550,
        y: 500,
        deltaX: 0,
        deltaY: options.zoomOut
      });
    }
    if (options.panY !== 0) {
      await cdp.send('Input.dispatchMouseEvent', {
        type: 'mousePressed', x: 550, y: 500, button: 'left', clickCount: 1
      });
      await cdp.send('Input.dispatchMouseEvent', {
        type: 'mouseMoved', x: 550, y: 500 + options.panY, button: 'left', buttons: 1
      });
      await cdp.send('Input.dispatchMouseEvent', {
        type: 'mouseReleased', x: 550, y: 500 + options.panY, button: 'left', clickCount: 1
      });
    }
    await sleep(800);
    const screenshot = await cdp.send('Page.captureScreenshot', {
      format: 'png',
      fromSurface: true,
      captureBeyondViewport: false
    });
    const outputPath = resolve(options.output);
    await mkdir(dirname(outputPath), { recursive: true });
    writeFileSync(outputPath, Buffer.from(screenshot.data, 'base64'));
    process.stdout.write(`${outputPath}: ${summary.nodes} nodes, ${summary.links} links, ${summary.status}\n`);
  } finally {
    if (cdp) cdp.close();
    if (browser.exitCode === null) {
      browser.kill('SIGTERM');
      await Promise.race([
        new Promise((resolvePromise) => browser.once('exit', resolvePromise)),
        sleep(3000)
      ]);
    }
    rmSync(profile, { recursive: true, force: true, maxRetries: 3, retryDelay: 200 });
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
