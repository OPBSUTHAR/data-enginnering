import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import os

# =====================================================================
# DATA ENGINEERING ENGINE: AUDIT, INTEGRATION & CLEANING
# =====================================================================
def run_data_engineering_pipeline():
    """Ingests raw laboratory datasets, performs structural quality audits, 
    and handles missing values securely through relational integration."""
    
    students_file = "students.csv"
    placements_file = "placements.csv"
    lms_file = "lms.json"
    attendance_file = "attendance.xlsx - Sheet1.csv" if os.path.exists("attendance.xlsx - Sheet1.csv") else "attendance.xlsx"

    missing_files = [f for f in [students_file, attendance_file, placements_file, lms_file] if not os.path.exists(f)]
    if missing_files:
        root_temp = tk.Tk()
        root_temp.withdraw()
        messagebox.showerror(
            "Ingestion Halt: Missing Assets", 
            f"The pipeline could not find these files in the working directory:\n{', '.join(missing_files)}"
        )
        raise FileNotFoundError(f"Missing files: {missing_files}")

    # Extract Phase (Ingestion) [cite: 9]
    df_students = pd.read_csv(students_file)
    df_attendance = pd.read_csv(attendance_file) if attendance_file.endswith('.csv') else pd.read_excel(attendance_file)
    df_placements = pd.read_csv(placements_file)
    df_lms = pd.read_json(lms_file)

    # Profiling Phase (Quality Auditing) [cite: 46]
    pre_merge_audit = {}
    for name, df in [("Students", df_students), ("Attendance", df_attendance), ("Placements", df_placements), ("LMS", df_lms)]:
        null_counts = df.isnull().sum()
        pre_merge_audit[name] = null_counts[null_counts > 0].to_dict()

    global att_col
    att_col = 'Attendance_Percentage' if 'Attendance_Percentage' in df_attendance.columns else \
              ('Attendance' if 'Attendance' in df_attendance.columns else df_attendance.select_dtypes(include=['float', 'int']).columns[0])

    student_keys = set(df_students['Student_ID'])
    lms_orphans = list(student_keys - set(df_lms['Student_ID']))
    placement_orphans = list(student_keys - set(df_placements['Student_ID']))

    # Transform & Load Phase (Data Integration & Cleaning) [cite: 58, 74]
    m1 = pd.merge(df_students, df_attendance, on='Student_ID', how='left')
    m2 = pd.merge(m1, df_placements, on='Student_ID', how='left')
    final_df = pd.merge(m2, df_lms, on='Student_ID', how='left')

    post_merge_null_audit = final_df.isnull().sum().to_dict()

    # Data Engineering Imputations [cite: 76, 78, 80]
    if 'Company' in final_df.columns:
        final_df['Company'] = final_df['Company'].fillna("Not Placed")
    if 'Salary_LPA' in final_df.columns:
        final_df['Salary_LPA'] = pd.to_numeric(final_df['Salary_LPA'], errors='coerce').fillna(0.0)
    if 'Videos_Watched' in final_df.columns:
        final_df['Videos_Watched'] = pd.to_numeric(final_df['Videos_Watched'], errors='coerce').fillna(0).astype(int)
    if 'Assignments_Submitted' in final_df.columns:
        final_df['Assignments_Submitted'] = pd.to_numeric(final_df['Assignments_Submitted'], errors='coerce').fillna(0).astype(int)

    final_df['CGPA'] = pd.to_numeric(final_df['CGPA'], errors='coerce').fillna(0.0)
    if att_col in final_df.columns:
        final_df[att_col] = pd.to_numeric(final_df[att_col], errors='coerce').fillna(0.0)

    final_df['LMS_Active'] = final_df['Videos_Watched'] > 0 # [cite: 82]

    return df_students, df_attendance, df_placements, df_lms, final_df, pre_merge_audit, post_merge_null_audit, lms_orphans, placement_orphans

# Initialize Engine
raw_student, raw_att, raw_place, raw_lms, integrated_df, pre_audit, post_audit, lms_miss, place_miss = run_data_engineering_pipeline()


# =====================================================================
# DESKTOP INTERFACE CONFIGURATIONS
# =====================================================================
root = tk.Tk()
root.title("Advanced Data Engineering Workspace & Multi-Visual Analytics Dashboard")
root.geometry("1400x900")

