# Extracting browser records and reporting unfinished exports

The immediate problem was to get the course out of browser storage. Menu-based
exports produced no file in the test browser, so JSON extraction became the
analysis path. The observations here belong to the 2026-09-12 run; no presentation
or video export is claimed.

## Discover the populated database

The browser contained `MAIC-Database` version 170 with all 16 stores empty,
`maic-documents` version 1 with the course, and `maic-runtime` version 1, empty.
The document database held one stage, one outline set and seven scenes. The
browser inventory described scene data as about 57 KB.

Inspecting the wrong database would have looked like missing data. The supplied
JavaScript preserves four separately pasteable console blocks for inspection,
loading and posting. Run them in the application tab's console, where its origin
can access the IndexedDB records.

## Receiver and console workflow

Start the receiver in a terminal:

```bash
python3 scripts/receiver.py --output exports --port 9977 --origin http://localhost:3000
```

These are example loopback defaults, not deployment addresses from the run.
Set `--origin` to the exact application origin; `localhost` and `127.0.0.1` origins
are different for CORS. The receiver always binds `127.0.0.1`, regardless of that
origin setting.

Run each numbered block in `scripts/indexeddb-export-snippets.js` separately:

1. Inspect the stores and keys in `MAIC-Database`.
2. Inspect stores in `maic-documents` and `maic-runtime`.
3. Read `stages`, `outlines` and `scenes` into `window.__maicDump`.
4. After selecting the intended course, POST its stage, outline and scenes.

Before the final block, set the receiver port in the console:

```javascript
window.OPENMAIC_RECEIVER_PORT = 9977;
```

The source run contained only one course. The published posting block rejects
multiple stage or outline records instead of silently mixing them. If the browser
contains multiple courses, select the matching records in `window.__maicDump`
before posting. The cross-course join fields are not specified by this study;
the snippets do not guess them. Scenes are sorted by `order` and named by order
and type.

The receiver writes the posted bytes to `<name>.json` in the chosen output folder.
It restricts names to `[A-Za-z0-9_-]+`, rejecting separators, traversal syntax,
encoded names and query strings. It also refuses a pre-existing symlink target.
These publication changes replace the original path-joining shortcut. Existing
regular files with the same accepted name are overwritten, so choose the intended
output directory before sending.

CORS headers permit the configured app origin; they are not authentication.
The receiver is a temporary local transfer helper, not a multi-user storage
service or a JSON schema validator. Stop it when extraction is complete.

## Verify the records

The recorded transfer produced nine JSON files, 75,530 bytes, at 19:41. The receiver
was available for under 20 seconds. Validation checked record content and structure,
including four roles, three quiz questions and interactive keys, not only file size.
No original content signatures are published.

For a new neutral course, verify its intended stage, outline set, scene order,
types and counts, then run the geometry checker on its slides. The historical
byte counts are not expected values for a different course.

An offline local transfer check is independent of the application:

```bash
curl -X POST --data '{}' http://127.0.0.1:9977/test
python3 -m json.tool exports/test.json
```

The test suite also invokes the receiver handler directly with byte streams and
mocks its server binding. It verifies writes, CORS headers and invalid-name
rejection without opening a socket. This is handler behavior evidence, not a
browser-to-receiver CORS acceptance test.

## Why MP4 was not produced

The export-video capability check was disabled. The video path builds a
Hyperframes project in the browser and renders it through a separate service
using Chromium headless shell, FFmpeg and Node 22.

The container attempt used `docker compose --profile video-export build render-service`.
The installed Docker CLI lacked the compose plugin, and the runtime daemon socket
was absent because the runtime VM had not started. No render container ran.

The standalone service had no installed dependencies in its folder and lacked
`chromium-headless-shell`. It also required 8 GiB available before listening, and
the host did not meet that service check. These were independent prerequisites,
not a measured rendering-performance failure.

Hyperframes CLI 0.7.60 and FFmpeg 8.1.1 were present. Their presence only identifies
a possible manual route; no manual render was attempted, and no MP4 was produced.
Hyperframes is a separate public project, and only its local version was confirmed.

## Why presentation and archive exports remain unverified

The PPTX, resource-pack and classroom ZIP menu items were clicked. No file arrived
in the downloads folder during the check window. Browser download blocking was
the recorded explanation, but the block itself was not separately confirmed.

An available menu and a PPTist-compatible element format do not prove export
success. This book ships neither a PPTX nor an archive from those routes and does
not present the paths as validated. A normal browser or the JSON receiver is the
supported next step for recovering the records.

## Avoid indefinite collection

An idle classroom tab kept polling a board API route. The recorded development
log accumulated 9,369 such requests, each 404, with repeated edge-runtime warnings
in 9,255 pairs. The session log reached 263,315 lines and 10.1 MB for a one-hour
session. The reason for the polling was not investigated.

Close the tab after extraction to stop that observed source of growth. Original
logs are not included, and the monitoring fixtures contain only synthetic text.

The rule is to establish a verified artifact recovery path before promising
presentation, archive or video outputs. Unmet prerequisites remain uncompleted
work, even when the necessary project or menu is visible.
