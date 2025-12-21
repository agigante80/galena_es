# Copilot / AI Agent Instructions — Galena.es

Brief: Make AI agents productive quickly. Focus on Jekyll site + AI content pipeline in `AI_scripts`.

- **Big picture:** This repo is a Jekyll static site whose content (_posts) is mostly produced by the Python-based AI pipeline in `AI_scripts/generate_article.py`. The pipeline:
  - reads topic rows from `AI_content/list_of_NEW_topics.csv`
  - uses prompt templates in `AI_scripts/prompts/*.txt` to call OpenAI for topics, images, alt-text and article body
  - saves images to `assets/images/` and articles to `_posts/` using a `CURRENT_DATE-Topic_Title.md` filename convention

- **Key files / dirs:**
  - `AI_scripts/generate_article.py` — main orchestrator (see env var checks, retry/backoff, CSV handling)
  - `AI_scripts/config.py` — paths, constants and required environment variable names
  - `AI_scripts/prompts/` — prompt templates used by the scripts; they are formatted with `.format(...)`
  - `AI_content/` — CSV topic queues: `list_of_NEW_topics.csv`, archived and error CSVs
  - `assets/images/` — saved/generated images
  - `_posts/` — generated markdown files consumed by Jekyll
  - `requirements.txt` — Python deps (`openai`, `requests`, `markdown-it-py`, `Pillow`)
  - `Gemfile` / `_config.yml` — Jekyll theme and build config

- **Required environment variables (must be present in CI/dev):**
  - `OPENAI_API_KEY` (required)
  - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (optional; used for notifications)
  - `INDEXNOW_API_KEY` (optional; used to notify search engines)

- **How to run the AI pipeline locally**
  1. Create a Python venv and install deps: `python -m venv .venv && .venv/bin/python -m pip install -r requirements.txt`
  2. Export `OPENAI_API_KEY` (and optional tokens):
     - `export OPENAI_API_KEY=sk_xxx`
     - `export TELEGRAM_BOT_TOKEN=...` (optional)
  3. Run: `python AI_scripts/generate_article.py`
  - Note: scripts ensure directories and CSVs exist; check logs for missing files or CSV line format issues.

- **How to serve the site locally (Jekyll)**
  - Install Ruby/Bundler, then: `bundle install` then `bundle exec jekyll serve` (Jekyll config in `_config.yml`)

- **Notable conventions & gotchas (project-specific)**
  - Prompts are plain text templates in `AI_scripts/prompts/` and use Python `.format(...)` placeholders: do not remove placeholders like `{WEBSITE_LANGUAGE}`.
  - OpenAI models used in code: variations of `gpt-4`, `gpt-4.1`, `gpt-4o-mini` and `dall-e-3`. Expect mixed API usages (chat completions + image generation). Be conservative when changing model call shapes.
  - CSV queue format: lines are either `affiliate_id` (single value) or `"topic","description"` (two values). `generate_article.py` expects 1 or 2 fields and will move malformed lines to `list_of_ERROR_topics.csv`.
  - Filenames: generated posts follow `CURRENT_DATE-topic_slug.md` where `CURRENT_DATE` is produced in `config.py` and sanitized in the script. Keep the naming logic if you modify publishing code.
  - Images are downloaded then resized; image filenames include the `CURRENT_DATE` prefix.

- **Testing**
  - A simple unittest file exists at `AI_scripts/my_unittest_generate_article.py` using `unittest` and mocks. Run: `python -m unittest AI_scripts.my_unittest_generate_article` but expect some tests to be tailored to local modifications.

- **Integration points / external dependencies**
  - OpenAI API for text and images (ensure billing/API permission for `dall-e-3` and gpt-4 family models)
  - Telegram API for notifications (optional)
  - IndexNow endpoints (optional)
  - GitHub Pages for hosting (site built with Jekyll)

- **When modifying prompts or model usage**
  - Update only prompt files in `AI_scripts/prompts/` then run the pipeline locally on a small sample (move some lines into a test CSV) to validate output formatting and front-matter correctness.
  - Avoid large-batch runs while iterating prompts to limit token usage.

- **What I (the agent) should never change without human confirmation**
  - `AI_scripts/config.py` path constants and environment variable names
  - `_config.yml` Jekyll settings that affect production hosting
  - The CSV queue handling logic or filename sanitization (these are relied upon by archival/IndexNow notifications)

If any part of this doc is unclear or you want more detail on particular files (examples of prompt placeholders, sample generated markdown front-matter, or CI hooks), tell me which area to expand. 
