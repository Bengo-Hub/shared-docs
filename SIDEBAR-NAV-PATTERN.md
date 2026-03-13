# Sidebar and navigation pattern

**Last updated:** March 2026

Standard for desktop sidebar and mobile navigation across Next.js frontends (treasury-ui, pos-ui, inventory-ui, notifications-ui, subscriptions-ui, logistics-ui, ordering-frontend, cafe-website).

---

## Desktop (e.g. lg and up)

- **Sidebar visible:** Fixed or sticky left column with nav links (Dashboard, section links, Settings, etc.).
- **Optional:** Collapsible sidebar (icon-only when collapsed) like logistics-ui or cafe-website dashboard.
- **Width:** e.g. `w-52` / `w-64`; when collapsed, icon-only width (e.g. `w-16`).

---

## Mobile

- **Sidebar hidden** on small viewports (e.g. below `lg`).
- **Header:** Hamburger button opens a full-height overlay drawer that contains the same nav links as the desktop sidebar.
- **Drawer behavior:**
  - Overlay (e.g. `bg-black/50`) behind the drawer; click overlay to close.
  - Drawer slides in from the left (e.g. `translate-x-0` when open, `-translate-x-full` when closed).
  - Close on route change (navigation) or overlay click.
  - Accessible: focus trap when open, aria labels (e.g. "Close menu"), escape to close.
- **Optional:** Bottom navigation bar for 3–5 primary actions (e.g. Dashboard, Orders, Account) where it fits the app (see ordering-frontend MobileBottomNav).

---

## Reference implementations

- **ordering-frontend:** [Sidebar](ordering-service/ordering-frontend/src/components/layout/sidebar.tsx) `hidden lg:block`; [SiteShell](ordering-service/ordering-frontend/src/components/layout/site-shell.tsx) with SiteHeader (hamburger opens UserMenuDrawer) and MobileBottomNav.
- **logistics-ui:** [Sidebar](logistics-service/logistics-ui/src/components/sidebar.tsx) with `open` / `onClose`; overlay and mobile drawer; header passes `onMenuClick` to open sidebar.
- **cafe-website:** [Dashboard layout](Cafe/cafe-website/src/app/(dashboard)/layout.tsx) with collapsible sidebar and mobile drawer; `isSidebarOpen` state; hamburger toggles drawer on mobile.

---

## Implementation checklist per service

- [ ] Desktop: sidebar visible from `lg` (or `md`) up; same nav items as mobile.
- [ ] Mobile: sidebar hidden; header has hamburger that opens overlay drawer.
- [ ] Drawer content: same links as sidebar; close on overlay click and route change.
- [ ] Optional: collapsible desktop sidebar; optional bottom nav for key actions.
- [ ] Accessibility: focus trap in drawer, aria-label on buttons, escape to close.
