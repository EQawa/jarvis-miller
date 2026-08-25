from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


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
        self._parse()

    def _parse(self):
        """Parses the Python file and extracts its structure."""

        try:
            source = self.file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, UnicodeDecodeError, SyntaxError):
            return

        self.file_imports = self._extract_imports(tree)

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                self.functions.append(
                    self._create_function(node, source)
                )

            elif isinstance(node, ast.AsyncFunctionDef):
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

        header = lines[start]

        return Function(
            function_header=header,
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
                self.folders.append(
                    Folder(path)
                )

            elif path.is_file() and path.suffix == ".py":
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

            # Git und andere versteckte Verzeichnisse ignorieren
            if path.name.startswith("."):
                continue

            if path.is_dir():
                self.folders.append(
                    Folder(path)
                )

            elif path.is_file() and path.suffix == ".py":
                self.files.append(
                    File(path)
                )