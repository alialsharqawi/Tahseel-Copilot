# Frontend

Next.js and React application for the executive dashboard, collection queue, customer profile, and AI approval panel.

## Run locally

Use Node.js 24.15 or newer. From this directory, install the locked dependencies and
start the development server:

```bash
npm ci
npm run dev
```

The app listens on `http://localhost:3000`. The starter page has English and Arabic
labels from centralized dictionaries with a persistent language toggle. The locale
provider updates the document language and direction (`en`/LTR or `ar`/RTL). Use CSS
logical properties for layouts that must work in both directions.

The role navigation is a reusable component that requires a `Role` from the
authenticated user; it does not select or establish a user's identity. It is not
mounted on the public welcome page; mount it in an authenticated layout when the
auth integration and protected routes exist. The Collection Queue is Collector-only
because it is the Collector's home screen in the [UI/UX design](../docs/lms/parts/06_UI_UX_Design.md).
The generic Tasks link is visible to all roles; D15 permits task assignment only
to the Owner and Finance Manager, so a future task screen must distinguish task
access from assignment actions. Customer data remains assigned-only for Collectors.
These are navigation conventions, not authorization. The backend must enforce
record scoping and every protected operation.

Use the shared `formatNumber`, `formatDate`, and `formatCurrency` utilities for
localized values. They use `Intl` with the `latn` numbering system so Arabic output
retains Western digits.

`GET /api/health` returns `{"status":"ok"}` for the Compose health check.

To create a production build, run `npm run build`; `npm start` serves that build.

## Lint and tests

Run ESLint and the frontend tests with:

```bash
npm run lint
npm test
npx tsc --noEmit
npm run build
```

The tests cover the language toggle, document direction and preference persistence,
role-specific navigation, Intl formatting and Western digits, logical CSS, and the
health API route.
