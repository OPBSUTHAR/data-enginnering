import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import seaborn as sns
import os
import sys

# =====================================================================
# DATA ENGINEERING ENGINE: AUDIT, INTEGRATION & CLEANING
# =====================================================================
def run_advanced_pipeline():
    """Ingests raw laboratory datasets, performs structural quality audits,
    and handles missing values securely through relational integration."""
    
    students_file = "students.csv"
    placements_file = "placements.csv"
    lms_file = "lms.json"
    attendance_file = "attendance.xlsx - Sheet1.csv" if os.path.exists("attendance.xlsx - Sheet1.csv") else "attendance.xlsx"

    if not all(os.path.exists(f) for f in [students_file, attendance_file, placements_file, lms_file]):
        root_temp = tk.Tk()
        root_temp.withdraw()
        messagebox.showerror("Pipeline Ingestion Fault", "Missing required source data files in your active execution directory.")
        sys.exit(1)

    # Extract Phase (Ingestion)
    df_students = pd.read_csv(students_file)
    df_attendance = pd.read_csv(attendance_file) if attendance_file.endswith('.csv') else pd.read_excel(attendance_file)
    df_placements = pd.read_csv(placements_file)
    df_lms = pd.read_json(lms_file)

    # Profiling Phase (Quality Auditing)
    source_profiles = {}
    pre_merge_null_logs = {}
    duplicate_logs = {}
    
    for name, df in [("Students", df_students), ("Attendance", df_attendance), ("Placements", df_placements), ("LMS", df_lms)]:
        source_profiles[name] = {
            "rows": df.shape[0],
            "cols": df.shape[1],
            "attributes": list(df.columns)
        }
        null_counts = df.isnull().sum()
        pre_merge_null_logs[name] = null_counts[null_counts > 0].to_dict()
        duplicate_logs[name] = int(df.duplicated().sum())

    # Resolve active attendance column naming conventions
    global att_col
    att_col = 'Attendance_Percentage' if 'Attendance_Percentage' in df_attendance.columns else \
              ('Attendance' if 'Attendance' in df_attendance.columns else df_attendance.select_dtypes(include=['float', 'int']).columns[0])

    # Referential Integrity Check: Identify unmapped cross-system keys
    student_keys = set(df_students['Student_ID'])
    lms_orphans = list(student_keys - set(df_lms['Student_ID']))
    placement_orphans = list(student_keys - set(df_placements['Student_ID']))

    # Transform & Load Phase (Data Integration & Cleaning)
    m1 = pd.merge(df_students, df_attendance, on='Student_ID', how='left')
    m2 = pd.merge(m1, df_placements, on='Student_ID', how='left')
    final_df = pd.merge(m2, df_lms, on='Student_ID', how='left')

    post_merge_null_logs = final_df.isnull().sum().to_dict()

    # Data Engineering Cleaning & Imputations
    final_df['Company'] = final_df['Company'].fillna("Not Placed")
    final_df['Salary_LPA'] = pd.to_numeric(final_df['Salary_LPA'], errors='coerce').fillna(0.0)
    final_df['Videos_Watched'] = pd.to_numeric(final_df['Videos_Watched'], errors='coerce').fillna(0).astype(int)
    final_df['Assignments_Submitted'] = pd.to_numeric(final_df['Assignments_Submitted'], errors='coerce').fillna(0).astype(int)
    final_df['CGPA'] = pd.to_numeric(final_df['CGPA'], errors='coerce').fillna(0.0)
    final_df[att_col] = pd.to_numeric(final_df[att_col], errors='coerce').fillna(0.0)
    final_df['LMS_Active'] = final_df['Videos_Watched'] > 0

    return (df_students, df_attendance, df_placements, df_lms, final_df, 
            pre_merge_null_logs, post_merge_null_logs, lms_orphans, placement_orphans)

# Initialize Engine
raw_student, raw_att, raw_place, raw_lms, integrated_df, pre_audit, post_audit, lms_miss, place_miss = run_advanced_pipeline()


# =====================================================================
# DESKTOP INTERFACE WORKSPACE CONFIGURATION
# =====================================================================
root = tk.Tk()
root.title("Data Engineering Warehouse Workstation")
root.geometry("1400x850")

# Clean teardown callback prevents active matplotlib windows from causing terminal hangs on exit
def secure_teardown_callback():
    plt.close('all')
    root.quit()
    root.destroy()
    sys.exit(0)

root.protocol("WM_DELETE_WINDOW", secure_teardown_callback)

