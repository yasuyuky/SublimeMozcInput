#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sublime_plugin
import sublime
import sys
import subprocess
import json

PY2 = sys.version_info < (3, 0)
if not PY2: basestring = str

settings = sublime.load_settings("MozcInput.sublime-settings")

helper = subprocess.Popen(settings.get("mozc_emacs_helper",
                                       "mozc_emacs_helper").split(),
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE)

helper.stdout.readline()

mozc_mode_line = settings.get("mozc_mode_line", "[Mozc]")
mozc_input_mode_line = settings.get("mozc_input_mode_line", u"✎Mozc")
mozc_highlight_style = settings.get("mozc_highlight_style", "string")
mozc_use_quick_panel = settings.get("mozc_use_quick_panel", True)
mozc_debug_mode = settings.get("mozc_debug_mode", False)


mozc_mode = False
mozc_input_mode = False
mozc_qp_mode = False
msg_count = 0
sess_count = 0
start_point = 0
last_point = 0

for w in sublime.windows():
    for v in w.views():
        v.set_status('_mozc', '')

whitesp = " \t\r\n"
tokens = "()"


def parse_sexp(sexp):
    sexp = sexp.strip(whitesp)
    if sexp[0] == '(':
        ret = []
        remain = sexp[1:]
        while remain[0] != ')':
            e, remain = parse_sexp(remain)
            ret.append(e)
        if len(ret) == 3 and ret[1] == '.':
            ret = (ret[0], ret[2])
        elif len(ret) > 1 and isinstance(ret[0], basestring):
            ret = (ret[0], ret[1:])
        if all(isinstance(e, tuple) for e in ret):
            ret = dict(ret)
        return ret, remain[1:]
    elif sexp[0] == '"':
        ret = u''
        escaped = False
        remain = sexp[1:]
        while escaped or remain[0] != '"':
            if escaped:
                escaped = False
                ret += remain[0]
                remain = remain[1:]
            elif remain[0] == '\\':
                escaped = True
                remain = remain[1:]
            else:
                ret += remain[0]
                remain = remain[1:]
        return ret, remain[1:]
    else:
        ret = ''
        remain = sexp
        while remain[0] not in whitesp+tokens:
            ret += remain[0]
            remain = remain[1:]
        return ret, remain


def communicate(cmd, arg=""):
    global helper, msg_count
    fullmsg = "({0} {1} {2})\n".format(msg_count, cmd, arg)
    helper.stdin.write(bytes(fullmsg.encode("utf-8")))
    helper.stdin.flush()
    msg_count += 1
    return parse_sexp(helper.stdout.readline().decode('utf-8'))[0]


def print_json(obj):
    print(json.dumps(obj, indent=1, ensure_ascii=False).encode('utf-8'))


def print_debug(*args):
    if mozc_debug_mode :
        print(*args)


class ToggleMozcCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if mozc_mode:
            self.view.run_command("deactivate_mozc")
        else:
            self.view.run_command("activate_mozc")


class ActivateMozcCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global mozc_mode, last_point
        mozc_mode = True
        self.view.set_status('_mozc', mozc_mode_line)
        last_point = self.view.sel()[0].begin()


class DeactivateMozcCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global mozc_mode
        if mozc_input_mode:
            self.view.run_command("mozc_end_input")
        mozc_mode = False
        self.view.set_status('_mozc', '')


class MozcReplaceTextCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        input_region = self.view.get_regions("_mozc")
        if not input_region: self.view.insert(edit, start_point, text)
        else: self.view.replace(edit, input_region[0], text)
        self.view.run_command("mozc_set_input_region")


class MozcSetInputRegionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        input_region = sublime.Region(start_point, self.view.sel()[0].end())
        self.view.add_regions('_mozc', [input_region], mozc_highlight_style)
        self.view.run_command("mozc_move_to_end")


class MozcMoveToEndCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        input_region = self.view.get_regions('_mozc')[0]
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(input_region.end()))


class MozcHighlightCommand(sublime_plugin.TextCommand):
    def run(self, edit, cursor, highlight, segments):
        accmum = 0
        segdic = {}
        for s in segments:
            segdic[accmum] = int(s["value-length"])
            accmum += int(s["value-length"])
        input_region = sublime.Region(start_point, start_point+cursor)
        self.view.add_regions('_mozc', [input_region], mozc_highlight_style)
        highlight_r = sublime.Region(start_point+highlight,
                                     start_point+highlight+segdic[highlight])
        self.view.sel().clear()
        self.view.sel().add(highlight_r)


