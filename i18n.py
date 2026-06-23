"""Internationalization — translation strings and locale detection."""

from PyQt5.QtCore import QLocale

STRINGS = {
    "zh": {
        "title": "成绩录入工具",
        "open": "打开",
        "go": "前往",
        "run": "运行",
        "address": "搜索或输入网址",
        "current_file": "当前文件",
        "done": "完成",
        "score_script_done": "成绩录入脚本已执行。",
        "error": "错误",
        "config_no_url": "config.json 未包含 base_url",
        "select_columns": "选择数据列",
        "column_1": "第一列（平时成绩）",
        "column_2": "第二列（期末成绩）",
        "start_row": "起始行",
        "end_row": "结束行",
        "sheet": "工作表",
        "ok": "确定",
        "cancel": "取消",
        "file_type_error": "不支持的文件类型：{}",
        "read_file_error": "读取文件出错：{}",
        "file_not_found": "文件不存在：{}",
        "no_data": "所选范围内没有数据",
        "tooltip_run": "读取已选文件并将成绩填入网页",
        "tooltip_go": "跳转到指定地址",
        "tooltip_open": "选择成绩文件（txt / xls / xlsx）",
        "tooltip_address": "在此输入或修改网址，按回车前往",
        "alert_no_iframe": "未找到 iframe[name=\"zhuti\"]，请确认页面是否正确。",
        "alert_no_save_btn": "未找到保存按钮",
        "open_filter": "成绩文件 (*.txt *.xls *.xlsx);;所有文件 (*)",
        "missing_openpyxl": "缺少依赖 openpyxl，无法读取 .xlsx 文件。请执行：pip install openpyxl",
        "missing_xlrd": "缺少依赖 xlrd，无法读取 .xls 文件。请执行：pip install xlrd",
    },
    "en": {
        "title": "Score Entry Tool",
        "open": "Open",
        "go": "Go",
        "run": "Run",
        "address": "Search or enter a URL",
        "current_file": "Current File",
        "done": "Done",
        "score_script_done": "Score entry script executed.",
        "error": "Error",
        "config_no_url": "config.json does not contain base_url",
        "select_columns": "Select Data Columns",
        "column_1": "Column 1 (Regular Score)",
        "column_2": "Column 2 (Final Score)",
        "start_row": "Start Row",
        "end_row": "End Row",
        "sheet": "Sheet",
        "ok": "OK",
        "cancel": "Cancel",
        "file_type_error": "Unsupported file type: {}",
        "read_file_error": "Error reading file: {}",
        "file_not_found": "File not found: {}",
        "no_data": "No data in selected range",
        "tooltip_run": "Read the selected file and fill scores into the page",
        "tooltip_go": "Navigate to the specified address",
        "tooltip_open": "Choose a score file (txt / xls / xlsx)",
        "tooltip_address": "Type or edit a URL, press Enter to go",
        "alert_no_iframe": "iframe[name=\"zhuti\"] not found, please verify the page.",
        "alert_no_save_btn": "Save button not found",
        "open_filter": "Score Files (*.txt *.xls *.xlsx);;All Files (*)",
        "missing_openpyxl": "Missing dependency 'openpyxl' for .xlsx files. Run: pip install openpyxl",
        "missing_xlrd": "Missing dependency 'xlrd' for .xls files. Run: pip install xlrd",
    },
}


def detect_language() -> str:
    """Return 'en' or 'zh' based on the system locale."""
    name = QLocale.system().name().lower()
    if name.startswith("en"):
        return "en"
    if name.startswith("zh"):
        return "zh"
    return "zh"


class I18n:
    """Tiny translation helper with safe fallbacks."""

    def __init__(self, lang: str):
        self.lang = lang if lang in STRINGS else "zh"

    def t(self, key: str, *args) -> str:
        s = STRINGS[self.lang].get(key, STRINGS["zh"].get(key, key))
        if args:
            try:
                return s.format(*args)
            except Exception:
                return s
        return s