style = ttk.Style()
style.theme_use('clam')
style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[12, 5])
style.configure('Header.TLabel', font=('Segoe UI', 13, 'bold'), foreground='#1e3a8a')

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=5, pady=5)

def build_grid_viewport(parent, df):
    frame = ttk.Frame(parent)
    frame.pack(fill='both', expand=True, padx=4, pady=4)
    tree = ttk.Treeview(frame, columns=list(df.columns), show='headings', height=8)
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    for col in df.columns:
        tree.heading(col, text=col, anchor='center')
        tree.column(col, width=110, anchor='center')
    for _, row in df.iterrows():
        tree.insert("", tk.END, values=[str(x) if pd.notnull(x) else "NaN" for x in row])
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    return tree

# --- Panel 1: Source Extractions ---
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="📂 Panel 1: Source Profiles")
paned = ttk.Panedwindow(tab1, orient=tk.HORIZONTAL)
paned.pack(fill='both', expand=True, padx=10, pady=5)
l_d = ttk.Frame(paned); r_d = ttk.Frame(paned); paned.add(l_d, weight=1); paned.add(r_d, weight=1)
ttk.Label(l_d, text="students.csv Raw Data View", font=('Segoe UI', 9, 'bold')).pack(anchor='w')
build_grid_viewport(l_d, raw_student)
ttk.Label(l_d, text="attendance.xlsx Raw Data View", font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(5,0))
build_grid_viewport(l_d, raw_att)
ttk.Label(r_d, text="placements.csv Raw Data View", font=('Segoe UI', 9, 'bold')).pack(anchor='w')
build_grid_viewport(r_d, raw_place)
ttk.Label(r_d, text="lms.json Telemetry Raw Data View", font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(5,0))
build_grid_viewport(r_d, raw_lms)

# --- Panel 2: Quality Logs ---
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="🔎 Panel 2: Quality Control Logs")
audit_box = tk.Text(tab2, font=('Consolas', 10), bg='#f8fafc', fg='#0f172a', wrap='word', padx=12, pady=12)
audit_box.pack(fill='both', expand=True, padx=10, pady=5)

report_txt = "=======================================================================================\n" \
             "DATA PIPELINE PRE-INTEGRATION COMPLIANCE & NULL VALUE AUDIT REPORT\n" \
             "=======================================================================================\n\n" \
             f"  LMS Activity Registry Missing Gaps: Total {len(lms_miss)} unmapped profiles.\n" \
             f"    └── Orphan Student IDs: {lms_miss if lms_miss else 'None'}\n" \
             f"  Career Placement Ledger Missing Gaps: Total {len(place_miss)} unmapped profiles.\n" \
             f"    └── Unmapped Student IDs: {place_miss if place_miss else 'None'}\n\n" \
             "[CHECK] INTEGRATED DATA WAREHOUSE POST-JOIN MATRIX VARIANCE EXPANSION:\n" \
             "---------------------------------------------------------------------------------------\n"
for col, count in post_audit.items(): report_txt += f"   • Destination Attribute Field '{col}': {count} null keys generated.\n"
audit_box.insert(tk.END, report_txt)
audit_box.config(state='disabled')


# ---------------------------------------------------------------------
# PANEL 3: RELATIONAL WAREHOUSE MATRIX OPERATIONS RESTORED
# ---------------------------------------------------------------------
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="⚙️ Panel 3: Warehouse State Explorer")
control_panel = ttk.Frame(tab3, width=320, padding=10)
control_panel.pack(side='left', fill='y')
warehouse_panel = ttk.Frame(tab3, padding=10)
warehouse_panel.pack(side='right', fill='both', expand=True)

ttk.Label(warehouse_panel, text="Unified Cleaned Warehouse State Matrix (Imputed Data Viewports)", style='Header.TLabel').pack(anchor='w', pady=5)

cgpa_filter = tk.StringVar(value="All Tiers")
att_filter = tk.StringVar(value="All Tiers")
lms_filter = tk.StringVar(value="All Tiers")

