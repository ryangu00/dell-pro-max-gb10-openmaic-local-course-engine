// 1. Inspect stores in MAIC-Database. Paste each numbered block separately.
// These blocks are console snippets, not a script to load into the application.
{
  const db = await new Promise((resolve, reject) => {
    const request = indexedDB.open('MAIC-Database');
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
  const result = {};
  for (const name of [...db.objectStoreNames]) {
    const store = db.transaction(name, 'readonly').objectStore(name);
    result[name] = await new Promise((resolve, reject) => {
      const request = store.getAllKeys();
      request.onsuccess = () => resolve({count: request.result.length, keys: request.result.slice(0, 5)});
      request.onerror = () => reject(request.error);
    });
  }
  db.close();
  console.log(result);
}

// 2. Inspect document and runtime stores; no private course identifier filter.
{
  const result = {};
  for (const name of ['maic-documents', 'maic-runtime']) {
    const db = await new Promise((resolve, reject) => {
      const request = indexedDB.open(name);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    result[name] = {};
    for (const storeName of [...db.objectStoreNames]) {
      const store = db.transaction(storeName, 'readonly').objectStore(storeName);
      result[name][storeName] = await new Promise((resolve, reject) => {
        const request = store.getAllKeys();
        request.onsuccess = () => resolve({count: request.result.length, keys: request.result.slice(0, 4).map(String)});
        request.onerror = () => reject(request.error);
      });
    }
    db.close();
  }
  console.log(result);
}

// 3. Read all records into memory. Select the intended course before block 4.
{
  const db = await new Promise((resolve, reject) => {
    const request = indexedDB.open('maic-documents');
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
  const get = name => new Promise((resolve, reject) => {
    const request = db.transaction(name, 'readonly').objectStore(name).getAll();
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
  const stages = await get('stages');
  const outlines = await get('outlines');
  const scenes = await get('scenes');
  window.__maicDump = {stages, outlines, scenes};
  db.close();
  console.log({stages: stages.length, outlines: outlines.length, scenes: scenes.length});
}

// 4. POST to the receiver. Set window.OPENMAIC_RECEIVER_PORT to its chosen port.
// This helper requires a single selected course; it does not join multiple courses.
{
  const port = String(window.OPENMAIC_RECEIVER_PORT || '');
  if (!/^\d+$/.test(port)) throw new Error('Set window.OPENMAIC_RECEIVER_PORT first');
  const data = window.__maicDump;
  if (!data || data.stages.length !== 1 || data.outlines.length !== 1) {
    throw new Error('Select one stage, its outline set and its scenes in window.__maicDump');
  }
  const post = async (name, object) => {
    if (!/^[A-Za-z0-9_-]+$/.test(name)) throw new Error('Unsafe export name');
    const response = await fetch('http://127.0.0.1:' + port + '/' + name, {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(object, null, 1)
    });
    if (!response.ok) throw new Error('Receiver rejected ' + name);
    return response.json();
  };
  const results = [await post('stage', data.stages[0]), await post('outline', data.outlines[0])];
  for (const scene of [...data.scenes].sort((a, b) => a.order - b.order)) {
    results.push(await post('scene-' + scene.order + '-' + scene.type, scene));
  }
  console.log(results);
}
