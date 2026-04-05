"""
INI 文件差异比较和补丁生成工具
"""
import configparser
from common import clean_ini_file, create_config_parser


def compare_and_generate_patch(original_file, modified_file, patch_file):
    """
    比较两个 INI 文件,生成只包含差异的补丁文件

    Args:
        original_file (str): 原始 INI 文件路径
        modified_file (str): 修改后的 INI 文件路径
        patch_file (str): 输出的补丁文件路径
    """
    print(f"正在读取原始文件: {original_file}")
    cleaned_original = clean_ini_file(original_file)
    
    print(f"正在读取修改后的文件: {modified_file}")
    cleaned_modified = clean_ini_file(modified_file)

    # 加载两个配置文件
    config_original = create_config_parser()
    config_original.read_file(cleaned_original)

    config_modified = create_config_parser()
    config_modified.read_file(cleaned_modified)

    # 创建补丁配置对象
    config_patch = create_config_parser()

    diff_count = 0
    added_sections = 0
    modified_sections = 0

    # 遍历修改后的文件中的所有节
    for section in config_modified.sections():
        # 如果原始文件中没有这个节,说明是新增的
        if not config_original.has_section(section):
            config_patch.add_section(section)
            for key, value in config_modified.items(section):
                config_patch.set(section, key, value)
            added_sections += 1
            diff_count += len(config_modified.items(section))
            print(f"  [+] 新增节: [{section}] ({len(config_modified.items(section))} 个键值对)")
        else:
            # 节存在,检查其中的键值对是否有差异
            section_has_diff = False
            for key, value in config_modified.items(section):
                # 检查原始文件中是否有这个键,以及值是否相同
                if not config_original.has_option(section, key):
                    # 新增的键
                    if not config_patch.has_section(section):
                        config_patch.add_section(section)
                    config_patch.set(section, key, value)
                    section_has_diff = True
                    diff_count += 1
                    print(f"  [+] 新增键: [{section}] {key} = {value}")
                elif config_original.get(section, key) != value:
                    # 值被修改了
                    if not config_patch.has_section(section):
                        config_patch.add_section(section)
                    config_patch.set(section, key, value)
                    section_has_diff = True
                    diff_count += 1
                    original_value = config_original.get(section, key)
                    print(f"  [*] 修改键: [{section}] {key}")
                    print(f"      原值: {original_value}")
                    print(f"      新值: {value}")
            
            if section_has_diff:
                modified_sections += 1

    # 写入补丁文件
    if diff_count > 0:
        with open(patch_file, 'w', encoding='utf-8') as f:
            config_patch.write(f)
        
        print("\n" + "="*60)
        print(f"补丁文件已生成: {patch_file}")
        print(f"总计差异: {diff_count} 处")
        print(f"  - 新增节: {added_sections} 个")
        print(f"  - 修改节: {modified_sections} 个")
        print("="*60)
    else:
        print("\n两个文件完全相同,无需生成补丁文件。")


if __name__ == "__main__":
    # 定义文件路径
    ORIGINAL_FILE = "rules.ini"
    MODIFIED_FILE = "rules_myadd.ini"
    PATCH_OUTPUT = "patch_rules.ini"

    print("开始比较 INI 文件并生成补丁...")
    print("="*60)
    
    try:
        compare_and_generate_patch(ORIGINAL_FILE, MODIFIED_FILE, PATCH_OUTPUT)
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