def execute_warehouse_slice():
    """Wired up all operations: Safely slices data across all 3 conditions simultaneously."""
    for item in main_tree.get_children(): main_tree.delete(item)
    df = integrated_df.copy()
    
    # 1. Academic Scale Operation
    c_sel = cgpa_filter.get()
    if c_sel == "High Academic (> 8.5)": df = df[df['CGPA'] > 8.5]
    elif c_sel == "Medium Academic (6.5 - 8.5)": df = df[(df['CGPA'] >= 6.5) & (df['CGPA'] <= 8.5)]
    elif c_sel == "Low Academic (< 6.5)": df = df[df['CGPA'] < 6.5]
        
    # 2. Attendance Scale Operation
    a_sel = att_filter.get()
    if a_sel == "High Attendance (> 90%)": df = df[df[att_col] > 90]
    elif a_sel == "Medium Attendance (75% - 90%)": df = df[(df[att_col] >= 75) & (df[att_col] <= 90)]
    elif a_sel == "Low Attendance (< 75%)": df = df[df[att_col] < 75]
        
    # 3. LMS Telemetry Engagement Operation
    l_sel = lms_filter.get()
    if l_sel == "High Engagement (> 20 videos)": df = df[df['Videos_Watched'] > 20]
    elif l_sel == "Moderate Engagement (1 - 20)": df = df[(df['Videos_Watched'] >= 1) & (df['Videos_Watched'] <= 20)]
    elif l_sel == "Inactive Platform Accounts": df = df[df['Videos_Watched'] == 0]
        
    for _, row in df.iterrows(): main_tree.insert("", tk.END, values=[str(x) for x in row])
    lbl_counter.config(text=f"Records Rendered: {len(df)} of {len(integrated_df)}")

ttk.Label(control_panel, text="Dynamic Matrix Filtering", font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=5)

f_cgpa = ttk.LabelFrame(control_panel, text=" Filter by Academic Tier ", padding=5); f_cgpa.pack(fill='x', pady=4)
for opt in ["All Tiers", "High Academic (> 8.5)", "Medium Academic (6.5 - 8.5)", "Low Academic (< 6.5)"]:
    ttk.Radiobutton(f_cgpa, text=opt, variable=cgpa_filter, value=opt, command=execute_warehouse_slice).pack(anchor='w')

f_att = ttk.LabelFrame(control_panel, text=" Filter by Attendance Tier ", padding=5); f_att.pack(fill='x', pady=4)
for opt in ["All Tiers", "High Attendance (> 90%)", "Medium Attendance (75% - 90%)", "Low Attendance (< 75%)"]:
    ttk.Radiobutton(f_att, text=opt, variable=att_filter, value=opt, command=execute_warehouse_slice).pack(anchor='w')

f_lms = ttk.LabelFrame(control_panel, text=" Filter by LMS Tier ", padding=5); f_lms.pack(fill='x', pady=4)
for opt in ["All Tiers", "High Engagement (> 20 videos)", "Moderate Engagement (1 - 20)", "Inactive Platform Accounts"]:
    ttk.Radiobutton(f_lms, text=opt, variable=lms_filter, value=opt, command=execute_warehouse_slice).pack(anchor='w')

lbl_counter = ttk.Label(control_panel, text="", font=('Segoe UI', 10, 'italic')); lbl_counter.pack(pady=10)

main_tree_frame = ttk.Frame(warehouse_panel); main_tree_frame.pack(fill='both', expand=True)
main_tree = build_grid_viewport(main_tree_frame, integrated_df)
execute_warehouse_slice()


# ---------------------------------------------------------------------
# PANEL 4: ACCURATE ANALYSIS AND TOOLTIP HOVER VISUAL SUITE (Q23 - Q40)
# ---------------------------------------------------------------------
tab4 = ttk.Frame(notebook)
notebook.add(tab4, text="📊 Panel 4: Interactive Charts Room")

top_bar = ttk.Frame(tab4, padding=8); top_bar.pack(fill='x', side='top')
def trigger_warehouse_export():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="student_analytics.csv", filetypes=[("CSV File", "*.csv")])
    if file_path:
        integrated_df.to_csv(file_path, index=False)
        messagebox.showinfo("Export Successful", f"Data table successfully saved to:\n{file_path}")
ttk.Button(top_bar, text="📥 Run Warehouse Export Engine (CSV File)", command=trigger_warehouse_export).pack(side='left', padx=10)

graph_control_box = ttk.LabelFrame(tab4, text=" Interactive Visual Exploration Framework ")
graph_control_box.pack(fill='both', expand=True, padx=15, pady=10)

