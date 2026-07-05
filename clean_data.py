import pandas as pd
import numpy as np
import re

df = pd.read_csv("data/raw/IT_Related_Jobs_Visiting_Links1.csv")
print("Raw shape:", df.shape)

# 1. Drop exact duplicate rows and duplicate job links
df = df.drop_duplicates()
df = df.drop_duplicates(subset="Job Link", keep="first")

# 2. Strip whitespace on all text columns
text_cols = df.select_dtypes(include="object").columns
for c in text_cols:
    df[c] = df[c].astype(str).str.strip().replace({"nan": np.nan})

# 3. Drop columns that are almost entirely empty or carry no information
df = df.drop(columns=[
    "Apply Online if applicable",  # 99.8% missing, redundant w/ Apply Online
    "Online Applicants",           # 99.5% missing, single constant value
    "WhatsApp Channel",            # constant value, no analytical use
    "Job Industry",                # constant value "IT Jobs" (whole dataset is IT jobs)
])

# 4. Parse dates
df["Date Posted"] = pd.to_datetime(df["Date Posted"], format="%d-%b-%Y", errors="coerce")

# Expected Last Date has trailing text like "or as per paper ad" -> extract the date part
df["Expected Last Date Clean"] = df["Expected Last Date"].str.extract(r"(\d{1,2}\s+\w+,\s*\d{4})")
df["Expected Last Date Clean"] = pd.to_datetime(df["Expected Last Date Clean"], format="%d %B, %Y", errors="coerce")
df = df.drop(columns=["Expected Last Date"]).rename(columns={"Expected Last Date Clean": "Expected Last Date"})

# 5. Fill categorical missing values with explicit labels
df["Education"] = df["Education"].fillna("Not Mentioned")
df["Newspaper"] = df["Newspaper"].fillna("Not Mentioned")
df["Area / Town"] = df["Area / Town"].fillna("Not Mentioned")
df["Gender"] = df["Gender"].fillna("Not Specified")
df["Apply Online"] = df["Apply Online"].fillna("Not Mentioned")

# 6. Standardize text casing
for c in ["Job Type", "City", "Organization", "Category / Sector", "Newspaper"]:
    df[c] = df[c].str.title()

# 7. Clean No. of Positions -> numeric (treat "35+" as 35, keep flag for open-ended)
df["Positions Open Ended"] = df["No. of Positions"].str.contains(r"\+", na=False)
df["No. of Positions"] = (
    df["No. of Positions"].str.replace("+", "", regex=False)
)
df["No. of Positions"] = pd.to_numeric(df["No. of Positions"], errors="coerce")

# 8. Parse salary range into min/max numeric columns (monthly, PKR)
def parse_salary(val):
    if pd.isna(val):
        return (np.nan, np.nan)
    nums = re.findall(r"\d+", val.replace(",", ""))
    nums = [int(n) for n in nums]
    if not nums:
        return (np.nan, np.nan)
    if len(nums) == 1:
        return (nums[0], nums[0])
    return (min(nums), max(nums))

sal = df["Expected Salary"].apply(parse_salary)
df["Salary Min (PKR)"] = sal.apply(lambda x: x[0])
df["Salary Max (PKR)"] = sal.apply(lambda x: x[1])
df["Salary Avg (PKR)"] = df[["Salary Min (PKR)", "Salary Max (PKR)"]].mean(axis=1)
df = df.drop(columns=["Expected Salary"])

# 9. Parse Job Experience into numeric minimum years required
def parse_experience(val):
    if pd.isna(val):
        return np.nan
    val = val.lower()
    nums = re.findall(r"\d+", val)
    if not nums:
        return np.nan
    return int(nums[0])

df["Min Experience (Years)"] = df["Job Experience"].apply(parse_experience)
df = df.drop(columns=["Job Experience"])

# 10. Feature engineering
df["Posting Month"] = df["Date Posted"].dt.month_name()
df["Posting Year"] = df["Date Posted"].dt.year
df["Posting Weekday"] = df["Date Posted"].dt.day_name()
df["Days Available"] = (df["Expected Last Date"] - df["Date Posted"]).dt.days
# Guard against negative/absurd values from bad OCR-like text dates
df.loc[df["Days Available"] < 0, "Days Available"] = np.nan
df.loc[df["Days Available"] > 120, "Days Available"] = np.nan

# 11. Drop the now-redundant "Date Posted / Updated" (string duplicate of Date Posted)
df = df.drop(columns=["Date Posted / Updated"])

# 12. Reorder columns sensibly
front = ["Job Title", "Organization", "City", "Area / Town", "Vacancy Location",
         "Category / Sector", "Job Type", "Education", "Min Experience (Years)",
         "Gender", "No. of Positions", "Positions Open Ended",
         "Salary Min (PKR)", "Salary Max (PKR)", "Salary Avg (PKR)",
         "Date Posted", "Expected Last Date", "Days Available",
         "Posting Month", "Posting Year", "Posting Weekday",
         "Newspaper", "Apply Online", "Job Link", "Description"]
df = df[front]

print("Cleaned shape:", df.shape)
print(df.isnull().sum().sort_values(ascending=False).head(10))

df.to_csv("data/processed/IT_Jobs_Cleaned.csv", index=False)
df.to_excel("data/processed/IT_Jobs_Cleaned.xlsx", index=False)
print("Saved cleaned data.")
