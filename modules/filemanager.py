import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import xlwings as xw
from openpyxl import load_workbook

from modules.customexceptions import PathResolutionError


class FileManager:
    def __init__(self):
        self.app = None

    def create_xlwings_instance(self):
        try:
            self.app = xw.App(visible=False)
            return self.app
        except Exception:
            raise RuntimeError("    [!] Can't obtain xlwings object")

    def get_base_path(self):
        try:
            base_path = None
            if getattr(sys, "frozen", False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        except Exception as e:
            raise PathResolutionError(
                f"\n    [!] Error: Could not determine base path.\n    Details: {e}",
            ) from e
        return base_path

    def get_file_paths(self, base_path):
        try:
            base_path = Path(base_path)
            errors = []
            files = list(base_path.glob("*"))

            xlsm_files = [
                f for f in files if f.suffix == ".xlsm" and not f.name.startswith("~$")
            ]
            xlsx_files = [
                f for f in files if f.suffix == ".xlsx" and not f.name.startswith("~$")
            ]

            if len(xlsm_files) != 1:
                errors.append(f"Expected exactly 1 .xlsm file, found {len(xlsm_files)}")
            if len(xlsx_files) != 1:
                errors.append(f"Expected exactly 1 .xlsx file, found {len(xlsx_files)}")

            if errors:
                raise ValueError("\n    - " + "\n    - ".join(errors))

            journal_path = xlsm_files[0]
            data_path = xlsx_files[0]

        except Exception as e:
            raise ValueError(
                f"\n    [!] File loading failed.\n"
                f"    Please ensure your working folder contains exactly one .xlsm file and one .xlsx file.\n"
                f"    Details: {e}\n",
            )
        return journal_path, data_path

    def check_files_are_closed(self, paths):
        for path in paths:
            try:
                with open(path, "r+"):
                    pass
            except PermissionError:
                raise ValueError(
                    f"\n    [!] Error: The file '{os.path.basename(path)}' is currently open.\n"
                    f"    Please close the file and try Journal Wings again.\n",
                )
        return True

    def open_with_openpyxl(self, data_path):
        try:
            data_workbook = load_workbook(data_path, data_only=True)
        except FileNotFoundError:
            raise ValueError(
                    "\n    [!] Error: Could not load workbook\n"
                    "    \n",
                )
        except PermissionError:
            raise ValueError(
                "\n    [!] Error: File is currently open or locked — please close it.\n",
            )
        return data_workbook

    def open_journal_with_xlwings(self, paths, app):
        # print("hello from open journal with xl wings")
        # print(paths[0])
        try:
            journal_object = app.books.open(paths[0])
            # webadi = journal_object.sheets['WebADI']
            return journal_object
        except Exception as e:
            raise RuntimeError(f"\n    [!] Error: Failed to open journal with xlwings: {e}\n")

    def file_rename(self, file, ctx):
        try:
            uploader_ref = ctx.dm.uploader_ref
            # print(uploader_ref)
            timestamp = datetime.today().strftime("%d%m%Y_%H%M%S")
            directory = os.path.dirname(file)
            _, ext = os.path.splitext(file)
            new_name=f"{uploader_ref}_{timestamp}{ext}"
            new_path = os.path.join(directory, new_name)
            shutil.copyfile(file, new_path)
            # print(timestamp, directory)
            # print(f"[✓] Copied file to: {new_path}")
        except Exception as e:
            print(f"[!] Error during file copy: {e}")



    def close_journal_xlwings(self, journal):
        try:
            if journal is not None:
                journal.close()
        except Exception as e:
            raise RuntimeError(f"    [!] Failed to close workbook: {e}")

