#!/usr/bin/env python3
"""
Feishu File Fetcher
从飞书媒体目录获取文件到 workspace

用法:
    python fetch_feishu_files.py --list              # 列出所有文件
    python fetch_feishu_files.py --list --type doc   # 列出文档文件
    python fetch_feishu_files.py --latest             # 获取最新文件
    python fetch_feishu_files.py filename.docx        # 获取指定文件
    python fetch_feishu_files.py --help              # 显示帮助
"""

import argparse
import shutil
import sys
from pathlib import Path
from datetime import datetime

# 设置标准输出编码为 UTF-8（Windows 兼容）
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# 配置
MEDIA_DIR = Path.home() / ".nanobot" / "media" / "feishu"
WORKSPACE_DIR = Path.cwd()


def list_files(file_type=None):
    """列出飞书媒体目录中的文件"""
    if not MEDIA_DIR.exists():
        print(f"❌ 飞书媒体目录不存在: {MEDIA_DIR}")
        return []

    files = []
    for filepath in MEDIA_DIR.iterdir():
        if filepath.is_file():
            if file_type and not _match_type(filepath, file_type):
                continue
            files.append(filepath)

    # 按修改时间排序
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    return files


def _match_type(filepath: Path, file_type: str) -> bool:
    """检查文件是否匹配指定类型"""
    ext = filepath.suffix.lower()

    type_map = {
        "image": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"},
        "doc": {".doc", ".docx", ".pdf", ".txt", ".md", ".xlsx", ".pptx"},
        "pdf": {".pdf"},
        "text": {".txt", ".md", ".py", ".js", ".html", ".css", ".json"},
        "all": set(),
    }

    if file_type not in type_map:
        return True

    return ext in type_map[file_type] or file_type == "all"


def format_filesize(size: int) -> str:
    """格式化文件大小"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def show_files(files):
    """显示文件列表"""
    if not files:
        print(f"📁 飞书媒体目录: {MEDIA_DIR}")
        print("   未找到文件")
        return

    print(f"📁 飞书媒体目录: {MEDIA_DIR}")
    print(f"   找到 {len(files)} 个文件\n")

    for i, filepath in enumerate(files, 1):
        stat = filepath.stat()
        size = format_filesize(stat.st_size)
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        # 文件名对齐显示
        name = filepath.name
        spacing = " " * (50 - len(name)) if len(name) < 50 else " "

        print(f"    {i}. {name}{spacing}{size:>10}  {mtime}")


def fetch_file(filename: str, output_dir: Path = None):
    """获取指定文件"""
    source_file = MEDIA_DIR / filename

    if not source_file.exists():
        print(f"❌ 文件不存在: {source_file}")
        return False

    # 确定目标目录
    if output_dir is None:
        output_dir = WORKSPACE_DIR

    output_dir.mkdir(parents=True, exist_ok=True)
    target_file = output_dir / filename

    # 复制文件
    try:
        shutil.copy2(source_file, target_file)
        size = format_filesize(source_file.stat().st_size)

        print(f"✅ 已复制: {filename}")
        print(f"   来源: {source_file}")
        print(f"   目标: {target_file}")
        print(f"   大小: {size}")

        return True
    except Exception as e:
        print(f"❌ 复制失败: {e}")
        return False


def fetch_latest(file_type=None, output_dir: Path = None):
    """获取最新文件"""
    files = list_files(file_type)

    if not files:
        print("❌ 未找到文件")
        return False

    latest = files[0]
    return fetch_file(latest.name, output_dir)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="从飞书媒体目录获取文件到 workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --list                    列出所有文件
  %(prog)s --list --type image       列出图片文件
  %(prog)s --list --type doc         列出文档文件
  %(prog)s --latest                  获取最新文件
  %(prog)s --latest --type doc       获取最新文档
  %(prog)s filename.docx             获取指定文件
  %(prog)s filename.docx --output ./downloads/  指定输出目录

支持的文件类型:
  all    所有文件
  image  图片文件 (png, jpg, jpeg, gif, webp, bmp, svg)
  doc    文档文件 (doc, docx, pdf, txt, md, xlsx, pptx)
  pdf    PDF 文件
  text   文本文件 (txt, md, py, js, html, css, json)
        """
    )

    parser.add_argument(
        "filename",
        nargs="?",
        help="要获取的文件名"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="列出飞书媒体目录中的文件"
    )

    parser.add_argument(
        "--latest",
        action="store_true",
        help="获取最新文件"
    )

    parser.add_argument(
        "--type",
        choices=["all", "image", "doc", "pdf", "text"],
        default="all",
        help="文件类型筛选 (默认: all)"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="输出目录 (默认: 当前 workspace)"
    )

    args = parser.parse_args()

    # 处理命令
    if args.list:
        files = list_files(args.type if args.type != "all" else None)
        show_files(files)
    elif args.latest:
        file_type = args.type if args.type != "all" else None
        fetch_latest(file_type, args.output)
    elif args.filename:
        fetch_file(args.filename, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
