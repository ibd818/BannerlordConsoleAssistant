import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from bannerlord_assistant.app import MainWindow, command_tags
from bannerlord_assistant.core import packaged_data_path


class GuiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_window_loads_and_generates_default_command(self):
        window = MainWindow(packaged_data_path())
        self.assertGreater(window.command_list.count(), 0)
        self.assertEqual(window.current_command.name, "启用作弊模式")
        self.assertEqual(window.generated_input.text(), "config.cheat_mode 1")
        self.assertTrue(window.copy_button.isEnabled())
        window.close()

    def test_context_tags_distinguish_normal_and_dangerous_commands(self):
        window = MainWindow(packaged_data_path())
        gold = next(command for command in window.commands if command.name == "增加金币")
        kill = next(command for command in window.commands if command.name == "杀死指定英雄")
        self.assertEqual(command_tags(gold), [("战役/沙盒", "info"), ("需要作弊模式", "info")])
        self.assertIn(("永久修改", "risk"), command_tags(kill))
        self.assertIn(("建议先保存", "risk"), command_tags(kill))
        window.close()


if __name__ == "__main__":
    unittest.main()
