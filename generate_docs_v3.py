#!/usr/bin/env python3
"""
Portfolio Documentation Generator v5.6
Автоматически анализирует Python- и JS/TS-проект, генерирует технические файлы пакета в docPRO/,
создает продающее описания проекта в папках по языкам:
- docPRO/RU/ (описания на русском)
- docPRO/EN/ (описания на английском)
и синхронизирует структуру с Obsidian и NotebookLM, убирая дублирование.

Использование:
    python generate_docs_v3.py
    python generate_docs_v3.py --overwrite
    python generate_docs_v3.py --complexity
"""

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import List, Set, Optional, Dict, Any

# ============================================================
# ⚙️  КОНФИГУРАЦИЯ ПО УМОЛЧАНИЮ
# ============================================================
DEFAULT_OBSIDIAN_SEARCH_ROOTS = [
    Path.home() / "Documents" / "Obsidian Memory 26",
    Path.home() / "Documents",
    Path.home() / "Obsidian",
    Path.home(),
]
DEFAULT_NOTEBOOKLM_SEARCH_ROOTS = [
    Path.home() / "Documents" / "NotebookLM",
    Path.home() / "NotebookLM",
]
DEFAULT_DOCS_FOLDER_NAME = "docPRO"

# ============================================================
# 📚 СЛОВАРИ И КАТЕГОРИИ СТЕКА
# ============================================================
IMPORT_TO_PACKAGE = {
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
    "bs4": "beautifulsoup4",
    "dotenv": "python-dotenv",
    "jwt": "PyJWT",
    "dateutil": "python-dateutil",
    "attr": "attrs",
    "Crypto": "pycryptodome",
    "magic": "python-magic",
}

STACK_KEYWORDS = {
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "aiogram": "Aiogram (Telegram)",
    "telebot": "pyTelegramBotAPI",
    "pytelegrambotapi": "pyTelegramBotAPI",
    "sqlalchemy": "SQLAlchemy",
    "asyncpg": "asyncpg",
    "psycopg2": "psycopg2",
    "pymongo": "PyMongo",
    "redis": "Redis",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "transformers": "HuggingFace Transformers",
    "openai": "OpenAI API",
    "anthropic": "Anthropic API",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "celery": "Celery",
    "boto3": "boto3 (AWS SDK)",
    "docker": "Docker SDK",
    "pytest": "Pytest",
    "mypy": "Mypy",
    "ruff": "Ruff",
    "black": "Black",
    "httpx": "HTTPX",
    "aiohttp": "aiohttp",
    "requests": "Requests",
}

TECH_CATEGORIES = {
    "Web / API": {
        "fastapi": "FastAPI",
        "flask": "Flask",
        "django": "Django",
        "aiogram": "Aiogram (Telegram)",
        "telebot": "pyTelegramBotAPI",
        "pytelegrambotapi": "pyTelegramBotAPI"
    },
    "Базы данных": {
        "sqlalchemy": "SQLAlchemy",
        "asyncpg": "asyncpg",
        "psycopg2": "psycopg2",
        "pymongo": "PyMongo",
        "redis": "Redis"
    },
    "Данные / ML": {
        "pandas": "Pandas",
        "numpy": "NumPy",
        "scipy": "SciPy",
        "torch": "PyTorch",
        "tensorflow": "TensorFlow",
        "transformers": "HuggingFace Transformers"
    },
    "AI / LLM": {
        "openai": "OpenAI API",
        "anthropic": "Anthropic API",
        "langchain": "LangChain",
        "llamaindex": "LlamaIndex"
    },
    "Инфраструктура": {
        "docker": "Docker SDK",
        "celery": "Celery",
        "boto3": "boto3 (AWS SDK)",
        "httpx": "HTTPX",
        "aiohttp": "aiohttp"
    },
    "Тесты / качество": {
        "pytest": "Pytest",
        "mypy": "Mypy",
        "ruff": "Ruff",
        "black": "Black"
    }
}

JS_STACK_MAP = {
    "Frontend / UI": {
        "next": "Next.js",
        "react": "React",
        "vue": "Vue.js",
        "angular": "@angular/core",
        "svelte": "Svelte",
        "tailwind": "TailwindCSS",
        "vite": "Vite",
        "typescript": "TypeScript"
    },
    "ORM / Database": {
        "drizzle-orm": "Drizzle ORM",
        "prisma": "Prisma",
        "sequelize": "Sequelize",
        "typeorm": "TypeORM",
        "mongoose": "Mongoose",
        "pg": "PostgreSQL Client"
    },
    "API / State": {
        "redux": "Redux",
        "axios": "Axios",
        "graphql": "GraphQL",
        "trpc": "@trpc/server",
        "react-query": "TanStack Query"
    },
    "Тесты / качество (JS)": {
        "jest": "Jest",
        "vitest": "Vitest",
        "eslint": "ESLint",
        "prettier": "Prettier",
        "playwright": "Playwright",
        "cypress": "Cypress"
    }
}

# ============================================================
# 🔍 АНАЛИЗ ПРОЕКТА
# ============================================================
def get_project_name() -> str:
    return Path.cwd().name.replace("_", " ").replace("-", " ").title()


def get_stdlib_modules() -> Set[str]:
    if hasattr(sys, "stdlib_module_names"):
        return set(sys.stdlib_module_names)
    return {
        "os", "sys", "re", "json", "math", "datetime", "time", "pathlib",
        "typing", "collections", "itertools", "functools", "io", "subprocess",
        "shutil", "glob", "hashlib", "logging", "unittest", "abc", "contextlib",
        "dataclasses", "enum", "copy", "string", "textwrap", "uuid", "secrets",
        "sqlite3", "csv", "pickle", "struct", "socket", "threading", "multiprocessing",
        "asyncio", "concurrent", "urllib", "http", "email", "html", "xml",
        "argparse", "configparser", "tempfile", "stat", "signal", "warnings",
    }


def scan_imports() -> Set[str]:
    """Сканирует все .py файлы проекта и собирает импорты верхнего уровня."""
    imports: Set[str] = set()
    skip_dirs = {
        "venv", ".venv", ".git", "docs", "docPRO", "__pycache__", "node_modules",
        "build", "dist", ".mypy_cache", ".pytest.cache", ".pytest_cache", ".next",
    }
    for py_file in Path.cwd().rglob("*.py"):
        if any(part in skip_dirs for part in py_file.parts):
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:
                    imports.add(node.module.split(".")[0])
    return imports


def get_local_modules() -> Set[str]:
    """Возвращает имена локальных модулей проекта для фильтрации сторонних библиотек."""
    local_mods: Set[str] = set()
    skip_dirs = {
        "venv", ".venv", ".git", "docs", "docPRO", "__pycache__", "node_modules",
        "build", "dist", ".mypy_cache", ".pytest.cache", ".pytest_cache", ".next",
    }
    for py_file in Path.cwd().rglob("*.py"):
        if any(part in skip_dirs for part in py_file.parts):
            continue
        local_mods.add(py_file.stem)
        try:
            rel = py_file.relative_to(Path.cwd())
            for part in rel.parts[:-1]:
                local_mods.add(part)
        except ValueError:
            pass
    return local_mods


def extract_deps_from_files() -> Set[str]:
    """Считывает зависимости из конфигурационных файлов проекта (если они есть)."""
    deps = set()
    
    # 1. requirements.txt
    req_file = Path("requirements.txt")
    if req_file.exists():
        try:
            content = req_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                match = re.match(r'^([a-zA-Z0-9_\-]+)', line)
                if match:
                    deps.add(match.group(1).replace("-", "_"))
        except Exception:
            pass
            
    # 2. pyproject.toml
    pyproj_file = Path("pyproject.toml")
    if pyproj_file.exists():
        try:
            content = pyproj_file.read_text(encoding="utf-8")
            dep_block_match = re.search(r'dependencies\s*=\s*\[([^\]]*)\]', content)
            if dep_block_match:
                block_content = dep_block_match.group(1)
                for match in re.finditer(r'["\']([a-zA-Z0-9_\-]+)[>=<!~]*[^"\']*["\']', block_content):
                    deps.add(match.group(1).replace("-", "_"))
        except Exception:
            pass
            
    # 3. setup.py
    setup_file = Path("setup.py")
    if setup_file.exists():
        try:
            content = setup_file.read_text(encoding="utf-8")
            install_req_match = re.search(r'install_requires\s*=\s*\[([^\]]*)\]', content)
            if install_req_match:
                block_content = install_req_match.group(1)
                for match in re.finditer(r'["\']([a-zA-Z0-9_\-]+)[>=<!~]*[^"\']*["\']', block_content):
                    deps.add(match.group(1).replace("-", "_"))
        except Exception:
            pass
            
    return deps


def detect_dependencies() -> List[str]:
    """Собирает полный список сторонних зависимостей проекта."""
    imports = scan_imports()
    local_mods = get_local_modules()
    imported_packages = set()
    
    for imp in imports:
        pkg = IMPORT_TO_PACKAGE.get(imp, imp)
        imported_packages.add(pkg.lower().replace("-", "_"))
        
    for dep in extract_deps_from_files():
        imported_packages.add(dep.lower().replace("-", "_"))
        
    stdlib = get_stdlib_modules()
    filtered_packages = []
    
    for pkg in sorted(imported_packages):
        if pkg in stdlib or pkg.startswith("_"):
            continue
        if pkg in [m.lower() for m in local_mods]:
            continue
        if pkg == Path.cwd().name.lower().replace("-", "_"):
            continue
            
        orig_name = None
        for k, v in IMPORT_TO_PACKAGE.items():
            if v.lower().replace("-", "_") == pkg:
                orig_name = v
                break
        if not orig_name:
            for k, v in STACK_KEYWORDS.items():
                if k.lower().replace("-", "_") == pkg:
                    orig_name = v
                    break
        if not orig_name:
            orig_name = pkg.replace("_", "-")
            
        if orig_name not in filtered_packages:
            filtered_packages.append(orig_name)
            
    return filtered_packages


