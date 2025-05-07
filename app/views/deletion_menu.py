import sys
from errno import ENOTEMPTY
from shutil import rmtree
from typing import Any, Callable

from loguru import logger
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from app.utils.generic import (
    attempt_chmod,
    delete_files_except_extension,
    delete_files_only_extension,
)
from app.utils.metadata import MetadataManager, ModMetadata
from app.views.dialogue import (
    show_dialogue_conditional,
    show_information,
    show_warning,
)


class ModDeletionMenu(QMenu):
    def __init__(
        self,
        get_selected_mod_metadata: Callable[[], list[ModMetadata]],
        remove_from_uuids: list[str] | None,
        menu_title: str = "删除选项",
        delete_mod: bool = True,
        delete_both: bool = True,
        delete_dds: bool = True,
    ):
        super().__init__(title=menu_title)
        self.remove_from_uuids = remove_from_uuids
        self.get_selected_mod_metadata = get_selected_mod_metadata
        self.metadata_manager = MetadataManager.instance()
        self.delete_actions: list[tuple[QAction, Callable[[], None]]] = []
        if delete_mod:
            self.delete_actions.append((QAction("删除模组"), self.delete_both))

        if delete_both:
            self.delete_actions.append(
                (QAction("删除模组（保留 .dds 文件）"), self.delete_mod_keep_dds)
            )
        if delete_dds:
            self.delete_actions.append(
                (
                    QAction("删除优化后的纹理（仅 .dds 文件）"),
                    self.delete_dds,
                )
            )

        self.aboutToShow.connect(self._refresh_actions)
        self._refresh_actions()

    def _refresh_actions(self) -> None:
        self.clear()
        for q_action, fn in self.delete_actions:
            q_action.triggered.connect(fn)
            self.addAction(q_action)

    def _iterate_mods(
        self, fn: Callable[[ModMetadata], bool], mods: list[ModMetadata]
    ) -> None:
        steamcmd_acf_pfid_purge: set[str] = set()

        count = 0
        for mod_metadata in mods:
            if mod_metadata[
                "data_source"  # Disallow Official Expansions
            ] != "expansion" or not mod_metadata["packageid"].startswith(
                "ludeon.rimworld"
            ):
                if fn(mod_metadata):
                    count = count + 1
                    if (
                        self.remove_from_uuids is not None
                        and "uuid" in mod_metadata
                        and mod_metadata["uuid"] in self.remove_from_uuids
                    ):
                        self.remove_from_uuids.remove(mod_metadata["uuid"])

                    if mod_metadata.get("steamcmd"):
                        steamcmd_acf_pfid_purge.add(mod_metadata["publishedfileid"])

        # Purge any deleted SteamCMD mods from acf metadata
        if steamcmd_acf_pfid_purge:
            self.metadata_manager.steamcmd_purge_mods(
                publishedfileids=steamcmd_acf_pfid_purge
            )

        show_information(
            title="RimSort", text=f"成功删除{count}个选择的模组。"
        )

    def delete_both(self) -> None:
        def _inner_delete_both(mod_metadata: dict[str, Any]) -> bool:
            try:
                rmtree(
                    mod_metadata["path"],
                    ignore_errors=False,
                    onexc=attempt_chmod,
                )
                return True
            except FileNotFoundError:
                logger.debug(
                    f"Unable to delete mod. Path does not exist: {mod_metadata['path']}"
                )
                return False
            except OSError as e:
                if sys.platform == "win32":
                    error_code = e.winerror
                else:
                    error_code = e.errno
                if e.errno == ENOTEMPTY:
                    warning_text = "模组目录非空。请关闭所有正在访问该目录内文件或子文件夹的程序（包括文件管理器），然后重试。"
                else:
                    warning_text = "删除模组时发生系统错误。"

                logger.warning(
                    f"Unable to delete mod located at the path: {mod_metadata['path']}"
                )
                show_warning(
                    title="无法删除模组",
                    text=warning_text,
                    information=f"{e.strerror} 发生于 {e.filename} 路径，错误代码：{error_code}。",
                )
            return False

        uuids = self.get_selected_mod_metadata()
        answer = show_dialogue_conditional(
            title="确认操作",
            text=f"您已选择删除{len(uuids)}个模组",
            information="此操作将从文件系统中删除模组的整个目录"
                        "<br>确定要继续吗？"
        )
        if answer == "&Yes":
            self._iterate_mods(_inner_delete_both, uuids)

    def delete_dds(self) -> None:
        mod_metadata = self.get_selected_mod_metadata()
        answer = show_dialogue_conditional(
            title="确认操作",
            text=f"您已选择{len(mod_metadata)}个模组 仅删除优化后的纹理（.dds文件）",
            information="此操作仅会删除模组文件中的优化纹理（仅.dds文件）"
                        "<br>确定要继续吗？"
        )
        if answer == "&Yes":
            self._iterate_mods(
                lambda mod_metadata: (
                    delete_files_only_extension(
                        directory=str(mod_metadata["path"]),
                        extension=".dds",
                    )
                ),
                mod_metadata,
            )

    def delete_mod_keep_dds(self) -> None:
        mod_metadata = self.get_selected_mod_metadata()
        answer = show_dialogue_conditional(
            title="确认操作",
            text=f"您已选择删除{len(mod_metadata)}个模组 但保留优化后的纹理（.dds文件）",
            information="此操作将彻底删除模组文件"
                        "<br>但会保留其中的.dds纹理文件"
                        "<br>确定要继续吗？"
        )
        if answer == "&Yes":
            self._iterate_mods(
                lambda mod_metadata: delete_files_except_extension(
                    directory=mod_metadata["path"],
                    extension=".dds",
                ),
                mod_metadata,
            )
