#!/usr/bin/env python3
"""Small architecture linter using only the Python standard library."""
import argparse
import ast
import fnmatch
import json
from pathlib import Path
from datetime import date
import tomllib

class Linter:
    def __init__(self, root, config):
        self.root = Path(root).resolve()
        self.cfg = config.get("tool", {}).get("reff_linter", {})
        self.findings = []
        self.files = []
        self.graph = {}

    def add(self, level, code, path, line, message):
        try:
            name = str(Path(path).resolve().relative_to(self.root))
        except ValueError:
            name = str(path)
        self.findings.append({"level": level, "code": code, "path": name, "line": line, "message": message})

    def excluded(self, path):
        rel = path.relative_to(self.root).as_posix()
        excluded = self.cfg.get("exclude", []) + self.cfg.get("baseline_exclude", [])
        return any(fnmatch.fnmatch(rel, pattern) for pattern in excluded)

    def exception(self, path):
        rel = path.relative_to(self.root).as_posix()
        for item in self.cfg.get("exception", []):
            if fnmatch.fnmatch(rel, item.get("pattern", "")):
                expires = item.get("expires", "")
                if expires and expires < date.today().isoformat():
                    self.add("error", "EXPIRED_EXCEPTION", path, 1, item.get("reason", "exception expired"))
                    return False
                return True
        return False

    def discover(self):
        include = self.cfg.get("include", [])
        for path in self.root.rglob("*.py"):
            rel = path.relative_to(self.root).as_posix()
            if path.is_file() and (not include or any(fnmatch.fnmatch(rel, pattern) for pattern in include)) and not self.excluded(path):
                self.files.append(path)

    def check_file(self, path):
        if self.exception(path):
            return
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        warn = int(self.cfg.get("warn_file_lines", 200))
        error = int(self.cfg.get("error_file_lines", 300))
        hard = int(self.cfg.get("hard_file_lines", 500))
        if len(lines) > hard:
            self.add("error", "FILE_HARD_LIMIT", path, 1, f"{len(lines)} lines exceeds {hard}")
        elif len(lines) > error:
            self.add("error", "FILE_TOO_LARGE", path, 1, f"{len(lines)} lines exceeds {error}")
        elif len(lines) > warn:
            self.add("warning", "FILE_LARGE", path, 1, f"{len(lines)} lines exceeds target {warn}")
        for number, line in enumerate(lines, 1):
            if any(x in line for x in ("TODO", "FIXME")) and "issue:" not in line.lower() and "reff-ignore" not in line:
                self.add("warning", "TODO_WITHOUT_ISSUE", path, number, "Add issue reference or reff-ignore reason")
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            self.add("error", "SYNTAX_ERROR", path, exc.lineno or 1, str(exc))
            return
        self.check_ast(path, tree)
        self.add_imports(path, tree)
    def check_ast(self, path, tree):
        max_lines = int(self.cfg.get("max_function_lines", 60))
        max_complexity = int(self.cfg.get("max_complexity", 10))
        max_nesting = int(self.cfg.get("max_nesting", 3))
        max_params = int(self.cfg.get("max_parameters", 7))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = getattr(node, "end_lineno", node.lineno)
                size = end - node.lineno + 1
                if size > max_lines:
                    self.add("warning", "FUNCTION_LARGE", path, node.lineno, f"{node.name}: {size} lines exceeds {max_lines}")
                args = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                names = [x.arg for x in args if x.arg not in ("self", "cls")]
                if node.args.vararg:
                    names.append(node.args.vararg.arg)
                if node.args.kwarg:
                    names.append(node.args.kwarg.arg)
                if len(names) > max_params:
                    self.add("warning", "TOO_MANY_PARAMETERS", path, node.lineno, f"{node.name}: {len(names)} parameters exceeds {max_params}")
                branch_nodes = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.With, ast.AsyncWith, ast.IfExp, ast.BoolOp)
                complexity = 1 + sum(isinstance(x, branch_nodes) for x in ast.walk(node))
                if complexity > max_complexity:
                    self.add("warning", "COMPLEXITY_HIGH", path, node.lineno, f"{node.name}: complexity {complexity} exceeds {max_complexity}")
                nesting = self.max_nesting(node)
                if nesting > max_nesting:
                    self.add("warning", "NESTING_HIGH", path, node.lineno, f"{node.name}: nesting {nesting} exceeds {max_nesting}")
            elif isinstance(node, ast.ImportFrom) and any(x.name == "*" for x in node.names):
                if self.cfg.get("check_wildcard_imports", True):
                    self.add("error", "WILDCARD_IMPORT", path, node.lineno, "Use explicit imports")

    def max_nesting(self, node, depth=0):
        controls = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)
        current = depth + 1 if isinstance(node, controls) else depth
        children = [self.max_nesting(x, current) for x in ast.iter_child_nodes(node)]
        return max([current] + children)

    def add_imports(self, path, tree):
        module = path.relative_to(self.root).with_suffix("").as_posix().replace("/", ".")
        if module.endswith(".__init__"):
            module = module[:-9]
        self.graph.setdefault(module, set())
        known = {p.relative_to(self.root).with_suffix("").as_posix().replace("/", ".") for p in self.files}
        for node in ast.walk(tree):
            target = None
            if isinstance(node, ast.Import) and node.names:
                target = node.names[0].name
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level:
                    parent = module.rsplit(".", node.level)[0] if "." in module else ""
                    target = parent + ("." if parent and base else "") + base
                else:
                    target = base
            if target:
                candidates = [target, target.rsplit(".", 1)[0] if "." in target else target]
                for candidate in candidates:
                    if candidate in known:
                        self.graph[module].add(candidate)
                        break

    def check_cycles(self):
        if not self.cfg.get("check_cycles", True):
            return
        visited, active, reported = set(), set(), set()
        def visit(node, stack):
            if node in active:
                start = stack.index(node)
                cycle = " -> ".join(stack[start:] + [node])
                key = tuple(sorted(stack[start:]))
                if key not in reported:
                    self.add("error", "IMPORT_CYCLE", node.replace(".", "/") + ".py", 1, cycle)
                    reported.add(key)
                return
            if node in visited:
                return
            active.add(node)
            for child in self.graph.get(node, set()):
                visit(child, stack + [child])
            active.remove(node)
            visited.add(node)
        for node in self.graph:
            visit(node, [node])
    def run(self):
        self.discover()
        for path in self.files:
            self.check_file(path)
        self.check_cycles()
        return self.findings

def main():
    parser = argparse.ArgumentParser(description="Lint Python architecture and refactoring limits")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--config", default=".reff-linter.toml")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.path).resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = root / config_path
    config = tomllib.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    findings = Linter(root, config).run()
    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        for item in findings:
            print(f"{item['level'].upper():7} {item['path']}:{item['line']} [{item['code']}] {item['message']}")
        errors = sum(x["level"] == "error" for x in findings)
        warnings = sum(x["level"] == "warning" for x in findings)
        print(f"reff_linter: {errors} errors, {warnings} warnings")
    errors = any(x["level"] == "error" for x in findings)
    warnings = any(x["level"] == "warning" for x in findings)
    strict = args.strict or config.get("tool", {}).get("reff_linter", {}).get("strict_warnings", False)
    return 1 if errors or (strict and warnings) else 0

if __name__ == "__main__":
    raise SystemExit(main())