def detect_tech_stack(packages: List[str]) -> Dict[str, List[str]]:
    """Категоризирует сторонние библиотеки по технологическим блокам."""
    detected = {cat: [] for cat in TECH_CATEGORIES}
    
    for pkg in packages:
        pkg_lower = pkg.lower().replace("-", "_")
        found = False
        for cat, cat_dict in TECH_CATEGORIES.items():
            for key, val in cat_dict.items():
                if key.lower().replace("-", "_") == pkg_lower:
                    if val not in detected[cat]:
                        detected[cat].append(val)
                    found = True
                    break
            if found:
                break
                
    if (Path.cwd() / "Dockerfile").is_file() or (Path.cwd() / "docker-compose.yml").is_file():
        if "Docker" not in detected["Инфраструктура"]:
            detected["Инфраструктура"].append("Docker")
            
    if (Path.cwd() / ".github" / "workflows").is_dir():
        if "GitHub Actions (CI/CD)" not in detected["Инфраструктура"]:
            detected["Инфраструктура"].append("GitHub Actions (CI/CD)")
            
    if (Path.cwd() / "tests").is_dir():
        if "Pytest" not in detected["Тесты / качество"]:
            detected["Тесты / качество"].append("Pytest")
            
    return {k: v for k, v in detected.items() if v}


def detect_js_dependencies() -> Dict[str, List[str]]:
    """Считывает package.json и возвращает сгруппированный JS стек."""
    detected = {}
    pkg_file = Path("package.json")
    if not pkg_file.exists():
        return detected
        
    try:
        data = json.loads(pkg_file.read_text(encoding="utf-8"))
        deps = {}
        if "dependencies" in data:
            deps.update(data["dependencies"])
        if "devDependencies" in data:
            deps.update(data["devDependencies"])
            
        for category, mappings in JS_STACK_MAP.items():
            cat_list = []
            for dep_key in deps.keys():
                dep_key_lower = dep_key.lower()
                for key, val in mappings.items():
                    if key in dep_key_lower:
                        if val not in cat_list:
                            cat_list.append(val)
            if cat_list:
                detected[category] = cat_list
    except Exception:
        pass
    return detected


