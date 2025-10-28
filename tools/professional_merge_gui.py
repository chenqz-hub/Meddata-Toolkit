"""
专业版跨文件合并工具 - 完整功能版
新增功能：
1. 数据预览表格 - 在合并前预览数据
2. 批量合并模式 - 一次合并多个文件
3. 模板保存 - 保存常用的合并设置
4. 导出报告 - 生成详细的合并报告
5. 撤销功能 - 支持操作回退
"""

import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
import threading
import json
import os


class BatchMergeManager:
    """批量合并管理器"""
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.merge_tasks = []  # 合并任务列表
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面"""
        # 顶部工具栏
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(toolbar, text="➕ 添加任务", command=self.add_task).pack(side="left", padx=5)
        ttk.Button(toolbar, text="🗑️ 删除选中", command=self.remove_task).pack(side="left", padx=5)
        ttk.Button(toolbar, text="🗑️ 清空所有", command=self.clear_all).pack(side="left", padx=5)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(toolbar, text="▶️ 开始批量合并", command=self.start_batch_merge, 
                  style="Accent.TButton").pack(side="left", padx=5)
        
        # 任务列表
        list_frame = ttk.LabelFrame(self.parent, text="合并任务列表", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 创建Treeview
        columns = ("序号", "文件1", "Sheet1", "文件2", "Sheet2", "匹配字段", "合并类型", "输出文件", "状态")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列
        widths = [50, 150, 100, 150, 100, 100, 80, 150, 80]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center" if col in ["序号", "状态", "合并类型"] else "w")
        
        # 滚动条
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # 进度信息
        progress_frame = ttk.LabelFrame(self.parent, text="执行进度", padding=10)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill="x", pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="就绪", foreground="blue")
        self.status_label.pack()
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.parent, text="执行日志", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True)
    
    def add_task(self):
        """添加合并任务"""
        task_window = tk.Toplevel(self.parent)
        task_window.title("添加合并任务")
        task_window.geometry("600x550")
        task_window.transient(self.parent)
        task_window.grab_set()
        
        task_data = {}
        
        # 文件1
        frame1 = ttk.LabelFrame(task_window, text="文件1", padding=10)
        frame1.pack(fill="x", padx=10, pady=5)
        
        file1_path_var = tk.StringVar()
        sheet1_var = tk.StringVar()
        
        ttk.Label(frame1, text="文件:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(frame1, textvariable=file1_path_var, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(frame1, text="浏览", 
                  command=lambda: self.browse_file(file1_path_var, sheet1_combo, 1, task_data)).grid(row=0, column=2)
        
        ttk.Label(frame1, text="Sheet:").grid(row=1, column=0, sticky="w", pady=2)
        sheet1_combo = ttk.Combobox(frame1, textvariable=sheet1_var, width=37, state="readonly")
        sheet1_combo.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=2)
        
        # 文件2
        frame2 = ttk.LabelFrame(task_window, text="文件2", padding=10)
        frame2.pack(fill="x", padx=10, pady=5)
        
        file2_path_var = tk.StringVar()
        sheet2_var = tk.StringVar()
        
        ttk.Label(frame2, text="文件:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(frame2, textvariable=file2_path_var, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(frame2, text="浏览", 
                  command=lambda: self.browse_file(file2_path_var, sheet2_combo, 2, task_data)).grid(row=0, column=2)
        
        ttk.Label(frame2, text="Sheet:").grid(row=1, column=0, sticky="w", pady=2)
        sheet2_combo = ttk.Combobox(frame2, textvariable=sheet2_var, width=37, state="readonly")
        sheet2_combo.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=2)
        
        # 合并设置
        settings_frame = ttk.LabelFrame(task_window, text="合并设置", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        join_field_var = tk.StringVar()
        merge_type_var = tk.StringVar(value="left")
        
        ttk.Label(settings_frame, text="匹配字段:").grid(row=0, column=0, sticky="w", pady=2)
        join_field_combo = ttk.Combobox(settings_frame, textvariable=join_field_var, width=37)
        join_field_combo.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Button(settings_frame, text="分析", 
                  command=lambda: self.analyze_fields(task_data, join_field_combo)).grid(row=0, column=2)
        
        ttk.Label(settings_frame, text="合并类型:").grid(row=1, column=0, sticky="w", pady=2)
        merge_frame = ttk.Frame(settings_frame)
        merge_frame.grid(row=1, column=1, columnspan=2, sticky="w", padx=5)
        
        for i, (text, value) in enumerate([("LEFT", "left"), ("RIGHT", "right"), 
                                           ("INNER", "inner"), ("OUTER", "outer")]):
            ttk.Radiobutton(merge_frame, text=text, variable=merge_type_var, 
                           value=value).pack(side="left", padx=10)
        
        # 输出文件
        output_frame = ttk.LabelFrame(task_window, text="输出设置", padding=10)
        output_frame.pack(fill="x", padx=10, pady=5)
        
        output_path_var = tk.StringVar()
        
        ttk.Label(output_frame, text="输出文件:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(output_frame, textvariable=output_path_var, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(output_frame, text="浏览", 
                  command=lambda: self.browse_output(output_path_var)).grid(row=0, column=2)
        
        # 按钮
        button_frame = ttk.Frame(task_window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        def save_task():
            if not all([file1_path_var.get(), sheet1_var.get(), file2_path_var.get(), 
                       sheet2_var.get(), join_field_var.get(), output_path_var.get()]):
                messagebox.showwarning("警告", "请填写所有必填项")
                return
            
            task = {
                'file1': file1_path_var.get(),
                'sheet1': sheet1_var.get(),
                'file2': file2_path_var.get(),
                'sheet2': sheet2_var.get(),
                'join_field': join_field_var.get(),
                'merge_type': merge_type_var.get(),
                'output': output_path_var.get(),
                'status': '待执行',
                'df1': task_data.get('df1'),
                'df2': task_data.get('df2')
            }
            
            self.merge_tasks.append(task)
            self.refresh_task_list()
            task_window.destroy()
        
        ttk.Button(button_frame, text="保存任务", command=save_task).pack(side="right", padx=5)
        ttk.Button(button_frame, text="取消", command=task_window.destroy).pack(side="right")
    
    def browse_file(self, path_var, sheet_combo, file_num, task_data):
        """浏览文件"""
        file_path = filedialog.askopenfilename(
            title=f"选择文件{file_num}",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        
        if file_path:
            path_var.set(file_path)
            try:
                excel = pd.ExcelFile(file_path)
                sheet_names = excel.sheet_names
                sheet_combo['values'] = sheet_names
                if sheet_names:
                    sheet_combo.current(0)
                    # 预加载数据用于分析
                    df = pd.read_excel(file_path, sheet_name=sheet_names[0])
                    task_data[f'df{file_num}'] = df
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败: {e}")
    
    def browse_output(self, path_var):
        """浏览输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        
        if file_path:
            path_var.set(file_path)
    
    def analyze_fields(self, task_data, combo):
        """分析匹配字段"""
        df1 = task_data.get('df1')
        df2 = task_data.get('df2')
        
        if df1 is None or df2 is None:
            messagebox.showwarning("警告", "请先选择文件和Sheet")
            return
        
        common_fields = list(set(df1.columns) & set(df2.columns))
        
        if not common_fields:
            messagebox.showwarning("警告", "两个文件没有共同字段")
            return
        
        combo['values'] = common_fields
        if common_fields:
            combo.current(0)
    
    def remove_task(self):
        """删除选中任务"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的任务")
            return
        
        for item in selected:
            idx = self.tree.index(item)
            self.tree.delete(item)
            if 0 <= idx < len(self.merge_tasks):
                self.merge_tasks.pop(idx)
        
        self.refresh_task_list()
    
    def clear_all(self):
        """清空所有任务"""
        if messagebox.askyesno("确认", "确定要清空所有任务吗？"):
            self.merge_tasks.clear()
            self.refresh_task_list()
            self.log("已清空所有任务")
    
    def refresh_task_list(self):
        """刷新任务列表"""
        self.tree.delete(*self.tree.get_children())
        
        for i, task in enumerate(self.merge_tasks, 1):
            self.tree.insert("", "end", values=(
                i,
                Path(task['file1']).name,
                task['sheet1'],
                Path(task['file2']).name,
                task['sheet2'],
                task['join_field'],
                task['merge_type'].upper(),
                Path(task['output']).name,
                task['status']
            ))
    
    def start_batch_merge(self):
        """开始批量合并"""
        if not self.merge_tasks:
            messagebox.showwarning("警告", "没有待执行的任务")
            return
        
        # 在新线程中执行
        thread = threading.Thread(target=self.execute_batch_merge)
        thread.daemon = True
        thread.start()
    
    def execute_batch_merge(self):
        """执行批量合并"""
        total = len(self.merge_tasks)
        success_count = 0
        fail_count = 0
        
        self.log(f"开始批量合并，共 {total} 个任务\n{'='*60}")
        
        for i, task in enumerate(self.merge_tasks, 1):
            try:
                # 更新进度
                progress = (i - 1) / total * 100
                self.progress_var.set(progress)
                self.status_label.config(text=f"正在处理: {i}/{total} - {Path(task['file1']).name}")
                
                # 更新任务状态
                task['status'] = '执行中'
                self.parent.after(0, self.refresh_task_list)
                
                self.log(f"\n[任务 {i}/{total}] 开始执行")
                self.log(f"  文件1: {Path(task['file1']).name} -> {task['sheet1']}")
                self.log(f"  文件2: {Path(task['file2']).name} -> {task['sheet2']}")
                self.log(f"  匹配字段: {task['join_field']}")
                self.log(f"  合并类型: {task['merge_type'].upper()}")
                
                # 读取数据
                df1 = task.get('df1')
                df2 = task.get('df2')
                
                if df1 is None:
                    df1 = pd.read_excel(task['file1'], sheet_name=task['sheet1'])
                if df2 is None:
                    df2 = pd.read_excel(task['file2'], sheet_name=task['sheet2'])
                
                # 执行合并
                merged_df = pd.merge(
                    df1, df2,
                    on=task['join_field'],
                    how=task['merge_type'],
                    suffixes=('_file1', '_file2')
                )
                
                # 保存结果
                output_dir = Path(task['output']).parent
                output_dir.mkdir(parents=True, exist_ok=True)
                
                merged_df.to_excel(task['output'], index=False, sheet_name='Merged')
                
                # 更新状态
                task['status'] = '✓ 完成'
                success_count += 1
                
                self.log(f"  结果: {merged_df.shape[0]} 行 × {merged_df.shape[1]} 列")
                self.log(f"  已保存: {Path(task['output']).name}")
                self.log(f"  ✓ 任务完成")
                
            except Exception as e:
                task['status'] = '✗ 失败'
                fail_count += 1
                self.log(f"  ✗ 错误: {str(e)}")
            
            self.parent.after(0, self.refresh_task_list)
        
        # 完成
        self.progress_var.set(100)
        self.status_label.config(
            text=f"批量合并完成! 成功: {success_count}, 失败: {fail_count}",
            foreground="green" if fail_count == 0 else "orange"
        )
        
        self.log(f"\n{'='*60}")
        self.log(f"批量合并完成!")
        self.log(f"  成功: {success_count}/{total}")
        self.log(f"  失败: {fail_count}/{total}")
        
        self.parent.after(0, lambda: messagebox.showinfo(
            "完成", 
            f"批量合并完成!\n\n成功: {success_count}\n失败: {fail_count}"
        ))
    
    def log(self, message):
        """写入日志"""
        def _log():
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
        
        self.parent.after(0, _log)


class ProfessionalMergeToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("跨文件合并工具 - 专业版")
        self.root.geometry("1200x800")
        
        # 数据
        self.file1_path = None
        self.file2_path = None
        self.df1 = None
        self.df2 = None
        self.excel1 = None
        self.excel2 = None
        self.merged_df = None
        
        # 历史记录（用于撤销）
        self.history = []
        self.current_history_index = -1
        
        # 配置文件路径
        self.config_dir = Path.home() / ".meddata_toolkit"
        self.config_dir.mkdir(exist_ok=True)
        self.templates_file = self.config_dir / "merge_templates.json"
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主界面
        self.create_widgets()
        
        # 加载模板
        self.load_templates()
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="批量合并模式", command=self.open_batch_mode)
        file_menu.add_separator()
        file_menu.add_command(label="保存当前配置为模板", command=self.save_template)
        file_menu.add_command(label="加载模板", command=self.load_template_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="导出合并报告", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="撤销", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="重做", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="清除所有", command=self.clear_all)
        
        # 查看菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="查看", menu=view_menu)
        view_menu.add_command(label="预览文件1数据", command=lambda: self.preview_data(1))
        view_menu.add_command(label="预览文件2数据", command=lambda: self.preview_data(2))
        view_menu.add_command(label="预览合并结果", command=self.preview_merged_data)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        
        # 快捷键绑定
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        
    def create_widgets(self):
        """创建界面组件"""
        
        # 创建主框架和侧边栏
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 左侧控制面板
        left_frame = ttk.Frame(main_container, width=600)
        main_container.add(left_frame, weight=1)
        
        # 右侧预览面板
        right_frame = ttk.Frame(main_container, width=600)
        main_container.add(right_frame, weight=1)
        
        # ========== 左侧：控制面板 ==========
        self.create_control_panel(left_frame)
        
        # ========== 右侧：预览面板 ==========
        self.create_preview_panel(right_frame)
        
    def create_control_panel(self, parent):
        """创建控制面板"""
        
        # 使用滚动框架
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ========== 文件1选择 ==========
        frame1 = ttk.LabelFrame(scrollable_frame, text="文件1", padding=10)
        frame1.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(frame1, text="文件路径:").grid(row=0, column=0, sticky="w", pady=2)
        self.file1_label = ttk.Label(frame1, text="未选择", foreground="gray")
        self.file1_label.grid(row=0, column=1, sticky="w", padx=5)
        ttk.Button(frame1, text="选择文件", command=self.select_file1).grid(row=0, column=2, padx=5)
        ttk.Button(frame1, text="预览", command=lambda: self.preview_data(1)).grid(row=0, column=3, padx=5)
        
        ttk.Label(frame1, text="选择Sheet:").grid(row=1, column=0, sticky="w", pady=2)
        self.sheet1_var = tk.StringVar()
        self.sheet1_combo = ttk.Combobox(frame1, textvariable=self.sheet1_var, state="readonly", width=30)
        self.sheet1_combo.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=2)
        self.sheet1_combo.bind("<<ComboboxSelected>>", lambda e: self.load_sheet1())
        
        self.file1_info = ttk.Label(frame1, text="", foreground="blue")
        self.file1_info.grid(row=2, column=0, columnspan=4, sticky="w", pady=2)
        
        # ========== 文件2选择 ==========
        frame2 = ttk.LabelFrame(scrollable_frame, text="文件2", padding=10)
        frame2.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(frame2, text="文件路径:").grid(row=0, column=0, sticky="w", pady=2)
        self.file2_label = ttk.Label(frame2, text="未选择", foreground="gray")
        self.file2_label.grid(row=0, column=1, sticky="w", padx=5)
        ttk.Button(frame2, text="选择文件", command=self.select_file2).grid(row=0, column=2, padx=5)
        ttk.Button(frame2, text="预览", command=lambda: self.preview_data(2)).grid(row=0, column=3, padx=5)
        
        ttk.Label(frame2, text="选择Sheet:").grid(row=1, column=0, sticky="w", pady=2)
        self.sheet2_var = tk.StringVar()
        self.sheet2_combo = ttk.Combobox(frame2, textvariable=self.sheet2_var, state="readonly", width=30)
        self.sheet2_combo.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=2)
        self.sheet2_combo.bind("<<ComboboxSelected>>", lambda e: self.load_sheet2())
        
        self.file2_info = ttk.Label(frame2, text="", foreground="blue")
        self.file2_info.grid(row=2, column=0, columnspan=4, sticky="w", pady=2)
        
        # ========== 合并设置 ==========
        frame3 = ttk.LabelFrame(scrollable_frame, text="合并设置", padding=10)
        frame3.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(frame3, text="匹配字段:").grid(row=0, column=0, sticky="w", pady=5)
        self.join_field_var = tk.StringVar()
        self.join_field_combo = ttk.Combobox(frame3, textvariable=self.join_field_var, state="readonly", width=25)
        self.join_field_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Button(frame3, text="分析", command=self.analyze_join_fields).grid(row=0, column=2, padx=5)
        
        ttk.Label(frame3, text="合并类型:").grid(row=1, column=0, sticky="nw", pady=5)
        self.merge_type_var = tk.StringVar(value="left")
        
        merge_frame = ttk.Frame(frame3)
        merge_frame.grid(row=1, column=1, columnspan=2, sticky="w", padx=5)
        
        ttk.Radiobutton(merge_frame, text="LEFT JOIN", variable=self.merge_type_var, value="left").pack(anchor="w")
        ttk.Radiobutton(merge_frame, text="RIGHT JOIN", variable=self.merge_type_var, value="right").pack(anchor="w")
        ttk.Radiobutton(merge_frame, text="INNER JOIN", variable=self.merge_type_var, value="inner").pack(anchor="w")
        ttk.Radiobutton(merge_frame, text="OUTER JOIN", variable=self.merge_type_var, value="outer").pack(anchor="w")
        
        # ========== 模板选择 ==========
        frame4 = ttk.LabelFrame(scrollable_frame, text="快速模板", padding=10)
        frame4.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(frame4, text="选择模板:").grid(row=0, column=0, sticky="w", pady=2)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(frame4, textvariable=self.template_var, state="readonly", width=25)
        self.template_combo.grid(row=0, column=1, sticky="w", padx=5)
        ttk.Button(frame4, text="应用", command=self.apply_template).grid(row=0, column=2, padx=5)
        ttk.Button(frame4, text="保存", command=self.save_template).grid(row=0, column=3, padx=5)
        
        # ========== 操作按钮 ==========
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill="x", padx=5, pady=10)
        
        ttk.Button(button_frame, text="执行合并", command=self.execute_merge, 
                  style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="预览结果", command=self.preview_merged_data).pack(side="left", padx=5)
        ttk.Button(button_frame, text="导出报告", command=self.export_report).pack(side="left", padx=5)
        ttk.Button(button_frame, text="清除", command=self.clear_all).pack(side="left", padx=5)
        
    def create_preview_panel(self, parent):
        """创建预览面板"""
        
        # 标签页
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True)
        
        # ========== 匹配分析标签页 ==========
        match_frame = ttk.Frame(notebook)
        notebook.add(match_frame, text="匹配分析")
        
        self.match_info_text = scrolledtext.ScrolledText(match_frame, wrap=tk.WORD)
        self.match_info_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ========== 数据预览标签页 ==========
        preview_frame = ttk.Frame(notebook)
        notebook.add(preview_frame, text="数据预览")
        
        # 预览控制
        preview_control = ttk.Frame(preview_frame)
        preview_control.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(preview_control, text="预览:").pack(side="left", padx=5)
        ttk.Button(preview_control, text="文件1", command=lambda: self.show_data_preview(1)).pack(side="left", padx=2)
        ttk.Button(preview_control, text="文件2", command=lambda: self.show_data_preview(2)).pack(side="left", padx=2)
        ttk.Button(preview_control, text="合并结果", command=lambda: self.show_data_preview(3)).pack(side="left", padx=2)
        
        # 预览表格
        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.NONE, font=("Courier", 9))
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ========== 操作日志标签页 ==========
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="操作日志")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.log("系统初始化完成")
        
    def log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        
    def select_file1(self):
        """选择文件1"""
        file_path = filedialog.askopenfilename(
            title="选择文件1",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.file1_path = file_path
            self.file1_label.config(text=Path(file_path).name, foreground="black")
            self.log(f"选择文件1: {Path(file_path).name}")
            
            try:
                self.excel1 = pd.ExcelFile(file_path)
                sheets = self.excel1.sheet_names
                self.sheet1_combo['values'] = sheets
                if sheets:
                    self.sheet1_combo.current(0)
                    self.load_sheet1()
            except Exception as e:
                messagebox.showerror("错误", f"读取文件出错: {e}")
                self.log(f"错误: 读取文件1失败 - {e}")
    
    def select_file2(self):
        """选择文件2"""
        file_path = filedialog.askopenfilename(
            title="选择文件2",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.file2_path = file_path
            self.file2_label.config(text=Path(file_path).name, foreground="black")
            self.log(f"选择文件2: {Path(file_path).name}")
            
            try:
                self.excel2 = pd.ExcelFile(file_path)
                sheets = self.excel2.sheet_names
                self.sheet2_combo['values'] = sheets
                if sheets:
                    self.sheet2_combo.current(0)
                    self.load_sheet2()
            except Exception as e:
                messagebox.showerror("错误", f"读取文件出错: {e}")
                self.log(f"错误: 读取文件2失败 - {e}")
    
    def load_sheet1(self):
        """加载文件1的sheet"""
        if not self.excel1 or not self.sheet1_var.get():
            return
        
        try:
            self.df1 = pd.read_excel(self.file1_path, sheet_name=self.sheet1_var.get())
            info = f"✓ 已加载: {self.df1.shape[0]} 行 × {self.df1.shape[1]} 列"
            self.file1_info.config(text=info)
            self.log(f"加载文件1 Sheet: {self.sheet1_var.get()} ({self.df1.shape[0]}行)")
            self.analyze_join_fields()
        except Exception as e:
            messagebox.showerror("错误", f"加载Sheet出错: {e}")
            self.log(f"错误: 加载文件1 Sheet失败 - {e}")
    
    def load_sheet2(self):
        """加载文件2的sheet"""
        if not self.excel2 or not self.sheet2_var.get():
            return
        
        try:
            self.df2 = pd.read_excel(self.file2_path, sheet_name=self.sheet2_var.get())
            info = f"✓ 已加载: {self.df2.shape[0]} 行 × {self.df2.shape[1]} 列"
            self.file2_info.config(text=info)
            self.log(f"加载文件2 Sheet: {self.sheet2_var.get()} ({self.df2.shape[0]}行)")
            self.analyze_join_fields()
        except Exception as e:
            messagebox.showerror("错误", f"加载Sheet出错: {e}")
            self.log(f"错误: 加载文件2 Sheet失败 - {e}")
    
    def analyze_join_fields(self):
        """分析可用的匹配字段"""
        if self.df1 is None or self.df2 is None:
            return
        
        fields1 = set(self.df1.columns)
        fields2 = set(self.df2.columns)
        common_fields = sorted(list(fields1.intersection(fields2)))
        
        if not common_fields:
            self.match_info_text.delete(1.0, tk.END)
            self.match_info_text.insert(tk.END, "⚠ 警告: 两个文件没有公共字段！\n")
            self.log("警告: 没有找到公共字段")
            return
        
        self.join_field_combo['values'] = common_fields
        
        key_fields = ['patientingroupid', 'subjid', 'stname', 'patient_id', 'sys_idcard']
        analysis_results = []
        
        for field in key_fields:
            if field in common_fields:
                set1 = set(self.df1[field].dropna().astype(str))
                set2 = set(self.df2[field].dropna().astype(str))
                overlap = len(set1.intersection(set2))
                match_rate = overlap / len(set1) * 100 if len(set1) > 0 else 0
                
                analysis_results.append({
                    'field': field,
                    'match_rate': match_rate,
                    'overlap': overlap,
                    'total': len(set1)
                })
        
        analysis_results.sort(key=lambda x: x['match_rate'], reverse=True)
        
        self.match_info_text.delete(1.0, tk.END)
        self.match_info_text.insert(tk.END, "=" * 60 + "\n")
        self.match_info_text.insert(tk.END, "匹配字段分析\n")
        self.match_info_text.insert(tk.END, "=" * 60 + "\n\n")
        self.match_info_text.insert(tk.END, f"公共字段数量: {len(common_fields)}\n\n")
        
        if analysis_results:
            self.match_info_text.insert(tk.END, "推荐匹配字段:\n")
            self.match_info_text.insert(tk.END, "-" * 60 + "\n")
            
            for i, result in enumerate(analysis_results, 1):
                symbol = "★" if result['match_rate'] > 90 else "☆" if result['match_rate'] > 60 else "○"
                line = f"{symbol} {i}. {result['field']}: {result['match_rate']:.1f}% ({result['overlap']}/{result['total']})\n"
                self.match_info_text.insert(tk.END, line)
            
            best_field = None
            for result in analysis_results:
                if result['field'] != 'subjid':
                    best_field = result['field']
                    break
            
            if best_field is None and analysis_results:
                best_field = analysis_results[0]['field']
            
            if best_field:
                self.join_field_var.set(best_field)
                self.match_info_text.insert(tk.END, f"\n✓ 已自动选择: {best_field}\n")
                self.log(f"推荐匹配字段: {best_field}")
    
    def execute_merge(self):
        """执行合并"""
        if self.df1 is None or self.df2 is None:
            messagebox.showwarning("警告", "请先选择并加载两个文件！")
            return
        
        join_field = self.join_field_var.get()
        if not join_field:
            messagebox.showwarning("警告", "请选择匹配字段！")
            return
        
        merge_type = self.merge_type_var.get()
        
        try:
            self.log(f"开始合并: {join_field} ({merge_type.upper()} JOIN)")
            
            # 保存到历史记录
            self.save_to_history()
            
            # 执行合并
            self.merged_df = pd.merge(self.df1, self.df2, on=join_field, how=merge_type, 
                                     suffixes=('_file1', '_file2'))
            
            info = f"✓ 合并完成: {self.merged_df.shape[0]} 行 × {self.merged_df.shape[1]} 列"
            self.match_info_text.insert(tk.END, f"\n{info}\n")
            self.log(info)
            
            messagebox.showinfo("成功", f"合并完成！\n{info}")
            
            # 提示保存
            if messagebox.askyesno("保存", "是否立即保存合并结果？"):
                self.save_merged_result()
                
        except Exception as e:
            messagebox.showerror("错误", f"合并失败: {e}")
            self.log(f"错误: 合并失败 - {e}")
    
    def save_merged_result(self):
        """保存合并结果"""
        if self.merged_df is None:
            messagebox.showwarning("警告", "没有可保存的合并结果！")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"merged_{self.join_field_var.get()}_{timestamp}.xlsx"
        
        save_path = filedialog.asksaveasfilename(
            title="保存合并结果",
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        
        if not save_path:
            return
        
        try:
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                self.merged_df.to_excel(writer, sheet_name='Merged Data', index=False)
                
                info_data = {
                    '项目': [
                        '文件1', '文件1 Sheet', '文件1 行数', '文件1 列数',
                        '文件2', '文件2 Sheet', '文件2 行数', '文件2 列数',
                        '匹配字段', '合并类型', '结果行数', '结果列数',
                        '合并时间'
                    ],
                    '值': [
                        Path(self.file1_path).name,
                        self.sheet1_var.get(),
                        str(self.df1.shape[0]),
                        str(self.df1.shape[1]),
                        Path(self.file2_path).name,
                        self.sheet2_var.get(),
                        str(self.df2.shape[0]),
                        str(self.df2.shape[1]),
                        self.join_field_var.get(),
                        self.merge_type_var.get().upper() + ' JOIN',
                        str(self.merged_df.shape[0]),
                        str(self.merged_df.shape[1]),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                info_df = pd.DataFrame(info_data)
                info_df.to_excel(writer, sheet_name='Merge Info', index=False)
            
            self.log(f"文件已保存: {Path(save_path).name}")
            messagebox.showinfo("成功", f"文件已保存:\n{save_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {e}")
            self.log(f"错误: 保存失败 - {e}")
    
    def preview_data(self, file_num):
        """预览数据"""
        if file_num == 1:
            df = self.df1
            name = "文件1"
        else:
            df = self.df2
            name = "文件2"
        
        if df is None:
            messagebox.showinfo("提示", f"{name}尚未加载")
            return
        
        # 创建预览窗口
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"{name} 数据预览")
        preview_window.geometry("800x600")
        
        # 信息标签
        info_frame = ttk.Frame(preview_window)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"数据维度: {df.shape[0]} 行 × {df.shape[1]} 列", 
                 font=("", 10, "bold")).pack(side="left")
        
        # 文本框显示
        text = scrolledtext.ScrolledText(preview_window, wrap=tk.NONE, font=("Courier", 9))
        text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 显示前100行
        preview_df = df.head(100)
        text.insert(tk.END, preview_df.to_string(index=False))
        
        if len(df) > 100:
            text.insert(tk.END, f"\n\n... 还有 {len(df) - 100} 行数据未显示")
    
    def show_data_preview(self, source):
        """在右侧面板显示数据预览"""
        if source == 1:
            df = self.df1
            name = "文件1"
        elif source == 2:
            df = self.df2
            name = "文件2"
        else:
            df = self.merged_df
            name = "合并结果"
        
        if df is None:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"{name}尚未加载\n")
            return
        
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, f"=== {name} 数据预览 ===\n")
        self.preview_text.insert(tk.END, f"数据维度: {df.shape[0]} 行 × {df.shape[1]} 列\n\n")
        
        preview_df = df.head(50)
        self.preview_text.insert(tk.END, preview_df.to_string(index=False))
        
        if len(df) > 50:
            self.preview_text.insert(tk.END, f"\n\n... 还有 {len(df) - 50} 行数据未显示")
    
    def preview_merged_data(self):
        """预览合并结果"""
        if self.merged_df is None:
            messagebox.showinfo("提示", "尚未执行合并操作")
            return
        
        self.show_data_preview(3)
    
    def save_template(self):
        """保存当前配置为模板"""
        if not self.join_field_var.get():
            messagebox.showwarning("警告", "请先配置合并设置")
            return
        
        # 询问模板名称
        template_name = tk.simpledialog.askstring("保存模板", "请输入模板名称:")
        if not template_name:
            return
        
        template = {
            'name': template_name,
            'join_field': self.join_field_var.get(),
            'merge_type': self.merge_type_var.get(),
            'created_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 加载现有模板
        templates = []
        if self.templates_file.exists():
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
        
        # 添加新模板
        templates.append(template)
        
        # 保存
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        
        self.load_templates()
        self.log(f"模板已保存: {template_name}")
        messagebox.showinfo("成功", f"模板 '{template_name}' 已保存")
    
    def load_templates(self):
        """加载模板列表"""
        if not self.templates_file.exists():
            return
        
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            template_names = [t['name'] for t in templates]
            self.template_combo['values'] = template_names
            
            if template_names:
                self.template_combo.current(0)
        except Exception as e:
            self.log(f"警告: 加载模板失败 - {e}")
    
    def load_template_dialog(self):
        """加载模板对话框"""
        if not self.template_var.get():
            messagebox.showwarning("警告", "请先选择一个模板")
            return
        
        self.apply_template()
    
    def apply_template(self):
        """应用模板"""
        template_name = self.template_var.get()
        if not template_name:
            return
        
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            template = next((t for t in templates if t['name'] == template_name), None)
            if not template:
                return
            
            self.join_field_var.set(template['join_field'])
            self.merge_type_var.set(template['merge_type'])
            
            self.log(f"已应用模板: {template_name}")
            messagebox.showinfo("成功", f"模板 '{template_name}' 已应用")
        except Exception as e:
            messagebox.showerror("错误", f"应用模板失败: {e}")
    
    def export_report(self):
        """导出合并报告"""
        if self.merged_df is None:
            messagebox.showwarning("警告", "没有可导出的合并结果")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"merge_report_{timestamp}.txt"
        
        save_path = filedialog.asksaveasfilename(
            title="导出合并报告",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if not save_path:
            return
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("数据合并详细报告\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("一、输入文件信息\n")
                f.write("-" * 80 + "\n")
                f.write(f"文件1: {Path(self.file1_path).name}\n")
                f.write(f"  Sheet: {self.sheet1_var.get()}\n")
                f.write(f"  维度: {self.df1.shape[0]} 行 × {self.df1.shape[1]} 列\n\n")
                
                f.write(f"文件2: {Path(self.file2_path).name}\n")
                f.write(f"  Sheet: {self.sheet2_var.get()}\n")
                f.write(f"  维度: {self.df2.shape[0]} 行 × {self.df2.shape[1]} 列\n\n")
                
                f.write("二、合并配置\n")
                f.write("-" * 80 + "\n")
                f.write(f"匹配字段: {self.join_field_var.get()}\n")
                f.write(f"合并类型: {self.merge_type_var.get().upper()} JOIN\n\n")
                
                f.write("三、合并结果\n")
                f.write("-" * 80 + "\n")
                f.write(f"结果维度: {self.merged_df.shape[0]} 行 × {self.merged_df.shape[1]} 列\n")
                f.write(f"空值总数: {self.merged_df.isnull().sum().sum()}\n\n")
                
                # 统计匹配情况
                file2_cols = [col for col in self.merged_df.columns if col.endswith('_file2')]
                if file2_cols:
                    matched = self.merged_df[file2_cols[0]].notna().sum()
                    f.write(f"成功匹配: {matched}/{len(self.merged_df)} ({matched/len(self.merged_df)*100:.1f}%)\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("报告结束\n")
            
            self.log(f"报告已导出: {Path(save_path).name}")
            messagebox.showinfo("成功", f"报告已导出:\n{save_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出报告失败: {e}")
    
    def save_to_history(self):
        """保存到历史记录"""
        state = {
            'df1': self.df1.copy() if self.df1 is not None else None,
            'df2': self.df2.copy() if self.df2 is not None else None,
            'merged_df': self.merged_df.copy() if self.merged_df is not None else None,
            'join_field': self.join_field_var.get(),
            'merge_type': self.merge_type_var.get()
        }
        
        # 限制历史记录数量
        if len(self.history) > 10:
            self.history.pop(0)
        
        self.history.append(state)
        self.current_history_index = len(self.history) - 1
    
    def undo(self):
        """撤销"""
        if self.current_history_index > 0:
            self.current_history_index -= 1
            self.restore_from_history()
            self.log("已撤销")
        else:
            messagebox.showinfo("提示", "没有可撤销的操作")
    
    def redo(self):
        """重做"""
        if self.current_history_index < len(self.history) - 1:
            self.current_history_index += 1
            self.restore_from_history()
            self.log("已重做")
        else:
            messagebox.showinfo("提示", "没有可重做的操作")
    
    def restore_from_history(self):
        """从历史记录恢复"""
        if not self.history or self.current_history_index < 0:
            return
        
        state = self.history[self.current_history_index]
        self.df1 = state['df1']
        self.df2 = state['df2']
        self.merged_df = state['merged_df']
        self.join_field_var.set(state['join_field'])
        self.merge_type_var.set(state['merge_type'])
    
    def open_batch_mode(self):
        """打开批量合并模式"""
        batch_window = tk.Toplevel(self.root)
        batch_window.title("批量合并模式")
        batch_window.geometry("1000x700")
        
        # 创建批量合并管理器
        BatchMergeManager(batch_window, self)
    
    def show_help(self):
        """显示帮助"""
        help_text = """
