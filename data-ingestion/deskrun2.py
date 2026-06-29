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
    
    # 1. Workspace Configuration & File Path Resolution
    students_file = "students.csv"
    placements_file = "placements.csv"
    lms_file = "lms.json"
    
    # Resolving variations in user naming for the attendance spreadsheet export
    attendance_file = "attendance.xlsx - Sheet1.csv" if os.path.exists("attendance.xlsx - Sheet1.csv") else "attendance.xlsx"

    missing_files = [f for f in [students_file, attendance_file, placements_file, lms_file] if not os.path.exists(f)]
    if missing_files:
        root_temp = tk.Tk()
        root_temp.withdraw()
        messagebox.showerror(
            "Ingestion Halt: Missing Assets", 
            f"The pipeline could not find these files in the working directory:\n{', '.join(missing_files)}\n\n"
            f"Current working directory: {os.getcwd()}"
        )
        raise FileNotFoundError(f"Missing files: {missing_files}")

    # 2. Extract Phase (Data Ingestion)
    df_students = pd.read_csv(students_file)
    df_attendance = pd.read_csv(attendance_file) if attendance_file.endswith('.csv') else pd.read_excel(attendance_file)
    df_placements = pd.read_csv(placements_file)
    df_lms = pd.read_json(lms_file)

    # 3. Profiling Phase (Data Quality Auditing)
    # Track raw null records before structural merges happen
    pre_merge_audit = {}
    for name, df in [("Students", df_students), ("Attendance", df_attendance), ("Placements", df_placements), ("LMS", df_lms)]:
        null_counts = df.isnull().sum()
        pre_merge_audit[name] = null_counts[null_counts > 0].to_dict()

    # Identify primary tracking keys and resolve attendance column names dynamically
    global att_col
    att_col = 'Attendance_Percentage' if 'Attendance_Percentage' in df_attendance.columns else \
              ('Attendance' if 'Attendance' in df_attendance.columns else df_attendance.select_dtypes(include=['float', 'int']).columns[0])

    # Referential Integrity Check: Track orphans across application operational logs
    student_keys = set(df_students['Student_ID'])
    lms_orphans = list(student_keys - set(df_lms['Student_ID']))
    placement_orphans = list(student_keys - set(df_placements['Student_ID']))

    # 4. Transform & Load Phase (Relational Integration Pipeline)
    # Left join onto master student matrix ensures no core profile is discarded
    m1 = pd.merge(df_students, df_attendance, on='Student_ID', how='left')
    m2 = pd.merge(m1, df_placements, on='Student_ID', how='left')
    final_df = pd.merge(m2, df_lms, on='Student_ID', how='left')

    # Capture state of missing values introduced via left-joins (unmapped records)
    post_merge_null_audit = final_df.isnull().sum().to_dict()

    # Expert Imputation & Cleaning Rules (Handling anomalies safely)
    final_df['Company'] = final_df['Company'].fillna("Not Placed")
    final_df['Salary_LPA'] = pd.to_numeric(final_df['Salary_LPA'], errors='coerce').fillna(0.0)
    
    if 'Videos_Watched' in final_df.columns:
        final_df['Videos_Watched'] = pd.to_numeric(final_df['Videos_Watched'], errors='coerce').fillna(0).astype(int)
    if 'Assignments_Submitted' in final_df.columns:
        final_df['Assignments_Submitted'] = pd.to_numeric(final_df['Assignments_Submitted'], errors='coerce').fillna(0).astype(int)

    # Clean up CGPA and Attendance numerical anomalies if missing from source sheets
    final_df['CGPA'] = pd.to_numeric(final_df['CGPA'], errors='coerce').fillna(0.0)
    if att_col in final_df.columns:
        final_df[att_col] = pd.to_numeric(final_df[att_col], errors='coerce').fillna(0.0)

    # Feature Engineering: Derive operational KPI flags
    final_df['LMS_Active'] = final_df['Videos_Watched'] > 0

    return df_students, df_attendance, df_placements, df_lms, final_df, pre_merge_audit, post_merge_null_audit, lms_orphans, placement_orphans

# Initialize Data Engineering Engine
raw_student, raw_att, raw_place, raw_lms, integrated_df, pre_audit, post_audit, lms_miss, place_miss = run_data_engineering_pipeline()


# =====================================================================
# INTERACTIVE WORKSTATION WORKSPACE WINDOW FRAME SETUP
# =====================================================================
root = tk.Tk()
root.title("Advanced Data Engineering Workstation & Validation Dashboard")
root.geometry("1400x850")

# Apply interface elements color mapping configurations
style = ttk.Style()
style.theme_use('clam')
style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[12, 6])
style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#1a365d')
style.configure('Alert.TLabel', font=('Segoe UI', 10, 'bold'), foreground='#c0392b')

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=5, pady=5)