style = ttk.Style()
style.theme_use('clam')
style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[12, 6])
style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#1a365d')

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=5, pady=5)

def build_grid(parent, df):
    frame = ttk.Frame(parent)
    frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    tree = ttk.Treeview(frame, columns=list(df.columns), show='headings', height=8)
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    for col in df.columns:
        tree.heading(col, text=col, anchor='center')
        tree.column(col, width=120, anchor='center')
        
    for _, row in df.iterrows():
        tree.insert("", tk.END, values=[str(x) if pd.notnull(x) else "NaN" for x in row])
        
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

# ---------------------------------------------------------------------
# TAB 1: Source Data Audits & Quality Control (Part C)
# ---------------------------------------------------------------------
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="🔎 Part C: Pre-Merge Quality Audit")

lbl1 = ttk.Label(tab1, text="Data Quality & Integrity Validation Framework Logs", style='Header.TLabel')
lbl1.pack(pady=10, padx=10, anchor='w')

audit_box = tk.Text(tab1, font=('Consolas', 11), bg='#fafafa', fg='#2c3e50', wrap='word', padx=10, pady=10)
audit_box.pack(fill='both', expand=True, padx=10, pady=5)

report_txt = f"=======================================================================================\n" \
             f"DATA PIPELINE PRE-INTEGRATION COMPLIANCE & NULL VALUE AUDIT REPORT\n" \
             f"=======================================================================================\n\n" \
             f"[STEP 1] INDIVIDUAL RAW FILE SOURCE DATA REPORT:\n" \
             f"---------------------------------------------------------------------------------------\n"
for source, anomalies in pre_audit.items():
    if anomalies:
        report_txt += f" ❌ Source table '{source}' contains unmapped missing rows:\n"
        for col, count in anomalies.items():
            report_txt += f"    └── Attribute '{col}': {count} missing elements discovered.\n"
    else:
        report_txt += f"  Core source profile framework cleanly tracked for '{source}' (0 missing values).\n"

report_txt += f"\n[STEP 2] REFERENTIAL INTEGRITY ORPHAN DISCOVERY AUDIT:\n" \
             f"---------------------------------------------------------------------------------------\n" \
             f" ⚡ LMS Tracking Records Discrepancy: {len(lms_miss)} missing entries in 'lms.json'.\n" \
             f"    └── Orphan Student IDs: {lms_miss if lms_miss else 'None'}\n" \
             f" ⚡ Career Placement Log Discrepancy: {len(place_miss)} missing entries in 'placements.csv'.\n" \
             f"    └── Unmapped Student IDs: {place_miss if place_miss else 'None'}\n\n" \
             f"[STEP 3] INTEGRATED JOINS STORAGE VARIANCE:\n" \
             f"---------------------------------------------------------------------------------------\n"

for col, count in post_audit.items():
    report_txt += f"   • Destination Field '{col}': {count} null values generated via relational joins.\n"

audit_box.insert(tk.END, report_txt)
audit_box.config(state='disabled')

# ---------------------------------------------------------------------
# TAB 2: Cleaned Data Warehouse Explorer & Advanced Filtering Suite
# ---------------------------------------------------------------------
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="⚙️ Parts D, E & F: Analytical Warehouse State")

control_panel = ttk.Frame(tab2, width=340, padding=10)
control_panel.pack(side='left', fill='y', padx=5, pady=5)

warehouse_panel = ttk.Frame(tab2, padding=10)
warehouse_panel.pack(side='right', fill='both', expand=True, padx=5, pady=5)

ttk.Label(warehouse_panel, text="Unified Integrated Data Warehouse State Matrix", style='Header.TLabel').pack(anchor='w', pady=5)

cgpa_filter = tk.StringVar(value="All")
att_filter = tk.StringVar(value="All")
lms_filter = tk.StringVar(value="All")

