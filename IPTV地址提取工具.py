import re
import tkinter as tk
from tkinter import filedialog, messagebox

def extract_channels(jsp_content):
    """从JSP内容中提取频道信息（处理到.smil为止）"""
    # 匹配ChannelName和TimeShiftURL，忽略问号后的参数
    pattern = r"Authentication\.CUSetConfig\(.*?ChannelName=\"(.*?)\".*?TimeShiftURL=\"([^?\"]*)"
    matches = re.findall(pattern, jsp_content, re.DOTALL)
    
    # 处理结果确保.smil完整性
    processed = []
    for name, url in matches:
        # 找到最后一个.smil的位置
        smil_index = url.rfind(".smil")
        if smil_index != -1:
            clean_url = url[:smil_index+5]  # +5保留.smil
        else:
            clean_url = url  # 如果没有.smil则保留原URL
        processed.append(f"{name},{clean_url}")
    
    return processed

def select_input_file():
    """选择输入文件"""
    file_path = filedialog.askopenfilename(
        title="选择JSP文件",
        filetypes=[("JSP文件", "*.jsp"), ("所有文件", "*.*")]
    )
    input_entry.delete(0, tk.END)
    input_entry.insert(0, file_path)

def select_output_file():
    """选择输出文件"""
    file_path = filedialog.asksaveasfilename(
        title="保存CSV文件",
        defaultextension=".csv",
        filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
    )
    output_entry.delete(0, tk.END)
    output_entry.insert(0, file_path)

def process_files():
    """处理文件主逻辑"""
    input_path = input_entry.get()
    output_path = output_entry.get()
    
    if not input_path or not output_path:
        messagebox.showerror("错误", "请先选择输入和输出文件")
        return
    
    try:
        # 读取文件内容
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 提取频道信息
        results = extract_channels(content)
        
        # 保存为CSV（使用utf-8-sig解决Excel乱码问题）
        with open(output_path, "w", encoding="utf-8-sig") as f:
            f.write("频道名称,播放地址\n")  # 添加标题行
            f.write("\n".join(results))
        
        # 显示处理结果
        info = f"成功提取 {len(results)} 条记录\n示例数据：\n" + "\n".join(results[:3])
        messagebox.showinfo("处理完成", info)
        
    except Exception as e:
        messagebox.showerror("错误", f"处理失败：\n{str(e)}")

# 创建主窗口
root = tk.Tk()
root.title("电视频道提取工具")
root.geometry("680x220")

# 输入文件区域
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="输入文件：", width=10).pack(side=tk.LEFT)
input_entry = tk.Entry(input_frame, width=50)
input_entry.pack(side=tk.LEFT, padx=5)
tk.Button(input_frame, text="选择文件", command=select_input_file).pack(side=tk.LEFT)

# 输出文件区域
output_frame = tk.Frame(root)
output_frame.pack(pady=10)

tk.Label(output_frame, text="输出文件：", width=10).pack(side=tk.LEFT)
output_entry = tk.Entry(output_frame, width=50)
output_entry.pack(side=tk.LEFT, padx=5)
tk.Button(output_frame, text="选择路径", command=select_output_file).pack(side=tk.LEFT)

# 处理按钮
process_btn = tk.Button(root, 
                       text="开始提取", 
                       command=process_files,
                       bg="#4CAF50",
                       fg="white",
                       height=2,
                       width=15)
process_btn.pack(pady=15)

# 版权信息
tk.Label(root, text="© 2024 频道提取工具 | 版本 1.1", fg="gray").pack(side=tk.BOTTOM)

root.mainloop()
