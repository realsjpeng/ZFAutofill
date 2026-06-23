"""Core score entry — injects scores into the page via JavaScript.

This module contains the ORIGINAL ``run_input_scores`` function, preserved
character-for-character.  Do not modify.
"""

from PyQt5.QtWidgets import QMessageBox


def run_input_scores(view, ps_lines, qm_lines):
    js_code = f"""
    (function() {{
        window.alert = function(msg) {{ console.log("Alert dismissed: " + msg); }};
        var iframe = document.querySelector('iframe[name="zhuti"]');
        if (!iframe) {{
            alert("未找到 iframe[name='zhuti']，请确认页面是否正确。");
            return;
        }}
        var iw = iframe.contentWindow;
        if (typeof iw.AjaxForm === 'undefined') {{
            iw.AjaxForm = function(){{}};
        }}
        var doc = iw.document;
        var rad = doc.querySelector('#rad_4');
        if (rad) {{ rad.checked = true; rad.dispatchEvent(new Event('change')); }}
        var ps = {ps_lines};
        var qm = {qm_lines};
        for (var i=0; i<ps.length; i++) {{
            var pin = doc.querySelector(`input[name="DataGrid1:_ctl${{i+2}}:ps"]`);
            var qin = doc.querySelector(`input[name="DataGrid1:_ctl${{i+2}}:qm"]`);
            if (pin) {{ pin.value = ps[i]; pin.dispatchEvent(new Event('change')); }}
            if (qin) {{ qin.value = qm[i]; qin.dispatchEvent(new Event('change')); }}
        }}
        var btn = doc.querySelector('button[name="保 存"], [role="button"]');
        if (btn) btn.click();
        else alert("未找到保存按钮");
    }})();
    """
    view.page().runJavaScript(js_code)
    QMessageBox.information(None, "完成", "成绩录入脚本已执行。")