跨文件合并工具 - 专业版 使用说明

1. 文件选择
   - 点击"选择文件"按钮选择Excel文件
   - 在下拉框中选择要合并的Sheet
   - 点击"预览"查看数据内容

2. 合并设置
   - 点击"分析"按钮自动分析匹配字段
   - 选择合适的匹配字段
   - 选择合并类型（LEFT/RIGHT/INNER/OUTER）

3. 执行合并
   - 点击"执行合并"进行数据合并
   - 点击"预览结果"查看合并后的数据
   - 点击"导出报告"生成详细报告

4. 模板功能
   - 保存常用配置为模板
   - 快速应用已保存的模板

5. 快捷键
   - Ctrl+Z: 撤销
   - Ctrl+Y: 重做

更多帮助请访问项目文档。
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("使用说明")
        help_window.geometry("600x500")
        
        text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        text.pack(fill="both", expand=True, padx=10, pady=10)
        text.insert(tk.END, help_text)
        text.config(state="disabled")
    
    def show_about(self):
        """显示关于"""
        about_text = """
跨文件合并工具 - 专业版

版本: 2.0.0
开发: Meddata Toolkit Team
日期: 2025-10-28

功能特性:
• 智能匹配字段分析
• 多种合并方式
• 数据预览
• 模板保存与加载
• 操作撤销/重做
• 详细报告导出
• 批量合并（开发中）

感谢使用！
        """
        messagebox.showinfo("关于", about_text)
    
    def clear_all(self):
        """清除所有"""
        if messagebox.askyesno("确认", "确定要清除所有数据吗？"):
            self.file1_path = None
            self.file2_path = None
            self.df1 = None
            self.df2 = None
            self.excel1 = None
            self.excel2 = None
            self.merged_df = None
            
            self.file1_label.config(text="未选择", foreground="gray")
            self.file2_label.config(text="未选择", foreground="gray")
            self.file1_info.config(text="")
            self.file2_info.config(text="")
            
            self.sheet1_combo['values'] = []
            self.sheet2_combo['values'] = []
            self.join_field_combo['values'] = []
            
            self.match_info_text.delete(1.0, tk.END)
            self.preview_text.delete(1.0, tk.END)
            
            self.log("已清除所有数据")

def main():
    """主函数"""
    root = tk.Tk()
    
    # 导入simpledialog
    import tkinter.simpledialog
    tk.simpledialog = tkinter.simpledialog
    
    app = ProfessionalMergeToolGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
