GORDO NATION TRADE CALCULATOR — v49
Week 17 refresh · data current through scoring period 131 (August 2, 2026)

WHAT'S IN THIS BUILD
  index.html          desktop calculator + all page tools
  mobile.html         mobile layout, same data
  service-worker.js   offline cache, version gordo-calc-v49-2026-08-04
  manifest.json       PWA manifest
  icon-*.png          app icons

DATA STATE (both index.html and mobile.html, verified identical)
  GNDAILY     131 scoring periods, through 8/2 — daily shapes + roster membership
  GNROS       v10 rest-of-season engine — 1,189 form entries, 76 reliever-role rows
  HISTORY     10 dated snapshots, newest 2026-08-04 — drives the manager-comparison EKG
  PLAYERS     2,122 valuations — drives the player inspector
  OPTIONS     tracker current through Week 17

INSTALLING
  Replace the contents of your existing calculator folder with these files.
  The service-worker version has changed, so the browser will fetch the new
  build on next load; a hard refresh (Cmd-Shift-R) forces it immediately.

NOTE — a stale folder was removed
  Previous zips carried an app/ subfolder holding a v44 copy frozen at scoring
  period 90 (June 22). It was never updated by the weekly refresh and is not
  part of the deployment. It has been dropped from this build. If your current
  install has an app/ folder, delete it.
