import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_icon():
    """创建应用图标"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 检查图标是否已存在
        if os.path.exists("icon.ico"):
            print("图标文件已存在，跳过创建")
            return True
            
        # 创建一个新的图像
        img = Image.new('RGBA', (256, 256), color=(76, 175, 80, 255))
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体，如果失败则使用默认字体
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except IOError:
            font = ImageFont.load_default()
        
        # 添加文本
        draw.text((128, 128), "IPTV", fill="white", font=font, anchor="mm")
        
        # 保存为ICO文件
        img.save('icon.ico')
        print("图标已创建: icon.ico")
        return True
    except ImportError:
        print("警告: 未安装PIL库，无法创建图标")
        return False
    except Exception as e:
        print(f"创建图标时出错: {e}")
        return False

def check_dependencies():
    """检查并安装依赖"""
    required_packages = ["nuitka", "ordered-set", "pillow"]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"正在安装 {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✓ {package} 安装完成")

def compile_app():
    """编译应用程序"""
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "IPTV频道提取工具.py")
    
    # 创建输出目录
    output_dir = os.path.join(current_dir, "dist")
    os.makedirs(output_dir, exist_ok=True)
    
    # 构建编译命令
    icon_path = os.path.join(current_dir, "icon.ico")
    
    # 基本编译选项
    compile_options = [
        sys.executable, "-m", "nuitka",
        "--mingw64",                    # 使用MinGW64编译器
        "--standalone",                 # 创建独立的可执行文件包
        "--show-progress",              # 显示编译进度
        "--show-memory",                # 显示内存使用情况
        "--plugin-enable=tk-inter",     # 启用tkinter插件支持
        "--windows-disable-console",    # 禁用控制台窗口
        f"--windows-icon-from-ico={icon_path}",  # 设置应用图标
        f"--output-dir={output_dir}",   # 输出目录
        # "--remove-output",              # 删除中间文件 - 暂时注释掉以便调试
        # "--lto=yes",                    # 启用链接时优化 - 暂时注释掉以便调试
        "--static-libpython=no",        # 不使用静态Python库
        # 暂时简化版本信息，减少可能的错误点
        "--windows-company-name=TraeAI",  # 公司名称(移除空格)
        "--windows-product-name=IPTVExtractor",  # 产品名称(使用英文)
        "--windows-file-version=1.2.0",  # 文件版本(简化)
        "--windows-product-version=1.2.0",  # 产品版本(简化)
        "--windows-file-description=IPTVExtractor",  # 文件描述(使用英文)
        app_path                        # 应用程序路径
    ]
    
    # 执行编译命令
    print("开始编译应用程序...")
    print(f"编译命令: {' '.join(compile_options)}")
    
    try:
        # 使用capture_output捕获输出以便调试
        result = subprocess.run(compile_options, check=False, capture_output=True, text=True)
        
        # 检查编译结果
        if result.returncode != 0:
            print(f"编译失败，返回代码: {result.returncode}")
            print("错误输出:")
            print(result.stderr)
            print("\n标准输出:")
            print(result.stdout)
            
            # 尝试更简单的编译命令
            print("\n尝试使用简化的编译命令...")
            simple_options = [
                sys.executable, "-m", "nuitka",
                "--standalone",
                "--plugin-enable=tk-inter",
                f"--output-dir={output_dir}",
                app_path
            ]
            print(f"简化命令: {' '.join(simple_options)}")
            
            simple_result = subprocess.run(simple_options, check=False, capture_output=True, text=True)
            if simple_result.returncode == 0:
                print("简化编译成功!")
                return True
            else:
                print("简化编译也失败了，错误输出:")
                print(simple_result.stderr)
                return False
        else:
            print("编译成功!")
            return True
    except Exception as e:
        print(f"编译过程中发生异常: {e}")
        return False

def cleanup_dist():
    """清理编译后的目录，删除不必要的文件"""
    dist_dir = Path("dist") / "IPTV频道提取工具.dist"
    
    if not dist_dir.exists():
        print(f"目录不存在: {dist_dir}")
        return
    
    print("正在清理编译目录...")
    
    # 要删除的文件扩展名
    extensions_to_remove = [".pdb", ".lib", ".a", ".pyc"]
    
    # 遍历目录删除不必要的文件
    for ext in extensions_to_remove:
        for file in dist_dir.glob(f"**/*{ext}"):
            try:
                file.unlink()
                print(f"已删除: {file}")
            except Exception as e:
                print(f"无法删除 {file}: {e}")
    
    print("清理完成!")

def main():
    """主函数"""
    print("=" * 50)
    print("IPTV频道提取工具编译脚本")
    print("=" * 50)
    
    # 检查并安装依赖
    print("\n[1/4] 检查依赖...")
    check_dependencies()
    
    # 创建图标
    print("\n[2/4] 创建应用图标...")
    create_icon()
    
    # 编译应用
    print("\n[3/4] 编译应用程序...")
    if compile_app():
        # 清理编译目录
        print("\n[4/4] 清理编译目录...")
        cleanup_dist()
        
        # 显示完成信息
        print("\n" + "=" * 50)
        print("编译成功! 可执行文件位于:")
        print(f"  {os.path.abspath('dist/IPTV频道提取工具.dist/IPTV频道提取工具.exe')}")
        print("=" * 50)
    else:
        print("\n编译失败，请检查错误信息")

if __name__ == "__main__":
    main()