class MozcStartInputCommand(sublime_plugin.TextCommand):
    def run(self, edit, key):
        global mozc_input_mode, sess_count, start_point
        if mozc_mode:
            if not mozc_input_mode:
                mozc_input_mode = True
                self.view.set_status('_mozc', mozc_input_mode_line)
                start_point = last_point
                oobj = communicate('CreateSession')
                print_debug("Start:", oobj)
                sess_count = int(oobj["emacs-session-id"])
            self.view.run_command("mozc_send_key", {"key": key})


class MozcFixInputCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global start_point
        start_point = self.view.get_regions("_mozc")[0].end()
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(start_point))
        self.view.run_command('mozc_set_input_region')


class MozcEndInputCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global mozc_input_mode,  sess_count
        if mozc_input_mode:
            mozc_input_mode = False
            print_debug("End:", communicate('DeleteSession ', sess_count))
            sess_count += 1
            self.view.add_regions('_mozc', [], mozc_highlight_style)
            self.view.set_status('_mozc', mozc_mode_line)


class MozcInsertPreeditCommand(sublime_plugin.TextCommand):
    def run(self, edit, preedit):
        preeditstr = ''.join(e["value"] for e in preedit["segment"])
        self.view.run_command("mozc_replace_text", {"text": preeditstr})
        if "highlighted-position" in preedit:
            self.view.run_command("mozc_highlight",
                                  {"highlight": int(preedit["highlighted-position"]),
                                   "cursor": int(preedit["cursor"]),
                                   "segments": preedit["segment"]})
        else:
            self.view.run_command("mozc_set_input_region")


class MozcShowSuggestCommand(sublime_plugin.TextCommand):
    def run(self, edit, all_candidate):
        global mozc_qp_mode
        candidates = [[c["value"], c["annotation"]["description"]] if "annotation" in c else [c["value"],""]
                      for c in all_candidate["candidates"]]
        focused_idx = int(all_candidate['focused-index'])

        def on_done(idx):
            global mozc_qp_mode
            mozc_qp_mode = False
            if idx == -1: return
            if idx > focused_idx:
                for i in range(idx-focused_idx-1):
                    communicate('SendKey', "{0} {1}".format(sess_count, "down"))
                oobj = communicate('SendKey', "{0} {1}".format(sess_count, "down"))["output"]
                self.view.run_command("mozc_insert_preedit", {"preedit": oobj["preedit"]})
            elif idx < focused_idx:
                for i in range(focused_idx-idx-1):
                    communicate('SendKey', "{0} {1}".format(sess_count, "up"))
                oobj = communicate('SendKey', "{0} {1}".format(sess_count, "up"))["output"]
                self.view.run_command("mozc_insert_preedit", {"preedit": oobj["preedit"]})

        mozc_qp_mode = True
        sublime.active_window().show_quick_panel(candidates, on_done)


class MozcSendKeyCommand(sublime_plugin.TextCommand):
    def run(self, edit, key):
        if mozc_mode and not mozc_qp_mode:
            oobj = communicate('SendKey', "{0} {1}".format(sess_count, key))["output"]
            if "performed-command" not in oobj: return
            performed = oobj["performed-command"]
            print_debug(key, performed)
            if 'result' in oobj:
                self.view.run_command("mozc_fix_input")
            if 'preedit' in oobj:
                self.view.run_command("mozc_insert_preedit", {"preedit": oobj["preedit"]})
            else:
                self.view.run_command("mozc_replace_text", {"text": ""})
                self.view.run_command("mozc_end_input")
            if performed == "Conversion_PredictAndConvert" or performed == "Conversion_ConvertNext":
                if mozc_use_quick_panel:
                    self.view.run_command("mozc_show_suggest", {"all_candidate": oobj["all-candidate-words"]})
            elif performed == "Conversion_Commit" or performed == "Composition_Commit":
                self.view.run_command("mozc_end_input")


class MozcInputListener(sublime_plugin.EventListener):

    def on_selection_modified(self, view):
        global last_point
        if mozc_mode and not mozc_input_mode:
            if view.sel():
                last_point = view.sel()[0].begin()

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "mozc_mode":
            return mozc_mode
        elif key == "mozc_input_mode":
            return mozc_input_mode
        elif key == "mozc_qp_mode":
            return mozc_qp_mode

    def on_activated(self, view):
        if not mozc_qp_mode:
            view.run_command("deactivate_mozc")

    def on_deactivated(self, view):
        if not mozc_qp_mode:
            view.run_command("deactivate_mozc")
