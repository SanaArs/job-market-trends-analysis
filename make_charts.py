import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.rcParams["font.size"] = 10
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

df = pd.read_csv("data/processed/IT_Jobs_Cleaned.csv", parse_dates=["Date Posted", "Expected Last Date"])

COLOR = "#2E86AB"
ACCENT = "#A23B72"

# 1. Top cities
fig, ax = plt.subplots(figsize=(8, 5))
top_cities = df["City"].value_counts().head(10).sort_values()
top_cities.plot(kind="barh", ax=ax, color=COLOR)
ax.set_title("Top 10 Cities by IT Job Postings", fontsize=13, fontweight="bold")
ax.set_xlabel("Number of Job Postings")
plt.tight_layout()
plt.savefig("visuals/01_top_cities.png", dpi=150)
plt.close()

# 2. Category / Sector breakdown
fig, ax = plt.subplots(figsize=(7, 7))
cat = df["Category / Sector"].value_counts()
cat_top = cat.head(5)
other = cat[5:].sum()
if other > 0:
    cat_top["Other"] = other
colors = plt.cm.Set2.colors
ax.pie(cat_top, labels=cat_top.index, autopct="%1.1f%%", colors=colors, startangle=90)
ax.set_title("Job Postings by Sector / Category", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("visuals/02_sector_breakdown.png", dpi=150)
plt.close()

# 3. Monthly posting trend
fig, ax = plt.subplots(figsize=(9, 5))
monthly = df.dropna(subset=["Date Posted"]).set_index("Date Posted").resample("ME").size()
monthly.plot(ax=ax, marker="o", color=COLOR)
ax.set_title("IT Job Postings Over Time (Monthly)", fontsize=13, fontweight="bold")
ax.set_ylabel("Number of Postings")
ax.set_xlabel("Month")
plt.tight_layout()
plt.savefig("visuals/03_monthly_trend.png", dpi=150)
plt.close()

# 4. Job type distribution
fig, ax = plt.subplots(figsize=(7, 5))
jt = df["Job Type"].value_counts()
ax.bar(jt.index, jt.values, color=ACCENT)
ax.set_title("Job Postings by Employment Type", fontsize=13, fontweight="bold")
ax.set_ylabel("Number of Postings")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("visuals/04_job_type.png", dpi=150)
plt.close()

# 5. Top hiring organizations
fig, ax = plt.subplots(figsize=(8, 5))
top_orgs = df["Organization"].value_counts().head(10).sort_values()
top_orgs.plot(kind="barh", ax=ax, color=COLOR)
ax.set_title("Top 10 Hiring Organizations", fontsize=13, fontweight="bold")
ax.set_xlabel("Number of Job Postings")
plt.tight_layout()
plt.savefig("visuals/05_top_organizations.png", dpi=150)
plt.close()

# 6. Days available to apply (distribution)
fig, ax = plt.subplots(figsize=(8, 5))
df["Days Available"].dropna().plot(kind="hist", bins=20, ax=ax, color=COLOR, edgecolor="white")
ax.set_title("Distribution of Application Window (Days Available)", fontsize=13, fontweight="bold")
ax.set_xlabel("Days Available to Apply")
ax.set_ylabel("Number of Postings")
plt.tight_layout()
plt.savefig("visuals/06_days_available.png", dpi=150)
plt.close()

# 7. Salary range where available (top orgs/roles with disclosed salary)
sal = df.dropna(subset=["Salary Avg (PKR)"]).copy()
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(sal["Salary Avg (PKR)"], bins=25, color=ACCENT, edgecolor="white")
ax.set_title(f"Disclosed Monthly Salary Distribution (n={len(sal)})", fontsize=13, fontweight="bold")
ax.set_xlabel("Average Expected Salary (PKR / month)")
ax.set_ylabel("Number of Postings")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig("visuals/07_salary_distribution.png", dpi=150)
plt.close()

# 8. Education requirement frequency (top 8)
fig, ax = plt.subplots(figsize=(8, 5))
edu = df["Education"].value_counts().head(8).sort_values()
edu.plot(kind="barh", ax=ax, color=COLOR)
ax.set_title("Most Common Education Requirements", fontsize=13, fontweight="bold")
ax.set_xlabel("Number of Job Postings")
plt.tight_layout()
plt.savefig("visuals/08_education.png", dpi=150)
plt.close()

print("Charts saved.")
