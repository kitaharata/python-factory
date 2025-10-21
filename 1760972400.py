import csv
import os
import winreg


def get_default_apps_by_file_type():
    """Outputs default application mappings by file type to a CSV file on the desktop."""
    output_path = "DefaultAppsByFileType.csv"

    HKEY = winreg.HKEY_CURRENT_USER
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts"

    results = []

    try:
        with winreg.OpenKey(HKEY, REG_PATH) as hkey:
            num_subkeys, _, _ = winreg.QueryInfoKey(hkey)
            for i in range(num_subkeys):
                ext = winreg.EnumKey(hkey, i)
                prog_id = ""
                user_choice_path = os.path.join(REG_PATH, ext, "UserChoice")
                try:
                    with winreg.OpenKey(HKEY, user_choice_path) as hkey_choice:
                        try:
                            value, type_id = winreg.QueryValueEx(hkey_choice, "ProgId")
                            if type_id == winreg.REG_SZ:
                                prog_id = value
                        except (FileNotFoundError, OSError):
                            pass
                except FileNotFoundError:
                    pass
                results.append({"Extension": ext, "ProgId": prog_id})
    except Exception as e:
        print(f"Error accessing registry: {e}")
        return

    if results:
        fieldnames = ["Extension", "ProgId"]
        try:
            with open(output_path, "w", encoding="utf-8", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                writer.writerows(results)
            print(f"Successfully exported default application mappings to {output_path}")
        except Exception as e:
            print(f"Error writing CSV file: {e}")


if __name__ == "__main__":
    get_default_apps_by_file_type()