def build_grid(parent, df):
    """Generates scrollable tree spreadsheets to view underlying structures."""
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
# TAB 1: Source Data Audits & Quality Control
# ---------------------------------------------------------------------
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="🔎 Part C: Pre-Merge Quality Audit")

lbl1 = ttk.Label(tab1, text="Data Quality & Integrity Validation Framework Logs", style='Header.TLabel')
lbl1.pack(pady=10, padx=10, anchor='w')

audit_box = tk.Text(tab1, font=('Consolas', 11), bg='#fafafa', fg='#2c3e50', wrap='word', padding=10)
audit_box.pack(fill='both', expand=True, padx=10, pady=5)

# Formatting clear, detailed textual audit feedback logs
report_txt = f"""=======================================================================================
DATA PIPELINE PRE-INTEGRATION COMPLIANCE & NULL VALUE AUDIT REPORT
=======================================================================================

[STEP 1] INDIVIDUAL RAW FILE SOURCE AMISS REPORT:
---------------------------------------------------------------------------------------
"""
for source, anomalies in pre_audit.items():
    if anomalies:
        report_txt += f" ❌ Source table '{source}' contains unmapped missing rows:\n"
        for col, count in anomalies.items():
            report_txt += f"    └── Attribute '{col}': {count} missing elements discovered.\n"
    else:
        report_txt += f"  Core source profile framework cleanly tracked for '{source}' (0 missing values).\n"

report_txt += f"""
[STEP 2] REFERENTIAL INTEGRITY ORPHAN DISCOVERY AUDIT:
---------------------------------------------------------------------------------------
The tracking key framework discovered unmapped records between our primary registry table
and backend operation transactional event systems.

 ⚡ LMS Tracking Records Discrepancy:
    {len(lms_miss)} student profile IDs are missing activity signatures in 'lms.json'.
    └── Orphan Student IDs: {lms_miss if lms_miss else 'None'}

 ⚡ Career Placement Log Discrepancy:
    {len(place_miss)} student profiles do not contain entries inside 'placements.csv'.
    └── Unmapped Student IDs: {place_miss if place_miss else 'None'}

[STEP 3] INDUCED LEFT JOIN STORAGE VARIANCE (POST-INTEGRATION NULL AUDIT):
---------------------------------------------------------------------------------------
When structural data warehouse integration combined the four subsystems via LEFT JOIN parameters, 
the missing records were securely tracked and materialized as the following system null pools:
\n"""

for col, count in post_audit.items():
    report_txt += f"   • Destination Attribute Field '{col}': {count} null values generated.\n"

report_txt += """\n=======================================================================================
[DATA ENGINEERING PIPELINE ACTION]: The workstation has dynamically cleaned these anomalies.
All text strings have defaulted to 'Not Placed', and missing numeric values have been imputed to '0' or '0.0'.
======================================================================================="""

audit_box.insert(tk.END, report_txt)
audit_box.config(state='disabled')


# ---------------------------------------------------------------------
# TAB 2: Cleaned Data Warehouse Explorer & Advanced Filtering Suite
# ---------------------------------------------------------------------
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="⚙️ Parts D, E & F: Analytical Warehouse State")

# Split panels setup
control_panel = ttk.Frame(tab2, width=340, padding=10)
control_panel.pack(side='left', fill='y', padx=5, pady=5)

warehouse_panel = ttk.Frame(tab2, padding=10)
warehouse_panel.pack(side='right', fill='both', expand=True, padx=5, pady=5)

ttk.Label(warehouse_panel, text="Unified Analytical Warehouse State (Post-Cleaning Imputations)", style='Header.TLabel').pack(anchor='w', pady=5)

# Selection parameters config setup
cgpa_filter = tk.StringVar(value="All")
att_filter = tk.StringVar(value="All")
lms_filter = tk.StringVar(value="All")