def execute_combined_filters():
    for item in main_tree.get_children():
        main_tree.delete(item)
    df = integrated_df.copy()
    
    c_sel = cgpa_filter.get()
    if 'CGPA' in df.columns:
        if c_sel == "High Tier (> 8.5)": df = df[df['CGPA'] > 8.5]
        elif c_sel == "Medium Tier (6.5 - 8.5)": df = df[(df['CGPA'] >= 6.5) & (df['CGPA'] <= 8.5)]
        elif c_sel == "Low Tier (< 6.5)": df = df[df['CGPA'] < 6.5]
        
    a_sel = att_filter.get()
    if att_col and att_col in df.columns:
        if a_sel == "High Attendance (> 90%)": df = df[df[att_col] > 90]
        elif a_sel == "Medium Attendance (75% - 90%)": df = df[(df[att_col] >= 75) & (df[att_col] <= 90)]
        elif a_sel == "Low Attendance (< 75%)": df = df[df[att_col] < 75]
        
    l_sel = lms_filter.get()
    if 'Videos_Watched' in df.columns:
        if l_sel == "High Active (> 20 videos)": df = df[df['Videos_Watched'] > 20]
        elif l_sel == "Moderate Active (1 - 20)": df = df[(df['Videos_Watched'] >= 1) & (df['Videos_Watched'] <= 20)]
        elif l_sel == "Inactive Users (0 videos)": df = df[df['Videos_Watched'] == 0]
        
    for _, row in df.iterrows():
        main_tree.insert("", tk.END, values=[str(x) for x in row])
    lbl_counter.config(text=f"Rows Filtered: {len(df)} of {len(integrated_df)} Records")

ttk.Label(control_panel, text="Cohort Performance Filters", font=('Segoe UI', 12, 'bold'), foreground='#1a365d').pack(anchor='w', pady=5)

lbl_cg = ttk.LabelFrame(control_panel, text=" Academic CGPA Scale Tiers ", padding=5)
lbl_cg.pack(fill='x', pady=5)
for text in ["All", "High Tier (> 8.5)", "Medium Tier (6.5 - 8.5)", "Low Tier (< 6.5)"]:
    ttk.Radiobutton(lbl_cg, text=text, variable=cgpa_filter, value=text, command=execute_combined_filters).pack(anchor='w')

lbl_at = ttk.LabelFrame(control_panel, text=" Attendance Operational Tiers ", padding=5)
lbl_at.pack(fill='x', pady=5)
for text in ["All", "High Attendance (> 90%)", "Medium Attendance (75% - 90%)", "Low Attendance (< 75%)"]:
    ttk.Radiobutton(lbl_at, text=text, variable=att_filter, value=text, command=execute_combined_filters).pack(anchor='w')

lbl_lm = ttk.LabelFrame(control_panel, text=" Platform LMS Interaction Activity ", padding=5)
lbl_lm.pack(fill='x', pady=5)
for text in ["All", "High Active (> 20 videos)", "Moderate Active (1 - 20)", "Inactive Users (0 videos)"]:
    ttk.Radiobutton(lbl_lm, text=text, variable=lms_filter, value=text, command=execute_combined_filters).pack(anchor='w')

lbl_counter = ttk.Label(control_panel, text="", font=('Segoe UI', 10, 'italic', 'bold'), foreground='#2c3e50')
lbl_counter.pack(pady=15)

main_tree_frame = ttk.Frame(warehouse_panel)
main_tree_frame.pack(fill='both', expand=True, pady=5)

main_tree = ttk.Treeview(main_tree_frame, columns=list(integrated_df.columns), show='headings')
m_vsb = ttk.Scrollbar(main_tree_frame, orient="vertical", command=main_tree.yview)
m_hsb = ttk.Scrollbar(main_tree_frame, orient="horizontal", command=main_tree.xview)
main_tree.configure(yscrollcommand=m_vsb.set, xscrollcommand=m_hsb.set)

for col in integrated_df.columns:
    main_tree.heading(col, text=col)
    main_tree.column(col, width=110, anchor='center')

main_tree.grid(row=0, column=0, sticky='nsew')
m_vsb.grid(row=0, column=1, sticky='ns')
m_hsb.grid(row=1, column=0, sticky='ew')
main_tree_frame.grid_columnconfigure(0, weight=1)
main_tree_frame.grid_rowconfigure(0, weight=1)

execute_combined_filters()

# ---------------------------------------------------------------------
# TAB 3: Visual Analytics Room (Parts G & H) - 6 simultanous charts!
# ---------------------------------------------------------------------
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="📊 Part G & H: Visual Analytics Matrix")

top_bar = ttk.Frame(tab3)
top_bar.pack(fill='x', side='top', pady=5, padx=10)

