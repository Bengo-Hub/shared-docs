# PWA install prompt standard

**Last updated:** March 2026

---

## Required behavior (all Next.js frontends with PWA)

1. **Do not show when already installed**  
   Before showing the install banner, check:
   - `window.matchMedia('(display-mode: standalone)').matches`  
   - Or on iOS: `navigator.standalone === true`  
   If either is true, do not show the prompt.

2. **Dismiss cooldown: 30 minutes**  
   - On "Dismiss" / "Later": `localStorage.setItem(KEY, Date.now().toString())`.  
   - Before showing: if `KEY` exists and `Date.now() - parseInt(KEY, 10) < 30 * 60 * 1000`, do not show.  
   - After 30 minutes, the prompt may be shown again (e.g. on next `beforeinstallprompt` or page load).

3. **Do not show again after install**  
   Listen for `appinstalled`. When fired, clear the deferred prompt state and hide the banner; do not show again in that session.

4. **UI**  
   Single pattern: bottom banner/card with app name, "Install" and "Dismiss" (or "Later"). Dismiss sets the timestamp and hides the banner. Re-show only after 30 min if not installed.

---

## LocalStorage key convention

Use a per-app key to avoid cross-app conflicts:

- `pwa-install-dismissed` (ordering-frontend)
- `pwa-install-dismissed-auth-ui` (auth-ui)
- `pwa-install-dismissed-treasury-ui`
- `pwa-install-dismissed-pos-ui`
- etc.

Pattern: `pwa-install-dismissed` or `pwa-install-dismissed-{appSlug}`.

---

## Reference snippet (logic only)

```ts
const DISMISS_KEY = 'pwa-install-dismissed-{appSlug}';
const DISMISS_DURATION_MS = 30 * 60 * 1000;

function isStandalone(): boolean {
  if (typeof window === 'undefined') return false;
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    ('standalone' in navigator && (navigator as { standalone?: boolean }).standalone === true)
  );
}

function wasDismissedRecently(): boolean {
  if (typeof window === 'undefined') return false;
  const raw = localStorage.getItem(DISMISS_KEY);
  if (!raw) return false;
  const ts = parseInt(raw, 10);
  return !Number.isNaN(ts) && Date.now() - ts < DISMISS_DURATION_MS;
}
```

- On mount: if `isStandalone()`, do not show.  
- On `beforeinstallprompt`: if `!wasDismissedRecently()`, show banner after a short delay (e.g. 2s).  
- On dismiss: `localStorage.setItem(DISMISS_KEY, Date.now().toString())`, hide banner.  
- On `appinstalled`: hide banner and clear deferred prompt.

---

## Services to align

auth-ui, ordering-frontend (reference), treasury-ui, pos-ui, inventory-ui, notifications-ui, subscriptions-ui, logistics-ui, rider-app, cafe-website (if it has a prompt).
