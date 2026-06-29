import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

students_df = pd.read_csv("students.csv")

print("--- First 5 Records ---")
print(students_df.head(5))

print("\n--- Last 5 Records ---")
print(students_df.tail(5))

attendance_df = pd.read_excel("attendance.xlsx")

print("--- First 5 Records ---")
print(attendance_df.head(5))

print(f"\nShape of Attendance Dataset (Rows, Columns): {attendance_df.shape}")

placements_df = pd.read_csv("placements.csv")

print(f"Dataset Shape: {placements_df.shape}")
print(f"Column Names: {list(placements_df.columns)}")

lms_df = pd.read_json("lms.json")

print("--- First 5 Records ---")
print(lms_df.head(5))

print("\n--- Data Types of All Attributes ---")
print(lms_df.dtypes)

datasets = {
    "Students": students_df,
    "Attendance": attendance_df,
    "Placements": placements_df,
    "LMS": lms_df
}

for name, df in datasets.items():
    print(f"Dataset: {name}")
    print(f"  Rows: {df.shape[0]}")
    print(f"  Columns: {df.shape[1]}")
    print(f"  Attribute Names: {list(df.columns)}\n")

    # The structural primary/foreign key across all tables is the Student ID
common_attribute = 'Student_ID'
print(f"The common attribute for data integration is: {common_attribute}")

for name, df in datasets.items():
    print(f"=== Summary Information for {name} ===")
    df.info()
    print("\n" + "="*40 + "\n")

    for name, df in datasets.items():
    print(f"=== Descriptive Statistics for {name} ===")
    print(df.describe())
    print("\n" + "="*40 + "\n")

    for name, df in datasets.items():
    print(f"=== Missing Values Check in {name} ===")
    print(df.isnull().sum())
    print("\n")

    for name, df in datasets.items():
    num_duplicates = df.duplicated().sum()
    print(f"Number of duplicate records found in {name}: {num_duplicates}")

    for name, df in datasets.items():
    if 'Student_ID' in df.columns:
        is_unique = df['Student_ID'].is_unique
        print(f"Is 'Student_ID' completely unique in {name}? {is_unique}")

        missing_lms_students = students_df[~students_df['Student_ID'].isin(lms_df['Student_ID'])]

print(f"Count of students missing LMS records: {len(missing_lms_students)}")
print("Student_ID values:")
print(missing_lms_students['Student_ID'].tolist())

# Performing a left join to keep all base student profiles intact
merged_df = pd.merge(students_df, attendance_df, on='Student_ID', how='left')
print(merged_df.head())

merged_df = pd.merge(merged_df, placements_df, on='Student_ID', how='left')
print(merged_df.head())

final_df = pd.merge(merged_df, lms_df, on='Student_ID', how='left')
print(final_df.head())

records, attributes = final_df.shape
print(f"Total number of records (rows): {records}")
print(f"Total number of attributes (columns): {attributes}")

print("Attributes containing missing values post-integration:")
print(final_df.isnull().sum())

print("\n--- Engineering Explanation ---")
print("These missing values (NaN) occurred because we utilized LEFT JOIN mechanics during")
print("integration. Students present in the baseline 'students.csv' file who did not possess")
print("corresponding entries in 'placements.csv' or 'lms.json' generated null values for those specific metrics.")

final_df['Company'] = final_df['Company'].fillna("Not Placed")

final_df['Salary_LPA'] = final_df['Salary_LPA'].fillna(0)

final_df['Videos_Watched'] = final_df['Videos_Watched'].fillna(0)
final_df['Assignments_Submitted'] = final_df['Assignments_Submitted'].fillna(0)

final_df['LMS_Active'] = final_df['Videos_Watched'] > 0

highest_cgpa_row = final_df.loc[final_df['CGPA'].idxmax()]
print(highest_cgpa_row)

# Swapping with 'Attendance' depending on your schema setup
attendance_col = 'Attendance_Percentage' if 'Attendance_Percentage' in final_df.columns else 'Attendance'

highest_attendance_row = final_df.loc[final_df[attendance_col].idxmax()]
print(highest_attendance_row)

avg_cgpa = final_df['CGPA'].mean()
print(f"Average CGPA of all students: {avg_cgpa:.2f}")  

attendance_col = 'Attendance_Percentage' if 'Attendance_Percentage' in final_df.columns else 'Attendance'