def extract_description() -> str:
    """Пытается извлечь описание проекта из Project Brain.md, docstring главного модуля, README или pyproject.toml."""
    raw_desc = ""
    
    # 1. Project Brain.md (наиболее надежный источник)
    brain_path = Path("Project Brain.md")
    if brain_path.is_file():
        try:
            content = brain_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if line and not any(line.startswith(c) for c in ("#", "!", "[", ">")):
                    if not (line.startswith("- ") or line.startswith("* ") or line.startswith("_ ") or line == "---"):
                        clean_line = line.replace("**", "").replace("*", "").replace("`", "").strip()
                        # Игнорируем технические строки
                        if clean_line and not any(clean_line.startswith(p) for p in ("Статус:", "Дата:", "Ветка:", "Version", "Frontend Status", "Deployment")):
                            raw_desc = clean_line
                            break
        except Exception:
            pass

    # 2. Если не нашли, ищем в python-файлах
    if not raw_desc:
        candidates = ["main.py", "app.py", "__init__.py", f"{Path.cwd().name.lower().replace('-', '_')}.py"]
        all_candidates = []
        for cand in candidates:
            all_candidates.append(Path(cand))
            all_candidates.append(Path("src") / cand)
            
        for path in all_candidates:
            if path.is_file():
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", SyntaxWarning)
                        tree = ast.parse(path.read_text(encoding="utf-8"))
                    doc = ast.get_docstring(tree)
                    if doc:
                        first_line = doc.strip().split("\n")[0]
                        if first_line:
                            raw_desc = first_line.strip()
                            break
                except Exception:
                    pass

    # 3. README.md (только если не содержит шаблонных фраз из генератора)
    if not raw_desc:
        readme_path = Path("README.md")
        if readme_path.is_file():
            try:
                content = readme_path.read_text(encoding="utf-8")
                for line in content.splitlines():
                    line = line.strip()
                    if line and not any(line.startswith(c) for c in ("#", "!", "[", ">")):
                        if not (line.startswith("- ") or line.startswith("* ") or line.startswith("_ ") or line == "---" or line == "***" or line == "___"):
                            clean_line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line)
                            clean_line = clean_line.replace("**", "").replace("*", "").replace("`", "")
                            # Защита от обратной связи: пропускаем строки-заглушки генератора
                            if clean_line and not any(p in clean_line for p in ("This project demonstrates", "Production-ready project", "Готовый к работе")):
                                raw_desc = clean_line.strip()
                                break
            except Exception:
                pass

    # 4. pyproject.toml
    if not raw_desc:
        pyproject_path = Path("pyproject.toml")
        if pyproject_path.is_file():
            try:
                content = pyproject_path.read_text(encoding="utf-8")
                match = re.search(r'^description\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
                if match:
                    raw_desc = match.group(1).strip()
            except Exception:
                pass

    if not raw_desc:
        raw_desc = "Production-ready application for portfolio presentation and practical use."

    # Чистим от ведущих blockquote-символов
    raw_desc = raw_desc.lstrip(">").strip()
    return raw_desc


def collect_metrics() -> Dict[str, Any]:
    """Собирает числовые и качественные метрики кодовой базы проекта (Python + JS/TS)."""
    metrics = {
        "py_files": 0, "py_loc": 0, "py_funcs": 0, "py_classes": 0,
        "js_files": 0, "js_loc": 0,
        "ts_files": 0, "ts_loc": 0,
        "has_tests": False, "has_cicd": False, "has_docker": False,
        "has_pyproject": False, "has_package_json": False, "has_tsconfig": False
    }
    
    skip_dirs = {
        "venv", ".venv", ".git", "docs", "docPRO", "__pycache__", "node_modules",
        "build", "dist", ".mypy_cache", ".pytest.cache", ".pytest_cache", ".next",
        ".vercel", "out"
    }
    
    # Python files analysis
    for py_file in Path.cwd().rglob("*.py"):
        if any(part in skip_dirs for part in py_file.parts):
            continue
        metrics["py_files"] += 1
        try:
            content = py_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                line_str = line.strip()
                if line_str and not line_str.startswith("#"):
                    metrics["py_loc"] += 1
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    metrics["py_funcs"] += 1
                elif isinstance(node, ast.ClassDef):
                    metrics["py_classes"] += 1
        except Exception:
            pass

    # JavaScript files analysis
    for js_file in Path.cwd().rglob("*.js"):
        if any(part in skip_dirs for part in js_file.parts):
            continue
        if js_file.name.endswith(".config.js") or js_file.name.endswith(".config.mjs"):
            continue
        metrics["js_files"] += 1
        try:
            content = js_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                line_str = line.strip()
                if line_str and not line_str.startswith("//") and not line_str.startswith("/*"):
                    metrics["js_loc"] += 1
        except Exception:
            pass

    # TypeScript / TSX files analysis
    for ts_file in Path.cwd().rglob("*.ts"):
        if any(part in skip_dirs for part in ts_file.parts):
            continue
        if ts_file.name.endswith(".d.ts") or ts_file.name.endswith(".config.ts"):
            continue
        metrics["ts_files"] += 1
        try:
            content = ts_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                line_str = line.strip()
                if line_str and not line_str.startswith("//") and not line_str.startswith("/*"):
                    metrics["ts_loc"] += 1
        except Exception:
            pass
            
    for tsx_file in Path.cwd().rglob("*.tsx"):
        if any(part in skip_dirs for part in tsx_file.parts):
            continue
        metrics["ts_files"] += 1
        try:
            content = tsx_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                line_str = line.strip()
                if line_str and not line_str.startswith("//") and not line_str.startswith("/*"):
                    metrics["ts_loc"] += 1
        except Exception:
            pass

    metrics["has_tests"] = (Path.cwd() / "tests").is_dir() or (Path.cwd() / "__tests__").is_dir()
    metrics["has_cicd"] = (Path.cwd() / ".github" / "workflows").is_dir()
    metrics["has_docker"] = (Path.cwd() / "Dockerfile").is_file() or (Path.cwd() / "docker-compose.yml").is_file()
    metrics["has_pyproject"] = (Path.cwd() / "pyproject.toml").is_file()
    metrics["has_package_json"] = (Path.cwd() / "package.json").is_file()
    metrics["has_tsconfig"] = (Path.cwd() / "tsconfig.json").is_file()
    
    return metrics


def get_git_repo_info() -> Optional[Dict[str, str]]:
    """Получает хост, владельца и имя репозитория из git remote origin."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return None
        url = result.stdout.strip()
        if url.startswith("git@github.com:"):
            without_git = url.split(":", 1)[1]
            owner_repo = without_git.removesuffix(".git")
            if "/" in owner_repo:
                owner, repo = owner_repo.split("/", 1)
                return {"host": "github.com", "owner": owner, "repo": repo}
        elif url.startswith("https://github.com/"):
            without_https = url.removeprefix("https://github.com/")
            owner_repo = without_https.removesuffix(".git")
            if "/" in owner_repo:
                owner, repo = owner_repo.split("/", 1)
                return {"host": "github.com", "owner": owner, "repo": repo}
    except Exception:
        pass
    return None


def ci_badge_markdown(repo_info: Optional[Dict[str, str]]) -> str:
    """Возвращает badge с состоянием GitHub Actions, если репозиторий на GitHub."""
    if not repo_info:
        return ""
    host = repo_info.get("host")
    owner = repo_info.get("owner")
    repo = repo_info.get("repo")
    if host == "github.com" and owner and repo:
        return f"![CI](https://github.com/{owner}/{repo}/actions/workflows/ci.yml/badge.svg)"
    return ""


# ============================================================
# 🔮 УМНЫЙ ЭКСТРАКТОР ИЗ Markdown (Project Brain.md и др.)
# ============================================================
def extract_sections_from_markdown() -> Dict[str, Any]:
    """Ищет файлы описания и вытаскивает оттуда реальные фичи и проблемы на RU/EN."""
    info = {
        "ru": {"problems": [], "features": [], "brief_description": ""},
        "en": {"problems": [], "features": [], "brief_description": ""}
    }
    
    # 1. Project Brain.md (обычно на русском)
    brain_path = Path("Project Brain.md")
    if brain_path.exists():
        try:
            content = brain_path.read_text(encoding="utf-8")
            
            # Краткое описание
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("!") and not line.startswith("[") and not line.startswith(">"):
                    info["ru"]["brief_description"] = line
                    break
                    
            # Разделы
            parts = re.split(r'^#+\s+', content, flags=re.MULTILINE)
            for part in parts:
                lines = part.splitlines()
                if not lines:
                    continue
                title = lines[0].lower().strip()
                
                # Миссия / Проблемы / Цели
                if any(k in title for k in ["миссия", "проблем", "цели"]):
                    for line in lines[1:]:
                        line = line.strip()
                        if line.startswith("-") or line.startswith("*"):
                            item = line.lstrip("-* ").strip()
                            if item and item not in info["ru"]["problems"]:
                                info["ru"]["problems"].append(item)
                                
                # Компоненты / Фичи
                if any(k in title for k in ["компоненты", "функционал", "структура слоев", "алгоритм"]):
                    for line in lines[1:]:
                        line = line.strip()
                        if line.startswith("-") or line.startswith("*"):
                            item = line.lstrip("-* ").strip()
                            if item and item not in info["ru"]["features"]:
                                info["ru"]["features"].append(item)
        except Exception:
            pass

    # 2. README.md (обычно на английском или русском)
    readme_path = Path("README.md")
    if readme_path.exists():
        try:
            content = readme_path.read_text(encoding="utf-8")
            
            # Краткое описание
            readme_desc = ""
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("!") and not line.startswith("[") and not line.startswith(">"):
                    readme_desc = line
                    break
                    
            parts = re.split(r'^#+\s+', content, flags=re.MULTILINE)
            for part in parts:
                lines = part.splitlines()
                if not lines:
                    continue
                title = lines[0].lower().strip()
                
                # Problems / About
                if any(k in title for k in ["problem", "about"]):
                    for line in lines[1:]:
                        line = line.strip()
                        if line.startswith("-") or line.startswith("*"):
                            item = line.lstrip("-* ").strip()
                            if item:
                                info["en"]["problems"].append(item)
                                
                # Features / Tech Stack / Roadmap
                if any(k in title for k in ["features", "tech stack", "roadmap"]):
                    for line in lines[1:]:
                        line = line.strip()
                        if line.startswith("-") or line.startswith("*"):
                            item = line.lstrip("-* ").strip()
                            if item:
                                info["en"]["features"].append(item)
                                
            info["en"]["brief_description"] = readme_desc
        except Exception:
            pass
            
    return info


# ============================================================
# 📝 ГЕНЕРАЦИЯ ТЕХНИЧЕСКИХ ФАЙЛОВ ПАКЕТА (EN / RU)
# ============================================================
def gen_pyproject_toml(name: str, desc: str, deps: List[str]) -> str:
    deps_str = "\n".join(f'    "{d}",' for d in deps) if deps else '    # add dependencies here'
    slug = name.lower().replace(" ", "-")
    return f'''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{slug}"
version = "0.1.0"
description = "{desc}"
readme = "READMEPro.md"
requires-python = ">=3.10"
authors = [
    {{name = "Your Name", email = "your@email.com"}}
]
keywords = ["python", "portfolio", "automation"]
classifiers = [
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
]
dependencies = [
{deps_str}
]

[project.urls]
Homepage = "https://github.com/yourusername/{slug}"
Repository = "https://github.com/yourusername/{slug}"
Issues = "https://github.com/yourusername/{slug}/issues"
'''


def gen_setup_py() -> str:
    return '''"""Legacy setup.py — для обратной совместимости.
Вся конфигурация в pyproject.toml (PEP 621).
"""
from setuptools import setup

setup()
'''


def gen_setup_cfg(name: str, desc: str) -> str:
    slug = name.lower().replace(" ", "-")
    return f'''[metadata]
name = {slug}
version = 0.1.0
description = {desc}
author = Your Name
author_email = your@email.com
url = https://github.com/yourusername/{slug}
license = MIT

[options]
python_requires = >=3.10
packages = find:
include_package_data = True

[options.packages.find]
exclude =
    tests*
    docs*
'''


def gen_requirements(deps: List[str]) -> str:
    return "\n".join(deps) + "\n" if deps else "# No third-party dependencies detected\n"


def gen_readme_pro(
    name: str,
    desc: str,
    stack: List[str],
    deps: List[str],
    ci_badge: str = "",
) -> str:
    slug = name.lower().replace(" ", "-")
    stack_md = "\n".join(f"- **{s}**" for s in stack) if stack else "- **Python 3.10+**"
    deps_md = "\n".join(f"- `{d}`" for d in deps) if deps else "- No third-party dependencies detected"
    year = datetime.now().year
    return f'''# {name}

> Production-ready project for portfolio presentation and practical use.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success){ci_badge}

---

## About

**{desc}**

This project demonstrates:
- Solid software engineering practices
- Work with third-party libraries and APIs
- Reproducible structure and maintainable documentation

## Problem It Solves

- Automates routine workflows
- Reduces manual effort and time costs
- Shows an end-to-end implementation approach

## Tech Stack

{stack_md}

## Dependencies

{deps_md}

## Project Structure

```text
.
├── docPRO/
├── README.md
├── pyproject.toml
├── requirements.txt
└── src/
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Roadmap

- Improve business-specific documentation
- Add tests for core flows
- Extend automation coverage

## License

MIT License

## Author

Your Name, {year}
GitHub: https://github.com/yourusername/{slug}
'''


def gen_readme_pro_ru(
    name: str,
    desc: str,
    stack: List[str],
    deps: List[str],
    ci_badge: str = "",
) -> str:
    slug = name.lower().replace(" ", "-")
    stack_md = "\n".join(f"- **{s}**" for s in stack) if stack else "- **Python 3.10+**"
    deps_md = "\n".join(f"- `{d}`" for d in deps) if deps else "- Сторонних зависимостей не обнаружено"
    year = datetime.now().year
    return f'''# {name}

> Готовый к работе в продакшене проект для презентации портфолио и практического использования.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success){ci_badge}

---

## О проекте

**{desc}**

Этот проект демонстрирует:
- Высокие стандарты разработки ПО
- Интеграцию со сторонними библиотеками и API
- Воспроизводимую структуру и поддерживаемую документацию

## Какую проблему решает

- Автоматизирует рутинные процессы
- Сокращает ручные операции и временные затраты
- Показывает сквозной подход к реализации продукта

## Технологический стек

{stack_md}

## Зависимости

{deps_md}

## Структура проекта

```text
.
├── docPRO/
├── README.md
├── pyproject.toml
├── requirements.txt
└── src/
```

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## План развития

- Улучшение бизнес-документации
- Добавление тестов для ключевых сценариев воронки
- Расширение покрытия автоматизации

## Лицензия

MIT License

## Автор

Ваше Имя, {year}
GitHub: https://github.com/yourusername/{slug}
'''


def gen_summary_md(
    project_name: str,
    description: str,
    imports: Set[str],
    dependencies: List[str],
    stack: List[str],
    complexity_md: str = "",
) -> str:
    return f"""# Documentation Summary

- Project: {project_name}
- Description: {description}
- Detected imports: {len(imports)}
- Third-party dependencies: {", ".join(dependencies) if dependencies else "none"}
- Stack: {", ".join(stack) if stack else "Python/JS"}
- Generated at: {datetime.now().isoformat(timespec="seconds")}
{complexity_md}
"""


def gen_summary_md_ru(
    project_name: str,
    description: str,
    imports: Set[str],
    dependencies: List[str],
    stack: List[str],
    complexity_md: str = "",
) -> str:
    return f"""# Сводная информация о документации

- Проект: {project_name}
- Описание: {description}
- Обнаружено импортов: {len(imports)}
- Сторонние зависимости: {", ".join(dependencies) if dependencies else "отсутствуют"}
- Стек: {", ".join(stack) if stack else "Python/JS"}
- Дата создания: {datetime.now().isoformat(timespec="seconds")}
{complexity_md}
"""


# ============================================================
# 📄 РАЗБОР ФАЙЛА ДАННЫХ ПОРТФОЛИО (PROJECT_INFO.md)
# ============================================================
def parse_project_info_file(filepath: Path) -> Dict[str, Any]:
    info = {
        "ru_brief": "",
        "en_brief": "",
        "ru_problems": [],
        "en_problems": [],
        "ru_features": [],
        "en_features": [],
        "ru_cv_stack": "",
        "ru_cv_feature": "",
        "ru_cv_result": "",
        "en_cv_stack": "",
        "en_cv_feature": "",
        "en_cv_result": ""
    }
    if not filepath.exists():
        return info
    
    current_section = None
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return info
        
    for line in content.splitlines():
        line_strip = line.strip()
        if not line_strip:
            continue
        if line_strip.startswith("##"):
            sec_title = line_strip.replace("##", "").strip().lower()
            if "brief description (ru)" in sec_title:
                current_section = "ru_brief"
            elif "brief description (en)" in sec_title:
                current_section = "en_brief"
            elif "problems solved (ru)" in sec_title:
                current_section = "ru_problems"
            elif "problems solved (en)" in sec_title:
                current_section = "en_problems"
            elif "key features (ru)" in sec_title:
                current_section = "ru_features"
            elif "key features (en)" in sec_title:
                current_section = "en_features"
            elif "cv resume bullet (ru)" in sec_title:
                current_section = "ru_cv"
            elif "cv resume bullet (en)" in sec_title:
                current_section = "en_cv"
            else:
                current_section = None
            continue
            
        if current_section:
            if current_section in ["ru_brief", "en_brief"]:
                val = line_strip.lstrip(">").strip()
                if val:
                    info[current_section] = val
            elif current_section in ["ru_problems", "en_problems", "ru_features", "en_features"]:
                if line_strip.startswith("-") or line_strip.startswith("*"):
                    item = line_strip.lstrip("-* ").strip()
                    if item:
                        info[current_section].append(item)
            elif current_section == "ru_cv":
                if "стек:" in line_strip.lower() or "stack:" in line_strip.lower():
                    info["ru_cv_stack"] = line_strip.split(":", 1)[1].strip().lstrip("[]-* ")
                elif "функционал:" in line_strip.lower() or "feature:" in line_strip.lower():
                    info["ru_cv_feature"] = line_strip.split(":", 1)[1].strip().lstrip("[]-* ")
                elif "результат:" in line_strip.lower() or "result:" in line_strip.lower():
                    info["ru_cv_result"] = line_strip.split(":", 1)[1].strip().lstrip("[]-* ")
            elif current_section == "en_cv":
                if "стек:" in line_strip.lower() or "stack:" in line_strip.lower():
                    info["en_cv_stack"] = line_strip.split(":", 1)[1].strip().lstrip("[]-* ")
                elif "функционал:" in line_strip.lower() or "feature:" in line_strip.lower():
                    info["en_cv_feature"] = line_strip.split(":", 1)[1].strip().lstrip("[]-* ")
                elif "результат:" in line_strip.lower() or "result:" in line_strip.lower():
                    info["en_cv_result"] = line_strip.split(":", 1)[1].strip().lstrip("[]-* ")
                    
    return info


def load_openrouter_api_key() -> Optional[str]:
    import os
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line_strip = line.strip()
            if line_strip.startswith("OPENROUTER_API_KEY="):
                val = line_strip.split("=", 1)[1].strip().strip("'\"")
                if val:
                    return val
    env_local_path = Path(".env.local")
    if env_local_path.exists():
        for line in env_local_path.read_text(encoding="utf-8").splitlines():
            line_strip = line.strip()
            if line_strip.startswith("OPENROUTER_API_KEY="):
                val = line_strip.split("=", 1)[1].strip().strip("'\"")
                if val:
                    return val
    return None


def generate_project_info_with_ai(project_name: str, description: str, tech_stack_str: str, deps_str: str, context: str) -> Optional[str]:
    api_key = load_openrouter_api_key()
    if not api_key:
        print("   ⚠️  OPENROUTER_API_KEY не найден в окружении или .env файле. Автогенерация AI пропущена.")
        return None
        
    print("   🤖 Запрашиваю генерацию PROJECT_INFO.md у OpenRouter AI...")
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    prompt = f"""You are an expert technical writer and senior software architect.
Your task is to write a professional, high-quality portfolio documentation description for the project: '{project_name}'.

We have parsed the project and gathered the following information:
- Description from files: {description}
- Detected Tech Stack: {tech_stack_str}
- Detected Dependencies: {deps_str}
- Context from Project Brain/README:
{context}

Please generate the content of a file named `PROJECT_INFO.md` in the following format. Your output must strictly follow the format below, without any other markdown wrappers, chat text, or explanation. It must contain the real business context and features of the project without generic placeholders.

Format:
# Project Portfolio Information

This file contains curated descriptions and features of the project used by `generate_docs_v3.py` to generate the final bilingual portfolios. Do not delete the headings.

## Brief Description (RU)
<A 1-2 sentence compelling summary of what the project is in Russian>

## Brief Description (EN)
<A 1-2 sentence compelling summary of what the project is in English>

## Problems Solved (RU)
- <Problem 1 solved by the project (e.g. manual overhead, business automation, UX issue, data storage)>
- <Problem 2...>
- <Problem 3...>
- <Problem 4...>

## Problems Solved (EN)
- <Problem 1 in English...>
- <Problem 2...>
- <Problem 3...>
- <Problem 4...>

## Key Features (RU)
- 🔹 <Feature 1 (specific technical feature, e.g. SVG drawing, custom canvas, state sync)>
- 🔹 <Feature 2...>
- 🔹 <Feature 3...>
- 🔹 <Feature 4...>
- 🔹 <Feature 5...>
- 🔹 <Feature 6...>

## Key Features (EN)
- 🔹 <Feature 1 in English...>
- 🔹 <Feature 2...>
- 🔹 <Feature 3...>
- 🔹 <Feature 4...>
- 🔹 <Feature 5...>
- 🔹 <Feature 6...>

## CV Resume Bullet (RU)
- Стек: <Curated list of key tech stack items, e.g. Next.js, React, Tailwind, PostgreSQL, Docker>
- Ключевой функционал: <1-sentence summary of the main feature/achievement of this developer, e.g. Developed a custom Canvas rendering engine for real-time visualization>
- Результат: <1-sentence business outcome/result matching XYZ formula, e.g. Implemented end-to-end checkout boosting conversion by X%>

## CV Resume Bullet (EN)
- Stack: <Curated list of key tech stack items in English>
- Key Feature: <1-sentence technical achievement in English>
- Result: <1-sentence business outcome/result in English>
"""

    payload = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2
    }
    
    try:
        import urllib.request
        import json
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://lumira.local",
                "X-Title": "LUMIRA Docs Generator"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            text = res_data["choices"][0]["message"]["content"]
            if text.startswith("```"):
                lines = text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                text = "\n".join(lines)
            return text.strip()
    except Exception as e:
        print(f"   ⚠️  Ошибка при обращении к OpenRouter API: {e}. Будет использован статический шаблон.")
        return None


def create_project_info_template(
    filepath: Path,
    project_name: str,
    description: str,
    packages: List[str],
    tech_stack: Dict[str, List[str]],
    js_tech_stack: Dict[str, List[str]]
):
    # Collect context
    context = ""
    for name in ["Project Brain.md", "README.md", "Project Brain", "README"]:
        p = Path(name)
        if p.exists():
            try:
                context += f"\n--- File: {name} ---\n" + p.read_text(encoding="utf-8")[:6000] + "\n"
            except Exception:
                pass
                
    # Format tech stack
    combined_tech = {}
    combined_tech.update(tech_stack)
    combined_tech.update(js_tech_stack)
    tech_stack_parts = []
    for cat, libs in combined_tech.items():
        if libs:
            tech_stack_parts.append(f"{cat}: {', '.join(libs)}")
    tech_stack_str = "; ".join(tech_stack_parts)
    
    deps_str = ", ".join(packages)
    
    # Try AI generation first
    ai_content = generate_project_info_with_ai(project_name, description, tech_stack_str, deps_str, context)
    if ai_content:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(ai_content, encoding="utf-8")
        print("   ✅ Файл docPRO/PROJECT_INFO.md успешно сгенерирован с помощью Gemini AI!")
        return

    # Static fallback template
    is_aethel = "aethel" in project_name.lower()
    if is_aethel:
        brief_ru = "Интерактивное веб-приложение (SPA) для расчета Карты энергий по дате рождения и конструирования персональных амулетов в реальном времени."
        brief_en = "Interactive web application (SPA) for calculating the Energy Chart (Matrix of Destiny) by date of birth and crafting personal amulets in real-time."
        
        problems_ru = """- Сложность ручного расчета: Автоматизирует расчет 9 ключевых арканов судьбы по дате рождения, исключая ошибки и необходимость ручных вычислений.
- Отсутствие визуализации продукта: Решает проблему «покупки вслепую», предоставляя клиенту живой Canvas-рендер амулета с инкрустацией камней прямо по ходу квиза.
- Потеря теплых клиентов: Создает интерактивный вовлекающий ритуал (микроанимации Framer Motion, частицы), удерживающий пользователя на сайте до этапа оформления заказа.
- Автоматизация бизнес-процессов: Заменяет ручной прием заявок на автоматизированное сохранение сессий в PostgreSQL (Drizzle ORM) и проведение платежей через YooKassa."""
        
        problems_en = """- Manual Destiny Matrix Calculations: Automates the complex computation of 9 destiny matrix energy nodes from birthdate inputs.
- Product Visualization Barrier: Replaces flat catalogs with a live client-side Canvas preview showing custom gemstones, shadows, and base textures.
- User Drop-off: Implements an interactive quiz with Framer Motion transitions and background particle systems to keep users highly engaged.
- Sales Operations Overhead: Streamlines order taking by persisting sessions via Drizzle ORM/PostgreSQL and handling payment validation."""
        
        features_ru = """- 🔹 Интерактивная SVG-Карта энергий: Анимированная отрисовка линий ромба судьбы с всплывающими подсказками (tooltips) по ховеру.
- 🔹 Canvas Amulet Preview Engine: Клиентский движок послойной отрисовки 3D-эффектов камней (cabochon градиенты, блики, тени, auric glow) и текстур дерева/металла.
- 🔹 FSM-Квиз на Zustand: Опросник для подбора минералов по целям и психотипу с персистентным сохранением состояния сессии в localStorage.
- 🔹 Управление уровнями кастомизации: Поддержка 4 уровней амулетов, включая уровень IV «Эксклюзив» с личным сопровождением мастера.
- 🔹 Интеграция YooKassa и CRM: Модуль генерации ссылок на оплату, а также валидация входящих вебхуков YooKassa с проверкой сумм и статусов.
- 🔹 Админ-панель управления: Настройка видимости разделов, параметров отображения кнопок сессии, цен, полей и ручного управления заказами."""
        
        features_en = """- 🔹 Interactive SVG Energy Chart: Fully animated matrix diagram with stroke drawing effects and hover tooltips for node descriptions.
- 🔹 Canvas Amulet Engine: Real-time client-side renderer of custom gemstones (cabochon gradients, highlights, auric glow) and wood/metal glazes.
- 🔹 Zustand State & FSM Quiz: Multi-step persistent questionnaire matching user goals to specific mineral catalogs.
- 🔹 Product Tier Customization: Multi-level configuration supporting up to 4 amulet tiers, including premium bespoke consultant packages.
- 🔹 YooKassa Payment Gateway: Dynamic checkout link creation, idempotent payment execution, and secure webhook validation.
- 🔹 Admin Panel & Operations: Back-office tool to manage gemstone catalogs, pricing, visibility toggles, and user sessions."""
        
        cv_ru = """- Стек: Next.js, React, TailwindCSS, TypeScript, Zustand, Drizzle ORM, YooKassa API, Gemini API
- Ключевой функционал: Разработал Canvas-движок 3D-отрисовки амулетов в реальном времени и анимированную SVG-карту энергий
- Результат: Реализован законченный цикл от расчета матрицы и квиза до онлайн-оплаты через YooKassa и отправки лидов в CRM, повысивший конверсию и вовлеченность клиентов."""
        
        cv_en = """- Stack: Next.js, React, TailwindCSS, TypeScript, Zustand, Drizzle ORM, YooKassa API, Gemini API
- Key Feature: Designed the real-time client-side Canvas amulet rendering engine and interactive SVG destiny matrix diagram
- Result: Implemented an end-to-end checkout flow from birthdate calculation to YooKassa payment integration, automating lead acquisition and boosting user engagement."""
    else:
        brief_ru = description
        brief_en = "Production-ready application for portfolio presentation and practical use."
        
        problems_ru = """- Рутина и ручные операции: Автоматизирует однотипные действия по администрированию и настройке проекта.
- Скорость процессов: Оптимизирует скорость загрузки страниц и обработки запросов.
- Сохранность данных: Обеспечивает надежное хранение информации и транзакций."""
        
        problems_en = """- Manual overhead & routine: Automates repetitive tasks for project configuration and administration.
- Process latency: Optimizes loading speeds and query responsiveness.
- Data integrity: Ensures secure storage of transactions and application state."""
        
        features_ru = """- 🔹 Интерактивный интерфейс: Современный адаптивный UI.
- 🔹 Управление данными: Надежное хранение сессий и конфигураций.
- 🔹 Контейнеризация и деплой: Готовые Docker-конфигурации для быстрого развертывания."""
        
        features_en = """- 🔹 Interactive Web Interface: Modern responsive user interface.
- 🔹 Data Access layer: Secure session and configuration management.
- 🔹 Containerization: Ready-to-go Docker configurations for quick local deployment."""
        
        cv_ru = """- Стек: Python, JavaScript
- Ключевой функционал: Разработал архитектуру приложения и автоматизировал ключевые модули
- Результат: Интегрировал современные инструменты автоматизации и контейнеризации, повысив скорость развертывания проекта."""
        
        cv_en = """- Stack: Python, JavaScript
- Key Feature: Designed the application core and automated core modules
- Result: Integrated modern automation and containerization tools, improving deployment speed."""

    content = f"""# Project Portfolio Information

This file contains curated descriptions and features of the project used by `generate_docs_v3.py` to generate the final bilingual portfolios. Do not delete the headings.

## Brief Description (RU)
{brief_ru}

## Brief Description (EN)
{brief_en}

## Problems Solved (RU)
{problems_ru}

## Problems Solved (EN)
{problems_en}

## Key Features (RU)
{features_ru}

## Key Features (EN)
{features_en}

## CV Resume Bullet (RU)
{cv_ru}

## CV Resume Bullet (EN)
{cv_en}
"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")


