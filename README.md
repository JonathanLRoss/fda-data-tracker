# U.S. Weather Tracker

![Tests](https://github.com/JonathanLRoss/fda-data-tracker/actions/workflows/tests.yml/badge.svg)

Tracks daily UTC weather forecasts for Little Rock, Fayetteville, Dallas, Houston, New York, Chicago, Los Angeles, Miami, Denver and Atlanta. Values are forecast snapshots, not verified observations. Each city is a separate request to the public Open-Meteo forecast JSON API (https://open-meteo.com/). Only the current UTC date and four daily metrics are requested. No API key is needed.

## Files
- pipeline.py: fetch, compress, rebuild history, calculate changes and status.
- requirements.txt: Python dependencies.
- tests/test_pipeline.py: pytest tests.
- .github/workflows/daily.yml: scheduled collection and issue updates.
- .github/workflows/tests.yml: tests on push.
- data/raw/YYYY-MM-DD/*.json.gz: original compressed JSON responses by city.
- data/history.csv: deterministic history.
- data/status.json: latest run and source outcomes.
- data/issue.md: generated daily issue body.
- index.html, browse.html, trends.html: website pages.
- app.js: browser calculations, charts, filters and favorites.
- style.css: shared appearance.
- manifest.json, sw.js, icon-192.png, icon-512.png: installable offline web app.
- README.md: documentation.

## History columns
- date: UTC collection date (YYYY-MM-DD).
- item_id: stable city slug.
- item: city name.
- source: city-specific Open-Meteo request slug.
- temperature_2m_max: daily maximum temperature (°F).
- temperature_2m_min: daily minimum temperature (°F).
- precipitation_sum: daily precipitation (inches).
- wind_speed_10m_max: daily maximum wind speed (mph).

Missing values are empty. The five largest absolute changes in maximum temperature between the latest run and preceding available date are reported, with old and new values; ties use city ID. New and missing cities are also reported. Same-day runs replace raw files for that date.

## Commands
`python pipeline.py --build` rebuilds history from raw files alone.
`python pipeline.py` collects today's data.
`python -m pytest` runs tests.

GitHub Pages serves the repository root. The Trends page calculates means from available observations, excluding missing values. Favorites are saved locally in the browser.
