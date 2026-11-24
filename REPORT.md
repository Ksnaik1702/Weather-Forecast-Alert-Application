# Repository readiness and verification

- The README describes installation, simulation/live modes, alert thresholds, API routes, scheduled jobs, local credential handling, project structure, and GitHub publishing.
- The detailed guide covers the original brief, staged learning plan, proof-building schedule, screenshots, and interview preparation.
- The project uses Open-Meteo without a required API key. Optional Telegram credentials belong in a local `.env` file.
- `.gitignore` excludes virtual environments, secrets, generated SQLite files, generated CSV reports, caches, and logs.
- Five automated checks pass for alert rules, missing fields, heatwave threshold, timestamp ordering/deduplication, and m/s normalization.
- The dashboard renders without Streamlit exceptions; the offline CLI simulation writes its CSV report successfully.

Before pushing, add any personal screenshots you want to share to `images/`, then review `git status` to confirm no secrets or generated data are staged.
