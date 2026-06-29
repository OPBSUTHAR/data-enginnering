import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

# =====================================================================
# DATA ENGINEERING PIPELINE LOGIC (Parts A to E)
# =====================================================================
def run_pipeline():
    # Source structures reflecting lab document specifications
    students_df = pd.DataFrame({
        'Student_ID': [101, 102, 103, 104, 105],
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
        'Department': ['CSE', 'ECE', 'CSE', 'ME', 'ECE'],
        'CGPA': [8.9, 7.8, 9.2, 6.5, 8.6]
    })
    
    attendance_df = pd.DataFrame({
        'Student_ID': [101, 102, 103, 104, 105],
        'Attendance_Percentage': [92, 84, 95, 78, 88]
    })
    
    placements_df = pd.DataFrame({
        'Student_ID': [101, 103, 105],
        'Company': ['Tech Corp', 'Global Solutions', 'Innovate LLC'],
        'Salary_LPA': [12.5, 18.0, 10.2]
    })
    
    lms_df = pd.DataFrame({
        'Student_ID': [101, 102, 104, 105],
        'Videos_Watched': [15, 0, 8, 22],
        'Assignments_Submitted': [4, 0, 2, 5]
    })
    
    # Part D & E Integration & Feature Engineering
    m1 = pd.merge(students_df, attendance_df, on='Student_ID', how='left')
    m2 = pd.merge(m1, placements_df, on='Student_ID', how='left')
    final_df = pd.merge(m2, lms_df, on='Student_ID', how='left')
    
    final_df['Company'] = final_df['Company'].fillna("Not Placed")
    final_df['Salary_LPA'] = final_df['Salary_LPA'].fillna(0.0)
    final_df['Videos_Watched'] = final_df['Videos_Watched'].fillna(0)
    final_df['Assignments_Submitted'] = final_df['Assignments_Submitted'].fillna(0)
    final_df['LMS_Active'] = final_df['Videos_Watched'] > 0
    
    return students_df, attendance_df, placements_df, lms_df, final_df

raw_student, raw_att, raw_place, raw_lms, integrated_df = run_pipeline()

# =====================================================================
# INTERACTIVE DESKTOP INTERFACE WORKSPACE
# =====================================================================
root = tk.Tk()
root.title("Advanced Student Analytics Data Engineering Pipeline Dashboard")
root.geometry("1280x800")

# Setup UI Styling themes
style = ttk.Style()
style.theme_use('clam')
style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[10, 5])
style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#1a365d')

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=5, pady=5)

def build_grid(parent, df):
    """Helper framework function to build crisp, highly scannable grid layouts."""
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
        tree.insert("", tk.END, values=list(row))
        
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')
    
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

# ---------------------------------------------------------------------
# TAB 1: Source Ingestion Inventories (Parts A & B)
# ---------------------------------------------------------------------
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="📂 Part A & B: Source Ingestion Layers")

lbl1 = ttk.Label(tab1, text="Ingested Tabular Profiles & Schema Framework Configurations", style='Header.TLabel')
lbl1.pack(pady=10, padx=10, anchor='w')

paned = ttk.Panedwindow(tab1, orient=tk.VERTICAL)
paned.pack(fill='both', expand=True, padx=10, pady=5)

# Upper Splitting Deck (Students & Attendance)
frame_top = ttk.Frame(paned)
lbl_s = ttk.Label(frame_top, text="students.csv Registry Ingestion", font=('Segoe UI', 10, 'bold'))
lbl_s.pack(anchor='w', padx=5)
build_grid(frame_top, raw_student)

lbl_a = ttk.Label(frame_top, text="attendance.xlsx Sheet Ingestion", font=('Segoe UI', 10, 'bold'))
lbl_a.pack(anchor='w', padx=5, pady=(10,0))
build_grid(frame_top, raw_att)
paned.add(frame_top, weight=1)

# Lower Splitting Deck (Placements & LMS logs)
frame_bottom = ttk.Frame(paned)
lbl_p = ttk.Label(frame_bottom, text="placements.csv Stream Ingestion", font=('Segoe UI', 10, 'bold'))
lbl_p.pack(anchor='w', padx=5)
build_grid(frame_bottom, raw_place)