# ============================================================
# 📄 ГЕНЕРАЦИЯ ЧЕЛОВЕКОЧИТАЕМЫХ ОПИСАНИЙ (RU / EN)
# ============================================================
def generate_project_description_ru(
    project_name: str,
    description: str,
    packages: List[str],
    tech_stack: Dict[str, List[str]],
    js_tech_stack: Dict[str, List[str]],
    metrics: Dict[str, Any],
    ci_badge_str: str = ""
) -> str:
    """Генерирует готовый PROJECT_DESCRIPTION_RU.md без заглушек, используя разбор файлов."""
    parsed_markdown = extract_sections_from_markdown()
    
    info_path = Path("docPRO/PROJECT_INFO.md")
    if not info_path.exists():
        create_project_info_template(info_path, project_name, description, packages, tech_stack, js_tech_stack)
    info = parse_project_info_file(info_path)
    
    # Краткое описание
    brief_desc = info["ru_brief"] if info["ru_brief"] else (parsed_markdown["ru"]["brief_description"] if parsed_markdown["ru"]["brief_description"] else description)

    # Объединенный стек
    combined_tech = {}
    combined_tech.update(tech_stack)
    combined_tech.update(js_tech_stack)
    
    tech_stack_md = ""
    for category in ["Web / API", "Frontend / UI", "ORM / Database", "Базы данных", "API / State", "Инфраструктура", "Тесты / качество", "Тесты / качество (JS)", "Данные / ML", "AI / LLM"]:
        if category in combined_tech and combined_tech[category]:
            tech_stack_md += f"- **{category}:** {', '.join(combined_tech[category])}\n"
    if not tech_stack_md:
        all_pkgs = packages + [val for sublist in js_tech_stack.values() for val in sublist]
        tech_stack_md = f"- **Стек:** {', '.join(all_pkgs) if all_pkgs else 'Python/JS'}\n"

    # Раздел проблем
    problems_md = ""
    if info["ru_problems"]:
        for p in info["ru_problems"]:
            problems_md += f"- {p}\n"
    elif parsed_markdown["ru"]["problems"]:
        for p in parsed_markdown["ru"]["problems"][:4]:
            problems_md += f"- {p}\n"
    else:
        problems_md = f"""- **Рутина и ручные операции:** Автоматизирует однотипные действия по администрированию и настройке проекта.
- **Скорость процессов:** Оптимизирует скорость загрузки страниц и обработки запросов за счет современного стека ({', '.join(combined_tech.get('Frontend / UI', ['Next.js']))}).
- **Сохранность данных:** Обеспечивает надежное хранение информации и транзакций с помощью СУБД ({', '.join(combined_tech.get('Базы данных', ['PostgreSQL']))}).
"""

    # Раздел фич
    features_md = ""
    if info["ru_features"]:
        for f in info["ru_features"]:
            prefix = "🔹 " if not f.startswith("🔹") else ""
            features_md += f"- {prefix}{f}\n"
    elif parsed_markdown["ru"]["features"]:
        for f in parsed_markdown["ru"]["features"][:6]:
            prefix = "🔹 " if not f.startswith("🔹") else ""
            features_md += f"- {prefix}{f}\n"
    else:
        features_md = f"""- 🔹 **Интерактивный интерфейс:** Современный адаптивный UI с использованием {', '.join(combined_tech.get('Frontend / UI', ['React/Next.js']))}.
- 🔹 **Управление данными:** Надежное хранение сессий и конфигураций в {', '.join(combined_tech.get('ORM / Database', ['Drizzle ORM']))}.
- 🔹 **Контейнеризация и деплой:** Готовые Docker-конфигурации для быстрого развертывания.
- 🔹 **Качество кода:** Полноценное покрытие тестами и статический анализ с использованием Pytest/ESLint.
"""

    git_url = "https://github.com/username/project"
    repo_info = get_git_repo_info()
    if repo_info:
        git_url = f"https://github.com/{repo_info['owner']}/{repo_info['repo']}"
        
    folder_name = Path.cwd().name

    badges = [
        "![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)",
        "![License](https://img.shields.io/badge/License-MIT-green)",
        "![Status](https://img.shields.io/badge/Status-Active-success)"
    ]
    if ci_badge_str:
        badges.append(ci_badge_str)
    badges_md = " ".join(badges)

    # Метрики на русском
    metrics_ru_list = []
    if metrics["py_files"] > 0:
        metrics_ru_list.append(f"- **Python-файлов:** {metrics['py_files']}")
        metrics_ru_list.append(f"- **Строк кода (Python):** {metrics['py_loc']} (чистый код без комментов и пустых строк)")
        metrics_ru_list.append(f"- **Функций (Python):** {metrics['py_funcs']}")
        metrics_ru_list.append(f"- **Классов (Python):** {metrics['py_classes']}")
    if metrics["ts_files"] > 0:
        metrics_ru_list.append(f"- **TypeScript-файлов:** {metrics['ts_files']}")
        metrics_ru_list.append(f"- **Строк кода (TypeScript/TSX):** {metrics['ts_loc']} (чистый код)")
    if metrics["js_files"] > 0:
        metrics_ru_list.append(f"- **JavaScript-файлов:** {metrics['js_files']}")
        metrics_ru_list.append(f"- **Строк кода (JavaScript):** {metrics['js_loc']} (чистый код)")
        
    metrics_ru_list.append(f"- **Покрытие тестами:** {'есть' if metrics['has_tests'] else 'нет'}")
    metrics_ru_list.append(f"- **CI/CD:** {'есть (GitHub Actions)' if metrics['has_cicd'] else 'нет'}")
    metrics_ru_list.append(f"- **Контейнеризация:** {'есть (Docker)' if metrics['has_docker'] else 'нет'}")
    metrics_ru_list.append(f"- **Соответствие стандартам (PEP 621):** {'есть (pyproject.toml)' if metrics['has_pyproject'] else 'нет'}")
    
    metrics_ru_md = "\n".join(metrics_ru_list)

    all_libs = packages + [val for sublist in js_tech_stack.values() for val in sublist]
    if info["ru_cv_stack"]:
        stack_inline = info["ru_cv_stack"]
    else:
        stack_inline = ", ".join(all_libs[:6]) if all_libs else "Python/JS"

    # Запуск
    launch_commands = ""
    if metrics["has_package_json"]:
        launch_commands = """# Установите зависимости npm
npm install

# Запустите проект в режиме разработки
npm run dev"""
    else:
        launch_commands = """# Создайте виртуальное окружение и активируйте его
python -m venv .venv
source .venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Запустите проект
python main.py"""

    # Резюме PSR
    psr_problem = info["ru_problems"][0] if info["ru_problems"] else (parsed_markdown["ru"]["problems"][0] if parsed_markdown["ru"]["problems"] else "Необходимость автоматизации рутинных бизнес-процессов и оптимизации обработки данных.")
    psr_solution = info["ru_brief"] if info["ru_brief"] else f"Разработал масштабируемое веб-приложение / API с использованием {stack_inline}."
    psr_result = info["ru_cv_result"] if info["ru_cv_result"] else "Автоматизирован ключевой функционал, минимизировано время выполнения процессов, обеспечена стабильность кодовой базы."
    cv_feature = info["ru_cv_feature"] if info["ru_cv_feature"] else (parsed_markdown["ru"]["features"][0] if parsed_markdown["ru"]["features"] else f"Разработал архитектуру приложения на {stack_inline}")

    content = f"""# 🚀 {project_name}
 
 > {brief_desc}
 
 {badges_md}
 
 ---
 
 ## 📝 Краткое описание (для резюме)
 **Проблема (Problem):** {psr_problem}
 **Решение (Solution):** {psr_solution}
 **Результат (Result):** {psr_result}
 
 ## 🎯 Какую проблему решает
 {problems_md}
 ## ✨ Ключевой функционал
 {features_md}
 ## 🛠 Технологический стек
 {tech_stack_md}
 ## 📊 Метрики проекта
 {metrics_ru_md}
 
 ## 🚀 Быстрый старт
 
 ```bash
 # Клонируйте репозиторий
 git clone {git_url}
 
 # Перейдите в папку проекта
 cd {folder_name}
 
 {launch_commands}
 ```
 
 ## 📌 Для вставки в резюме (короткая версия)
 
 **{project_name}**
 - **Стек:** {stack_inline}
 - **Ключевой функционал:** {cv_feature}
 - **Результат:** {psr_result} (Сделал X, измеренный Y, сделав Z)
 """
    return content


