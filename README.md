# Ghost Audit

Ghost Audit is a React + TypeScript web application for reviewing and analyzing audit cases, findings, and evidence. The app loads structured audit data from local JSON files and presents it in an interactive UI for investigation and review.

## Project overview

This project includes:
- A Vite + React frontend
- TypeScript support
- Tailwind-based styling
- Local JSON data for audit cases and summaries
- A Python-based data/audit workflow in the repository for generating or evaluating audit evidence

## Tech stack

- React 19
- TypeScript
- Vite
- Tailwind CSS
- Express (used in the project ecosystem)
- Google GenAI SDK
- Python scripts for audit/evaluation support

## Repository structure

```bash
.
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css
│   └── data/
│       ├── audit_summary.json
│       └── full_audit_data.json
├── public/
├── .env.example
├── .gitignore
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── evaluate_samples.py
├── full_test.py
├── match_all_requests.py
├── match_samples.py
├── parse_all_evidence.py
├── pipeline_prototype.py
├── test_*.py
├── output.csv
├── metadata.json
├── code.zip
└── README.md
```

## Prerequisites

Before running the app, make sure you have installed:

- Node.js 18 or later
- npm or yarn
- Git

## Installation

1. Clone the repository:

```bash
git clone https://github.com/guptasargam954/Ghost.git
cd Ghost
```

2. Install the dependencies:

```bash
npm install
```

3. Set up environment variables:

Copy the example env file:

```bash
cp .env.example .env
```

Then update the file with your values:

```env
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
APP_URL="http://localhost:3000"
```

Notes:
- `GEMINI_API_KEY` is required for Gemini AI calls.
- `APP_URL` is used for app URLs and callback references.

## How the website runs

This project uses Vite as the frontend development server.

Run the app locally with:

```bash
npm run dev
```

This starts the development server on:

```bash
http://localhost:3000
```

If the port is changed or blocked, check the Vite config in `vite.config.ts`.

## Production build

To create a production build:

```bash
npm run build
```

The output is generated in the `dist` folder.

To preview the production build locally:

```bash
npm run preview
```

## Lint / type check

```bash
npm run lint
```

This runs TypeScript validation without emitting files.

## Important notes

- The app is configured to run on port 3000.
- The Vite config has HMR settings for AI Studio compatibility.
- Some Python scripts in the repo are used for audit processing and evaluation support and may not be required for the UI to run.
- If you are using AI Studio or a remote runtime, secrets may be injected automatically rather than defined in `.env`.

## Useful commands

```bash
npm install
npm run dev
npm run build
npm run preview
npm run lint
```

## License

This project does not currently include a license file. If needed, add one before publishing or sharing the project publicly.

## Contact

For questions about the project, contact the repository owner or update the project documentation as needed.
