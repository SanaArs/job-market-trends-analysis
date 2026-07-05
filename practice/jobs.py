from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

driver = webdriver.Chrome()

driver.get("https://www.jobz.pk/")

# Wait until both containers are loaded
WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "first_big_4col"))
)

# Get all divs with class first_big_4col
containers = driver.find_elements(By.CLASS_NAME, "first_big_4col")

jobs = []

# Loop through each container
for container in containers:

    # Get all rows from the current container
    rows = container.find_elements(By.CLASS_NAME, "row_container")

    # Skip the first row (header)
    for row in rows[1:]:

        try:
            job_title = row.find_element(By.CLASS_NAME, "cell1").text.strip()
        except:
            job_title = ""

        try:
            department = row.find_element(By.CLASS_NAME, "cell2").text.strip()
        except:
            department = ""

        try:
            inner_cells = row.find_elements(By.CLASS_NAME, "inner_cell")

            city = inner_cells[0].text.strip() if len(inner_cells) > 0 else ""
            date = inner_cells[1].text.strip() if len(inner_cells) > 1 else ""

        except:
            city = ""
            date = ""

        jobs.append({
            "Job Title": job_title,
            "Department": department,
            "City": city,
            "Date Posted": date
        })

driver.quit()

# Save all data into one DataFrame
df = pd.DataFrame(jobs)

print(df)

df.to_csv("jobs.csv", index=False)
df.to_excel("jobs.xlsx", index=False)

print("Total Jobs:", len(df))
print("Data saved to jobs.csv and jobs.xlsx")