lbl_l = ttk.Label(frame_bottom, text="lms.json Unstructured Interaction Log", font=('Segoe UI', 10, 'bold'))
lbl_l.pack(anchor='w', padx=5, pady=(10,0))
build_grid(frame_bottom, raw_lms)
paned.add(frame_bottom, weight=1)

# ---------------------------------------------------------------------
# TAB 2: Dynamic Analytics and Integration (Parts C, D, E & F)
# ---------------------------------------------------------------------
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="⚙️ Part C to F: Warehouse Pipeline & Metrics")

# Left Column Layout Control Panel
left_panel = ttk.Frame(tab2, width=350)
left_panel.pack(side='left', fill='y', padx=10, pady=10)

# Right Column Integrated Table Display Window Frame
right_panel = ttk.Frame(tab2)
right_panel.pack(side='right', fill='both', expand=True, padx=10, pady=10)

ttk.Label(right_panel, text="Final Integrated and Cleaned Data Warehouse State", style='Header.TLabel').pack(anchor='w', pady=5)

# Interactive Search / Filter Controls
ttk.Label(left_panel, text="Pipeline View Filter Controls", font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=5)

filter_var = tk.StringVar(value="Show All")
def apply_filter():
    # Clear active grid records
    for item in main_tree.get_children():
        main_tree.delete(item)
        
    selected = filter_var.get()
    filtered_df = integrated_df
    
    if selected == "Low Attendance (< 85%)":
        filtered_df = integrated_df[integrated_df['Attendance_Percentage'] < 85]
    elif selected == "High CGPA (> 8.5)":
        filtered_df = integrated_df[integrated_df['CGPA'] > 8.5]
    elif selected == "Placed Students":
        filtered_df = integrated_df[integrated_df['Company'] != "Not Placed"]
        
    for _, row in filtered_df.iterrows():
        main_tree.insert("", tk.END, values=list(row))

# Dynamic KPI Filter Buttons
for opt in ["Show All", "Low Attendance (< 85%)", "High CGPA (> 8.5)", "Placed Students"]:
    ttk.Radiobutton(left_panel, text=opt, variable=filter_var, value=opt, command=apply_filter).pack(anchor='w', pady=3)

# Core KPIs computation card view block
ttk.Label(left_panel, text="\nCohort Computed Key Metrics", font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=5)

kpi_frame = ttk.LabelFrame(left_panel, text=" Real-Time Engine Signals ", padding=10)
kpi_frame.pack(fill='x', expand=False, pady=5)

placed_count = integrated_df[integrated_df['Company'] != "Not Placed"].shape[0]
placement_rate = (placed_count / len(integrated_df)) * 100

ttk.Label(kpi_frame, text=f"• Cohort Mean CGPA: {integrated_df['CGPA'].mean():.2f}", font=('Consolas', 10)).pack(anchor='w')
ttk.Label(kpi_frame, text=f"• Cohort Attendance: {integrated_df['Attendance_Percentage'].mean():.1f}%", font=('Consolas', 10)).pack(anchor='w')
ttk.Label(kpi_frame, text=f"• Placement Rate: {placement_rate:.1f}%", font=('Consolas', 10)).pack(anchor='w')
ttk.Label(kpi_frame, text=f"• Active LMS Users: {int(integrated_df['LMS_Active'].sum())}", font=('Consolas', 10)).pack(anchor='w')

# Assemble the main dynamic view spreadsheet grid
main_tree_frame = ttk.Frame(right_panel)
main_tree_frame.pack(fill='both', expand=True, pady=5)

main_tree = ttk.Treeview(main_tree_frame, columns=list(integrated_df.columns), show='headings')
m_vsb = ttk.Scrollbar(main_tree_frame, orient="vertical", command=main_tree.yview)
m_hsb = ttk.Scrollbar(main_tree_frame, orient="horizontal", command=main_tree.xview)
main_tree.configure(yscrollcommand=m_vsb.set, xscrollcommand=m_hsb.set)