def generate_project_description_en(
    project_name: str,
    description: str,
    packages: List[str],
    tech_stack: Dict[str, List[str]],
    js_tech_stack: Dict[str, List[str]],
    metrics: Dict[str, Any],
    ci_badge_str: str = ""
) -> str:
    """Генерирует готовый PROJECT_DESCRIPTION_EN.md без заглушек, используя разбор файлов."""
    parsed_markdown = extract_sections_from_markdown()
    
    info_path = Path("docPRO/PROJECT_INFO.md")
    if not info_path.exists():
        create_project_info_template(info_path, project_name, description, packages, tech_stack, js_tech_stack)
    info = parse_project_info_file(info_path)
    
    # Краткое описание
    brief_desc = info["en_brief"] if info["en_brief"] else (parsed_markdown["en"]["brief_description"] if parsed_markdown["en"]["brief_description"] else description)
    if not brief_desc or brief_desc.startswith("Production-ready Python project"):
        brief_desc = "Production-ready application for portfolio presentation and practical use."

    # Объединенный стек
    combined_tech = {}
    combined_tech.update(tech_stack)
    combined_tech.update(js_tech_stack)
    
    tech_stack_md = ""
    for category in ["Web / API", "Frontend / UI", "ORM / Database", "Базы данных", "API / State", "Инфраструктура", "Тесты / качество", "Тесты / качество (JS)", "Данные / ML", "AI / LLM"]:
        if category in combined_tech and combined_tech[category]:
            tech_stack_md += f"- **{category}:** {', '.join(combined_tech[category])}\n"
    if not tech_stack_md:
        all_pkgs = packages + [val for sublist in js_tech_stack.values() for val in sublist]
        tech_stack_md = f"- **Stack:** {', '.join(all_pkgs) if all_pkgs else 'Python/JS'}\n"

    # Раздел проблем (EN)
    problems_md = ""
    if info["en_problems"]:
        for p in info["en_problems"]:
            problems_md += f"- {p}\n"
    elif parsed_markdown["en"]["problems"]:
        for p in parsed_markdown["en"]["problems"][:4]:
            problems_md += f"- {p}\n"
    else:
        problems_md = f"""- **Manual overhead & routine:** Automates repetitive tasks for project configuration and administration.
- **Process latency:** Optimizes loading speeds and query responsiveness using a modern stack ({', '.join(combined_tech.get('Frontend / UI', ['Next.js']))}).
- **Data integrity:** Ensures secure storage of transactions and application state via DBMS ({', '.join(combined_tech.get('Базы данных', ['PostgreSQL']))}).
"""

    # Раздел фич (EN)
    features_md = ""
    if info["en_features"]:
        for f in info["en_features"]:
            prefix = "🔹 " if not f.startswith("🔹") else ""
            features_md += f"- {prefix}{f}\n"
    elif parsed_markdown["en"]["features"]:
        for f in parsed_markdown["en"]["features"][:6]:
            prefix = "🔹 " if not f.startswith("🔹") else ""
            features_md += f"- {prefix}{f}\n"
    else:
        features_md = f"""- 🔹 **Interactive Web Interface:** Modern responsive user interface built using {', '.join(combined_tech.get('Frontend / UI', ['React/Next.js']))}.
- 🔹 **Data Access layer:** Secure session and configuration management via {', '.join(combined_tech.get('ORM / Database', ['Drizzle ORM']))}.
- 🔹 **Containerization:** Ready-to-go Docker configurations for quick local deployment.
- 🔹 **Quality Assurance:** Unit test coverage and static analysis with Pytest/ESLint.
"""

    git_url = "https://github.com/username/project"
    repo_info = get_git_repo_info()
    if repo_info:
        git_url = f"https://github.com/{repo_info['owner']}/{repo_info['repo']}"
        
    folder_name = Path.cwd().name

    badges = [
        "![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)",
        "![License](https://img.shields.io/badge/License-MIT-green)",
        "![Status](https://img.shields.io/badge/Status-Active-success)"
    ]
    if ci_badge_str:
        badges.append(ci_badge_str)
    badges_md = " ".join(badges)

    # Метрики на английском
    metrics_en_list = []
    if metrics["py_files"] > 0:
        metrics_en_list.append(f"- **Python files:** {metrics['py_files']}")
        metrics_en_list.append(f"- **Lines of code (Python):** {metrics['py_loc']} (clean code without comments & blank lines)")
        metrics_en_list.append(f"- **Functions (Python):** {metrics['py_funcs']}")
        metrics_en_list.append(f"- **Classes (Python):** {metrics['py_classes']}")
    if metrics["ts_files"] > 0:
        metrics_en_list.append(f"- **TypeScript files:** {metrics['ts_files']}")
        metrics_en_list.append(f"- **Lines of code (TypeScript/TSX):** {metrics['ts_loc']} (clean code)")
    if metrics["js_files"] > 0:
        metrics_en_list.append(f"- **JavaScript files:** {metrics['js_files']}")
        metrics_en_list.append(f"- **Lines of code (JavaScript):** {metrics['js_loc']} (clean code)")
        
    metrics_en_list.append(f"- **Unit Tests:** {'Available' if metrics['has_tests'] else 'None'}")
    metrics_en_list.append(f"- **CI/CD:** {'Configured (GitHub Actions)' if metrics['has_cicd'] else 'None'}")
    metrics_en_list.append(f"- **Containerization:** {'Available (Docker)' if metrics['has_docker'] else 'None'}")
    metrics_en_list.append(f"- **PEP 621 Compliance:** {'Yes (pyproject.toml)' if metrics['has_pyproject'] else 'No'}")
    
    metrics_en_md = "\n".join(metrics_en_list)

    all_libs = packages + [val for sublist in js_tech_stack.values() for val in sublist]
    if info["en_cv_stack"]:
        stack_inline = info["en_cv_stack"]
    else:
        stack_inline = ", ".join(all_libs[:6]) if all_libs else "Python/JS"

    # Запуск
    launch_commands = ""
    if metrics["has_package_json"]:
        launch_commands = """# Install npm dependencies
npm install

# Run the development server
npm run dev"""
    else:
        launch_commands = """# Create virtual environment and activate
python -m venv .venv
source .venv/bin/activate

# Install pip packages
pip install -r requirements.txt

# Run main script
python main.py"""

    # Резюме PSR (EN)
    psr_problem = info["en_problems"][0] if info["en_problems"] else (parsed_markdown["en"]["problems"][0] if parsed_markdown["en"]["problems"] else "Need for automation of manual tasks and data processing bottlenecks.")
    psr_solution = info["en_brief"] if info["en_brief"] else f"Developed a scalable web app / API layer using {stack_inline}."
    psr_result = info["en_cv_result"] if info["en_cv_result"] else "Automated core workflows, minimized processing delay, and improved pipeline reliability."
    cv_feature = info["en_cv_feature"] if info["en_cv_feature"] else (parsed_markdown["en"]["features"][0] if parsed_markdown["en"]["features"] else f"Designed the application core using {stack_inline}")

    content = f"""# 🚀 {project_name}
 
 > {brief_desc}
 
 {badges_md}
 
 ---
 
 ## 📝 Brief Description (for CV/Resume)
 **Problem:** {psr_problem}
 **Solution:** {psr_solution}
 **Result:** {psr_result}
 
 ## 🎯 Problem It Solves
 {problems_md}
 ## ✨ Key Features
 {features_md}
 ## 🛠 Tech Stack
 {tech_stack_md}
 ## 📊 Project Metrics
 {metrics_en_md}
 
 ## 🚀 Quick Start

```bash
# Clone the repository
git clone {git_url}

# Navigate to the project directory
cd {folder_name}

{launch_commands}
```

## 📌 Resume Snippet (Short Version)

**{project_name}**
- **Stack:** {stack_inline}
- **Key Feature:** {cv_feature}
- **Result:** Implemented containerization and automated workflows, improving deployment speed and system stability. (Accomplished X, measured by Y, by doing Z)
"""
    return content


