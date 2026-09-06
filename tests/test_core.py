import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bannerlord_assistant.core import (
    CommandLibraryError,
    ensure_user_library,
    filter_catalog,
    filter_commands,
    load_commands,
    load_entity_catalogs,
    packaged_data_path,
    packaged_entity_catalog_path,
)


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.commands = load_commands(packaged_data_path())

    def test_default_library_loads(self):
        self.assertEqual(len(self.commands), 166)
        self.assertIn("经济", {command.category for command in self.commands})
        names = {command.command.split()[0] for command in self.commands}
        self.assertIn("campaign.add_gold_to_hero", names)
        self.assertIn("campaign.heal_player_party", names)
        self.assertNotIn("campaign.add_denars", names)
        self.assertNotIn("campaign.add_companions", names)

    def test_render_command(self):
        gold = next(command for command in self.commands if command.name == "增加金币")
        self.assertEqual(gold.render({"amount": "100000"}), "campaign.add_gold_to_hero 100000")

    def test_multi_argument_commands_use_pipe_separator(self):
        troops = next(command for command in self.commands if command.command.startswith("campaign.add_troops "))
        self.assertEqual(
            troops.render({"troop_id": "imperial_legionary", "amount": "50", "party_name": ""}),
            "campaign.add_troops imperial_legionary | 50",
        )

    def test_versioned_entity_catalogs_load_and_match_bilingual_targets(self):
        catalogs = load_entity_catalogs(packaged_entity_catalog_path())
        self.assertGreaterEqual(len(catalogs["heroes"]), 400)
        self.assertGreaterEqual(len(catalogs["troops"]), 200)
        self.assertGreaterEqual(len(catalogs["items"]), 900)
        self.assertGreaterEqual(len(catalogs["settlement_ids"]), 500)

        troop = next(entry for entry in catalogs["troops"] if entry.value == "imperial_legionary")
        self.assertIn("帝国", troop.label)
        self.assertEqual(troop.display_text, f"imperial_legionary（{troop.label}）")
        self.assertEqual(troop.metadata["tier"], "T5")
        self.assertEqual(troop.metadata["level"], 26)
        self.assertEqual(troop.metadata["tier_source"], "模块 level")
        self.assertEqual(troop.metadata["culture"], "帝国")
        self.assertIn("T5", troop.selector_text)
        self.assertIn(troop, filter_catalog(catalogs["troops"], "legionary"))
        self.assertIn(troop, filter_catalog(catalogs["troops"], "帝国"))

        expected_t6 = {
            "aserai_vanguard_faris",
            "battanian_fian_champion",
            "druzhinnik_champion",
            "imperial_elite_cataphract",
            "khuzait_khans_guard",
            "nord_huscarl",
            "vlandian_banner_knight",
        }
        actual_t6 = {
            entry.value for entry in catalogs["troops"]
            if entry.metadata["tier"] == "T6"
        }
        self.assertEqual(actual_t6, expected_t6)
        for entry in catalogs["troops"]:
            self.assertEqual(entry.metadata["tier_source"], "模块 level")
            expected_tier = max(0, min(6, (entry.metadata["level"] - 1) // 5))
            self.assertEqual(entry.metadata["tier"], f"T{expected_tier}")

        grain = next(entry for entry in catalogs["items"] if entry.value == "grain")
        self.assertEqual(grain.label, "谷物")
        self.assertEqual(grain.metadata["category"], "商品")
        self.assertEqual(grain.metadata["tier"], "不适用")
        settlement = next(entry for entry in catalogs["settlements"] if entry.value == "Ain Baliq Castle")
        self.assertEqual(settlement.metadata["settlement_type"], "城堡")
        self.assertEqual(settlement.metadata["faction"], "阿塞莱")
        self.assertEqual(next(entry for entry in catalogs["modifiers"] if entry.value == "balanced").label, "均衡")

    def test_object_parameters_reference_catalogs(self):
        troops = next(command for command in self.commands if command.name == "添加士兵")
        self.assertEqual(troops.parameters[0].catalog, "troops")
        relation = next(command for command in self.commands if command.name == "修改英雄关系")
        self.assertEqual(relation.parameters[0].catalog, "heroes")
        self.assertEqual(relation.parameters[1].catalog, "heroes")
        numeric = next(command for command in self.commands if command.name == "增加金币")
        self.assertEqual(numeric.parameters[0].catalog, "")

    def test_empty_optional_middle_parameter_removes_one_separator(self):
        item = next(command for command in self.commands if command.name == "添加物品到玩家部队")
        self.assertEqual(
            item.render({"item_id": "grain", "modifier_id": "", "amount": "5"}),
            "campaign.add_item_to_player_party grain | 5",
        )

    def test_required_parameter(self):
        settlement = next(command for command in self.commands if command.name == "将领地授予玩家")
        with self.assertRaisesRegex(ValueError, "领地"):
            settlement.render({"settlement_name": ""})

    def test_searches_name_description_and_keywords(self):
        self.assertGreaterEqual(len(filter_commands(self.commands, "全部", "金币")), 1)
        self.assertTrue(any(c.name == "添加士兵" for c in filter_commands(self.commands, "军队", "troop")))
        self.assertEqual(filter_commands(self.commands, "经济", "伙伴"), [])

    def test_all_display_names_are_chinese(self):
        untranslated = [command.name for command in self.commands if not re.search(r"[\u4e00-\u9fff]", command.name)]
        self.assertEqual(untranslated, [])

    def test_internal_scan_messages_are_not_shown(self):
        banned = ("已从本机", "本机程序集", "确认注册", "DLL 帮助", "Format is", "Usage:")
        visible_text = "\n".join(
            f"{command.name}\n{command.description}\n{command.note}" for command in self.commands
        )
        for phrase in banned:
            self.assertNotIn(phrase, visible_text)

    def test_simple_parameter_format_is_supported(self):
        payload = [{
            "name": "测试", "description": "测试说明", "command": "do {amount}",
            "parameters": ["amount"], "category": "其他"
        }]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "commands.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            command = load_commands(path)[0]
        self.assertEqual(command.render({"amount": "3"}), "do 3")

    def test_rejects_mismatched_parameters(self):
        payload = [{
            "name": "错误", "description": "错误", "command": "do {amount}",
            "parameters": [], "category": "其他"
        }]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "commands.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(CommandLibraryError):
                load_commands(path)

    def test_old_user_library_is_backed_up_and_upgraded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "packaged.json"
            source.write_text(json.dumps({"library_version": "new", "commands": []}), encoding="utf-8")
            destination = root / "Bannerlord Console Assistant" / "commands.json"
            destination.parent.mkdir(parents=True)
            destination.write_text(json.dumps({"commands": [{"old": True}]}), encoding="utf-8")
            with patch.dict(os.environ, {"LOCALAPPDATA": str(root)}), patch(
                "bannerlord_assistant.core.packaged_data_path", return_value=source
            ):
                self.assertEqual(ensure_user_library(), destination)
            upgraded = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(upgraded["library_version"], "new")
            self.assertEqual(len(list(destination.parent.glob("commands.backup-*.json"))), 1)


if __name__ == "__main__":
    unittest.main()