def execute_combined_filters():
    """Combines multi-variable choices to dynamically slice data tiers."""
    for item in main_tree.get_children():
        main_tree.delete(item)
        
    df = integrated_df.copy()
    
    # Tier 1 filtering check: CGPA scales
    c_sel = cgpa_filter.get()
    if 'CGPA' in df.columns:
        if c_sel == "High Tier (> 8.5)": df = df[df['CGPA'] > 8.5]
        elif c_sel == "Medium Tier (6.5 - 8.5)": df = df[(df['CGPA'] >= 6.5) & (df['CGPA'] <= 8.5)]
        elif c_sel == "Low Tier (< 6.5)": df = df[df['CGPA'] < 6.5]
        
    # Tier 2 filtering check: Attendance percentage bounds
    a_sel = att_filter.get()
    if att_col and att_col in df.columns:
        if a_sel == "High Attendance (> 90%)": df = df[df[att_col] > 90]
        elif a_sel == "Medium Attendance (75% - 90%)": df = df[(df[att_col] >= 75) & (df[att_col] <= 90)]
        elif a_sel == "Low Attendance (< 75%)": df = df[df[att_col] < 75]
        
    # Tier 3 filtering check: Video metrics views activity
    l_sel = lms_filter.get()
    if 'Videos_Watched' in df.columns:
        if l_sel == "High Active (> 20 videos)": df = df[df['Videos_Watched'] > 20]
        elif l_sel == "Moderate Active (1 - 20)": df = df[(df['Videos_Watched'] >= 1) & (df['Videos_Watched'] <= 20)]
        elif l_sel == "Inactive Users (0 videos)": df = df[df['Videos_Watched'] == 0]
        
    for _, row in df.iterrows():
        main_tree.insert("", tk.END, values=[str(x) for x in row])
        
    lbl_counter.config(text=f"Rows Filtered: {len(df)} of {len(integrated_df)} Records")

# Building the interactive sidebar control interface layout
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

# Primary central table layout execution mapping
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
# TAB 3: Visual Reporting Analytics Suites (Parts G & H)
# ---------------------------------------------------------------------
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="📊 Part G & H: Visual Analytics Room")

top_bar = ttk.Frame(tab3)
top_bar.pack(fill='x', side='top', pady=5, padx=10)

def trigger_export():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="student_analytics.csv", filetypes=[("CSV File", "*.csv")])
    if file_path:
        integrated_df.to_csv(file_path, index=False)
        messagebox.showinfo("Export Automation", f"Clean warehouse output written to:\n{file_path}")

ttk.Button(top_bar, text="📥 Save Final Cleaned Warehouse Matrix State (student_analytics.csv)", command=trigger_export).pack(side='left', padx=5)

chart_var = tk.StringVar(value="Departmental Comparisons (Q35 & Q36)")
chart_canvas_frame = ttk.Frame(tab3)
chart_canvas_frame.pack(fill='both', expand=True, padx=10, pady=5)

def render_selected_chart_node(*args):
    for widget in chart_canvas_frame.winfo_children():
        widget.destroy()
        
    choice = chart_var.get()
    sns.set_theme(style="whitegrid")
    
    has_dept = 'Department' in integrated_df.columns
    has_cgpa = 'CGPA' in integrated_df.columns
    
    if choice == "Departmental Comparisons (Q35 & Q36)":
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
        if has_dept and has_cgpa:
            sns.barplot(data=integrated_df, x='Department', y='CGPA', ax=ax1, palette="Blues_d", errorbar=None)
        ax1.set_title("Department-wise Average CGPA (Q35)")
        
        if has_dept and att_col and att_col in integrated_df.columns:
            sns.barplot(data=integrated_df, x='Department', y=att_col, ax=ax2, palette="Greens_d", errorbar=None)
        ax2.set_title("Department-wise Average Attendance % (Q36)")
        
    elif choice == "Cohort Attendance Density Profile (Q37)":
        fig, ax = plt.subplots(figsize=(10, 4.5))
        if att_col and att_col in integrated_df.columns:
            sns.histplot(data=integrated_df, x=att_col, kde=True, color="purple", bins=10, ax=ax)
        ax.set_title("Cohort Attendance Distribution Histogram (Q37)")
        
    else:
        fig, ax = plt.subplots(figsize=(6, 4.5))
        if 'Company' in integrated_df.columns:
            p_count = integrated_df[integrated_df['Company'] != "Not Placed"].shape[0]
            up_count = len(integrated_df) - p_count
            ax.pie([p_count, up_count], labels=['Placed', 'Not Placed'], autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], startangle=140)
        ax.set_title("Corporate Placement Distribution Ratio (Q38)")

    fig.tight_layout()
    fig.savefig('dashboard_report_snapshot.png', dpi=150)
    
    canvas = FigureCanvasTkAgg(fig, master=chart_canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    plt.close(fig)

ttk.Label(top_bar, text="  Select Active Visualization: ").pack(side='left', padx=5)
chart_selector = ttk.Combobox(top_bar, textvariable=chart_var, values=[
    "Departmental Comparisons (Q35 & Q36)",
    "Cohort Attendance Density Profile (Q37)",
    "Corporate Placement Distribution Ratio (Q38)"
], width=45, state="readonly")
chart_selector.pack(side='left', padx=5)
chart_selector.bind("<<ComboboxSelected>>", render_selected_chart_node)

render_selected_chart_node()
root.mainloop()