# ============================================================
# 🛠️ УТИЛИТЫ И БЕЗОПАСНЫЙ ПОИСК
# ============================================================
def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def get_safe_output_path(base_path: Path) -> Path:
    """Защита от перезаписи: предлагает версию с суффиксом или перезаписывает по выбору."""
    if not base_path.exists():
        return base_path
    
    if sys.stdin.isatty():
        try:
            answer = input(f"⚠️ Файл '{base_path.name}' уже существует. Перезаписать? [y/N]: ").strip().lower()
            if answer in ('y', 'yes'):
                return base_path
        except (KeyboardInterrupt, EOFError):
            print("\n[info] Отменено пользователем. Создаём файл с суффиксом...")
            
    # Если запущен не в TTY или пользователь отказался
    parent = base_path.parent
    stem = base_path.stem
    ext = base_path.suffix
    counter = 2
    while True:
        new_path = parent / f"{stem}_v{counter}{ext}"
        if not new_path.exists():
            return new_path
        counter += 1


def find_obsidian_vaults(roots: List[Path]) -> List[Path]:
    """Быстрый поиск хранилищ Obsidian (с ограничением глубины для безопасности)."""
    vaults = []
    skip_dirs = {
        "Library", "Applications", "System", "Downloads", "Desktop", "Pictures", "Music", "Movies",
        "venv", ".venv", ".git", "node_modules", "Cache", "caches", "Local/State", "shared", "Containers",
        "Group Containers", "Saved Application State", "CloudStorage"
    }
    for root in roots:
        if not root.exists() or not root.is_dir():
            continue
        if (root / ".obsidian").is_dir():
            vaults.append(root)
            continue
        
        try:
            for p1 in root.iterdir():
                try:
                    if p1.name.startswith(".") or not p1.is_dir() or p1.name in skip_dirs:
                        continue
                    if (p1 / ".obsidian").is_dir():
                        vaults.append(p1)
                        continue
                    # Level 2 scan
                    for p2 in p1.iterdir():
                        try:
                            if p2.name.startswith(".") or not p2.is_dir() or p2.name in skip_dirs:
                                continue
                            if (p2 / ".obsidian").is_dir():
                                vaults.append(p2)
                        except OSError:
                            pass
                except OSError:
                    pass
        except OSError:
            pass
    return vaults


