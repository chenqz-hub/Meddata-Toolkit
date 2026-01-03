"""
增强版跨文件合并工具 - 带图形界面
功能：
- 文件选择弹窗
- Sheet选择下拉框
- 左右侧合并选项（LEFT/RIGHT/INNER/OUTER JOIN）
- 匹配字段选择
- 实时预览
"""

import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime
import threading

class MergeToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("跨文件合并工具 - 增强版")
        self.root.geometry("900x700")
        
        # 数据
        self.file1_path = None
        self.file2_path = None
        self.df1 = None
        self.df2 = None
        self.excel1 = None
        self.excel2 = None
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面组件"""
        
        # ========== 文件1选择 ==========
        frame1 = ttk.LabelFrame(self.root, text="文件1", padding=10)
        frame1.pack(fill="x", padx=10, pady=5)
        
        # 文件路径
        ttk.Label(frame1, text="文件路径:").grid(row=0, column=0, sticky="w", pady=2)
        self.file1_label = ttk.Label(frame1, text="未选择", foreground="gray")
        self.file1_label.grid(row=0, column=1, sticky="w", padx=5)
        ttk.Button(frame1, text="选择文件", command=self.select_file1).grid(row=0, column=2, padx=5)
        
        # Sheet选择
        ttk.Label(frame1, text="选择Sheet:").grid(row=1, column=0, sticky="w", pady=2)
        self.sheet1_var = tk.StringVar()
        self.sheet1_combo = ttk.Combobox(frame1, textvariable=self.sheet1_var, state="readonly", width=40)
        self.sheet1_combo.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=2)
        self.sheet1_combo.bind("<<ComboboxSelected>>", lambda e: self.load_sheet1())
        
        # 数据信息
        self.file1_info = ttk.Label(frame1, text="", foreground="blue")
        self.file1_info.grid(row=2, column=0, columnspan=3, sticky="w", pady=2)
        
        # ========== 文件2选择 ==========
        frame2 = ttk.LabelFrame(self.root, text="文件2", padding=10)
        frame2.pack(fill="x", padx=10, pady=5)
        
        # 文件路径
        ttk.Label(frame2, text="文件路径:").grid(row=0, column=0, sticky="w", pady=2)
        self.file2_label = ttk.Label(frame2, text="未选择", foreground="gray")
        self.file2_label.grid(row=0, column=1, sticky="w", padx=5)
        ttk.Button(frame2, text="选择文件", command=self.select_file2).grid(row=0, column=2, padx=5)
        
        # Sheet选择
        ttk.Label(frame2, text="选择Sheet:").grid(row=1, column=0, sticky="w", pady=2)
        self.sheet2_var = tk.StringVar()
        self.sheet2_combo = ttk.Combobox(frame2, textvariable=self.sheet2_var, state="readonly", width=40)
        self.sheet2_combo.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=2)
        self.sheet2_combo.bind("<<ComboboxSelected>>", lambda e: self.load_sheet2())
        
        # 数据信息
        self.file2_info = ttk.Label(frame2, text="", foreground="blue")
        self.file2_info.grid(row=2, column=0, columnspan=3, sticky="w", pady=2)
        
        # ========== 合并设置 ==========
        frame3 = ttk.LabelFrame(self.root, text="合并设置", padding=10)
        frame3.pack(fill="x", padx=10, pady=5)
        
        # 匹配字段
        ttk.Label(frame3, text="匹配字段:").grid(row=0, column=0, sticky="w", pady=5)
        self.join_field_var = tk.StringVar()
        self.join_field_combo = ttk.Combobox(frame3, textvariable=self.join_field_var, state="readonly", width=30)
        self.join_field_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Button(frame3, text="分析匹配字段", command=self.analyze_join_fields).grid(row=0, column=2, padx=5)
        
        # 合并类型
        ttk.Label(frame3, text="合并类型:").grid(row=1, column=0, sticky="w", pady=5)
        self.merge_type_var = tk.StringVar(value="left")
        
        merge_frame = ttk.Frame(frame3)
        merge_frame.grid(row=1, column=1, columnspan=2, sticky="w", padx=5)
        
        ttk.Radiobutton(merge_frame, text="LEFT JOIN (保留文件1所有记录)", 
                       variable=self.merge_type_var, value="left").pack(anchor="w")
        ttk.Radiobutton(merge_frame, text="RIGHT JOIN (保留文件2所有记录)", 
                       variable=self.merge_type_var, value="right").pack(anchor="w")
        ttk.Radiobutton(merge_frame, text="INNER JOIN (只保留匹配的记录)", 
                       variable=self.merge_type_var, value="inner").pack(anchor="w")
        ttk.Radiobutton(merge_frame, text="OUTER JOIN (保留所有记录)", 
                       variable=self.merge_type_var, value="outer").pack(anchor="w")
        
        # ========== 匹配信息 ==========
        frame4 = ttk.LabelFrame(self.root, text="匹配分析", padding=10)
        frame4.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 滚动文本框
        text_frame = ttk.Frame(frame4)
        text_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.match_info_text = tk.Text(text_frame, height=10, yscrollcommand=scrollbar.set)
        self.match_info_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.match_info_text.yview)
        
        # ========== 操作按钮 ==========
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="执行合并", command=self.execute_merge, 
                  style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="清除", command=self.clear_all).pack(side="left", padx=5)
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side="right", padx=5)
        
    def _normalize_join_key(self, series: pd.Series) -> pd.Series:
        """将匹配键标准化到可安全合并的字符串形式。
        - 统一为 pandas StringDtype
        - 去除首尾空白、全角空格
        - 折叠连续空白
        - 去除小数点.0（由Excel读取数字造成的浮点展示）
        """
        try:
            s = series.astype('string')
        except Exception:
            # 兜底：某些混合类型无法直接转换到 StringDtype
            s = series.astype(str)
        # 清洗
        if hasattr(s, 'str'):
            s = s.str.replace('\u3000', ' ', regex=False).str.strip()
            s = s.str.replace(r'\s+', ' ', regex=True)
            s = s.str.replace(r'\.0$', '', regex=True)
        return s

    def select_file1(self):
        """选择文件1"""
        file_path = filedialog.askopenfilename(
            title="选择文件1",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.file1_path = file_path
            self.file1_label.config(text=Path(file_path).name, foreground="black")
            
            try:
                self.excel1 = pd.ExcelFile(file_path)
                sheets = self.excel1.sheet_names
                self.sheet1_combo['values'] = sheets
                if sheets:
                    self.sheet1_combo.current(0)
                    self.load_sheet1()
            except Exception as e:
                messagebox.showerror("错误", f"读取文件出错: {e}")
    
    def select_file2(self):
        """选择文件2"""
        file_path = filedialog.askopenfilename(
            title="选择文件2",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.file2_path = file_path
            self.file2_label.config(text=Path(file_path).name, foreground="black")
            
            try:
                self.excel2 = pd.ExcelFile(file_path)
                sheets = self.excel2.sheet_names
                self.sheet2_combo['values'] = sheets
                if sheets:
                    self.sheet2_combo.current(0)
                    self.load_sheet2()
            except Exception as e:
                messagebox.showerror("错误", f"读取文件出错: {e}")
    
    def load_sheet1(self):
        """加载文件1的sheet"""
        if not self.excel1 or not self.sheet1_var.get():
            return
        
        try:
            self.df1 = pd.read_excel(self.file1_path, sheet_name=self.sheet1_var.get())
            info = f"✓ 已加载: {self.df1.shape[0]} 行 × {self.df1.shape[1]} 列"
            self.file1_info.config(text=info)
            self.analyze_join_fields()
        except Exception as e:
            messagebox.showerror("错误", f"加载Sheet出错: {e}")
    
    def load_sheet2(self):
        """加载文件2的sheet"""
        if not self.excel2 or not self.sheet2_var.get():
            return
        
        try:
            self.df2 = pd.read_excel(self.file2_path, sheet_name=self.sheet2_var.get())
            info = f"✓ 已加载: {self.df2.shape[0]} 行 × {self.df2.shape[1]} 列"
            self.file2_info.config(text=info)
            self.analyze_join_fields()
        except Exception as e:
            messagebox.showerror("错误", f"加载Sheet出错: {e}")
    
    def analyze_join_fields(self):
        """分析可用的匹配字段"""
        if self.df1 is None or self.df2 is None:
            return
        
        # 获取公共字段
        fields1 = set(self.df1.columns)
        fields2 = set(self.df2.columns)
        common_fields = sorted(list(fields1.intersection(fields2)))
        
        if not common_fields:
            self.match_info_text.delete(1.0, tk.END)
            self.match_info_text.insert(tk.END, "⚠ 警告: 两个文件没有公共字段！\n")
            return
        
        # 更新下拉框
        self.join_field_combo['values'] = common_fields
        
        # 分析关键字段
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
        
        # 按匹配率排序
        analysis_results.sort(key=lambda x: x['match_rate'], reverse=True)
        
        # 显示分析结果
        self.match_info_text.delete(1.0, tk.END)
        self.match_info_text.insert(tk.END, "=" * 60 + "\n")
        self.match_info_text.insert(tk.END, "匹配字段分析\n")
        self.match_info_text.insert(tk.END, "=" * 60 + "\n\n")
        
        self.match_info_text.insert(tk.END, f"公共字段数量: {len(common_fields)}\n\n")
        
        if analysis_results:
            self.match_info_text.insert(tk.END, "推荐匹配字段 (按匹配率排序):\n")
            self.match_info_text.insert(tk.END, "-" * 60 + "\n")
            
            for i, result in enumerate(analysis_results, 1):
                symbol = "★" if result['match_rate'] > 90 else "☆" if result['match_rate'] > 60 else "○"
                line = f"{symbol} {i}. {result['field']}: {result['match_rate']:.1f}% ({result['overlap']}/{result['total']})\n"
                self.match_info_text.insert(tk.END, line)
            
            # 自动选择最佳字段（排除subjid）
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
        else:
            self.match_info_text.insert(tk.END, "其他公共字段:\n")
            for field in common_fields[:10]:
                self.match_info_text.insert(tk.END, f"  - {field}\n")
            if len(common_fields) > 10:
                self.match_info_text.insert(tk.END, f"  ... 还有 {len(common_fields) - 10} 个字段\n")
            
            if common_fields:
                self.join_field_var.set(common_fields[0])
    
    def execute_merge(self):
        """执行合并"""
        # 验证输入
        if self.df1 is None or self.df2 is None:
            messagebox.showwarning("警告", "请先选择并加载两个文件！")
            return
        
        join_field = self.join_field_var.get()
        if not join_field:
            messagebox.showwarning("警告", "请选择匹配字段！")
            return
        
        merge_type = self.merge_type_var.get()
        
        # 确认对话框
        merge_type_name = {
            'left': 'LEFT JOIN (保留文件1所有记录)',
            'right': 'RIGHT JOIN (保留文件2所有记录)',
            'inner': 'INNER JOIN (只保留匹配记录)',
            'outer': 'OUTER JOIN (保留所有记录)'
        }
        
        msg = f"确认合并设置:\n\n"
        msg += f"文件1: {Path(self.file1_path).name}\n"
        msg += f"  Sheet: {self.sheet1_var.get()}\n"
        msg += f"  数据: {self.df1.shape[0]} 行 × {self.df1.shape[1]} 列\n\n"
        msg += f"文件2: {Path(self.file2_path).name}\n"
        msg += f"  Sheet: {self.sheet2_var.get()}\n"
        msg += f"  数据: {self.df2.shape[0]} 行 × {self.df2.shape[1]} 列\n\n"
        msg += f"匹配字段: {join_field}\n"
        msg += f"合并类型: {merge_type_name[merge_type]}\n\n"
        msg += "是否继续？"
        
        if not messagebox.askyesno("确认合并", msg):
            return
        
        # 执行合并（在新线程中）
        thread = threading.Thread(target=self.do_merge, args=(join_field, merge_type))
        thread.start()
    
    def do_merge(self, join_field, merge_type):
        """实际执行合并操作"""
        try:
            self.root.after(0, lambda: self.match_info_text.insert(tk.END, "\n\n正在合并...\n"))

            # 合并前键列类型提示
            dtype_msg = (
                f"键列类型（合并前）: 文件1={self.df1[join_field].dtype}, 文件2={self.df2[join_field].dtype}\n"
            )
            self.root.after(0, lambda m=dtype_msg: self.match_info_text.insert(tk.END, m))

            # 复制并规范化键列，避免 int64 vs object 的类型不一致
            df1 = self.df1.copy()
            df2 = self.df2.copy()
            df1[join_field] = self._normalize_join_key(df1[join_field])
            df2[join_field] = self._normalize_join_key(df2[join_field])

            dtype_after_msg = (
                f"键列类型（标准化后）: 文件1={df1[join_field].dtype}, 文件2={df2[join_field].dtype}\n"
            )
            self.root.after(0, lambda m=dtype_after_msg: self.match_info_text.insert(tk.END, m))

            # 执行合并
            merged_df = pd.merge(df1, df2, on=join_field, how=merge_type, 
                                 suffixes=('_file1', '_file2'))
            
            self.root.after(0, lambda: self.match_info_text.insert(
                tk.END, f"✓ 合并完成: {merged_df.shape[0]} 行 × {merged_df.shape[1]} 列\n"))
            
            # 选择保存位置
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_name = f"merged_{join_field}_{timestamp}.xlsx"
            
            self.root.after(0, lambda: self.save_result(merged_df, default_name, join_field, merge_type))
            
        except Exception as e:
            # 捕获异常消息，避免在 after 回调中访问已释放的异常变量
            err_msg = f"合并失败: {e}"
            self.root.after(0, lambda m=err_msg: messagebox.showerror("错误", m))
    
    def save_result(self, merged_df, default_name, join_field, merge_type):
        """保存结果"""
        save_path = filedialog.asksaveasfilename(
            title="保存合并结果",
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        
        if not save_path:
            messagebox.showinfo("提示", "已取消保存")
            return
        
        try:
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                # 保存合并数据
                merged_df.to_excel(writer, sheet_name='Merged Data', index=False)
                
                # 保存合并信息
                info_data = {
                    '项目': [
                        '文件1', '文件1 Sheet', '文件1 行数', '文件1 列数',
                        '文件2', '文件2 Sheet', '文件2 行数', '文件2 列数',
                        '匹配字段', '合并类型', '结果行数', '结果列数'
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
                        join_field,
                        merge_type.upper() + ' JOIN',
                        str(merged_df.shape[0]),
                        str(merged_df.shape[1])
                    ]
                }
                info_df = pd.DataFrame(info_data)
                info_df.to_excel(writer, sheet_name='Merge Info', index=False)
            
            messagebox.showinfo("成功", f"文件已保存:\n{save_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {e}")
    
    def clear_all(self):
        """清除所有"""
        self.file1_path = None
        self.file2_path = None
        self.df1 = None
        self.df2 = None
        self.excel1 = None
        self.excel2 = None
        
        self.file1_label.config(text="未选择", foreground="gray")
        self.file2_label.config(text="未选择", foreground="gray")
        self.file1_info.config(text="")
        self.file2_info.config(text="")
        
        self.sheet1_combo['values'] = []
        self.sheet2_combo['values'] = []
        self.join_field_combo['values'] = []
        
        self.match_info_text.delete(1.0, tk.END)

def main():
    """主函数"""
    root = tk.Tk()
    app = MergeToolGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
