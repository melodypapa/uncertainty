#!/usr/bin/env python3
"""
ISO 29148 Requirements Extraction Tool

Extracts ISO/IEC/IEEE 29148 compliant requirements from code implementation.
Supports Python, JavaScript/TypeScript, Go, Java, and C/C++.

New features:
- Configurable output directory (default: docs/requirements)
- Automatic file splitting for large projects based on features
"""

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any


class RequirementType(Enum):
    """ISO 29148 requirement types."""
    FUNCTIONAL = "Functional"
    NON_FUNCTIONAL = "Non-Functional"
    INTERFACE = "Interface"
    DATA = "Data"


class Priority(Enum):
    """Requirement priority levels."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Status(Enum):
    """Requirement status values."""
    DRAFT = "Draft"
    APPROVED = "Approved"
    IMPLEMENTED = "Implemented"
    REJECTED = "Rejected"


@dataclass
class Requirement:
    """Represents a single ISO 29148 requirement."""
    id: str
    text: str
    type: RequirementType
    priority: Priority = Priority.MEDIUM
    status: Status = Status.DRAFT
    verification: str = ""
    parent_id: Optional[str] = None
    source: str = ""
    rationale: str = ""
    feature: Optional[str] = None  # For grouping into feature-based files


@dataclass
class ExtractionResult:
    """Results of requirements extraction."""
    requirements: List[Requirement] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    source_file: str = ""
    language: str = ""
    features: Dict[str, List[Requirement]] = field(default_factory=dict)


class LanguageDetector:
    """Detects programming language from file extension."""

    LANGUAGE_MAP = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.go': 'Go',
        '.java': 'Java',
        '.c': 'C',
        '.cpp': 'C++',
        '.h': 'C',
        '.hpp': 'C++',
    }

    @classmethod
    def detect(cls, file_path: str) -> Optional[str]:
        """Detect language from file extension."""
        ext = Path(file_path).suffix.lower()
        return cls.LANGUAGE_MAP.get(ext)


class PythonAnalyzer:
    """Analyzes Python code for requirements."""

    def __init__(self, source_file: str, detect_features: bool = False):
        self.source_file = source_file
        self.result = ExtractionResult(source_file=source_file, language='Python')
        self._req_counter = 1
        self.detect_features = detect_features

    def analyze(self) -> ExtractionResult:
        """Analyze Python code and extract requirements."""
        try:
            with open(self.source_file, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self._extract_function_requirements(node)
                elif isinstance(node, ast.ClassDef):
                    self._extract_class_requirements(node)
                elif isinstance(node, ast.Assign):
                    self._extract_constant_requirements(node)

            # Group requirements by features if enabled
            if self.detect_features:
                self._group_by_features()

        except SyntaxError as e:
            self.result.errors.append(f"Syntax error: {e}")
        except Exception as e:
            self.result.errors.append(f"Error analyzing file: {e}")

        return self.result

    def _extract_function_requirements(self, node: ast.FunctionDef) -> None:
        """Extract requirements from function definition."""
        req_id = f"REQ-{self._req_counter:03d}"
        self._req_counter += 1

        # Build requirement text from function name and docstring
        func_name = node.name
        docstring = ast.get_docstring(node) or ""
        params = [arg.arg for arg in node.args.args]

        # Remove 'self' parameter if present
        clean_params = [p for p in params if p != 'self']

        # Detect feature from function name or class context
        feature = self._detect_feature(func_name)

        # Clean up function name (remove leading underscores for private methods)
        if func_name.startswith('_'):
            clean_name = func_name.lstrip('_').replace('_', ' ')
        else:
            clean_name = func_name.replace('_', ' ')

        # Format requirement text
        if 'authenticate' in func_name.lower():
            text = f"System shall {clean_name} users"
        elif 'validate' in func_name.lower():
            text = f"System shall {clean_name} input data"
        elif 'process' in func_name.lower():
            text = f"System shall {clean_name} operations"
        elif 'get' in func_name.lower() or 'fetch' in func_name.lower():
            text = f"System shall {clean_name} data"
        else:
            text = f"System shall {clean_name}"

        # Add parameters if present
        if clean_params:
            text += f" using {', '.join(clean_params[:3])}"

        # Determine priority based on naming
        priority = self._infer_priority(func_name)

        # Create verification criteria
        verification = self._create_verification_criteria(func_name, clean_params)

        requirement = Requirement(
            id=req_id,
            text=text,
            type=RequirementType.FUNCTIONAL,
            priority=priority,
            verification=verification,
            source=f"{self.source_file}:{func_name}",
            rationale=docstring.split('\n')[0] if docstring else "",
            feature=feature
        )

        self.result.requirements.append(requirement)

    def _extract_class_requirements(self, node: ast.ClassDef) -> None:
        """Extract requirements from class definition."""
        class_name = node.name
        feature = self._detect_feature(class_name)

        # Check for authentication/security-related classes
        if 'auth' in class_name.lower() or 'security' in class_name.lower():
            req_id = f"REQ-{self._req_counter:03d}"
            self._req_counter += 1

            requirement = Requirement(
                id=req_id,
                text=f"System shall provide {class_name.replace('_', ' ')} functionality",
                type=RequirementType.FUNCTIONAL,
                priority=Priority.HIGH,
                verification=f"Verify {class_name} class is properly instantiated and functional",
                source=f"{self.source_file}:{class_name}",
                rationale=f"Core {class_name.lower()} component",
                feature=feature
            )
            self.result.requirements.append(requirement)

    def _extract_constant_requirements(self, node: ast.Assign) -> None:
        """Extract non-functional requirements from constants."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id.lower()
                feature = self._detect_feature(name)

                # Security constants
                if 'max_attempt' in name or 'threshold' in name:
                    req_id = f"REQ-{self._req_counter:03d}"
                    self._req_counter += 1

                    # Try to extract constant value
                    value = "specified limit"
                    if isinstance(node.value, ast.Constant):
                        value = str(node.value.value)

                    requirement = Requirement(
                        id=req_id,
                        text=f"System shall limit {name.replace('_', ' ')} to {value}",
                        type=RequirementType.NON_FUNCTIONAL,
                        priority=Priority.HIGH,
                        verification=f"Verify operation fails after {value} attempts",
                        source=f"{self.source_file}:{target.id}",
                        rationale="Security threshold",
                        feature=feature
                    )
                    self.result.requirements.append(requirement)

    def _detect_feature(self, name: str) -> Optional[str]:
        """Detect feature area from class/function/constant name."""
        name_lower = name.lower()

        # Feature detection patterns
        feature_patterns = {
            'authentication': ['auth', 'login', 'password', 'credential', 'session', 'token'],
            'user-management': ['user', 'profile', 'account', 'registration'],
            'data-storage': ['storage', 'database', 'db', 'persist', 'save', 'load'],
            'api': ['api', 'endpoint', 'route', 'request', 'response'],
            'messaging': ['message', 'notification', 'email', 'sms', 'alert'],
            'search': ['search', 'query', 'filter', 'find'],
            'analytics': ['analytics', 'metric', 'report', 'stat'],
            'security': ['security', 'permission', 'role', 'access'],
            'validation': ['validate', 'verify', 'check'],
        }

        for feature, patterns in feature_patterns.items():
            if any(pattern in name_lower for pattern in patterns):
                return feature

        return None

    def _group_by_features(self) -> None:
        """Group requirements by detected features."""
        self.result.features = {'general': []}

        for req in self.result.requirements:
            if req.feature:
                if req.feature not in self.result.features:
                    self.result.features[req.feature] = []
                self.result.features[req.feature].append(req)
            else:
                self.result.features['general'].append(req)

    def _infer_priority(self, func_name: str) -> Priority:
        """Infer priority from function name patterns."""
        name_lower = func_name.lower()

        if any(word in name_lower for word in ['authenticate', 'login', 'security', 'password']):
            return Priority.CRITICAL
        elif any(word in name_lower for word in ['validate', 'check', 'verify', 'save', 'delete']):
            return Priority.HIGH
        elif any(word in name_lower for word in ['log', 'track', 'monitor']):
            return Priority.MEDIUM
        else:
            return Priority.LOW

    def _create_verification_criteria(self, func_name: str, params: List[str]) -> str:
        """Create verification criteria for a function."""
        name_lower = func_name.lower()

        if 'authenticate' in name_lower:
            return "Verify successful authentication with valid credentials"
        elif 'validate' in name_lower:
            return "Verify validation accepts valid input and rejects invalid input"
        elif 'get' in name_lower or 'fetch' in name_lower:
            return "Verify data retrieval returns expected results"
        else:
            return f"Verify {func_name} executes correctly with expected inputs"