avg_attendance = final_df[attendance_col].mean()
print(f"Average Attendance Percentage: {avg_attendance:.2f}%")

dept_cgpa = final_df.groupby('Department')['CGPA'].mean()
print(dept_cgpa)

attendance_col = 'Attendance_Percentage' if 'Attendance_Percentage' in final_df.columns else 'Attendance'

dept_attendance = final_df.groupby('Department')[attendance_col].mean()
print(dept_attendance)

placed_count = final_df[final_df['Company'] != "Not Placed"].shape[0]
print(f"Total number of placed students: {placed_count}")

highest_salary_row = final_df.loc[final_df['Salary_LPA'].idxmax()]
print(f"Company: {highest_salary_row['Company']} | Package: {highest_salary_row['Salary_LPA']} LPA")

attendance_col = 'Attendance_Percentage' if 'Attendance_Percentage' in final_df.columns else 'Attendance'

low_attendance_students = final_df[final_df[attendance_col] < 85]
print(low_attendance_students)

high_cgpa_students = final_df[final_df['CGPA'] > 8.5]
print(high_cgpa_students)

placed_students = final_df[final_df['Company'] != "Not Placed"].shape[0]
total_students = len(final_df)

placement_percentage = (placed_students / total_students) * 100
print(f"Placement Percentage: {placement_percentage:.2f}%")

active_lms_count = final_df[final_df['LMS_Active'] == True].shape[0]
print(f"Number of students actively using the LMS platform: {active_lms_count}")

plt.figure(figsize=(8, 5))
sns.barplot(data=final_df, x='Department', y='CGPA', errorbar=None, palette="Blues_d")
plt.title('Department-wise Average CGPA')
plt.ylabel('Average CGPA')
plt.tight_layout()
plt.show()

attendance_col = 'Attendance_Percentage' if 'Attendance_Percentage' in final_df.columns else 'Attendance'

plt.figure(figsize=(8, 5))
sns.barplot(data=final_df, x='Department', y=attendance_col, errorbar=None, palette="Greens_d")
plt.title('Department-wise Average Attendance')
plt.ylabel('Average Attendance (%)')
plt.tight_layout()
plt.show()

attendance_col = 'Attendance_Percentage' if 'Attendance_Percentage' in final_df.columns else 'Attendance'

plt.figure(figsize=(8, 5))
sns.histplot(data=final_df, x=attendance_col, kde=True, color="purple", bins=15)
plt.title('Attendance Distribution')
plt.xlabel('Attendance (%)')
plt.tight_layout()
plt.show()

plt.figure(figsize=(6, 6))
placed_num = final_df[final_df['Company'] != "Not Placed"].shape[0]
unplaced_num = len(final_df) - placed_num

plt.pie([placed_num, unplaced_num], labels=['Placed', 'Not Placed'], autopct='%1.1f%%', colors=['#66b3ff','#ff9999'], startangle=90)
plt.title('Placed vs. Non-Placed Students')
plt.tight_layout()
plt.show()

final_df.to_csv("student_analytics.csv", index=False)
print("Saved final integrated data to student_analytics.csv")

# Department Average CGPA Bar Chart
plt.figure(figsize=(8, 5))
sns.barplot(data=final_df, x='Department', y='CGPA', errorbar=None, palette="Blues_d")
plt.title('Department-wise Average CGPA')
plt.tight_layout()
plt.savefig('dept_avg_cgpa.png')
plt.close()

# Department Average Attendance Bar Chart
plt.figure(figsize=(8, 5))
sns.barplot(data=final_df, x='Department', y=attendance_col, errorbar=None, palette="Greens_d")
plt.title('Department-wise Average Attendance')
plt.tight_layout()
plt.savefig('dept_avg_attendance.png')
plt.close()

# Attendance Distribution Histogram
plt.figure(figsize=(8, 5))
sns.histplot(data=final_df, x=attendance_col, kde=True, color="purple")
plt.title('Attendance Distribution')
plt.tight_layout()
plt.savefig('attendance_distribution.png')
plt.close()

# Placement State Pie Chart
plt.figure(figsize=(6, 6))
plt.pie([placed_num, unplaced_num], labels=['Placed', 'Not Placed'], autopct='%1.1f%%', colors=['#66b3ff','#ff9999'], startangle=90)
plt.title('Placed vs. Non-Placed Students')
plt.tight_layout()
plt.savefig('placement_pie_chart.png')
plt.close()

print("All charts have been written successfully to your execution directory!")