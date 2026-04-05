"""
公共工具模块 - 提供 INI 文件处理的通用功能
"""
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
    # 尝试多种编码方式读取文件
    encodings = ['utf-8', 'latin-1', 'cp1252', 'gbk']
    content = None
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.readlines()
            print(f"成功使用 {encoding} 编码读取文件")
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if content is None:
        raise UnicodeDecodeError(f"无法使用以下编码读取文件: {encodings}")
    
    for line_num, line in enumerate(content, 1):
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
                # 节标题可能后面有注释，如: [Section] ;comment
                # 所以只需检查是否以 '[' 开头并包含 ']'
                if not (stripped_line.startswith('[') and ']' in stripped_line):
                    # print(f"已删除行 {line_num}: 缺少 '=' 或格式不正确 - '{stripped_line}'")
                    continue

            # 如果以上检查都通过，则保留该行
            cleaned_lines.append(line)

    # 将清理后的内容放入一个内存文件对象中，方便 configparser 读取
    return io.StringIO("".join(cleaned_lines))


def create_config_parser():
    """
    创建并配置一个 ConfigParser 对象
    
    Returns:
        configparser.ConfigParser: 配置好的 ConfigParser 对象
    """
    config = configparser.ConfigParser(interpolation=None, strict=False, delimiters=('=',))
    config.optionxform = str
    config.write_delim_same_as_delimiters = True
    return config


def apply_patch(main_config_file, patch_config_file, backup=True):
    """
    将补丁文件应用到主配置文件
    
    Args:
        main_config_file (str): 主配置文件路径
        patch_config_file (str): 补丁文件路径
        backup (bool): 是否创建备份，默认为 True
        
    Returns:
        bool: 操作是否成功
    """
    backup_config_file = f"{main_config_file}.backup"
    
    try:
        # 步骤 1: 备份原始主文件
        if backup and os.path.exists(main_config_file):
            shutil.copyfile(main_config_file, backup_config_file)
            print(f"原始文件已备份到 '{backup_config_file}'")
        elif not os.path.exists(main_config_file):
            print(f"错误：主文件 '{main_config_file}' 不存在。")
            return False

        # 步骤 2: 清理主文件，并获取其内存对象
        cleaned_main_file_obj = clean_ini_file(main_config_file)

        # 步骤 3: 将清理后的主文件内容加载到 configparser 对象
        config = create_config_parser()
        config.read_file(cleaned_main_file_obj)

        # 步骤 4: 读取并合并补丁文件
        # 尝试多种编码方式读取补丁文件
        patch_encodings = ['utf-8', 'latin-1', 'cp1252', 'gbk']
        patch_read_success = False
        for encoding in patch_encodings:
            try:
                config.read(patch_config_file, encoding=encoding)
                print(f"成功使用 {encoding} 编码读取补丁文件")
                patch_read_success = True
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if not patch_read_success:
            raise UnicodeDecodeError(f"无法使用以下编码读取补丁文件: {patch_encodings}")
        
        print(f"文件 '{patch_config_file}' 已成功合并。")

        # 步骤 5: 将合并后的配置写入回原始主文件
        # 使用 latin-1 编码以保持与原始 RA2 文件格式兼容
        with open(main_config_file, 'w', encoding='latin-1') as configfile:
            config.write(configfile)

        print(f"合并后的配置已成功写入到 '{main_config_file}'")
        return True

    except Exception as e:
        print(f"在操作过程中发生错误: {e}")
        return False