class RequirementsFormatter:
    """Formats extracted requirements for output."""

    @staticmethod
    def to_markdown(result: ExtractionResult) -> str:
        """Format requirements as Markdown."""
        lines = [
            "# Software Requirements Specification",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Source:** {result.source_file}",
            f"**Language:** {result.language}",
            "",
        ]

        # Group by type
        by_type: Dict[str, List[Requirement]] = {
            "Functional": [],
            "Non-Functional": [],
            "Interface": [],
            "Data": []
        }

        for req in result.requirements:
            by_type[req.type.value].append(req)

        # Output each section
        for type_name, requirements in by_type.items():
            if requirements:
                lines.append(f"## {type_name} Requirements")
                lines.append("")

                for req in requirements:
                    lines.append(f"### {req.id}: {req.text}")
                    lines.append(f"**Type:** {req.type.value}")
                    lines.append(f"**Priority:** {req.priority.value}")
                    lines.append(f"**Status:** {req.status.value}")
                    lines.append("")
                    lines.append("**Description:** " + req.text)
                    lines.append("")
                    lines.append(f"**Verification:** {req.verification}")
                    lines.append("")
                    lines.append(f"**Source:** {req.source}")
                    if req.rationale:
                        lines.append(f"**Rationale:** {req.rationale}")
                    lines.append("")
                    lines.append("---")
                    lines.append("")

        return "\n".join(lines)

    @staticmethod
    def to_markdown_multi(result: ExtractionResult) -> Dict[str, str]:
        """Format requirements as multiple Markdown files by feature."""
        files = {}

        # Create index file
        index_lines = [
            "# Software Requirements Specification",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Source:** {result.source_file}",
            f"**Language:** {result.language}",
            "",
            "## Document Index",
            "",
            "This specification is organized into the following feature-based documents:",
            "",
        ]

        for feature, requirements in result.features.items():
            filename = f"{feature.lower().replace('-', '_')}_requirements.md"
            index_lines.append(f"- [{feature.replace('-', ' ').title()} Requirements]({filename}) ({len(requirements)} requirements)")

        index_lines.append("")
        index_lines.append("---")
        index_lines.append("")
        index_lines.append("## Summary Statistics")
        index_lines.append("")
        index_lines.append(f"- Total requirements: {len(result.requirements)}")
        for feature, reqs in result.features.items():
            index_lines.append(f"- {feature.replace('-', ' ').title()}: {len(reqs)} requirements")

        files["index.md"] = "\n".join(index_lines)

        # Create feature-specific files
        for feature, requirements in result.features.items():
            filename = f"{feature.lower().replace('-', '_')}_requirements.md"

            lines = [
                f"# {feature.replace('-', ' ').title()} Requirements",
                "",
                f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"**Source:** {result.source_file}",
                f"**Feature:** {feature}",
                f"**Language:** {result.language}",
                "",
            ]

            # Group by type within feature
            by_type: Dict[str, List[Requirement]] = {
                "Functional": [],
                "Non-Functional": [],
                "Interface": [],
                "Data": []
            }

            for req in requirements:
                by_type[req.type.value].append(req)

            # Output each section
            for type_name, type_requirements in by_type.items():
                if type_requirements:
                    lines.append(f"## {type_name} Requirements")
                    lines.append("")

                    for req in type_requirements:
                        lines.append(f"### {req.id}: {req.text}")
                        lines.append(f"**Type:** {req.type.value}")
                        lines.append(f"**Priority:** {req.priority.value}")
                        lines.append(f"**Status:** {req.status.value}")
                        lines.append("")
                        lines.append("**Description:** " + req.text)
                        lines.append("")
                        lines.append(f"**Verification:** {req.verification}")
                        lines.append("")
                        lines.append(f"**Source:** {req.source}")
                        if req.rationale:
                            lines.append(f"**Rationale:** {req.rationale}")
                        lines.append("")
                        lines.append("---")
                        lines.append("")

            files[filename] = "\n".join(lines)

        return files

    @staticmethod
    def to_csv(result: ExtractionResult) -> str:
        """Format requirements as DOORS-compatible CSV."""
        lines = [
            "ID,Text,Type,Priority,Status,Verification,Parent_ID,Source,Rationale,Feature"
        ]

        for req in result.requirements:
            # Escape text for CSV
            escaped_text = req.text.replace('"', '""')
            escaped_verification = req.verification.replace('"', '""')
            escaped_rationale = req.rationale.replace('"', '""')
            escaped_feature = req.feature.replace('"', '""') if req.feature else ""

            line = [
                req.id,
                f'"{escaped_text}"',
                req.type.value,
                req.priority.value,
                req.status.value,
                f'"{escaped_verification}"',
                req.parent_id or "",
                req.source,
                f'"{escaped_rationale}"' if escaped_rationale else "",
                f'"{escaped_feature}"' if escaped_feature else ""
            ]

            lines.append(",".join(line))

        return "\n".join(lines)

    @staticmethod
    def to_json(result: ExtractionResult) -> str:
        """Format requirements as JSON."""
        data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "source": result.source_file,
                "language": result.language,
                "requirement_count": len(result.requirements),
                "features": list(result.features.keys()) if result.features else []
            },
            "requirements": [
                {
                    "id": req.id,
                    "text": req.text,
                    "type": req.type.value,
                    "priority": req.priority.value,
                    "status": req.status.value,
                    "verification": req.verification,
                    "parent_id": req.parent_id,
                    "source": req.source,
                    "rationale": req.rationale,
                    "feature": req.feature
                }
                for req in result.requirements
            ],
            "warnings": result.warnings,
            "errors": result.errors
        }
        return json.dumps(data, indent=2)


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Extract ISO 29148 compliant requirements from code"
    )
    parser.add_argument(
        "file",
        help="Source code file or directory to analyze"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory path (default: docs/requirements)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["md", "csv", "json", "multi"],
        default="md",
        help="Output format: md, csv, json, or multi for multiple feature-based files (default: md)"
    )
    parser.add_argument(
        "--split",
        action="store_true",
        help="Split output into multiple files by feature (implies --format multi)"
    )
    parser.add_argument(
        "--single-file",
        action="store_true",
        help="Output to single file even in multi mode (creates index.md with all requirements)"
    )

    args = parser.parse_args()

    # Default output directory
    output_dir = args.output or "docs/requirements"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Detect language and check if file or directory
    file_path = Path(args.file)
    if file_path.is_dir():
        print(f"Error: Directory analysis not yet implemented. Please specify a single file.", file=sys.stderr)
        sys.exit(1)

    language = LanguageDetector.detect(args.file)
    if not language:
        print(f"Error: Unsupported file type: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Determine format
    output_format = args.format
    if args.split:
        output_format = "multi"

    # Select analyzer based on language
    if language == "Python":
        analyzer = PythonAnalyzer(args.file, detect_features=(output_format == "multi"))
    else:
        print(f"Error: {language} analyzer not yet implemented", file=sys.stderr)
        sys.exit(1)

    # Analyze code
    result = analyzer.analyze()

    # Handle output based on format
    if output_format == "multi":
        files = RequirementsFormatter.to_markdown_multi(result)

        if args.single_file:
            # Create single file with all requirements
            output = RequirementsFormatter.to_markdown(result)
            output_file = os.path.join(output_dir, "requirements.md")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Extracted {len(result.requirements)} requirements")
            print(f"Output written to: {output_file}")
        else:
            # Write multiple files
            for filename, content in files.items():
                output_file = os.path.join(output_dir, filename)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)

            print(f"Extracted {len(result.requirements)} requirements across {len(files)} feature files")
            print(f"Output directory: {output_dir}")
            print(f"Main index: {os.path.join(output_dir, 'index.md')}")

    elif output_format == "md":
        output = RequirementsFormatter.to_markdown(result)
        output_file = os.path.join(output_dir, "requirements.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Extracted {len(result.requirements)} requirements")
        print(f"Output written to: {output_file}")

    elif output_format == "csv":
        output = RequirementsFormatter.to_csv(result)
        output_file = os.path.join(output_dir, "requirements.csv")
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            f.write(output)
        print(f"Extracted {len(result.requirements)} requirements")
        print(f"Output written to: {output_file}")

    else:  # json
        output = RequirementsFormatter.to_json(result)
        output_file = os.path.join(output_dir, "requirements.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Extracted {len(result.requirements)} requirements")
        print(f"Output written to: {output_file}")

    # Display warnings and errors
    if result.warnings:
        print(f"\nWarnings ({len(result.warnings)}):", file=sys.stderr)
        for w in result.warnings:
            print(f"  - {w}", file=sys.stderr)

    if result.errors:
        print(f"\nErrors ({len(result.errors)}):", file=sys.stderr)
        for e in result.errors:
            print(f"  - {e}", file=sys.stderr)


if __name__ == "__main__":
    main()