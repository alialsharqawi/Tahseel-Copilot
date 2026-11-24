# Frontend

Next.js and React application for the executive dashboard, collection queue, customer profile, and AI approval panel.

## Run locally

Use Node.js 20.9 or newer. From this directory, install the locked dependencies and
start the development server:

```bash
npm ci
npm run dev
```

The app listens on `http://localhost:3000`. The starter page has English and Arabic
labels with a language toggle; Arabic mode uses right-to-left layout. `GET /api/health`
returns `{"status":"ok"}` for the Compose health check.

To create a production build, run `npm run build`; `npm start` serves that build.

## Lint and tests

Run ESLint and the frontend tests with:

```bash
npm run lint
npm test
```

The tests cover the language toggle and the health API route.