for col in integrated_df.columns:
    main_tree.heading(col, text=col)
    main_tree.column(col, width=115, anchor='center')

main_tree.grid(row=0, column=0, sticky='nsew')
m_vsb.grid(row=0, column=1, sticky='ns')
m_hsb.grid(row=1, column=0, sticky='ew')
main_tree_frame.grid_columnconfigure(0, weight=1)
main_tree_frame.grid_rowconfigure(0, weight=1)

# Populate initial view values
apply_filter()

# ---------------------------------------------------------------------
# TAB 3: Interactive Reporting Charts Room (Parts G & H)
# ---------------------------------------------------------------------
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="📊 Part G & H: Executive Visualization Suite")

top_bar = ttk.Frame(tab3)
top_bar.pack(fill='x', side='top', pady=5, padx=10)

def trigger_export():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="student_analytics.csv", filetypes=[("CSV File", "*.csv")])
    if file_path:
        integrated_df.to_csv(file_path, index=False)
        messagebox.showinfo("Pipeline Output Message", f"Data table successfully exported to:\n{file_path}")

ttk.Button(top_bar, text="📥 Export Integrated Analytical CSV File (Question 39)", command=trigger_export).pack(side='left', padx=5)

# Dropdown menu configuration selector allows toggling clean fullscreen charts
chart_var = tk.StringVar(value="Departmental Performance Comparisons (Q35 & Q36)")

chart_canvas_frame = ttk.Frame(tab3)
chart_canvas_frame.pack(fill='both', expand=True, padx=10, pady=5)

def render_selected_chart_node(*args):
    # Wipe prior canvas elements to clear memory leaks
    for widget in chart_canvas_frame.winfo_children():
        widget.destroy()
        
    choice = chart_var.get()
    sns.set_theme(style="whitegrid")
    
    if choice == "Departmental Performance Comparisons (Q35 & Q36)":
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
        sns.barplot(data=integrated_df, x='Department', y='CGPA', ax=ax1, palette="Blues_d", errorbar=None)
        ax1.set_title("Department-wise Average CGPA (Q35)")
        
        sns.barplot(data=integrated_df, x='Department', y='Attendance_Percentage', ax=ax2, palette="Greens_d", errorbar=None)
        ax2.set_title("Department-wise Average Attendance % (Q36)")
        
    elif choice == "Cohort Attendance Density Profile (Q37)":
        fig, ax = plt.subplots(figsize=(10, 4.5))
        sns.histplot(data=integrated_df, x='Attendance_Percentage', kde=True, color="purple", bins=5, ax=ax)
        ax.set_title("Cohort Attendance Distribution Histogram (Q37)")
        
    else:
        fig, ax = plt.subplots(figsize=(6, 4.5))
        p_count = integrated_df[integrated_df['Company'] != "Not Placed"].shape[0]
        up_count = len(integrated_df) - p_count
        ax.pie([p_count, up_count], labels=['Placed', 'Not Placed'], autopct='%1.1f%%', colors=['#4facfe', '#ffb199'], startangle=140)
        ax.set_title("Corporate Placement Distribution Ratio (Q38)")

    fig.tight_layout()
    
    # Save step matching script assignment parameters (Question 40 rule check verification)
    fig.savefig('dashboard_report_snapshot.png', dpi=150)
    
    canvas = FigureCanvasTkAgg(fig, master=chart_canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    plt.close(fig)

ttk.Label(top_bar, text="  Toggle Analytics Display Layout View: ").pack(side='left', padx=5)
chart_selector = ttk.Combobox(top_bar, textvariable=chart_var, values=[
    "Departmental Performance Comparisons (Q35 & Q36)",
    "Cohort Attendance Density Profile (Q37)",
    "Corporate Placement Distribution Ratio (Q38)"
], width=45, state="readonly")
chart_selector.pack(side='left', padx=5)
chart_selector.bind("<<ComboboxSelected>>", render_selected_chart_node)

# Initialize standard plotting components across the workspace canvas frame structure
render_selected_chart_node()

root.mainloop()