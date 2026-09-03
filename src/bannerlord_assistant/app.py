"""PySide6 desktop application."""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QFont, QIcon, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QCompleter,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from .core import (
    CatalogEntry,
    Command,
    CommandLibraryError,
    ensure_user_library,
    filter_commands,
    load_commands,
    load_entity_catalogs,
)


CATEGORIES = (
    "常用工具",
    "经济",
    "角色",
    "军队",
    "物品与锻造",
    "领地",
    "政治",
    "时间与地图",
    "任务与事件",
    "战斗任务",
    "War Sails 航海",
    "多人游戏",
    "界面与调试",
    "其他",
)


STYLE = """
QWidget { color: #e8edf5; font-family: "Microsoft YaHei UI"; font-size: 13px; }
QMainWindow, QWidget#root { background: #111722; }
QFrame#sidebar { background: #151d2a; border-right: 1px solid #293345; }
QFrame#panel { background: #182130; border: 1px solid #2a364a; border-radius: 12px; }
QLabel#tagInfo { background: #17385d; color: #b9dcff; border: 1px solid #28598a; border-radius: 7px; padding: 6px 10px; font-size: 11px; font-weight: 600; }
QLabel#tagRisk { background: #49351d; color: #ffc76d; border: 1px solid #7b5523; border-radius: 7px; padding: 6px 10px; font-size: 11px; font-weight: 600; }
QLabel#brand { font-size: 20px; font-weight: 700; color: #ffffff; }
QLabel#eyebrow { color: #8493a8; font-size: 11px; font-weight: 600; }
QLabel#title { font-size: 24px; font-weight: 700; color: #ffffff; }
QLabel#section { font-size: 14px; font-weight: 700; color: #bac7d9; }
QLabel#muted { color: #91a0b5; }
QLabel#template { background: #0e1520; color: #80d4ff; padding: 12px; border: 1px solid #29384d; border-radius: 8px; font-family: Consolas; }
QLineEdit { background: #0f1723; border: 1px solid #344258; border-radius: 8px; padding: 9px 11px; selection-background-color: #2b78d0; }
QLineEdit:focus { border: 1px solid #4aa8ff; }
QComboBox { background: #0f1723; border: 1px solid #344258; border-radius: 8px; padding: 9px 11px; selection-background-color: #2b78d0; }
QComboBox:focus { border: 1px solid #4aa8ff; }
QComboBox QAbstractItemView { background: #182130; border: 1px solid #344258; selection-background-color: #2b78d0; padding: 4px; }
QListWidget { background: transparent; border: none; outline: none; }
QListWidget::item { padding: 10px 12px; margin: 2px 0; border-radius: 7px; }
QListWidget::item:hover { background: #202c3d; }
QListWidget::item:selected { background: #1f5f9e; color: white; }
QPushButton { background: #263449; border: 1px solid #354861; border-radius: 8px; padding: 9px 14px; font-weight: 600; }
QPushButton:hover { background: #30445e; }
QPushButton:pressed { background: #213249; }
QPushButton#primary { background: #2785d8; border-color: #3996e4; color: white; padding: 11px 18px; }
QPushButton#primary:hover { background: #3195e8; }
QPushButton:disabled { color: #657287; background: #1b2533; }
QScrollArea { border: none; background: transparent; }
QSplitter::handle { background: #111722; width: 7px; }
QStatusBar { background: #0d131c; color: #91a0b5; border-top: 1px solid #273244; }
"""


def command_tags(command: Command) -> list[tuple[str, str]]:
    """Return concise, user-facing context tags for a command."""
    base = command.command.split()[0].casefold()
    tags: list[tuple[str, str]] = []

    if base.startswith("campaign."):
        tags.extend((("战役/沙盒", "info"), ("需要作弊模式", "info")))
    elif base.startswith("mission."):
        tags.append(("战斗任务", "info"))
    elif base.startswith("naval."):
        tags.extend((("War Sails", "info"), ("海战/自定义海战", "info")))
    elif base.startswith(("mp_", "customserver.", "dcshelper.")):
        tags.append(("多人游戏", "info"))
        if base.startswith("mp_admin."):
            tags.append(("需要管理员权限", "info"))
    elif base.startswith(("benchmark.", "facegen.", "state_string.", "replay_mission.", "ui.")):
        tags.append(("调试功能", "info"))
    elif base.startswith("config.cheat_mode"):
        tags.append(("全局设置", "info"))
    elif base == "help":
        tags.append(("控制台内置", "info"))

    dangerous_markers = (
        "kill", "clear_settlement", "remove_militias", "ban_player",
        "declare_war", "marry_", "conceive_child", "set_all_heroes",
    )
    if any(marker in base for marker in dangerous_markers):
        tags.extend((("永久修改", "risk"), ("建议先保存", "risk")))
    return tags