def trigger_export():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="student_analytics.csv", filetypes=[("CSV File", "*.csv")])
    if file_path:
        integrated_df.to_csv(file_path, index=False)
        messagebox.showinfo("Export Automation", f"Clean data warehouse successfully written out:\n{file_path}")

ttk.Button(top_bar, text="📥 Save Final Cleaned Warehouse State (student_analytics.csv)", command=trigger_export).pack(side='left', padx=5)

# Container for the 2x3 Plot Grid Layout Frame
scroll_canvas = tk.Canvas(tab3)
scrollbar_y = ttk.Scrollbar(tab3, orient="vertical", command=scroll_canvas.yview)
grid_frame = ttk.Frame(scroll_canvas)

grid_frame.bind(
    "<Configure>",
    lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
)
scroll_canvas.create_window((0, 0), window=grid_frame, anchor="nw")
scroll_canvas.configure(yscrollcommand=scrollbar_y.set)

scroll_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
scrollbar_y.pack(side="right", fill="y")

def generate_analytical_plots():
    sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(13, 11))
    
    has_dept = 'Department' in integrated_df.columns
    has_cgpa = 'CGPA' in integrated_df.columns
    
    # Chart 1: Department-wise Average CGPA (Q35)
    ax1 = fig.add_subplot(3, 2, 1)
    if has_dept and has_cgpa:
        sns.barplot(data=integrated_df, x='Department', y='CGPA', ax=ax1, palette="Blues_d", errorbar=None)
    ax1.set_title("1. Department-wise Average CGPA (Q35)", fontsize=10, weight='bold')
    ax1.set_ylabel("Avg CGPA")
    
    # Chart 2: Department-wise Average Attendance % (Q36)
    ax2 = fig.add_subplot(3, 2, 2)
    if has_dept and att_col and att_col in integrated_df.columns:
        sns.barplot(data=integrated_df, x='Department', y=att_col, ax=ax2, palette="Greens_d", errorbar=None)
    ax2.set_title("2. Department-wise Average Attendance % (Q36)", fontsize=10, weight='bold')
    ax2.set_ylabel("Avg Attendance %")
    
    # Chart 3: Cohort Attendance Distribution Density Histogram (Q37)
    ax3 = fig.add_subplot(3, 2, 3)
    if att_col and att_col in integrated_df.columns:
        sns.histplot(data=integrated_df, x=att_col, kde=True, color="purple", bins=8, ax=ax3)
    ax3.set_title("3. Cohort Attendance Density Distribution (Q37)", fontsize=10, weight='bold')
    
    # Chart 4: Corporate Placement Distribution Ratio Pie Chart (Q38)
    ax4 = fig.add_subplot(3, 2, 4)
    if 'Company' in integrated_df.columns:
        p_count = integrated_df[integrated_df['Company'] != "Not Placed"].shape[0]
        up_count = len(integrated_df) - p_count
        ax4.pie([p_count, up_count], labels=['Placed', 'Not Placed'], autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], startangle=140)
    ax4.set_title("4. Corporate Placement Distribution Ratio (Q38)", fontsize=10, weight='bold')
    
    # Chart 5: NEW ANALYSIS - CGPA vs Attendance Percentage Scatter Plot
    ax5 = fig.add_subplot(3, 2, 5)
    if has_cgpa and att_col and att_col in integrated_df.columns:
        sns.scatterplot(data=integrated_df, x=att_col, y='CGPA', hue='Department', palette="Set2", s=80, ax=ax5)
    ax5.set_title("5. CGPA vs Attendance Correlation Matrix", fontsize=10, weight='bold')
    
    # Chart 6: NEW ANALYSIS - Average LMS Activity across Departments
    ax6 = fig.add_subplot(3, 2, 6)
    if has_dept and 'Videos_Watched' in integrated_df.columns:
        sns.barplot(data=integrated_df, x='Department', y='Videos_Watched', ax=ax6, palette="Oranges_d", errorbar=None)
    ax6.set_title("6. Departmental LMS System Activity Profile", fontsize=10, weight='bold')
    ax6.set_ylabel("Avg Videos Watched")

    fig.tight_layout()
    
    # Save step matching script assignment parameters (Question 40 verification rule)
    fig.savefig('executive_analytics_report.png', dpi=180)
    
    canvas = FigureCanvasTkAgg(fig, master=grid_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    plt.close(fig)

# Render the 6 charts concurrently
generate_analytical_plots()

root.mainloop()