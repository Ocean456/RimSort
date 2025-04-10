from PySide6.QtCore import Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class TroubleshootingDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle("疑难解答")
        self.resize(800, 600)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # game files recovery section
        group_box = QGroupBox("游戏文件恢复")
        main_layout.addWidget(group_box)
        group_layout = QVBoxLayout()
        group_box.setLayout(group_layout)
        group_layout.setSpacing(10)

        # warning label with icon
        warning_layout = QHBoxLayout()
        warning_icon = QLabel("⚠️")
        warning_icon.setStyleSheet("color: #FF4444; font-size: 16px;")
        warning_layout.addWidget(warning_icon)

        warning_label = QLabel(
            "警告：这些操作将永久删除选定的文件！"
        )
        warning_label.setStyleSheet("color: #FF4444; font-weight: bold;")
        warning_layout.addWidget(warning_label)
        warning_layout.addStretch()
        group_layout.addLayout(warning_layout)

        # info label
        info_label = QLabel(
            "如果您在游戏中遇到问题，可以尝试以下恢复选项。\n"
            "Steam将在下次启动时自动重新下载已删除的文件。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666666;")
        group_layout.addWidget(info_label)

        # checkboxes for integrity options
        self.integrity_delete_game_files = QCheckBox(
            "重置游戏文件（保留本地模组，删除并重新下载游戏文件）"
        )
        self.integrity_delete_game_files.setStyleSheet("padding: 5px;")
        group_layout.addWidget(self.integrity_delete_game_files)

        self.integrity_delete_steam_mods = QCheckBox(
            "重置Steam创意工坊模组（删除并重新下载所有Steam模组）"
        )
        self.integrity_delete_steam_mods.setStyleSheet("padding: 5px;")
        group_layout.addWidget(self.integrity_delete_steam_mods)

        self.integrity_delete_mod_configs = QCheckBox(
            "重置模组配置（保留ModsConfig.xml和Prefs.xml）"
        )
        self.integrity_delete_mod_configs.setStyleSheet("padding: 5px;")
        group_layout.addWidget(self.integrity_delete_mod_configs)

        self.integrity_delete_game_configs = QCheckBox(
            "重置游戏配置（ModsConfig.xml, Prefs.xml, KeyPrefs.xml）*"
        )
        self.integrity_delete_game_configs.setStyleSheet("padding: 5px;")
        group_layout.addWidget(self.integrity_delete_game_configs)

        # note about ModsConfig.xml
        note_label = QLabel(
            "*注意：重置游戏配置后，请直接通过Steam启动游戏\n"
            "以重新生成ModsConfig.xml，然后重新启动RimSort。"
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: #666666; font-style: italic; padding: 5px;")
        group_layout.addWidget(note_label)

        # buttons layout
        button_layout: QHBoxLayout = QHBoxLayout()
        group_layout.addLayout(button_layout)

        button_layout.addStretch()
        self.integrity_apply_button = QPushButton("应用恢复")
        self.integrity_apply_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        self.integrity_cancel_button = QPushButton("取消")
        self.integrity_cancel_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                border-radius: 3px;
            }
        """)
        button_layout.addWidget(self.integrity_cancel_button)
        button_layout.addWidget(self.integrity_apply_button)

        # mod configuration options section
        mod_config_group = QGroupBox("模组配置选项")
        main_layout.addWidget(mod_config_group)
        mod_config_layout = QVBoxLayout()
        mod_config_group.setLayout(mod_config_layout)
        mod_config_layout.setSpacing(10)

        # info label for mod configuration
        mod_config_info = QLabel(
            "管理您的模组配置和加载顺序。这些选项可帮助您组织和分享模组设置。"
        )
        mod_config_info.setWordWrap(True)
        mod_config_info.setStyleSheet("color: #666666;")
        mod_config_layout.addWidget(mod_config_info)

        # mod list import/export section
        mod_list_layout = QHBoxLayout()
        mod_config_layout.addLayout(mod_list_layout)

        mod_list_buttons_layout = QVBoxLayout()
        mod_list_layout.addLayout(mod_list_buttons_layout)

        self.mod_export_list_button = QPushButton("导出模组列表")
        self.mod_export_list_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 3px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        mod_list_buttons_layout.addWidget(self.mod_export_list_button)

        self.mod_import_list_button = QPushButton("导入模组列表")
        self.mod_import_list_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 3px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        mod_list_buttons_layout.addWidget(self.mod_import_list_button)

        mod_list_desc = QLabel(
            "将当前模组列表保存为.rml文件以与他人共享，\n"
            "或导入其他玩家的.rml格式模组列表"
        )
        mod_list_desc.setStyleSheet("color: #666666; padding-left: 10px;")
        mod_list_layout.addWidget(mod_list_desc)
        mod_list_layout.addStretch()

        # Clear mods section (in red)
        clear_mods_layout = QHBoxLayout()
        mod_config_layout.addLayout(clear_mods_layout)

        self.clear_mods_button = QPushButton("清除模组")
        self.clear_mods_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 3px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_mods_layout.addWidget(self.clear_mods_button)

        clear_mods_desc = QLabel(
            "⚠️ 警告：此操作将删除您的Mods文件夹中的所有Mod，并重置为原版状态"
        )
        clear_mods_desc.setStyleSheet(
            "color: #e74c3c; padding-left: 10px; font-weight: bold;"
        )
        clear_mods_layout.addWidget(clear_mods_desc)
        clear_mods_layout.addStretch()

        # steam tools section
        steam_group = QGroupBox("Steam 工具")
        main_layout.addWidget(steam_group)
        steam_layout = QVBoxLayout()
        steam_group.setLayout(steam_layout)
        steam_layout.setSpacing(10)

        # Initialize steam buttons
        self.steam_clear_cache_button = QPushButton("🔄 清除下载缓存")
        self.steam_verify_game_button = QPushButton("✓ 验证游戏文件")
        self.steam_repair_library_button = QPushButton("🔧 修复Steam库")

        # steam buttons with icons and descriptions
        steam_buttons = [
            (
                self.steam_clear_cache_button,
                "删除 Steam 下载缓存文件夹以解决下载问题",
            ),
            (
                self.steam_verify_game_button,
                "检查并修复 RimWorld 游戏文件",
            ),
            (
                self.steam_repair_library_button,
                "验证所有已安装 Steam 游戏的完整性",
            ),
        ]

        button_style = """
            QPushButton {
                text-align: left;
                padding: 8px;
                border-radius: 3px;
                background-color: #4a90e2;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """

        for button, description in steam_buttons:
            button_container = QVBoxLayout()
            button.setStyleSheet(button_style)
            desc_label = QLabel(description)
            desc_label.setStyleSheet(
                "color: #666666; font-size: 11px; padding: 5px 8px;"
            )
            button_container.addWidget(button)
            button_container.addWidget(desc_label)
            steam_layout.addLayout(button_container)

        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)
        button_layout.addStretch()

        self.close_button = QPushButton("关闭")
        self.close_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border-radius: 3px;
            }
        """)
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.close_button.setFocus()
