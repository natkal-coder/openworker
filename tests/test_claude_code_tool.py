"""ask_claude's wire contract: fixed minimal CLI flags, prompt over stdin, errors surfaced."""

import subprocess

from coworker.tools import claude_code
from coworker.tools.claude_code import CLAUDE_CMD, claude_code_tools


def _tool(monkeypatch, run):
    monkeypatch.setattr(claude_code.shutil, "which", lambda _: "/usr/bin/claude")
    monkeypatch.setattr(claude_code.subprocess, "run", run)
    (spec,) = claude_code_tools()
    return spec


def test_minimal_flags_and_stdin_prompt(monkeypatch):
    seen = {}

    def run(cmd, **kw):
        seen.update(cmd=cmd, input=kw.get("input"))
        return subprocess.CompletedProcess(cmd, 0, stdout="answer\n", stderr="")

    assert _tool(monkeypatch, run)(prompt="-q?") == {"answer": "answer"}
    assert seen["cmd"] == CLAUDE_CMD
    assert seen["input"] == "-q?"  # stdin, never argv (a leading dash must not become a flag)
    assert seen["cmd"][seen["cmd"].index("--tools") + 1] == ""  # no tools → no nested agent
    assert "--effort" in seen["cmd"] and "opus" in seen["cmd"]


def test_nonzero_exit_surfaces_stderr(monkeypatch):
    def run(cmd, **kw):
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="Not logged in\n")

    assert _tool(monkeypatch, run)(prompt="x") == {"error": "Not logged in"}


def test_missing_cli(monkeypatch):
    monkeypatch.setattr(claude_code.shutil, "which", lambda _: None)
    (spec,) = claude_code_tools()
    assert "not found" in spec(prompt="x")["error"]


def test_schema_name_matches_risk_table():
    from coworker.risk import RiskClass, classify

    assert classify("ask_claude") is RiskClass.EGRESS
