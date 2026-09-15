
### Part A: Dataset Ingestion

#### Question 1

Import the necessary Python libraries required for data ingestion and analysis.

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

```

#### Question 2

Load the Student Information dataset (`students.csv`) into a Pandas DataFrame. Display the first five records and the last five records.

```python
df_students = pd.read_csv("students.csv")
print("--- First 5 Records ---")
print(df_students.head(5))

print("\n--- Last 5 Records ---")
print(df_students.tail(5))

```

#### Question 3

Load the Attendance dataset (`attendance.xlsx` or its CSV export). Display the first five records and the number of rows and columns.

```python
attendance_file = "attendance.xlsx - Sheet1.csv" if os.path.exists("attendance.xlsx - Sheet1.csv") else "attendance.xlsx"
df_attendance = pd.read_csv(attendance_file) if attendance_file.endswith('.csv') else pd.read_excel(attendance_file)

print("--- First 5 Records ---")
print(df_attendance.head(5))

print(f"\nDimensions (Rows, Columns): {df_attendance.shape}")

```

#### Question 4

Load the Placement dataset (`placements.csv`). Display the dataset shape and column names.

```python
df_placements = pd.read_csv("placements.csv")

print(f"Dataset Shape: {df_placements.shape}")
print(f"Column Names: {list(df_placements.columns)}")

```

#### Question 5

Load the LMS dataset (`lms.json`). Display the first five records and the data types of all attributes.

```python
df_lms = pd.read_json("lms.json")

print("--- First 5 Records ---")
print(df_lms.head(5))

print("\n--- Attribute Data Types ---")
print(df_lms.dtypes)

```

---

### Part B: Understanding Tabular Representation

#### Question 6

For each dataset, determine the number of rows, number of columns, and attribute names.

```python
datasets = {
    "Students": df_students,
    "Attendance": df_attendance,
    "Placements": df_placements,
    "LMS": df_lms
}

for name, df in datasets.items():
    print(f"Dataset: {name}")
    print(f"  Rows: {df.shape[0]}")
    print(f"  Columns: {df.shape[1]}")
    print(f"  Attributes: {list(df.columns)}\n")

```

#### Question 7

Identify the common attribute that can be used to integrate all four datasets.

```python
common_key = "Student_ID"
print(f"The structural attribute identified for integration is: {common_key}")

```

#### Question 8

Display the summary information of each dataset using suitable Pandas functions.

```python
for name, df in datasets.items():
    print(f"=== Summary Info for {name} ===")
    df.info()
    print("\n" + "="*50 + "\n")

```

#### Question 9

Generate descriptive statistics for all numerical attributes.

```python
for name, df in datasets.items():
    print(f"=== Descriptive Statistics for {name} ===")
    print(df.describe())
    print("\n" + "="*50 + "\n")

```

---

### Part C: Data Quality Assessment

#### Question 10

Check whether any dataset contains missing values and display the count of missing values for each attribute.

```python
for name, df in datasets.items():
    print(f"Missing values count in {name}:")
    print(df.isnull().sum())
    print("-" * 30)

```

#### Question 11

Identify duplicate records in each dataset and display the number of duplicate records found.

```python
for name, df in datasets.items():
    print(f"Number of duplicated rows in {name}: {df.duplicated().sum()}")

```

#### Question 12

Determine whether the `Student_ID` column contains unique values in each dataset.

```python
for name, df in datasets.items():
    if "Student_ID" in df.columns:
        print(f"Is Student_ID unique in {name}? {df['Student_ID'].is_unique}")

```

#### Question 13

Identify students who do not have LMS records and display their `Student_ID` values.

```python
lms_orphans = df_students[~df_students['Student_ID'].isin(df_lms['Student_ID'])]['Student_ID'].tolist()
print(f"Student IDs missing from LMS tracking logs: {lms_orphans}")

```

---

### Part D: Data Integration

#### Question 14

Merge the Student dataset and Attendance dataset using the common key and display the resulting dataset.

```python
merged_df = pd.merge(df_students, df_attendance, on='Student_ID', how='left')
print(merged_df.head())

