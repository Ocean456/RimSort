import os
import time
from loguru import logger
from app.windows.runner_panel import RunnerPanel
from app.controllers.settings_controller import SettingsController


class RimTransInterface:
    def __init__(self):
        self.trans_exe_path = os.path.abspath(r"rimtrans\Trans.exe")

        self.core_path = ""
        self.dll_path = ""

    def execute_trans_cmd(self, mod_metadata: dict, runner: RunnerPanel, game_folder: str):
        self.core_path = os.path.join(game_folder, "Data", "Core")
        self.dll_path = os.path.join(game_folder, "RimWorldWin64_Data", "Managed", "Assembly-CSharp.dll")

        mod_path = mod_metadata["path"]
        mod_name = mod_metadata.get("name", mod_metadata["packageid"])
        temp_xml_path = os.path.join(os.path.dirname(self.trans_exe_path), "translation_project.rtp.xml")

        xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<RimTransProject>
  <ModPath>{mod_path}</ModPath>
  <GenerateOption>Standard</GenerateOption>
  <Languages>
    <Language>
      <RealName>ChineseSimplified</RealName>
      <NativeName>简体中文</NativeName>
      <IsChecked>true</IsChecked>
      <IsCustom>false</IsCustom>
      <CustomPath></CustomPath>
    </Language>
  </Languages>
</RimTransProject>"""

        try:
            with open(temp_xml_path, "w", encoding="utf-8") as f:
                f.write(xml_content)

            for _ in range(20):
                if os.path.exists(temp_xml_path) and os.path.getsize(temp_xml_path) > 0:
                    break
                time.sleep(0.1)
            else:
                runner.message("Failed to write XML file: Not generated within the specified time.")
                return
            
            args = [
                f'-p:{temp_xml_path}',
                f'-Dll:{self.dll_path}',
                f'-Core:{self.core_path}',
            ]

            if not os.path.exists(temp_xml_path):
                runner.message(f"XML file not generated: {temp_xml_path}")
                return

            if os.path.exists(self.trans_exe_path):
                runner.message(f"Starting translation extraction: {mod_name}")
                runner.execute(self.trans_exe_path, args, -1)
            else:
                runner.message("Trans.exe not found, please confirm the path is correct.")

        except Exception as e:
            logger.error(f"Failed to extract translation: {e}")
            runner.message(f"Error: {str(e)}")
