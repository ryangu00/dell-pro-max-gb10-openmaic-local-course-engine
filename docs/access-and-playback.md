# Shared access, browser storage and playback dependencies

The application generated a course, but that does not establish a shared-service
security model or an offline classroom. This chapter separates source findings
at commit `d5be393` from runtime observations in the 2026-09-12 run. Authentication
behavior and learner-side network traffic were not dynamically tested.

## Shared-code mechanics

If `ACCESS_CODE` is unset, middleware permits requests. It was unset in the run.
The development server advertised network reachability, so its pages and APIs
were available to anyone able to reach that listening port.

When the code is set, the browser submits it to a verification route. The server
compares the code in constant time and sets `openmaic_access`, an `HttpOnly`,
`SameSite=Lax` cookie. Its browser lifetime is 7 days; it has `Secure` only when
`NODE_ENV=production`.

The cookie value combines a timestamp with an HMAC-SHA256 signature of that
timestamp keyed by the shared code. The server checks the signature but does not
check the embedded timestamp's age. Browser cookie expiration and server-side
token expiry are therefore not the same property in this implementation.

Without a valid cookie, protected API routes return 401. Page requests pass
through and the front end displays a modal. The health route and access-code
routes are exempt. This is not server-side protection of every page request.

There is one shared identity: everyone with the code is indistinguishable.
The inspected README, environment example and middleware did not provide per-user
identity, roles, SSO, SAML or OIDC. Rotating the code is the available revocation
mechanism described in the source findings.

## Persistence is a separate boundary

The recorded run used browser IndexedDB only and started no database. Courses
stored there are not automatically isolated by a server account system.
The study inspected three databases and found the course in `maic-documents`.

An optional server-backed profile stores courses in PostgreSQL. Its documentation
describes a browser-visible persistence token without confidentiality or user
isolation, intended for localhost or trusted-network single-user use. Its
development authenticator refuses production mode unless an explicit opt-in is
set. That profile was not enabled or tested here.

These facts do not establish encryption, multi-user isolation or production
authentication. The study did not test cookie forgery, brute force, rate limiting
or an identity-aware reverse proxy.

## Why the interactive scene references a CDN

The interactive-page post-processor injects KaTeX 0.16.9 unless the page already
mentions KaTeX. It inserts a stylesheet, the main library and the auto-render
add-on, using three URLs on `cdn.jsdelivr.net`.

Those references were present in the exported interactive page. The five slide
scenes and quiz had no external URL. A single HTML page with inline script is
therefore still not an offline-complete artifact: opening it normally leads the
browser to request those dependencies. Actual playback traffic was not captured,
and behavior with the CDN blocked was not tested.

The generation endpoint's locality says nothing about this browser fetch path.
Likewise, inspecting URLs in a saved page is not a complete browser egress audit.

## The new URL rewriter

`scripts/vendor_katex.py` rewrites the exact pinned URL prefixes for these assets:

```text
katex.min.css
katex.min.js
contrib/auto-render.min.js
```

It accepts HTML or JSON text, replaces the corresponding CDN references, and
writes a separate output path. It does not parse arbitrary script behavior,
download dependencies or claim to remove every possible remote reference.
Its default asset prefix is a local relative path; remote prefixes are rejected.

```bash
python3 scripts/vendor_katex.py fixtures/interactive.html fixtures/interactive-local.html
```

The synthetic fixture exercises all three substitutions. The tests verify that
unrelated text stays unchanged, JSON remains parseable and a repeat rewrite makes
no further substitutions. They do not load a browser or render mathematics.

For a reader's generated artifact, place a genuine matching KaTeX distribution at
the path served by the chosen local asset prefix, including the resources its CSS
requires. Exact asset packaging and serving behavior were not established by the
recorded study. In particular, the correct prefix depends on how the interactive
HTML is embedded and served; this repository does not establish that deployment.

The fact sheet does not provide the original full URL spellings. The helper
targets the canonical pinned paths used in the synthetic fixture; check that its
replacement count covers the actual references in a fresh artifact.

The fresh artifact must then be opened with external network access blocked and
checked for rendering and requests. That browser check remains unrun. No KaTeX
distribution is bundled, and the rewrite test alone is not offline-playback proof.

## Supported next checks, not measured fixes

Set the access code and verify an unauthenticated protected API request returns
401. Bind an evaluation instance to loopback or firewall the port. For shared
use, put identity-aware authentication in front of the whole application.

Vendor the playback dependencies or block the CDN and confirm whether the widget
still renders. These are the supported next steps from the study, not changes
that were deployed or validated in the run.

The rule is to evaluate application identity, storage isolation, generation
locality and playback locality independently. None can be inferred from a single
successful generation request.