```

#### Question 15

Integrate the Placement dataset with the merged dataset using a LEFT JOIN and display the resulting dataset.

```python
merged_df = pd.merge(merged_df, df_placements, on='Student_ID', how='left')
print(merged_df.head())

```

#### Question 16

Integrate the LMS dataset with the existing dataset and display the final integrated dataset.

```python
final_df = pd.merge(merged_df, df_lms, on='Student_ID', how='left')
print(final_df.head())

```

#### Question 17

Determine the total number of records and attributes in the final integrated dataset.

```python
rows, cols = final_df.shape
print(f"Total rows (records): {rows}")
print(f"Total columns (attributes): {cols}")

```

#### Question 18

Identify the attributes that contain missing values after integration and explain why these missing values occurred.

```python
print("Missing values in final integrated dataset:")
print(final_df.isnull().sum())

print("\nExplanation:")
print("Missing values (NaN) occur because we used a LEFT JOIN. Students present in the primary")
print("'students.csv' file who do not have matching activity records in 'placements.csv' or")
print("'lms.json' result in null values for those respective columns post-integration.")

```

---

### Part E: Data Transformation

#### Question 19

Replace missing values in the `Company` column with "Not Placed".

```python
if 'Company' in final_df.columns:
    final_df['Company'] = final_df['Company'].fillna("Not Placed")

```

#### Question 20

Replace missing values in `Salary_LPA` with 0.

```python
if 'Salary_LPA' in final_df.columns:
    final_df['Salary_LPA'] = pd.to_numeric(final_df['Salary_LPA'], errors='coerce').fillna(0.0)

```

#### Question 21

Replace missing values in `Videos_Watched` and `Assignments_Submitted` with 0.

```python
if 'Videos_Watched' in final_df.columns:
    final_df['Videos_Watched'] = pd.to_numeric(final_df['Videos_Watched'], errors='coerce').fillna(0).astype(int)

if 'Assignments_Submitted' in final_df.columns:
    final_df['Assignments_Submitted'] = pd.to_numeric(final_df['Assignments_Submitted'], errors='coerce').fillna(0).astype(int)

```

#### Question 22

Create a new attribute called `LMS_Active`. Condition: True if `Videos_Watched` is greater than 0, False otherwise.

```python
final_df['LMS_Active'] = final_df['Videos_Watched'] > 0

```

---

### Part F: Data Analysis

*(Note: `att_col` represents your dynamic attendance column identifier).*

```python
att_col = 'Attendance_Percentage' if 'Attendance_Percentage' in final_df.columns else 'Attendance'

```

#### Question 23

Display the student with the highest CGPA.

```python
highest_cgpa_student = final_df.loc[[final_df['CGPA'].idxmax()]]
print(highest_cgpa_student)

```

#### Question 24

Display the student with the highest attendance percentage.

```python
highest_attendance_student = final_df.loc[[final_df[att_col].idxmax()]]
print(highest_attendance_student)

```

#### Question 25

Compute the average CGPA of all students.

```python
avg_cgpa = final_df['CGPA'].mean()
print(f"Average CGPA of all students: {avg_cgpa:.2f}")

```

#### Question 26

Compute the average attendance percentage.

```python
avg_att = final_df[att_col].mean()
print(f"Average Attendance Percentage: {avg_att:.2f}%")

```

#### Question 27

Display department-wise average CGPA.

```python
dept_avg_cgpa = final_df.groupby('Department')['CGPA'].mean()
print(dept_avg_cgpa)

```

#### Question 28

Display department-wise average attendance.

```python
dept_avg_att = final_df.groupby('Department')[att_col].mean()
print(dept_avg_att)

```

#### Question 29

Count the total number of placed students.

```python
placed_count = final_df[final_df['Company'] != "Not Placed"].shape[0]
print(f"Total number of placed students: {placed_count}")

```

#### Question 30

Find the company offering the highest salary package.

```python
highest_salary_row = final_df.loc[final_df['Salary_LPA'].idxmax()]
print(f"Company: {highest_salary_row['Company']} | Salary: {highest_salary_row['Salary_LPA']} LPA")

