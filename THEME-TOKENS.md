# Theme tokens standard

**Last updated:** March 2026

All Next.js frontends in the Codevertex ecosystem use a shared theme so light/dark mode is consistent.

---

## Light mode (default) — auth-ui base

Use auth-ui's `:root` CSS variables as the base for light mode. Values are HSL (without `hsl()` wrapper for Tailwind).

```css
:root {
  --background: 48 100% 96%;
  --foreground: 222.2 47.4% 11.2%;
  --card: 0 0% 100%;
  --card-foreground: 222.2 47.4% 11.2%;
  --popover: 0 0% 100%;
  --popover-foreground: 222.2 47.4% 11.2%;
  --primary: 330 81% 60%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 16% 96%;
  --secondary-foreground: 222.2 47.4% 11.2%;
  --muted: 210 16% 96%;
  --muted-foreground: 215 20% 47%;
  --accent: 210 16% 96%;
  --accent-foreground: 222.2 47.4% 11.2%;
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 0 0% 98%;
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 330 81% 60%;
  --radius: 0.5rem;
}
```

Tailwind: `darkMode: 'class'`. Apply class on `<html>` via next-themes or your theme provider.

---

## Dark mode — cafe-website style

Use cafe-website's dark palette for a consistent dark experience. Apps can use CSS variables or Tailwind theme extension.

**Cafe globals (.dark):**

- `--foreground-rgb: 251, 252, 249`
- `--background-rgb: 44, 26, 2`
- `--sidebar-bg: #1a0f01`
- `--sidebar-foreground: #f5f1ec`
- `--sidebar-accent: #ea8022`
- `--sidebar-muted`, `--sidebar-border` (see cafe-website globals.css)

**Auth-ui .dark (alternative — blue-tinted):**

- `--background: 222.2 84% 4.9%`
- `--foreground: 210 40% 98%`
- `--primary: 210 100% 66%`
- (rest in auth-ui globals.css)

For a warm dark theme across services, prefer cafe-website values. For a neutral/slate dark, use auth-ui .dark. Document which variant each app uses so switching is consistent.

---

## Typography

**Primary font:** Geist (sans).  
**Monospace/code:** Geist Mono.

Load via Next.js:

```ts
import { Geist, Geist_Mono } from 'next/font/google';

const geistSans = Geist({ variable: '--font-geist-sans', subsets: ['latin'] });
const geistMono = Geist_Mono({ variable: '--font-geist-mono', subsets: ['latin'] });
```

Apply to `<body className={geistSans.variable}>` or set `--font-sans` and `--font-mono` on html/body.

Tailwind:

```js
theme: {
  extend: {
    fontFamily: {
      sans: ['var(--font-geist-sans)', 'system-ui', 'sans-serif'],
      mono: ['var(--font-geist-mono)', 'monospace'],
    },
  },
}
```

All Next.js frontends (auth-ui, ordering-frontend, treasury-ui, pos-ui, inventory-ui, notifications-ui, subscriptions-ui, logistics-ui, rider-app, cafe-website) use Geist + Geist Mono for consistency.

---

## Applying tokens in an app

- Ensure `darkMode: 'class'` in tailwind.config and that the theme provider toggles the `dark` class on `<html>`.
- For apps using HSL variables (e.g. shadcn): copy the `:root` and `.dark` blocks from auth-ui (light) and cafe-website (dark) into the app's globals.css so variable names and values match.
- For apps using oklch or other formats: use the same logical values (background, foreground, primary, etc.) and convert as needed; see auth-ui and cafe-website for reference.
