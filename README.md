# Ghost Audit

<p align="center">
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white" alt="React 19" />
  <img src="https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/Status-Active-22C55E" alt="Status" />
</p>

Ghost Audit is a data-audit dashboard and investigation interface built with React + TypeScript. It presents evidence-driven audit cases, workflow summaries, validation status, and downloadable reports in a polished, browser-based UI.

This repository combines a frontend web app with supporting audit/data artifacts and related Python challenge tooling under the `repo/` directory.

## Features

- Interactive dashboard with data summary cards and status metrics
- Case explorer with filters, search, sorting, and pagination
- Evidence explorer for audit artifacts and forensic file previews
- Validation section with benchmark-style checks
- Reports & downloads panel with file export links
- Clean responsive UI built with Tailwind CSS
- Local JSON-driven data model for audit workflow visualization

## Tech Stack

- React 19
- TypeScript
- Vite
- Tailwind CSS
- Lucide icons
- Google GenAI SDK
- Express / Node tooling
- Python scripts for supporting audit dataset processing

## Project Structure

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
│   ├── output.csv
│   ├── evaluation_report.md
│   ├── usage_report.md
│   └── log.txt
├── repo/
│   └── hackerrank-orchestrate-october26-main/
│       ├── code/
│       ├── dataset/
│       ├── README.md
│       └── output.csv
├── .env.example
├── .gitignore
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── output.csv
├── log.txt
├── metadata.json
├── code.zip
├── evaluate_samples.py
├── full_test.py
├── match_all_requests.py
├── match_samples.py
├── parse_all_evidence.py
├── pipeline_prototype.py
├── test_account_link.py
├── test_audit_records.py
├── test_batches.py
├── test_evaluator.py
├── test_facts.py
├── test_link_sample_runs.py
├── test_pipeline.py
├── test_workflow_linking.py
├── trace_ev_content.py
└── README.md
```

## Prerequisites

Make sure you have the following installed:

- Node.js 18+
- npm
- Git

## Installation

1. Clone the repository:

```bash
git clone https://github.com/guptasargam954/Ghost.git
cd Ghost
```

2. Install dependencies:

```bash
npm install
```

3. Set up your environment variables:

```bash
cp .env.example .env
```

Then update `.env` with your values:

```env
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
APP_URL="http://localhost:3000"
```

Notes:
- `GEMINI_API_KEY` is used for Gemini AI API calls.
- `APP_URL` is helpful for app links, callback usage, and self-referential URLs.
- In some hosted environments, these values may be injected automatically by the platform.

## How the Website Runs

This project uses Vite as the frontend development server.

Start the app locally:

```bash
npm run dev
```

Then open the app in your browser:

```bash
http://localhost:3000
```

The app loads its audit data from the local JSON files in `src/data/` and renders the dashboard UI automatically.

## Production Build

To create a production build:

```bash
npm run build
```

The bundled output is generated into the `dist/` directory.

To preview the production build locally:

```bash
npm run preview
```

## Lint / Type Check

```bash
npm run lint
```

This runs TypeScript validation without generating output files.

## Optional Python Audit Tools

The repository also includes Python scripts for audit/evaluation workflow processing under the root and `repo/hackerrank-orchestrate-october26-main/` path. These are mainly used for dataset processing, sample matching, and evaluation tasks.

Example:

```bash
python3 code/main.py
```

This is relevant to the audit challenge logic and not required for normal frontend development.

## Useful Commands

```bash
npm install
npm run dev
npm run build
npm run preview
npm run lint
```

## Troubleshooting

### Port already in use
If port 3000 is occupied, stop the running process or change the dev server configuration in `vite.config.ts`.

### Missing environment variables
If the app expects Gemini-related values, verify that `.env` exists and contains valid entries.

### Dependency errors
Run a clean install:

```bash
rm -rf node_modules package-lock.json
npm install
```

## License

This repository does not currently include a license file. If you plan to publish or distribute it publicly, consider adding an appropriate license.

## Contact

For project questions or contribution updates, contact the repository owner or maintainers directly.
