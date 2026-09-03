"""Data loading and command rendering without GUI dependencies."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PLACEHOLDER_PATTERN = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


class CommandLibraryError(ValueError):
    """Raised when the command data file is invalid."""


@dataclass(frozen=True)
class Parameter:
    key: str
    label: str
    default: str = ""
    placeholder: str = ""
    description: str = ""
    required: bool = True
    type: str = "text"
    catalog: str = ""


@dataclass(frozen=True)
class CatalogEntry:
    """A finite game target with a display label and command-safe value."""

    value: str
    label: str
    aliases: tuple[str, ...] = field(default_factory=tuple)

    @property
    def display_text(self) -> str:
        if self.label and self.label != self.value:
            return f"{self.value}（{self.label}）"
        return self.value

    @property
    def searchable_text(self) -> str:
        return " ".join((self.value, self.label, *self.aliases)).casefold()


@dataclass(frozen=True)
class Command:
    name: str
    description: str
    command: str
    parameters: tuple[Parameter, ...]
    category: str
    keywords: tuple[str, ...] = field(default_factory=tuple)
    note: str = ""

    def render(self, values: dict[str, str]) -> str:
        rendered = self.command
        missing: list[str] = []
        for parameter in self.parameters:
            value = str(values.get(parameter.key, parameter.default)).strip()
            if parameter.required and not value:
                missing.append(parameter.label)
            token = "{" + parameter.key + "}"
            if not value and not parameter.required:
                # Remove an empty optional argument together with one adjacent
                # pipe separator. This supports optional first, middle, and
                # trailing arguments without producing dangling separators.
                if token + " | " in rendered:
                    rendered = rendered.replace(token + " | ", "", 1)
                elif " | " + token in rendered:
                    rendered = rendered.replace(" | " + token, "", 1)
                else:
                    rendered = rendered.replace(token, "", 1)
            else:
                rendered = rendered.replace(token, value)
        if missing:
            raise ValueError("请填写：" + "、".join(missing))
        return rendered.strip().rstrip("|").rstrip()

    @property
    def searchable_text(self) -> str:
        return " ".join(
            (self.name, self.description, self.category, self.command, *self.keywords)
        ).casefold()


def _parameter_from_raw(raw: Any) -> Parameter:
    if isinstance(raw, str):
        return Parameter(key=raw, label=raw, placeholder=f"请输入 {raw}")
    if not isinstance(raw, dict) or not raw.get("key"):
        raise CommandLibraryError("参数必须是字符串或包含 key 的对象")
    return Parameter(
        key=str(raw["key"]),
        label=str(raw.get("label", raw["key"])),
        default=str(raw.get("default", "")),
        placeholder=str(raw.get("placeholder", "")),
        description=str(raw.get("description", "")),
        required=bool(raw.get("required", True)),
        type=str(raw.get("type", "text")),
        catalog=str(raw.get("catalog", "")),
    )


def load_commands(path: Path) -> list[Command]:
    try:
        raw_data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CommandLibraryError(f"无法读取命令库：{exc}") from exc

    items = raw_data.get("commands") if isinstance(raw_data, dict) else raw_data
    if not isinstance(items, list):
        raise CommandLibraryError("commands.json 顶层必须是数组，或包含 commands 数组")

    commands: list[Command] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise CommandLibraryError(f"第 {index} 条命令不是对象")
        required = ("name", "description", "command", "category")
        absent = [key for key in required if not str(item.get(key, "")).strip()]
        if absent:
            raise CommandLibraryError(f"第 {index} 条命令缺少字段：{', '.join(absent)}")
        parameters = tuple(_parameter_from_raw(p) for p in item.get("parameters", []))
        declared = {parameter.key for parameter in parameters}
        placeholders = set(PLACEHOLDER_PATTERN.findall(str(item["command"])))
        if placeholders != declared:
            raise CommandLibraryError(
                f"第 {index} 条命令的参数与模板不一致：模板 {sorted(placeholders)}，参数 {sorted(declared)}"
            )
        keywords = item.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [keywords]
        commands.append(
            Command(
                name=str(item["name"]),
                description=str(item["description"]),
                command=str(item["command"]),
                parameters=parameters,
                category=str(item["category"]),
                keywords=tuple(str(k) for k in keywords),
                note=str(item.get("note", "")),
            )
        )
    return commands


def packaged_data_path() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "bannerlord_assistant" / "data" / "commands.json"
    return Path(__file__).resolve().parent / "data" / "commands.json"


def packaged_entity_catalog_path() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "bannerlord_assistant" / "data" / "entities.json"
    return Path(__file__).resolve().parent / "data" / "entities.json"


def load_entity_catalogs(path: Path | None = None) -> dict[str, tuple[CatalogEntry, ...]]:
    """Load versioned finite target catalogs used by the GUI completers."""
    catalog_path = path or packaged_entity_catalog_path()
    try:
        raw_data = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CommandLibraryError(f"无法读取目标目录：{exc}") from exc

    if not isinstance(raw_data, dict) or not isinstance(raw_data.get("catalogs"), dict):
        raise CommandLibraryError("entities.json 必须包含 catalogs 对象")

    catalogs: dict[str, tuple[CatalogEntry, ...]] = {}
    for catalog_name, raw_entries in raw_data["catalogs"].items():
        if not isinstance(catalog_name, str) or not catalog_name.strip():
            raise CommandLibraryError("目标目录名称不能为空")
        if not isinstance(raw_entries, list):
            raise CommandLibraryError(f"目标目录 {catalog_name} 必须是数组")
        entries: list[CatalogEntry] = []
        for index, raw_entry in enumerate(raw_entries, start=1):
            if not isinstance(raw_entry, dict) or not str(raw_entry.get("value", "")).strip():
                raise CommandLibraryError(f"目标目录 {catalog_name} 第 {index} 项缺少 value")
            aliases = raw_entry.get("aliases", [])
            if isinstance(aliases, str):
                aliases = [aliases]
            if not isinstance(aliases, list):
                raise CommandLibraryError(f"目标目录 {catalog_name} 第 {index} 项 aliases 必须是数组")
            entries.append(
                CatalogEntry(
                    value=str(raw_entry["value"]),
                    label=str(raw_entry.get("label", raw_entry["value"])),
                    aliases=tuple(str(alias) for alias in aliases if str(alias).strip()),
                )
            )
        catalogs[catalog_name] = tuple(entries)
    return catalogs


def filter_catalog(entries: tuple[CatalogEntry, ...] | list[CatalogEntry], query: str) -> list[CatalogEntry]:
    """Find catalog entries by substring in ID, English name, Chinese label, or alias."""
    needle = query.strip().casefold()
    return [entry for entry in entries if not needle or needle in entry.searchable_text]


def user_data_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
    return base / "Bannerlord Console Assistant" / "commands.json"


def ensure_user_library() -> Path:
    destination = user_data_path()
    source = packaged_data_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        shutil.copyfile(source, destination)
        return destination

    # Upgrade a previously initialized default library while preserving a backup.
    # Equal versions are never overwritten, so users can freely edit commands.json.
    try:
        source_meta = json.loads(source.read_text(encoding="utf-8-sig"))
        destination_meta = json.loads(destination.read_text(encoding="utf-8-sig"))
        source_version = source_meta.get("library_version") if isinstance(source_meta, dict) else None
        destination_version = destination_meta.get("library_version") if isinstance(destination_meta, dict) else None
    except (OSError, json.JSONDecodeError):
        return destination
    if source_version and source_version != destination_version:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = destination.with_name(f"commands.backup-{stamp}.json")
        shutil.copyfile(destination, backup)
        shutil.copyfile(source, destination)
    return destination


def filter_commands(commands: list[Command], category: str, query: str) -> list[Command]:
    needle = query.strip().casefold()
    return [
        command
        for command in commands
        if (category == "全部" or command.category == category)
        and (not needle or needle in command.searchable_text)
    ]
