"""
Feishu File Handler Skill
自动处理从飞书发送的文件
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any


class FeishuFileHandler:
    """处理飞书文件消息的类"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化文件处理器

        Args:
            config_path: 配置文件路径，默认为当前目录的 config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.debug = False
        self.processed_messages = self._load_processed_messages()

    def _log(self, message: str):
        """调试日志"""
        if self.debug:
            print(f"[DEBUG] {message}")

    def _load_processed_messages(self) -> Dict[str, str]:
        """
        加载已处理的消息记录

        Returns:
            dict: {message_id: timestamp}
        """
        processed_file = Path(self.config.get("processed_messages_file",
                                              "memory/processed_feishu_messages.json"))

        if processed_file.exists():
            try:
                with open(processed_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self._log(f"加载已处理消息记录失败: {e}")
                return {}

        return {}

    def _save_processed_message(self, message_id: str, filepath: str):
        """
        保存已处理的消息记录

        Args:
            message_id: 消息 ID
            filepath: 文件路径
        """
        processed_file = Path(self.config.get("processed_messages_file",
                                              "memory/processed_feishu_messages.json"))
        processed_file.parent.mkdir(parents=True, exist_ok=True)

        self.processed_messages[message_id] = {
            "timestamp": datetime.now().isoformat(),
            "filepath": filepath
        }

        with open(processed_file, "w", encoding="utf-8") as f:
            json.dump(self.processed_messages, f, ensure_ascii=False, indent=2)

        self._log(f"已记录处理消息: {message_id}")

    def _is_processed(self, message_id: str) -> bool:
        """
        检查消息是否已处理

        Args:
            message_id: 消息 ID

        Returns:
            bool: 是否已处理
        """
        return message_id in self.processed_messages

    def _should_trigger_review(self, filename: str) -> bool:
        """
        判断是否应该触发合同审查

        Args:
            filename: 文件名

        Returns:
            bool: 是否触发审查
        """
        if not self.config.get("auto_trigger_review", False):
            return False

        # 检查文件扩展名
        ext = Path(filename).suffix.lower()
        if ext not in self.config.get("supported_filetypes", []):
            return False

        # 检查文件名关键词
        keywords = ["合同", "协议", "条款", "补充", "约定", "contract", "agreement"]
        return any(keyword in filename for keyword in keywords)

    def _find_source_file(self, file_key: str, filename: str) -> Optional[Path]:
        """
        在源目录中查找文件

        Args:
            file_key: 飞书文件 key
            filename: 文件名

        Returns:
            Path or None: 文件路径
        """
        source_dir = Path(self.config["source_dir"]).expanduser()

        if not source_dir.exists():
            self._log(f"源目录不存在: {source_dir}")
            return None

        self._log(f"在目录中查找文件: {source_dir}")
        self._log(f"查找关键词: file_key={file_key}, filename={filename}")

        # 方案 1: 直接通过文件名匹配
        exact_match = source_dir / filename
        if exact_match.exists():
            self._log(f"找到精确匹配: {exact_match}")
            return exact_match

        # 方案 2: 遍历目录查找（处理文件名可能被修改的情况）
        for filepath in source_dir.iterdir():
            if filepath.is_file():
                self._log(f"检查文件: {filepath.name}")
                # 检查文件名是否包含 filename
                if filename in filepath.name:
                    self._log(f"找到模糊匹配: {filepath}")
                    return filepath

        self._log(f"未找到文件: {filename}")
        return None

    def _copy_to_workspace(self, source_file: Path, filename: str) -> Path:
        """
        将文件复制到工作目录

        Args:
            source_file: 源文件路径
            filename: 文件名

        Returns:
            Path: 目标文件路径
        """
        target_dir = Path(self.config["target_dir"])
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file = target_dir / filename

        # 处理文件名冲突
        if target_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = Path(filename).stem
            ext = Path(filename).suffix
            target_file = target_dir / f"{stem}_{timestamp}{ext}"
            self._log(f"文件已存在，使用新文件名: {target_file.name}")

        # 复制文件
        shutil.copy2(source_file, target_file)
        self._log(f"文件已复制: {source_file} -> {target_file}")

        return target_file

    def handle_file_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理飞书文件消息

        Args:
            message: 飞书消息对象

        Returns:
            dict: 处理结果
        """
        message_id = message.get("message_id")

        # 检查是否已处理
        if self._is_processed(message_id):
            self._log(f"消息已处理，跳过: {message_id}")
            return {
                "success": True,
                "message": "文件已在之前处理过",
                "already_processed": True,
                "user_message": "ℹ️ 该文件已在之前处理过"
            }

        self._log(f"开始处理文件消息: {message_id}")

        # 提取文件信息
        try:
            msg_type = message.get("msg_type")
            if msg_type != "file":
                return {
                    "success": False,
                    "message": f"不支持的消息类型: {msg_type}",
                    "user_message": "❌ 只能处理文件类型的消息"
                }

            content = message.get("content", {})
            if isinstance(content, str):
                # 如果 content 是字符串，尝试解析 JSON
                content = json.loads(content)

            file_key = content.get("file_key")
            filename = content.get("filename")

            if not file_key or not filename:
                self._log(f"缺少文件信息: file_key={file_key}, filename={filename}")
                return {
                    "success": False,
                    "message": "缺少文件信息",
                    "user_message": "❌ 无法获取文件信息"
                }

            self._log(f"文件信息: file_key={file_key}, filename={filename}")

            # 查找源文件
            source_file = self._find_source_file(file_key, filename)
            if not source_file:
                return {
                    "success": False,
                    "message": f"未找到文件: {filename}",
                    "user_message": f"❌ 未找到文件【{filename}】，请确认文件是否已下载"
                }

            # 复制到工作目录
            target_file = self._copy_to_workspace(source_file, filename)

            # 记录已处理
            self._save_processed_message(message_id, str(target_file))

            # 判断是否触发审查
            trigger_review = self._should_trigger_review(filename)

            # 构建用户消息
            user_message = f"✅ 已收到文件【{filename}】，已存档至 workspace"
            if trigger_review:
                user_message += "\n📋 正在开始合同审查..."

            self._log(f"处理完成: {target_file}")

            return {
                "success": True,
                "message": "文件已处理",
                "source_file": str(source_file),
                "target_file": str(target_file),
                "filename": filename,
                "file_key": file_key,
                "message_id": message_id,
                "trigger_review": trigger_review,
                "user_message": user_message
            }

        except Exception as e:
            self._log(f"处理失败: {e}")
            return {
                "success": False,
                "message": str(e),
                "user_message": f"❌ 处理文件时出错: {str(e)}"
            }


# 便捷函数
def handle_feishu_file(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    便捷函数：直接处理飞书文件消息

    Args:
        message: 飞书消息对象

    Returns:
        dict: 处理结果
    """
    handler = FeishuFileHandler()
    return handler.handle_file_message(message)


if __name__ == "__main__":
    # 测试代码
    import sys

    handler = FeishuFileHandler()
    handler.debug = True

    # 模拟测试消息
    test_message = {
        "msg_type": "file",
        "message_id": "om_test_123456",
        "content": {
            "file_key": "v3_test_key",
            "filename": "测试合同.txt"
        },
        "sender": {
            "sender_id": "ou_test_user",
            "sender_type": "user"
        },
        "create_time": "1773113696"
    }

    result = handler.handle_file_message(test_message)
    print("\n处理结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
