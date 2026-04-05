import io
import configparser
import os
import shutil


def clean_ini_file(file_path):
    """
    清理 .ini 文件中的不规范行，包括：
    1. 以 '//' 开头的行（非标准注释格式）
    2. 以 ':' 开头的行（非标准键值对或注释格式）
    3. 不包含 '=' 符号的非空行（非键值对）

    Args:
        file_path (str): 待清理的 .ini 文件的路径。

    Returns:
        io.StringIO: 包含清理后内容的内存文件对象，可以直接传递给 configparser。
    """
    cleaned_lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stripped_line = line.strip()

            # 忽略空行
            if not stripped_line:
                cleaned_lines.append(line)  # 保留空行以维持结构，但它们会被configparser忽略
                continue

            # 1. 检查以 '//' 开头的行
            if stripped_line.startswith('//'):
                # print(f"已删除行 {line_num}: 非标准注释 // - '{stripped_line}'")
                continue

            # 2. 检查以 ':' 开头的行
            if stripped_line.startswith(':'):
                # print(f"已删除行 {line_num}: 非标准格式 : - '{stripped_line}'")
                continue

            # 3. 检查不包含 '=' 符号的非空行 (排除标准注释 # 或 ;)
            # configparser 默认会处理以 # 或 ; 开头的标准注释
            if '=' not in stripped_line and \
                    not stripped_line.startswith('#') and \
                    not stripped_line.startswith(';'):
                # 进一步检查，如果行是合法的 [section] 头，则保留
                # configparser 严格模式下会处理重复节，但在这里我们只关注格式错误
                if not (stripped_line.startswith('[') and stripped_line.endswith(']')):
                    # print(f"已删除行 {line_num}: 缺少 '=' 或格式不正确 - '{stripped_line}'")
                    continue

            # 如果以上检查都通过，则保留该行
            cleaned_lines.append(line)

    # 将清理后的内容放入一个内存文件对象中，方便 configparser 读取
    return io.StringIO("".join(cleaned_lines))


# 定义主配置文件和补丁文件的路径
MAIN_CONFIG_FILE = "E:/Games/RA2/rules.ini"
PATCH_CONFIG_FILE = "patch_rules.ini"
BACKUP_CONFIG_FILE = f"{MAIN_CONFIG_FILE}.backup"  # 备份文件路径


try:
    # 步骤 1: 备份原始主文件
    if os.path.exists(MAIN_CONFIG_FILE):
        shutil.copyfile(MAIN_CONFIG_FILE, BACKUP_CONFIG_FILE)
        print(f"原始文件已备份到 '{BACKUP_CONFIG_FILE}'")
    else:
        print(f"错误：主文件 '{MAIN_CONFIG_FILE}' 不存在，无法备份。")
        exit()

    # 步骤 2: 清理主文件，并获取其内存对象
    cleaned_main_file_obj = clean_ini_file(MAIN_CONFIG_FILE)

    # 步骤 3: 将清理后的主文件内容加载到 configparser 对象
    config = configparser.ConfigParser(interpolation=None, strict=False, delimiters=('=',))
    config.optionxform = str
    config.write_delim_same_as_delimiters = True
    config.read_file(cleaned_main_file_obj)

    # 步骤 4: 读取并合并 patched.ini 文件
    config.read(PATCH_CONFIG_FILE, encoding='utf-8')
    print(f"文件 '{PATCH_CONFIG_FILE}' 已成功合并。")

    # 步骤 5: 将合并后的配置写入回原始主文件
    with open(MAIN_CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

    print(f"合并后的配置已成功写入到 '{MAIN_CONFIG_FILE}'")


except Exception as e:
    print(f"在操作过程中发生错误: {e}")