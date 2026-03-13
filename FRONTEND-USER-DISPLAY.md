# Frontend user display standard

**Last updated:** March 2026  
**Related:** [sso-integration-guide.md](./sso-integration-guide.md), [SSO-AUTHENTICATED-REQUESTS-AND-401.md](./SSO-AUTHENTICATED-REQUESTS-AND-401.md)

---

## Canonical user shape

All Next.js frontends that show a logged-in user (header, profile dropdown, sidebar) must use a consistent shape derived from SSO `/me` or service `/auth/me`:

| Field | Type | Description |
|-------|------|-------------|
| `displayName` | string | Derived: `fullName ?? name ?? email?.split('@')[0] ?? 'Account'`. Never use hardcoded fallbacks like "Super Admin" or "Administrator". |
| `email` | string | User email. |
| `roles` | string[] | Array of role slugs; may be empty. |
| `fullName` or `name` | string (optional) | Raw from API; use for displayName derivation. |

Backend responses may use `fullName`, `name`, or `profile.name`; frontends must map to a single display name for the header/avatar.

---

## Rules

1. **Show profile only when authenticated**  
   Render the logged-in profile block (name, role, avatar) only when the app has a valid session and a populated user object (after SSO callback or successful `/me`). Otherwise show "Sign in" (or loading).

2. **No hardcoded role or name fallbacks**  
   Do not fall back to "Super Admin", "Administrator", or "Member" when `user.fullName` / `user.name` or `user.roles` are missing. Use:
   - Display name: `user.fullName ?? user.name ?? user.email?.split('@')[0] ?? 'Account'`
   - Role: `user.roles?.[0]` if present, otherwise omit the role line or show nothing.

3. **Avatar**  
   Show the first letter of the display name (or email). If there is no name/email, show a generic User icon only. Do not show a placeholder name in the header when the user is in an error state (e.g. callback "Session expired"); in that case do not render the profile block.

4. **Callback error state**  
   "Authentication Failed" and "Session expired" belong only on the auth callback page when verifier is missing or token exchange fails. The main app header must not show the profile block with fallback text when the app is in that error state; show "Sign in" or loading until the user is confirmed.

---

## Implementation checklist

- [ ] Auth store (or `/me` mapping) sets `displayName` (or equivalent) from API response.
- [ ] Header/profile component uses displayName and optional first role only; no "Super Admin" / "Administrator".
- [ ] Profile block is rendered only when `user` exists and status is authenticated (or equivalent).
- [ ] Cafe-website and all service UIs (treasury, pos, notifications, inventory, subscriptions, logistics) follow this standard.