def spawn_responsive_chart(chart_id):
    """Spawns an independent, synchronized window frame utilizing mouse hovers and data labels perfectly."""
    sns.set_theme(style="whitegrid")
    pop_win = tk.Toplevel(root)
    pop_win.geometry("800x600")
    
    pop_win.update_idletasks()
    
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    df = integrated_df.copy()
    
    has_dept = 'Department' in df.columns
    has_cgpa = 'CGPA' in df.columns

    # FIXED: Replaced 'fg' attribute with standalone text color initialization property configurations
    annot = ax.annotate("", xy=(0,0), xytext=(12,12), textcoords="offset points", color="white",
                        bbox=dict(boxstyle="round,pad=0.4", fc="#1e293b", ec="none", alpha=0.92),
                        arrowprops=dict(arrowstyle="->", color="#64748b"))
    annot.set_visible(False)

    artists_list = []
    hover_type = "bar" 
    names_arr = []
    sc_df_reference = [] 

    if chart_id == 1:
        pop_win.title("Analysis 1: Departmental Average CGPA Profiles (Q35)")
        if has_dept and has_cgpa:
            grouped = df.groupby('Department')['CGPA'].mean().reset_index()
            names_arr = grouped['Department'].tolist()
            bars = ax.bar(names_arr, grouped['CGPA'], color=sns.color_palette("Blues_d", len(grouped)))
            ax.bar_label(bars, fmt='%.2f', padding=4, weight='bold', color='#1e3a8a')
            artists_list = bars
        ax.set_title("Department-wise Average CGPA Metric Profile", fontsize=11, weight='bold')
        ax.set_ylabel("Avg CGPA")
        
    elif chart_id == 2:
        pop_win.title("Analysis 2: Departmental Attendance Distribution Breakdown (Q36)")
        if has_dept and att_col in df.columns:
            grouped = df.groupby('Department')[att_col].mean().reset_index()
            names_arr = grouped['Department'].tolist()
            bars = ax.bar(names_arr, grouped[att_col], color=sns.color_palette("Greens_d", len(grouped)))
            ax.bar_label(bars, fmt='%.1f%%', padding=4, weight='bold', color='#14532d')
            artists_list = bars
        ax.set_title("Department-wise Average Attendance Percentage Breakdown", fontsize=11, weight='bold')
        ax.set_ylabel("Avg Attendance %")
        
    elif chart_id == 3:
        pop_win.title("Analysis 3: Global Attendance Distribution Density (Q37)")
        if att_col in df.columns:
            counts, bins, bars = ax.hist(df[att_col].dropna(), bins=6, color="#a855f7", edgecolor='#6b21a8', alpha=0.75)
            ax.bar_label(bars, fmt='%.0f', padding=3, weight='bold', color='#6b21a8')
            artists_list = bars
        ax.set_title("Cohort Attendance Distribution Density Histogram", fontsize=11, weight='bold')
        ax.set_xlabel("Attendance Value Ranges")
        ax.set_ylabel("Student Count")
        
    elif chart_id == 4:
        pop_win.title("Analysis 4: Corporate Placement Conversion Share (Q38)")
        if 'Company' in df.columns:
            p_count = df[df['Company'] != "Not Placed"].shape[0]
            up_count = len(df) - p_count
            wedges, texts, autotexts = ax.pie(
                [p_count, up_count], labels=['Placed', 'Not Placed'], autopct='%1.1f%%', 
                colors=['#10b981', '#ef4444'], startangle=140, wedgeprops={'edgecolor':'#ffffff', 'linewidth':2}
            )
            plt.setp(autotexts, size=10, weight="bold", color="white")
            artists_list = wedges
            hover_type = "pie"
        ax.set_title("Corporate Placement Conversion Share Ratio", fontsize=11, weight='bold')
        
    elif chart_id == 5:
        pop_win.title("Analysis 5: Academic Performance vs Attendance Scaling Correlation")
        if has_cgpa and att_col in df.columns:
            unique_depts = df['Department'].unique() if has_dept else ['All']
            palette = sns.color_palette("Set2", len(unique_depts))
            dept_color_map = dict(zip(unique_depts, palette))
            
            for d, group in df.groupby('Department' if has_dept else lambda x: 'All'):
                sc = ax.scatter(group[att_col], group['CGPA'], label=d, s=110, color=dept_color_map[d], edgecolor='#334155', alpha=0.85)
                artists_list.append(sc)
                sc_df_reference.append(group.reset_index(drop=True))
            ax.legend(title="Departments")
            hover_type = "scatter"
        ax.set_title("CGPA vs Attendance Correlation Matrix (Mouse-Hover Enabled)", fontsize=11, weight='bold')
        ax.set_xlabel("Attendance %")
        ax.set_ylabel("CGPA")
        
    elif chart_id == 6:
        pop_win.title("Analysis 6: Departmental System LMS Interaction Log Profiles")
        if has_dept and 'Videos_Watched' in df.columns:
            grouped = df.groupby('Department')['Videos_Watched'].mean().reset_index()
            names_arr = grouped['Department'].tolist()
            bars = ax.bar(names_arr, grouped['Videos_Watched'], color=sns.color_palette("Oranges_d", len(grouped)))
            ax.bar_label(bars, fmt='%.0f', padding=4, weight='bold', color='#7c2d12')
            artists_list = bars
        ax.set_title("Departmental LMS Operational Infrastructure Activity Profile", fontsize=11, weight='bold')
        ax.set_ylabel("Avg Videos Watched")

    fig.tight_layout()
    fig.savefig(f'chart_snapshot_analysis_{chart_id}.png', dpi=150)

    def update_tooltip(target_artist, index, h_type, bar_name="", scatter_group_idx=0):
        if h_type == "scatter":
            pos = target_artist.get_offsets()[index]
            annot.xy = pos
            matched_row = sc_df_reference[scatter_group_idx].iloc[index]
            card_info = f"Student ID: {matched_row['Student_ID']}\n" \
                        f"Name: {matched_row['Name']}\n" \
                        f"Dept: {matched_row['Department']}\n" \
                        f"CGPA: {matched_row['CGPA']:.2f}\n" \
                        f"Attendance: {matched_row[att_col]:.1f}%\n" \
                        f"Company: {matched_row['Company']}"
        elif h_type == "bar":
            bar_geom = target_artist
            annot.xy = (bar_geom.get_x() + bar_geom.get_width()/2, bar_geom.get_height())
            h_val = bar_geom.get_height()
            if chart_id == 1: card_info = f"Dept: {bar_name}\nAvg CGPA: {h_val:.2f}"
            elif chart_id == 2: card_info = f"Dept: {bar_name}\nAvg Attendance: {h_val:.1f}%"
            elif chart_id == 3: card_info = f"Range: {bar_geom.get_x():.1f}% - {(bar_geom.get_x()+bar_geom.get_width()):.1f}%\nCount: {h_val:.0f} students"
            elif chart_id == 6: card_info = f"Dept: {bar_name}\nAvg Videos Watched: {h_val:.1f}"
        elif h_type == "pie":
            annot.xy = (0, 0)
            p_count = df[df['Company'] != "Not Placed"].shape[0]
            if index == 0: card_info = f"Placed: {p_count} students\nRatio: {(p_count/len(df))*100:.1f}%"
            else: card_info = f"Not Placed: {len(df)-p_count} students\nRatio: {((len(df)-p_count)/len(df))*100:.1f}%"

        annot.set_text(card_info)
        annot.get_bbox_patch().set_facecolor("#1e293b")
        annot.get_bbox_patch().set_alpha(0.95)

    def process_mouse_movement(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            is_found = False
            if hover_type == "scatter":
                for g_idx, sc in enumerate(artists_list):
                    cont, ind = sc.contains(event)
                    if cont:
                        update_tooltip(sc, ind['ind'][0], "scatter", scatter_group_idx=g_idx)
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                        is_found = True
                        break
            elif hover_type == "bar":
                for idx, bar in enumerate(artists_list):
                    cont, _ = bar.contains(event)
                    if cont:
                        b_name = names_arr[idx] if idx < len(names_arr) else ""
                        update_tooltip(bar, idx, "bar", b_name)
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                        is_found = True
                        break
            elif hover_type == "pie":
                for idx, wedge in enumerate(artists_list):
                    cont, _ = wedge.contains(event)
                    if cont:
                        update_tooltip(wedge, idx, "pie")
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                        is_found = True
                        break
            if not is_found and vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", process_mouse_movement)

    canvas = FigureCanvasTkAgg(fig, master=pop_win)
    canvas.draw()
    
    toolbar = NavigationToolbar2Tk(canvas, pop_win)
    toolbar.update()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=6, pady=6)

button_frame = ttk.Frame(graph_control_box)
button_frame.place(relx=0.5, rely=0.5, anchor='center')

buttons_spec = [
    ("📊 View Department Average CGPA (Q35)", 1, 0, 0),
    ("📈 View Department Average Attendance (Q36)", 2, 0, 1),
    ("🍇 View Attendance Density Histogram (Q37)", 3, 1, 0),
    ("🍩 View Corporate Placement Pie Share (Q38)", 4, 1, 1),
    ("🎯 View CGPA vs Attendance Correlation Scatter", 5, 2, 0),
    ("💻 View Departmental LMS Interaction Metrics", 6, 2, 1)
]

for label, cid, r_idx, c_idx in buttons_spec:
    btn = ttk.Button(button_frame, text=label, command=lambda c=cid: spawn_responsive_chart(c), width=48)
    btn.grid(row=r_idx, column=c_idx, padx=18, pady=18, ipady=12)

root.mainloop()