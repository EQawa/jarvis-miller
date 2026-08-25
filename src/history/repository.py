from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py",
}


IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "site-packages",
}


@dataclass
class Function:
    function_header: str
    function_body: str
    function_summary: str | None = None


@dataclass
class Class:
    class_name: str
    class_methods: list[Function] = field(default_factory=list)
    class_summary: str | None = None


@dataclass
class File:
    file_path: Path
    file_imports: str = ""
    file_classes: list[Class] = field(default_factory=list)
    functions: list[Function] = field(default_factory=list)
    file_summary: str | None = None

    def __post_init__(self):
        if self.file_path.suffix == ".py":
            self._parse_python()

    def _parse_python(self):
        try:
            source = self.file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(self.file_path))
        except (OSError, UnicodeDecodeError, SyntaxError):
            return

        self.file_imports = self._extract_imports(tree)

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.functions.append(
                    self._create_function(node, source)
                )

            elif isinstance(node, ast.ClassDef):
                self.file_classes.append(
                    self._create_class(node, source)
                )

    def _extract_imports(self, tree: ast.Module) -> str:
        imports = []

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node))

        return "\n".join(imports)

    def _create_class(
        self,
        node: ast.ClassDef,
        source: str
    ) -> Class:
        class_methods = []

        for child in node.body:
            if isinstance(
                child,
                (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                class_methods.append(
                    self._create_function(child, source)
                )

        return Class(
            class_name=node.name,
            class_methods=class_methods
        )

    def _create_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        source: str
    ) -> Function:
        lines = source.splitlines()

        start = node.lineno - 1
        end = node.end_lineno

        function_body = "\n".join(lines[start:end])

        return Function(
            function_header=lines[start],
            function_body=function_body
        )


@dataclass
class Folder:
    folder_path: Path
    files: list[File] = field(default_factory=list)
    folders: list[Folder] = field(default_factory=list)
    folder_summary: str | None = None

    def __post_init__(self):
        self._parse()

    def _parse(self):
        if not self.folder_path.exists():
            return

        for path in sorted(self.folder_path.iterdir()):
            if path.is_dir():
                if path.name in IGNORED_DIRECTORIES:
                    continue

                if path.name.startswith("."):
                    continue

                self.folders.append(
                    Folder(path)
                )

            elif path.is_file():
                if path.suffix not in SUPPORTED_EXTENSIONS:
                    continue

                self.files.append(
                    File(path)
                )


class Repository:
    def __init__(self, repository_path: Path | str):
        self.repository_path = Path(repository_path).resolve()

        self.files: list[File] = []
        self.folders: list[Folder] = []

        self.repository_summary: str | None = None

        self._parse()

    def _parse(self):
        if not self.repository_path.exists():
            raise FileNotFoundError(
                f"Repository does not exist: {self.repository_path}"
            )

        if not self.repository_path.is_dir():
            raise NotADirectoryError(
                f"Repository path is not a directory: "
                f"{self.repository_path}"
            )

        for path in sorted(self.repository_path.iterdir()):
            if path.is_dir():
                if path.name in IGNORED_DIRECTORIES:
                    continue

                if path.name.startswith("."):
                    continue

                self.folders.append(Folder(path))

            elif path.is_file():
                if path.suffix not in SUPPORTED_EXTENSIONS:
                    continue

                self.files.append(File(path))

    def print_repo(self, functions: bool = False):
        print(self.repository_path.name)

        # Dateien direkt im Repository
        for file in self.files:
            self._print_file(
                file=file,
                prefix="├── ",
                functions=functions
            )

        # Ordner im Repository
        for index, folder in enumerate(self.folders):
            is_last = index == len(self.folders) - 1

            self._print_folder(
                folder=folder,
                prefix="",
                is_last=is_last,
                functions=functions
            )

    def _print_folder(
        self,
        folder: Folder,
        prefix: str,
        is_last: bool,
        functions: bool
    ):
        connector = "└── " if is_last else "├── "

        print(
            f"{prefix}{connector}{folder.folder_path.name}/"
        )

        child_prefix = prefix + (
            "    " if is_last else "│   "
        )

        # Dateien
        for index, file in enumerate(folder.files):
            is_last_file = (
                index == len(folder.files) - 1
                and len(folder.folders) == 0
            )

            self._print_file(
                file=file,
                prefix=child_prefix,
                connector="└── " if is_last_file else "├── ",
                functions=functions
            )

        # Unterordner
        for index, child_folder in enumerate(folder.folders):
            is_last_folder = (
                index == len(folder.folders) - 1
            )

            self._print_folder(
                folder=child_folder,
                prefix=child_prefix,
                is_last=is_last_folder,
                functions=functions
            )

    def _print_file(
        self,
        file: File,
        prefix: str,
        functions: bool,
        connector: str = "├── "
    ):
        print(
            f"{prefix}{connector}{file.file_path.name}"
        )

        if not functions:
            return

        function_prefix = prefix + "    "

        # Freie Funktionen
        for function in file.functions:
            print(
                f"{function_prefix}├── "
                f"{function.function_header}"
            )

        # Klassen und deren Methoden
        for class_index, class_ in enumerate(file.file_classes):
            is_last_class = (
                class_index == len(file.file_classes) - 1
            )

            class_connector = (
                "└── " if is_last_class else "├── "
            )

            print(
                f"{function_prefix}{class_connector}"
                f"class {class_.class_name}"
            )

            method_prefix = function_prefix + (
                "    "
            )

            for method_index, method in enumerate(
                class_.class_methods
            ):
                method_connector = (
                    "└── "
                    if method_index == len(class_.class_methods) - 1
                    else "├── "
                )

                print(
                    f"{method_prefix}{method_connector}"
                    f"{method.function_header}"
                )