def find_notebooklm_folders(roots: List[Path]) -> List[Path]:
    """Быстрый поиск локальных папок NotebookLM."""
    folders = []
    for root in roots:
        if not root.exists() or not root.is_dir():
            continue
        if root.name == "NotebookLM":
            folders.append(root)
        else:
            cand = root / "NotebookLM"
            if cand.exists() and cand.is_dir():
                folders.append(cand)
    return folders


def run_radon_analysis() -> str:
    """Запускает radon (если установлен) и возвращает markdown-блок с результатами."""
    try:
        import radon  # type: ignore
    except ImportError:
        return ""
    try:
        raw_out = subprocess.check_output(
            [sys.executable, "-m", "radon", "raw", "-s", "."],
            stderr=subprocess.STDOUT,
            text=True,
        )
        cc_out = subprocess.check_output(
            [sys.executable, "-m", "radon", "cc", "-s", "-a", "."],
            stderr=subprocess.STDOUT,
            text=True,
        )
        mi_out = subprocess.check_output(
            [sys.executable, "-m", "radon", "mi", "-s", "."],
            stderr=subprocess.STDOUT,
            text=True,
        )
    except Exception as e:
        return f"\n> ⚠️ Не удалось выполнить анализ сложности: {e}\n"

    md = "\n## Code Complexity (via Radon)\n\n"
    md += "<details><summary>Raw metrics</summary>\n\n```\n"
    md += raw_out.strip() + "\n```\n</details>\n\n"
    md += "<details><summary>Cyclomatic Complexity</summary>\n\n```\n"
    md += cc_out.strip() + "\n```\n</details>\n\n"
    md += "<details><summary>Maintainability Index</summary>\n\n```\n"
    md += mi_out.strip() + "\n```\n</details>\n"
    return md


def archive_generated_docs(docs_dir: Path):
    archive_root = docs_dir / "archive"
    archive_root.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_archive_dir = archive_root / timestamp
    run_archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Копируем RU папку
    ru_src = docs_dir / "RU"
    if ru_src.exists():
        shutil.copytree(ru_src, run_archive_dir / "RU", dirs_exist_ok=True)
        
    # Копируем EN папку
    en_src = docs_dir / "EN"
    if en_src.exists():
        shutil.copytree(en_src, run_archive_dir / "EN", dirs_exist_ok=True)
        
    # Копируем PROJECT_INFO.md
    info_src = docs_dir / "PROJECT_INFO.md"
    if info_src.exists():
        shutil.copy(info_src, run_archive_dir / "PROJECT_INFO.md")
        
    print(f"   📦 Резервная копия создана в архиве: docPRO/archive/{timestamp}/")