```

#### Question 31

Display students whose attendance is below 85%.

```python
low_attendance = final_df[final_df[att_col] < 85]
print(low_attendance[['Student_ID', 'Name', att_col]])

```

#### Question 32

Display students whose CGPA is greater than 8.5.

```python
high_cgpa = final_df[final_df['CGPA'] > 8.5]
print(high_cgpa[['Student_ID', 'Name', 'CGPA']])

```

#### Question 33

Calculate the placement percentage using the formula provided.

```python
placement_pct = (final_df[final_df['Company'] != "Not Placed"].shape[0] / len(final_df)) * 100
print(f"Placement Percentage: {placement_pct:.2f}%")

```

#### Question 34

Determine how many students actively use the LMS platform.

```python
active_lms_count = final_df[final_df['LMS_Active'] == True].shape[0]
print(f"Number of active LMS platform users: {active_lms_count}")

```

---

### Part G: Reporting (Visualizations)

#### Question 35

Create a bar chart showing department-wise average CGPA.

```python
fig, ax = plt.subplots(figsize=(6, 4))
grouped = final_df.groupby('Department')['CGPA'].mean().reset_index()
bars = ax.bar(grouped['Department'], grouped['CGPA'], color='skyblue')
ax.bar_label(bars, fmt='%.2f', padding=3)
ax.set_title("Department-wise Average CGPA")
plt.show()

```

#### Question 36

Create a bar chart showing department-wise average attendance.

```python
fig, ax = plt.subplots(figsize=(6, 4))
grouped = final_df.groupby('Department')[att_col].mean().reset_index()
bars = ax.bar(grouped['Department'], grouped[att_col], color='lightgreen')
ax.bar_label(bars, fmt='%.1f%%', padding=3)
ax.set_title("Department-wise Average Attendance %")
plt.show()

```

#### Question 37

Create a histogram showing attendance distribution.

```python
fig, ax = plt.subplots(figsize=(6, 4))
counts, bins, bars = ax.hist(final_df[att_col].dropna(), bins=6, color='purple', edgecolor='black', alpha=0.7)
ax.bar_label(bars, fmt='%.0f', padding=3)
ax.set_title("Cohort Attendance Distribution Density")
plt.show()

```

#### Question 38

Create a pie chart showing placed vs. non-placed students.

```python
fig, ax = plt.subplots(figsize=(5, 5))
p_count = final_df[final_df['Company'] != "Not Placed"].shape[0]
up_count = len(final_df) - p_count
ax.pie([p_count, up_count], labels=['Placed', 'Not Placed'], autopct='%1.1f%%', colors=['#10b981', '#ef4444'], startangle=140)
ax.set_title("Placement Share Ratio")
plt.show()

```

---

### Part H: Exporting Results

#### Question 39

Export the final integrated dataset to a CSV file named `student_analytics.csv`.

```python
final_df.to_csv("student_analytics.csv", index=False)
print("The final cleaned integrated dataset has been successfully exported.")

```

#### Question 40

Save all generated visualizations as image files.

```python
# Department CGPA
fig, ax = plt.subplots()
grouped = final_df.groupby('Department')['CGPA'].mean().reset_index()
ax.bar(grouped['Department'], grouped['CGPA'])
fig.savefig("chart_snapshot_analysis_1.png", dpi=150)
plt.close(fig)

# Department Attendance
fig, ax = plt.subplots()
grouped = final_df.groupby('Department')[att_col].mean().reset_index()
ax.bar(grouped['Department'], grouped[att_col])
fig.savefig("chart_snapshot_analysis_2.png", dpi=150)
plt.close(fig)

# Attendance Histogram
fig, ax = plt.subplots()
ax.hist(final_df[att_col].dropna(), bins=6)
fig.savefig("chart_snapshot_analysis_3.png", dpi=150)
plt.close(fig)

# Placement Pie Chart
fig, ax = plt.subplots()
p_count = final_df[final_df['Company'] != "Not Placed"].shape[0]
ax.pie([p_count, len(final_df)-p_count], labels=['Placed', 'Not Placed'])
fig.savefig("chart_snapshot_analysis_4.png", dpi=150)
plt.close(fig)

print("All individual plots have been recorded as localized snapshot image files.")

```