class CatalogComboBox(QComboBox):
    """Editable candidate selector that emits the original command value."""

    def __init__(self, entries: tuple[CatalogEntry, ...], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.entries = tuple(entries)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setMaxVisibleItems(14)
        for entry in self.entries:
            self.addItem(entry.display_text, entry.value)

        completer = QCompleter(self.model(), self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setMaxVisibleItems(14)
        self.setCompleter(completer)
        self.lineEdit().setPlaceholderText("输入 ID、英文名或中文名，可模糊匹配…")
        completer.activated[str].connect(self._select_completion)

    def set_entry_value(self, value: str) -> None:
        needle = value.strip().casefold()
        for index, entry in enumerate(self.entries):
            candidates = (entry.value, entry.label, entry.display_text, *entry.aliases)
            if any(needle == candidate.casefold() for candidate in candidates):
                self.setCurrentIndex(index)
                return
        self.setEditText(value)

    def raw_value(self) -> str:
        text = self.lineEdit().text().strip()
        index = self.currentIndex()
        if 0 <= index < len(self.entries) and text == self.itemText(index):
            return str(self.itemData(index))
        needle = text.casefold()
        for entry in self.entries:
            candidates = (entry.value, entry.label, entry.display_text, *entry.aliases)
            if any(needle == candidate.casefold() for candidate in candidates):
                return entry.value
        return text

    def _select_completion(self, text: str) -> None:
        for index, entry in enumerate(self.entries):
            if text == entry.display_text:
                self.setCurrentIndex(index)
                return
        self.setEditText(text)


class MainWindow(QMainWindow):
    def __init__(self, library_path: Path) -> None:
        super().__init__()
        self.library_path = library_path
        self.commands: list[Command] = []
        self.entity_catalogs: dict[str, tuple[CatalogEntry, ...]] = {}
        self.visible_commands: list[Command] = []
        self.current_command: Command | None = None
        self.parameter_inputs: dict[str, QWidget] = {}
        self.tag_labels: list[QLabel] = []
        self.setWindowTitle("Bannerlord Console Assistant")
        self.setMinimumSize(1000, 650)
        self.resize(1240, 760)
        self._build_ui()
        self.reload_library(initial=True)

    def _build_ui(self) -> None:
        root = QWidget(objectName="root")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = QFrame(objectName="sidebar")
        sidebar.setFixedWidth(210)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(20, 24, 20, 18)
        brand = QLabel("BANNERLORD")
        brand.setObjectName("brand")
        subtitle = QLabel("CONSOLE ASSISTANT")
        subtitle.setObjectName("eyebrow")
        side_layout.addWidget(brand)
        side_layout.addWidget(subtitle)
        side_layout.addSpacing(28)
        category_label = QLabel("命令分类")
        category_label.setObjectName("section")
        side_layout.addWidget(category_label)
        self.category_list = QListWidget()
        self.category_list.setSpacing(1)
        self.category_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.category_list.currentTextChanged.connect(self._on_category_changed)
        side_layout.addWidget(self.category_list)
        self.library_button = QPushButton("打开命令库")
        self.library_button.clicked.connect(self._open_library)
        reload_button = QPushButton("重新加载")
        reload_button.clicked.connect(self.reload_library)
        side_layout.addWidget(self.library_button)
        side_layout.addWidget(reload_button)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        list_panel = self._build_list_panel()
        detail_panel = self._build_detail_panel()
        splitter.addWidget(list_panel)
        splitter.addWidget(detail_panel)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)
        splitter.setSizes([410, 620])

        root_layout.addWidget(sidebar)
        root_layout.addWidget(splitter, 1)
        self.setCentralWidget(root)
        self.setStatusBar(QStatusBar())

    def _build_list_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(22, 24, 14, 18)
        title = QLabel("命令库")
        title.setObjectName("title")
        self.result_label = QLabel("查找并选择一条命令")
        self.result_label.setObjectName("muted")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索名称、功能或关键词…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._refresh_list)
        self.command_list = QListWidget()
        self.command_list.setSpacing(4)
        self.command_list.setWordWrap(True)
        self.command_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.command_list.currentRowChanged.connect(self._show_selected)
        layout.addWidget(title)
        layout.addWidget(self.result_label)
        layout.addSpacing(8)
        layout.addWidget(self.search_input)
        layout.addSpacing(8)
        layout.addWidget(self.command_list, 1)
        return panel

    def _build_detail_panel(self) -> QWidget:
        wrapper = QWidget()
        outer = QVBoxLayout(wrapper)
        outer.setContentsMargins(10, 24, 22, 18)
        panel = QFrame(objectName="panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(24, 22, 24, 22)

        self.category_badge = QLabel("选择命令")
        self.category_badge.setObjectName("eyebrow")
        self.name_label = QLabel("从中间的列表选择一条命令")
        self.name_label.setObjectName("title")
        self.name_label.setWordWrap(True)
        self.description_label = QLabel("参数输入完成后，命令会自动生成。")
        self.description_label.setObjectName("muted")
        self.description_label.setWordWrap(True)
        panel_layout.addWidget(self.category_badge)
        panel_layout.addWidget(self.name_label)
        panel_layout.addWidget(self.description_label)
        self.tag_widget = QWidget()
        self.tag_layout = QHBoxLayout(self.tag_widget)
        self.tag_layout.setContentsMargins(0, 5, 0, 2)
        self.tag_layout.setSpacing(8)
        self.tag_layout.addStretch(1)
        self.tag_widget.hide()
        panel_layout.addWidget(self.tag_widget)
        panel_layout.addSpacing(12)

        template_heading = QLabel("命令模板")
        template_heading.setObjectName("section")
        self.template_label = QLabel("—")
        self.template_label.setObjectName("template")
        self.template_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.template_label.setWordWrap(True)
        panel_layout.addWidget(template_heading)
        panel_layout.addWidget(self.template_label)
        panel_layout.addSpacing(14)

        parameter_heading = QLabel("参数")
        parameter_heading.setObjectName("section")
        panel_layout.addWidget(parameter_heading)
        self.form_widget = QWidget()
        self.form_layout = QFormLayout(self.form_widget)
        self.form_layout.setContentsMargins(0, 4, 0, 4)
        self.form_layout.setHorizontalSpacing(16)
        self.form_layout.setVerticalSpacing(11)
        panel_layout.addWidget(self.form_widget)
        panel_layout.addStretch(1)

        generated_heading = QLabel("生成命令")
        generated_heading.setObjectName("section")
        self.generated_input = QLineEdit()
        self.generated_input.setReadOnly(True)
        self.generated_input.setPlaceholderText("填写参数后自动生成")
        self.copy_button = QPushButton("复制命令")
        self.copy_button.setObjectName("primary")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self._copy_command)
        panel_layout.addWidget(generated_heading)
        panel_layout.addWidget(self.generated_input)
        panel_layout.addWidget(self.copy_button)
        outer.addWidget(panel)
        return wrapper

    def reload_library(self, checked: bool = False, initial: bool = False) -> None:
        del checked
        try:
            self.commands = load_commands(self.library_path)
            self.entity_catalogs = load_entity_catalogs()
        except CommandLibraryError as exc:
            QMessageBox.critical(self, "命令库错误", str(exc))
            return
        counts = Counter(command.category for command in self.commands)
        previous = self._selected_category()
        self.category_list.blockSignals(True)
        self.category_list.clear()
        self.category_list.addItem(f"全部  ·  {len(self.commands)}")
        ordered = list(CATEGORIES) + sorted(set(counts) - set(CATEGORIES))
        for category in ordered:
            if counts[category]:
                self.category_list.addItem(f"{category}  ·  {counts[category]}")
        target_row = 0
        for row in range(self.category_list.count()):
            if self.category_list.item(row).text().split("  ·  ")[0] == previous:
                target_row = row
                break
        self.category_list.setCurrentRow(target_row)
        self.category_list.blockSignals(False)
        self._refresh_list()
        message = f"已加载 {len(self.commands)} 条命令"
        self.statusBar().showMessage(message, 3500)
        if not initial:
            QMessageBox.information(self, "重新加载", message)

    def _selected_category(self) -> str:
        item = self.category_list.currentItem()
        return item.text().split("  ·  ")[0] if item else "全部"

    def _on_category_changed(self, _text: str) -> None:
        self._refresh_list()

    def _refresh_list(self) -> None:
        category = self._selected_category()
        self.visible_commands = filter_commands(self.commands, category, self.search_input.text())
        selected_name = self.current_command.name if self.current_command else ""
        self.command_list.blockSignals(True)
        self.command_list.clear()
        selected_row = -1
        for row, command in enumerate(self.visible_commands):
            item = QListWidgetItem(f"{command.name}\n{command.description}")
            item.setData(Qt.UserRole, row)
            item.setToolTip(command.command)
            self.command_list.addItem(item)
            if command.name == selected_name:
                selected_row = row
        self.command_list.blockSignals(False)
        self.result_label.setText(f"{category} · {len(self.visible_commands)} 条结果")
        if self.visible_commands:
            self.command_list.setCurrentRow(selected_row if selected_row >= 0 else 0)
        else:
            self._clear_detail("没有匹配的命令")

    def _show_selected(self, row: int) -> None:
        if row < 0 or row >= len(self.visible_commands):
            return
        command = self.visible_commands[row]
        self.current_command = command
        self.category_badge.setText(command.category.upper())
        self.name_label.setText(command.name)
        self.description_label.setText(command.description)
        self._show_tags(command)
        self.template_label.setText(command.command)
        self._clear_form()
        if command.parameters:
            for parameter in command.parameters:
                entries = self.entity_catalogs.get(parameter.catalog, ())
                if parameter.catalog and entries:
                    field: QWidget = CatalogComboBox(entries)
                    field.set_entry_value(parameter.default)  # type: ignore[attr-defined]
                    field.currentTextChanged.connect(self._update_generated)  # type: ignore[attr-defined]
                    field.lineEdit().textChanged.connect(self._update_generated)  # type: ignore[attr-defined]
                    field.setToolTip(
                        (parameter.description + "\n" if parameter.description else "")
                        + "可从下拉列表选择，或输入 ID、英文名、中文名的一部分进行匹配；生成命令使用英文原始值。"
                    )
                else:
                    field = QLineEdit(parameter.default)
                    field.setPlaceholderText(parameter.placeholder or parameter.description)
                    if parameter.type == "integer":
                        field.setInputMethodHints(Qt.ImhDigitsOnly)
                    field.textChanged.connect(self._update_generated)
                    if parameter.description:
                        field.setToolTip(parameter.description)
                label = parameter.label + (" *" if parameter.required else "")
                self.form_layout.addRow(label, field)
                self.parameter_inputs[parameter.key] = field
        else:
            no_parameters = QLabel("此命令不需要参数")
            no_parameters.setObjectName("muted")
            self.form_layout.addRow(no_parameters)
        self._update_generated()

    def _clear_form(self) -> None:
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)
        self.parameter_inputs.clear()

    def _show_tags(self, command: Command) -> None:
        self._clear_tags()
        tags = command_tags(command)
        for text, kind in tags:
            label = QLabel(text)
            label.setObjectName("tagRisk" if kind == "risk" else "tagInfo")
            label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
            self.tag_layout.insertWidget(self.tag_layout.count() - 1, label)
            self.tag_labels.append(label)
        self.tag_widget.setVisible(bool(tags))

    def _clear_tags(self) -> None:
        for label in self.tag_labels:
            self.tag_layout.removeWidget(label)
            label.deleteLater()
        self.tag_labels.clear()
        self.tag_widget.hide()

    def _clear_detail(self, title: str) -> None:
        self.current_command = None
        self.category_badge.setText("命令库")
        self.name_label.setText(title)
        self.description_label.setText("请调整分类或搜索关键词。")
        self._clear_tags()
        self.template_label.setText("—")
        self._clear_form()
        self.generated_input.clear()
        self.copy_button.setEnabled(False)

    def _update_generated(self) -> None:
        if not self.current_command:
            return
        values = {key: self._field_value(field) for key, field in self.parameter_inputs.items()}
        try:
            rendered = self.current_command.render(values)
        except ValueError as exc:
            self.generated_input.clear()
            self.generated_input.setPlaceholderText(str(exc))
            self.copy_button.setEnabled(False)
        else:
            self.generated_input.setText(rendered)
            self.copy_button.setEnabled(True)

    @staticmethod
    def _field_value(field: QWidget) -> str:
        if isinstance(field, CatalogComboBox):
            return field.raw_value()
        if isinstance(field, QLineEdit):
            return field.text()
        return ""

    def _copy_command(self) -> None:
        command = self.generated_input.text().strip()
        if not command:
            return
        QApplication.clipboard().setText(command)
        old_text = self.copy_button.text()
        self.copy_button.setText("已复制 ✓")
        self.statusBar().showMessage("命令已复制到剪贴板", 2500)
        QTimer.singleShot(1400, lambda: self.copy_button.setText(old_text))

    def _open_library(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.library_path)))


def _configure_palette(app: QApplication) -> None:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#111722"))
    palette.setColor(QPalette.WindowText, QColor("#e8edf5"))
    palette.setColor(QPalette.Base, QColor("#0f1723"))
    palette.setColor(QPalette.Text, QColor("#e8edf5"))
    palette.setColor(QPalette.Highlight, QColor("#2785d8"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)


def main() -> int:
    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setApplicationName("Bannerlord Console Assistant")
    app.setOrganizationName("Bannerlord Console Assistant")
    app.setStyle("Fusion")
    app.setFont(QFont("Microsoft YaHei UI", 10))
    app.setStyleSheet(STYLE)
    _configure_palette(app)
    try:
        library_path = ensure_user_library()
    except OSError as exc:
        QMessageBox.critical(None, "启动失败", f"无法初始化命令库：{exc}")
        return 1
    window = MainWindow(library_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
