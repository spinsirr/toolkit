"""Run: python3 tests/check.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "plugin/hooks"), str(ROOT / "scripts")]

from apply import BLOCK_MARK, for_tool, merge, set_toml_keys, with_block
from decide import offers_next_step
from guard import reason

for bad in ["rm -rf /", "rm -rf ~", "rm -fr $HOME", "sudo rm -rf /*", "git push --force origin main", "git push -f origin master", "mkfs.ext4 /dev/sda1", "dd if=x of=/dev/disk2"]:
    assert reason(bad), bad
for bad in ['pkill -f "cs login"', "pkill -9 -f agent-browser", "sleep 1; pkill -fl node"]:
    assert reason(bad).startswith("pkill -f"), bad
for ok in ["rm -rf node_modules", "pkill -x node", "kill 1234", "pgrep -f node", "rm -rf ./build", "rm -rf ~/tmp/cache", "git push origin main", "git push --force origin feature", "ls -la /"]:
    assert not reason(ok), ok

assert merge({"a": [1], "b": {"x": 1}, "k": 0}, {"a": [1, 2], "b": {"y": 2}}) == {"a": [1, 2], "b": {"x": 1, "y": 2}, "k": 0}

toml = 'model = "m"\nx = 1\n\n[desktop]\nx = 2\n'
out = set_toml_keys(toml, ["x = 5", "new = true"])
assert out.startswith('model = "m"\nx = 5\nnew = true\n'), out
assert "[desktop]\nx = 2\n" in out, out
assert set_toml_keys(out, ["x = 5", "new = true"]) == out
assert set_toml_keys("", ["a = 1"]) == "a = 1\n\n"
env = {"LORE_PROFILE_CLAUDE": "", "LORE_PROFILE_CODEX": "codex", "X": "1"}
assert for_tool(env, "codex")["LORE_PROFILE"] == "codex"
assert for_tool(env, "claude")["LORE_PROFILE"] == ""
assert for_tool(env, "claude")["X"] == "1"
once = with_block("platform\n", "toolkit v1\n")
assert once == f"platform\n\n{BLOCK_MARK}\ntoolkit v1\n", once
assert with_block(once, "toolkit v2\n") == f"platform\n\n{BLOCK_MARK}\ntoolkit v2\n"
assert with_block("", "t\n") == f"{BLOCK_MARK}\nt\n"
for offer in ["四轮全部跑完。\n\n要我按上面这几点改 skill，再重跑 Sonnet 吗？", "Tests pass. Shall I push the branch?", "Done. Want me to open the PR?"]:
    assert offers_next_step(offer), offer
for done in ["四轮全部跑完。结论如下。", "Which of these two designs do you prefer?", "Shall I push? I did it already.\n\nThe PR is open."]:
    assert not offers_next_step(done), done
print("ok")
