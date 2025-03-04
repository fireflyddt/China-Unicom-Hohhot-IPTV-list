import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os

class IPTVExtractor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IPTV频道提取工具")
        self.root.geometry("700x500")
        # 设置最小窗口尺寸，确保所有元素可见
        self.root.minsize(650, 600)
        
        # 设置主题颜色
        self.primary_color = "#4CAF50"
        self.bg_color = "#f5f5f5"
        self.root.configure(bg=self.bg_color)
        
        # 预编译正则表达式提高性能
        self.channel_pattern = re.compile(r"Authentication\.CUSetConfig\(.*?ChannelName=\"(.*?)\".*?TimeShiftURL=\"([^\"]*)", re.DOTALL)
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面组件"""
        # 创建标题
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(
            title_frame, 
            text="IPTV频道提取工具", 
            font=("Arial", 16, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        ).pack()
        
        # 创建主框架
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # 输入文件区域
        input_frame = tk.LabelFrame(main_frame, text="输入设置", bg=self.bg_color, padx=10, pady=10)
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="输入文件：", bg=self.bg_color).grid(row=0, column=0, sticky=tk.W)
        self.input_entry = tk.Entry(input_frame, width=50)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Button(input_frame, text="选择文件", command=self.select_input_file).grid(row=0, column=2, padx=5)
        
        # 输出文件区域
        output_frame = tk.LabelFrame(main_frame, text="输出设置", bg=self.bg_color, padx=10, pady=10)
        output_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(output_frame, text="输出文件：", bg=self.bg_color).grid(row=0, column=0, sticky=tk.W)
        self.output_entry = tk.Entry(output_frame, width=50)
        self.output_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Button(output_frame, text="选择路径", command=self.select_output_file).grid(row=0, column=2, padx=5)
        
        # 配置列权重
        input_frame.columnconfigure(1, weight=1)
        output_frame.columnconfigure(1, weight=1)
        
        # 选项区域
        options_frame = tk.LabelFrame(main_frame, text="提取选项", bg=self.bg_color, padx=10, pady=10)
        options_frame.pack(fill=tk.X, pady=5)
        
        self.extract_smil_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame, 
            text="提取.smil格式地址", 
            variable=self.extract_smil_var,
            bg=self.bg_color
        ).grid(row=0, column=0, sticky=tk.W)
        
        self.extract_m3u8_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame, 
            text="提取.m3u8格式地址", 
            variable=self.extract_m3u8_var,
            bg=self.bg_color
        ).grid(row=0, column=1, sticky=tk.W)
        
        # 进度条
        progress_frame = tk.Frame(main_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill=tk.X)
        
        self.status_var = tk.StringVar(value="准备就绪")
        tk.Label(progress_frame, textvariable=self.status_var, bg=self.bg_color).pack(pady=5)
        
        # 结果显示区域
        result_frame = tk.LabelFrame(main_frame, text="提取结果", bg=self.bg_color, padx=10, pady=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.result_text = tk.Text(result_frame, height=5, wrap=tk.WORD)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # 按钮区域
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        # 设置按钮样式
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background=self.primary_color)
        
        self.process_btn = ttk.Button(
            button_frame, 
            text="开始提取", 
            command=self.start_processing,
            style="Accent.TButton"
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="清空结果", 
            command=self.clear_results
        ).pack(side=tk.LEFT, padx=5)
        
        # 版权信息
        footer_frame = tk.Frame(self.root, bg=self.bg_color)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        tk.Label(
            footer_frame, 
            text="版本 1.2.0 | 由Trae AI优化", 
            fg="gray",
            bg=self.bg_color
        ).pack(side=tk.RIGHT, padx=10)
    
    def select_input_file(self):
        """选择输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择JSP文件",
            filetypes=[("JSP文件", "*.jsp"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, file_path)
            
            # 修改默认输出文件名为"全部频道.csv"
            output_dir = os.path.dirname(file_path)
            default_output = os.path.join(output_dir, "全部频道.csv")
            
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, default_output)
    
    def select_output_file(self):
        """选择输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".csv",
            initialfile="全部频道.csv",
            filetypes=[
                ("CSV文件", "*.csv"), 
                ("文本文件", "*.txt"), 
                ("M3U文件", "*.m3u"),
                ("M3U8文件", "*.m3u8"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file_path)
    # 跳过购物频道功能添加
    def extract_channels(self, content):
        """从内容中提取频道信息"""
        results = []
        skipped_channels = []  # 记录跳过的频道
        skipped_shopping_channels = []  # 新增：记录跳过的购物频道
        extract_smil = self.extract_smil_var.get()
        extract_m3u8 = self.extract_m3u8_var.get()
        
        # 使用预编译的正则表达式提高性能
        matches = self.channel_pattern.findall(content)
        
        # 处理匹配结果
        for name, url in matches:
            # 跳过包含"购物"关键词的频道
            if "购物" in name:
                skipped_shopping_channels.append(name)
                continue
                    
            added = False
            
            # 如果URL为空或不包含有效地址，则跳过并记录
            if not url or url.startswith("/-?") or (not ".smil" in url and not ".m3u8" in url):
                skipped_channels.append(name)
                continue
            
            # 根据用户选择的格式进行处理
            if extract_smil and ".smil" in url:
                smil_index = url.rfind(".smil")
                if smil_index != -1:
                    results.append((name, f"{name},{url[:smil_index+5]}"))
                    added = True
            
            if extract_m3u8 and ".m3u8" in url:
                m3u8_index = url.rfind(".m3u8")
                if m3u8_index != -1:
                    results.append((name, f"{name},{url[:m3u8_index+5]}"))
                    added = True
            
            # 如果两种格式都没选，或URL中没有这两种格式，则保留原URL
            if not added and (not extract_smil and not extract_m3u8 or 
                             not (".smil" in url or ".m3u8" in url)):
                results.append((name, f"{name},{url}"))
        
        # 对结果进行排序
        sorted_results = self.sort_channels(results)
        
        return sorted_results, skipped_channels, skipped_shopping_channels  # 返回结果和两种跳过的频道
    def start_processing(self):
        """在新线程中启动处理"""
        self.process_btn.config(state=tk.DISABLED)
        self.status_var.set("正在处理...")
        self.progress["value"] = 0
        
        # 启动新线程处理文件
        threading.Thread(target=self.process_files, daemon=True).start()
    def sort_channels(self, channels):
        """对频道进行排序"""
        # 创建不同类别的列表
        categories = {
            'cctv_hd_4k': [],  # CCTV高清/4K频道
            'weishi_hd': [],   # 卫视高清频道
            'bendi': [],       # 本地频道
            'other_hd': [],    # 其他高清频道
            'weishi': [],      # 卫视标清(不含高清)
            'others': []       # 其他频道
        }
        
        # 对频道进行分类
        for name, full_info in channels:
            # CCTV高清或4K频道
            if "CCTV" in name and ("高清" in name or "4K" in name):
                categories['cctv_hd_4k'].append(full_info)
            # 卫视高清频道
            elif "卫视" in name and "高清" in name and "内蒙古" not in name:
                categories['weishi_hd'].append(full_info)
            # 本地区频道
            elif ("内蒙古" in name and "高清" in name) or "呼和浩特" in name:
                categories['bendi'].append(full_info)
            # 其他高清频道
            elif "高清" in name and "卫视" not in name and "内蒙古" not in name:
                categories['other_hd'].append(full_info)
            # 卫视标清(不含高清)
            elif "卫视" in name:
                categories['weishi'].append(full_info)
            # 其他所有频道
            else:
                categories['others'].append(full_info)
        
        # 按照优先级顺序合并结果
        return (categories['cctv_hd_4k'] + categories['weishi_hd'] + 
                categories['bendi'] + categories['other_hd'] + 
                categories['weishi'] + categories['others'])
    def format_results_with_headers(self, results):
        """为分类的结果添加标题行"""
        # 创建不同类别的列表
        categories = {
            'cctv_hd_4k': [],  # CCTV高清/4K频道
            'weishi_hd': [],   # 卫视高清频道
            'bendi': [],       # 本地频道
            'other_hd': [],    # 其他高清频道
            'weishi': [],      # 卫视标清(不含高清)
            'others': []       # 其他频道
        }
        
        # 分类标题映射
        category_titles = {
            'cctv_hd_4k': '央视高清,#genre#',
            'weishi_hd': '卫视高清,#genre#',
            'bendi': '本地频道,#genre#',
            'other_hd': '其他高清,#genre#',
            'weishi': '卫视标清,#genre#',
            'others': '其他频道,#genre#'
        }
        
        # 对频道进行分类
        for item in results:
            name = item.split(',')[0]  # 从结果中提取频道名称
            
            # CCTV高清或4K频道
            if "CCTV" in name and ("高清" in name or "4K" in name):
                categories['cctv_hd_4k'].append(item)
            # 卫视高清频道
            elif "卫视" in name and "高清" in name and "内蒙古" not in name:
                categories['weishi_hd'].append(item)
            # 本地区频道
            elif ("内蒙古" in name and "高清" in name) or "呼和浩特" in name:
                categories['bendi'].append(item)
            # 其他高清频道
            elif "高清" in name and "卫视" not in name and "内蒙古" not in name:
                categories['other_hd'].append(item)
            # 卫视标清(不含高清)
            elif "卫视" in name:
                categories['weishi'].append(item)
            # 其他所有频道
            else:
                categories['others'].append(item)
        
        # 合并结果，添加分类标题
        formatted_results = []
        for category, title in category_titles.items():
            if categories[category]:  # 只有当该分类有频道时才添加标题
                formatted_results.append(title)
                formatted_results.extend(categories[category])
                # 不添加空行，保持格式一致性
        
        return formatted_results
    def process_files(self):
        """处理文件主逻辑"""
        input_path = self.input_entry.get()
        output_path = self.output_entry.get()
        
        if not input_path or not output_path:
            self.show_error("请先选择输入和输出文件")
            return
        
        try:
            # 读取文件内容
            with open(input_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.progress["value"] = 30
            
            # 提取频道信息
            results, skipped_channels, skipped_shopping_channels = self.extract_channels(content)
            
            self.progress["value"] = 60
            
            if not results:
                self.show_error("未找到任何有效频道信息")
                return
            
            # 获取带有分类标题的格式化结果
            formatted_results = self.format_results_with_headers(results)
            
            # 保存为CSV（使用utf-8-sig解决Excel乱码问题）
            with open(output_path, "w", encoding="utf-8-sig") as f:
                f.write("\n".join(formatted_results))
            
            self.progress["value"] = 100
            
            # 显示处理结果
            self.show_results(results, skipped_channels, skipped_shopping_channels)
            
        except Exception as e:
            self.show_error(f"处理失败：\n{str(e)}")
        finally:
            self.process_btn.config(state=tk.NORMAL)
            self.status_var.set(f"处理完成，共提取 {len(results) if 'results' in locals() else 0} 条记录")
    def show_results(self, results, skipped_channels, skipped_shopping_channels):
        """在结果区域显示提取结果"""
        self.result_text.delete(1.0, tk.END)
        
        # 显示统计信息
        self.result_text.insert(tk.END, f"成功提取 {len(results)} 条记录\n")
        self.result_text.insert(tk.END, f"跳过 {len(skipped_channels)} 条无效地址记录\n")
        self.result_text.insert(tk.END, f"跳过 {len(skipped_shopping_channels)} 条购物频道\n\n")
        
        # 显示前5条记录作为示例
        self.result_text.insert(tk.END, "示例数据：\n")
        for i, result in enumerate(results[:5]):
            self.result_text.insert(tk.END, f"{i+1}. {result}\n")
        
        # 如果有更多记录，显示省略信息
        if len(results) > 5:
            self.result_text.insert(tk.END, f"\n... 还有 {len(results)-5} 条记录\n")
        
        # 显示部分跳过的频道
        if skipped_channels:
            self.result_text.insert(tk.END, f"\n跳过的无效地址频道示例：\n")
            for i, name in enumerate(skipped_channels[:3]):
                self.result_text.insert(tk.END, f"{i+1}. {name}\n")
            
            if len(skipped_channels) > 3:
                self.result_text.insert(tk.END, f"... 还有 {len(skipped_channels)-3} 个跳过的频道\n")
        
        # 显示部分跳过的购物频道
        if skipped_shopping_channels:
            self.result_text.insert(tk.END, f"\n跳过的购物频道示例：\n")
            for i, name in enumerate(skipped_shopping_channels[:3]):
                self.result_text.insert(tk.END, f"{i+1}. {name}\n")
            
            if len(skipped_shopping_channels) > 3:
                self.result_text.insert(tk.END, f"... 还有 {len(skipped_shopping_channels)-3} 个购物频道\n")
        
        # 显示输出文件路径
        self.result_text.insert(tk.END, f"\n完整数据已保存至：\n{self.output_entry.get()}")
    
    def show_error(self, message):
        """显示错误信息"""
        messagebox.showerror("错误", message)
        self.status_var.set("处理出错")
        self.process_btn.config(state=tk.NORMAL)
    
    def clear_results(self):
        """清空结果区域"""
        self.result_text.delete(1.0, tk.END)
        self.progress["value"] = 0
        self.status_var.set("准备就绪")
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = IPTVExtractor()
    app.run()