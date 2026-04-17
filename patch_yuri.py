"""
红色警戒2: 尤里的复仇 (Yuri's Revenge) 补丁应用脚本
"""
from common import apply_patch

# 定义主配置文件和补丁文件的路径
MAIN_CONFIG_FILE = "E:/Games/YURI/rulesmd.ini"
PATCH_CONFIG_FILE = "patch_rulesmd.ini"

if __name__ == "__main__":
    print("开始应用 Yuri's Revenge 补丁...")
    print("="*60)
    success = apply_patch(MAIN_CONFIG_FILE, PATCH_CONFIG_FILE)
    if success:
        print("\n补丁应用成功！")
    else:
        print("\n补丁应用失败！")