# ============================================================
# 🔄 СИНХРОНИЗАЦИЯ С БАЗАМИ ЗНАНИЙ
# ============================================================
def sync_portfolio_folder(
    src_dir: Path,
    obsidian_path_arg: Optional[str] = None,
    notebooklm_path_arg: Optional[str] = None
) -> None:
    """Синхронизирует всю папку Portfolio со всеми сгенерированными файлами."""
    print("\n🔄 Синхронизация с базами знаний...")
    project_name = Path.cwd().name
    
    # 1. Поиск путей Obsidian
    obsidian_vaults = []
    if obsidian_path_arg:
        p = Path(obsidian_path_arg)
        if p.exists() and p.is_dir():
            obsidian_vaults = [p]
        else:
            print(f"   ⚠️  Указанный путь Obsidian не существует: {obsidian_path_arg}")
    else:
        obsidian_vaults = find_obsidian_vaults(DEFAULT_OBSIDIAN_SEARCH_ROOTS)

    # Синхронизация в Obsidian
    if obsidian_vaults:
        for vault in obsidian_vaults:
            dest_dir = vault / "Projects" / project_name / "Portfolio"
            try:
                # Очищаем старые файлы и папки RU/EN в Portfolio для предотвращения дублирования
                if dest_dir.exists():
                    for item in dest_dir.iterdir():
                        if item.is_dir() and item.name in ("RU", "EN"):
                            shutil.rmtree(item)
                        elif item.is_file():
                            item.unlink()
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                # Копируем RU и EN папки
                for lang in ("RU", "EN"):
                    lang_src = src_dir / lang
                    lang_dest = dest_dir / lang
                    if lang_src.exists():
                        shutil.copytree(lang_src, lang_dest)
                        
                display_path = str(dest_dir).replace(str(Path.home()), "~")
                print(f"   ✅ Obsidian: {display_path}/")
            except Exception as e:
                print(f"   ❌ Ошибка при копировании в Obsidian ({vault.name}): {e}")
    else:
        print("   ⚠️  Obsidian: не найден (пропущено)")

    # 2. Поиск путей NotebookLM
    notebooklm_folders = []
    if notebooklm_path_arg:
        p = Path(notebooklm_path_arg)
        if p.exists() and p.is_dir():
            notebooklm_folders = [p]
        else:
            print(f"   ⚠️  Указанный путь NotebookLM не существует: {notebooklm_path_arg}")
    else:
        notebooklm_folders = find_notebooklm_folders(DEFAULT_NOTEBOOKLM_SEARCH_ROOTS)

    # Синхронизация в NotebookLM
    if notebooklm_folders:
        for folder in notebooklm_folders:
            dest_dir = folder / "Projects" / project_name / "Portfolio"
            try:
                # Очищаем старые файлы и папки RU/EN в Portfolio
                if dest_dir.exists():
                    for item in dest_dir.iterdir():
                        if item.is_dir() and item.name in ("RU", "EN"):
                            shutil.rmtree(item)
                        elif item.is_file():
                            item.unlink()
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                # Копируем RU и EN папки
                for lang in ("RU", "EN"):
                    lang_src = src_dir / lang
                    lang_dest = dest_dir / lang
                    if lang_src.exists():
                        shutil.copytree(lang_src, lang_dest)
                        
                display_path = str(dest_dir).replace(str(Path.home()), "~")
                print(f"   ✅ NotebookLM: {display_path}/")
            except Exception as e:
                print(f"   ❌ Ошибка при копировании в NotebookLM ({folder.name}): {e}")
    else:
        print("   ⚠️  NotebookLM: не найден (пропущено)")


# ============================================================
# 🚀 MAIN
# ============================================================
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Генерирует файлы в docPRO/, раскладывает по RU/EN и синхронизирует с Obsidian/NotebookLM."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Перезаписать существующие PROJECT_DESCRIPTION_*.md без запроса.",
    )
    parser.add_argument(
        "--obsidian-path",
        type=str,
        help="Явный путь к хранилищу Obsidian (в обход автопоиска).",
    )
    parser.add_argument(
        "--notebooklm-path",
        type=str,
        help="Явный путь к папке NotebookLM (в обход автопоиска).",
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default=DEFAULT_DOCS_FOLDER_NAME,
        help=f"Имя технической папки с документацией (по умолчанию: {DEFAULT_DOCS_FOLDER_NAME}).",
    )
    parser.add_argument(
        "--ci-badge",
        action="store_true",
        default=True,
        help="Добавить badge состояния GitHub Actions в описание.",
    )
    parser.add_argument(
        "--complexity",
        action="store_true",
        help="Запустить анализ сложности кода с помощью radon (если установлен).",
    )
    args = parser.parse_args()

    print("🔍 Анализирую проект...")
    project_name = get_project_name()
    description = extract_description()
    en_description = description
    if any(c in description for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"):
        if "aethel" in project_name.lower():
            en_description = "Interactive web application (SPA) for calculating the Energy Chart (Matrix of Destiny) by date of birth and crafting personal amulets in real-time."
        else:
            en_description = "Production-ready application for portfolio presentation and practical use."
    dependencies = detect_dependencies()
    tech_stack = detect_tech_stack(dependencies)
    js_tech_stack = detect_js_dependencies()
    metrics = collect_metrics()

    # Сводная информация
    total_py_files = metrics["py_files"]
    total_js_ts_files = metrics["js_files"] + metrics["ts_files"]
    print(f"   📁 Найдено {total_py_files} Python-файлов и {total_js_ts_files} JS/TS-файлов")
    print(f"   📦 Обнаружено {len(dependencies)} сторонних Python-зависимостей")
    
    # Объединенный стек для консоли
    all_stack = []
    for cat, list_vals in tech_stack.items():
        all_stack.extend(list_vals)
    for cat, list_vals in js_tech_stack.items():
        all_stack.extend(list_vals)
    print(f"   🧠 Стек: {', '.join(all_stack) if all_stack else 'Python/JS'}")

    # Удаляем старые файлы описаний в корне проекта
    for root_file in ["PROJECT_DESCRIPTION.md", "PROJECT_DESCRIPTION_RU.md", "PROJECT_DESCRIPTION_EN.md"]:
        f_path = Path.cwd() / root_file
        if f_path.exists():
            try:
                f_path.unlink()
                print(f"   🗑️ Устаревший {root_file} удален из корня")
            except Exception:
                pass

    # Создаем языковые поддиректории в docPRO
    docs_dir = Path.cwd() / args.docs_dir
    ru_docs_dir = docs_dir / "RU"
    en_docs_dir = docs_dir / "EN"
    
    # Удаляем и пересоздаем структуру, чтобы не копить старые дубли
    if docs_dir.exists():
        shutil.rmtree(docs_dir)
    ru_docs_dir.mkdir(parents=True, exist_ok=True)
    en_docs_dir.mkdir(parents=True, exist_ok=True)

    ci_badge_str = ""
    if args.ci_badge:
        repo_info = get_git_repo_info()
        ci_badge_str = ci_badge_markdown(repo_info)

    # Генерация контента описаний
    desc_ru_content = generate_project_description_ru(
        project_name,
        description,
        dependencies,
        tech_stack,
        js_tech_stack,
        metrics,
        ci_badge_str=ci_badge_str
    )
    desc_en_content = generate_project_description_en(
        project_name,
        en_description,
        dependencies,
        tech_stack,
        js_tech_stack,
        metrics,
        ci_badge_str=ci_badge_str
    )

    # Создание файлов в docPRO/RU/ (все файлы строго на русском)
    write_text_file(ru_docs_dir / "PROJECT_DESCRIPTION.md", desc_ru_content)
    write_text_file(
        ru_docs_dir / "READMEPro.md",
        gen_readme_pro_ru(project_name, description, all_stack, dependencies, ci_badge=ci_badge_str)
    )
    complexity_md = run_radon_analysis() if args.complexity else ""
    write_text_file(
        ru_docs_dir / "SUMMARY.md",
        gen_summary_md_ru(project_name, description, scan_imports(), dependencies, all_stack, complexity_md)
    )

    # Создание файлов в docPRO/EN/ (все файлы строго на английском)
    write_text_file(en_docs_dir / "PROJECT_DESCRIPTION.md", desc_en_content)
    write_text_file(
        en_docs_dir / "READMEPro.md",
        gen_readme_pro(project_name, en_description, all_stack, dependencies, ci_badge=ci_badge_str)
    )
    write_text_file(
        en_docs_dir / "SUMMARY.md",
        gen_summary_md(project_name, en_description, scan_imports(), dependencies, all_stack, complexity_md)
    )
    write_text_file(en_docs_dir / "pyproject.toml", gen_pyproject_toml(project_name, en_description, dependencies))
    write_text_file(en_docs_dir / "setup.py", gen_setup_py())
    write_text_file(en_docs_dir / "setup.cfg", gen_setup_cfg(project_name, en_description))
    write_text_file(en_docs_dir / "requirements.txt", gen_requirements(dependencies))
    
    print(f"   ✅ Технические и продающие файлы распределены по папкам {args.docs_dir}/RU и {args.docs_dir}/EN")

    # Создаем резервную архивную копию
    archive_generated_docs(docs_dir)

    # Синхронизация всей папки Portfolio
    sync_portfolio_folder(
        docs_dir,
        obsidian_path_arg=args.obsidian_path,
        notebooklm_path_arg=args.notebooklm_path
    )

    # Опционально: перезапись файлов в корне, если указан флаг --overwrite
    if args.overwrite:
        print("\n[info] Обновление основных файлов в корне проекта...")
        root_files = {
            "pyproject.toml": en_docs_dir / "pyproject.toml",
            "setup.py": en_docs_dir / "setup.py",
            "setup.cfg": en_docs_dir / "setup.cfg",
        }
        for target_name, source_path in root_files.items():
            target_path = Path.cwd() / target_name
            write_text_file(target_path, source_path.read_text(encoding="utf-8"))
            
        req_target = Path.cwd() / "requirements.txt"
        if not req_target.exists():
            write_text_file(req_target, (en_docs_dir / "requirements.txt").read_text(encoding="utf-8"))
        else:
            print("   ⚠️  Существующий requirements.txt в корне не был изменён.")
        print("   ✅ Файлы в корне проекта обновлены.")

    print("\n🎉 Готово! Описания и документация проекта реорганизованы по языковым папкам и синхронизированы.")
    return 0


if __name__ == "__main__":
    sys.exit(main())