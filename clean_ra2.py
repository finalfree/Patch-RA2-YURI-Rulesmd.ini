"""
红色警戒2 (RA2) INI 文件清理脚本
仅执行清理操作，不应用任何补丁
"""
from common import clean_ini_file
import os

# 定义需要清理的配置文件路径
CONFIG_FILE = "E:/Games/RA2/rules.ini"

if __name__ == "__main__":
    print("开始清理 RA2 配置文件...")
    print("="*60)
    
    # 检查文件是否存在
    if not os.path.exists(CONFIG_FILE):
        print(f"错误：文件 '{CONFIG_FILE}' 不存在。")
        exit(1)
    
    try:
        # 清理文件并获取清理后的内容
        cleaned_content = clean_ini_file(CONFIG_FILE)
        
        # 将清理后的内容写回原文件
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(cleaned_content.getvalue())
        
        print(f"文件 '{CONFIG_FILE}' 清理完成！")
        print("已移除以下内容：")
        print("  - 以 '//' 开头的非标准注释行")
        print("  - 以 ':' 开头的非标准格式行")
        print("  - 不包含 '=' 的非空行（排除标准注释和节标题）")
        
    except Exception as e:
        print(f"清理过程中发生错误: {e}")
        exit(1)
