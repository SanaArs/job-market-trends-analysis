# IT Jobs (jobz.pk) — Cleaning & Insights Summary

## Data Cleaning (`clean_data.py`)
Applied to `data/raw/IT_Related_Jobs_Visiting_Links1.csv` (1,750 rows, 23 columns):

- Removed exact duplicate rows and duplicate `Job Link` entries.
- Trimmed whitespace across all text fields.
- Dropped 4 low-value columns that were constant or almost entirely empty:
  `Apply Online if applicable` (99.8% missing), `Online Applicants` (99.5% missing, single constant value),
  `WhatsApp Channel` (constant value), `Job Industry` (constant — every row is "IT Jobs").
- Parsed `Date Posted` into real datetimes.
- Extracted a clean `Expected Last Date` from the messy text field (e.g. stripped
  "...or as per paper ad" suffixes).
- Filled missing categorical values with explicit labels (`Not Mentioned` / `Not Specified`)
  instead of leaving blanks.
- Standardized casing for `City`, `Organization`, `Job Type`, `Category / Sector`, `Newspaper`.
- Converted `No. of Positions` to numeric, flagging open-ended postings (e.g. "35+") separately.
- Split `Expected Salary` text (e.g. "70000 - 80000 Rs. Monthly") into numeric
  `Salary Min / Max / Avg (PKR)` columns.
- Converted `Job Experience` text into a numeric `Min Experience (Years)` column.
- Engineered `Posting Month`, `Posting Year`, `Posting Weekday`, and `Days Available`
  (application window length, with unrealistic negative/very-large values nulled out).

**Result:** `data/processed/IT_Jobs_Cleaned.csv` / `.xlsx` — 1,750 rows, 25 well-typed columns.

## Key Insights

- **Data spans Feb 2022 – Jul 2026**, with postings concentrated in the most recent months —
  the scrape captures an active, ongoing job feed rather than a fixed historical snapshot.
- **Karachi, Islamabad, and Lahore dominate** the market, together accounting for the large
  majority of postings; Rawalpindi and Peshawar are distant next-largest hubs.
- **Private sector leads hiring** (~40% of postings), followed by Government (~24%) and
  Classifieds-style listings (~23%) — Direct Office Jobs and Overseas postings make up the rest.
- **Full-Time roles dominate** (~88%), with Temporary postings a distant second (~10%);
  Internships, Part-Time, and Contract roles are rare in this feed.
- **"IT Company" and "Private Company" are the most frequent (generic) employer names**,
  suggesting many listings don't disclose a specific organization — a useful data-quality flag
  for anyone using this for employer-level analysis. Named organizations like the Ministry of
  IT & Telecom (MOIT) and Pakistan Single Window (PSW) are the most frequent *named* hirers.
- **Bachelor/Master combinations are the standard requirement** — over 60% of postings ask for
  some combination of Bachelor, Master, BS, or MS; only ~1% explicitly say "Not Mentioned."
- **Salary transparency is low**: only ~9% of postings disclose an expected salary. Where
  disclosed, the median monthly salary is **~51,250 PKR**, with a long right tail (a handful of
  senior/technical roles quoted much higher).
- **Experience requirements are under-disclosed too** (~44% of postings specify a number),
  but where stated, **2 years is by far the most common minimum** requirement.
- **Median application window is 15 days**, with 75% of postings closing within a month —
  candidates generally need to act fast after a posting appears.

## Visualizations (`visuals/`)
1. `01_top_cities.png` — Top 10 cities by job count
2. `02_sector_breakdown.png` — Sector/category share (pie)
3. `03_monthly_trend.png` — Job postings over time
4. `04_job_type.png` — Employment type distribution
5. `05_top_organizations.png` — Top 10 hiring organizations
6. `06_days_available.png` — Distribution of application windows
7. `07_salary_distribution.png` — Disclosed salary distribution
8. `08_education.png` — Most common education requirements
