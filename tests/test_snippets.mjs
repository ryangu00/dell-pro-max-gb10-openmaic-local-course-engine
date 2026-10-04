import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../scripts/indexeddb-export-snippets.js', import.meta.url), 'utf8');
const blocks = source.split(/^\/\/ [1-4]\. /m).slice(1).map(block => '// ' + block);

function environment() {
  const scene = {order: 1, type: 'slide', synthetic: true};
  const databases = {
    'MAIC-Database': {empty: []},
    'maic-runtime': {empty: []},
    'maic-documents': {stages: [{synthetic: true}], outlines: [{synthetic: true}], scenes: [scene]}
  };
  const posts = [];
  const request = value => {
    const result = {result: value};
    queueMicrotask(() => result.onsuccess());
    return result;
  };
  const context = vm.createContext({
    window: {OPENMAIC_RECEIVER_PORT: 9977}, console: {log() {}},
    indexedDB: {open(name) {
      const stores = databases[name];
      return request({objectStoreNames: Object.keys(stores), close() {}, transaction(store, mode) {
        assert.equal(mode, 'readonly');
        return {objectStore() {return {
          getAll: () => request(stores[store]),
          getAllKeys: () => request(stores[store].map((_, index) => index))
        };}};
      }});
    }},
    fetch: async (url, options) => {
      posts.push({url, options});
      return {ok: true, json: async () => ({saved: url.split('/').pop() + '.json', bytes: options.body.length})};
    }
  });
  return {context, posts, databases};
}

const run = (block, context) => vm.runInContext('(async () => {\n' + block + '\n})()', context);

test('four numbered snippets inspect, load and export synthetic records', async () => {
  assert.equal(blocks.length, 4);
  const {context, posts} = environment();
  for (const block of blocks) await run(block, context);
  assert.equal(context.window.__maicDump.scenes.length, 1);
  assert.deepEqual(posts.map(post => post.url.split('/').pop()), ['stage', 'outline', 'scene-1-slide']);
  for (const post of posts) {
    assert.equal(post.options.method, 'POST');
    assert.equal(JSON.parse(post.options.body).synthetic, true);
  }
});

test('missing port rejects before sending', async () => {
  const {context, posts} = environment();
  delete context.window.OPENMAIC_RECEIVER_PORT;
  await assert.rejects(run(blocks[3], context), /RECEIVER_PORT/);
  assert.equal(posts.length, 0);
});

test('multiple courses require explicit selection', async () => {
  const {context, posts, databases} = environment();
  databases['maic-documents'].stages.push({synthetic: true});
  await run(blocks[2], context);
  await assert.rejects(run(blocks[3], context), /Select one stage/);
  assert.equal(posts.length, 0);
});

test('receiver errors propagate', async () => {
  const {context} = environment();
  context.fetch = async () => ({ok: false});
  await run(blocks[2], context);
  await assert.rejects(run(blocks[3], context), /Receiver rejected stage/);
});

test('scenes are exported by order rather than record key', async () => {
  const {context, posts, databases} = environment();
  databases['maic-documents'].scenes = [{order: 3, type: 'slide'}, {order: 1, type: 'slide'}];
  await run(blocks[2], context);
  await run(blocks[3], context);
  assert.deepEqual(posts.slice(2).map(post => post.url.split('/').pop()), ['scene-1-slide', 'scene-3-slide']);
});
