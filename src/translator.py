# -*- coding: utf-8 -*-
"""离线机器翻译 (Argos Translate) 封装。

用于把英文词句翻译成中文释义, 完全离线运行。
安装依赖与英→中语言包(一次性):

    pip install argostranslate
    python -c "import argostranslate.package as p; p.update_package_index(); \
pkgs=[x for x in p.get_available_packages() if x.from_code=='en' and x.to_code=='zh']; \
p.install_from_path(pkgs[0].download())"

"""

import re

_translator = None
_state = None  # None | "ready" | "error"
_message = ""

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def _ensure():
    global _translator, _state, _message
    if _state is not None:
        return

    try:
        import argostranslate.translate as at
    except ImportError:
        _state = "error"
        _message = "未安装 argostranslate，请先执行：pip install argostranslate"
        return
    except Exception as e:  # pragma: no cover
        _state = "error"
        _message = "argostranslate 初始化失败：%s" % e
        return

    try:
        installed = at.get_installed_languages()
        from_lang = next((l for l in installed if l.code == "en"), None)
        to_lang = next((l for l in installed if l.code == "zh"), None)
    except Exception as e:  # pragma: no cover
        _state = "error"
        _message = "argostranslate 初始化失败：%s" % e
        return

    if from_lang is None or to_lang is None:
        _state = "error"
        _message = (
            "未安装 英→中(zh) 语言包。请运行：\n"
            'python -c "import argostranslate.package as p; p.update_package_index(); '
            "pkgs=[x for x in p.get_available_packages() if x.from_code=='en' and x.to_code=='zh']; "
            'p.install_from_path(pkgs[0].download())"'
        )
        return

    try:
        _translator = from_lang.get_translation(to_lang)
        _state = "ready"
        _message = ""
    except Exception as e:  # pragma: no cover
        _state = "error"
        _message = "argostranslate 初始化失败：%s" % e


def is_ready():
    _ensure()
    return _state == "ready"


def status_message():
    _ensure()
    return _message


def translate(text):
    text = str(text).strip()
    if not text:
        return ""
    if _CJK_RE.search(text):
        return ""  # 已是中文, 无需再译
    _ensure()
    if _state != "ready":
        return ""
    try:
        return _translator.translate(text).strip()
    except Exception:  # pragma: no cover
        return ""
