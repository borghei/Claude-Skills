#!/usr/bin/env python3
"""
Test Suite Generator

Scans React/TypeScript components and generates Jest + React Testing Library
test stubs with proper structure, accessibility tests, and common patterns.

Usage:
    python test_suite_generator.py src/components/ --output __tests__/
    python test_suite_generator.py src/ --include-a11y --scan-only
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class ComponentInfo:
    """Information about a detected React component"""
    name: str
    file_path: str
    component_type: str  # 'functional', 'class', 'forwardRef', 'memo'
    has_props: bool
    props: List[str]
    has_hooks: List[str]
    has_context: bool
    has_effects: bool
    has_state: bool
    has_callbacks: bool
    exports: List[str]
    imports: List[str]
    prop_types: Dict[str, Any] = field(default_factory=dict)  # name -> (type, optional)


@dataclass
class TestCase:
    """A single test case to generate"""
    name: str
    description: str
    test_type: str  # 'render', 'interaction', 'a11y', 'props', 'state'
    code: str


@dataclass
class TestFile:
    """A complete test file to generate"""
    component: ComponentInfo
    test_cases: List[TestCase] = field(default_factory=list)
    imports: Set[str] = field(default_factory=set)


PROP_TYPE_BLOCK = re.compile(r'(?:interface|type)\s+(\w*Props)\s*=?\s*\{([^}]*)\}')
PROP_ENTRY = re.compile(r'^\s*(?:readonly\s+)?(\w+)(\?)?\s*:\s*([^;,\n]+)', re.MULTILINE)


def extract_prop_types(content: str) -> Dict[str, Any]:
    """Parse the first `XProps` interface/type into {prop: (type, optional)}."""
    block = PROP_TYPE_BLOCK.search(content)
    if not block:
        return {}
    return {m.group(1): (m.group(3).strip(), bool(m.group(2)))
            for m in PROP_ENTRY.finditer(block.group(2))}


class ComponentScanner:
    """Scans source files for React components"""

    # Patterns for detecting React components
    FUNCTIONAL_COMPONENT = re.compile(
        r'^(?:export\s+)?(?:const|function)\s+([A-Z][a-zA-Z0-9]*)\s*[=:]?\s*(?:\([^)]*\)\s*(?::\s*[^=]+)?\s*=>|function\s*\([^)]*\))',
        re.MULTILINE
    )

    FUNCTION_DECLARATION = re.compile(
        r'^(?:export\s+(?:default\s+)?)?function\s+([A-Z][a-zA-Z0-9]*)\s*\(',
        re.MULTILINE
    )

    ARROW_COMPONENT = re.compile(
        r'^(?:export\s+)?const\s+([A-Z][a-zA-Z0-9]*)\s*=\s*(?:React\.)?(?:memo|forwardRef)?\s*\(',
        re.MULTILINE
    )

    CLASS_COMPONENT = re.compile(
        r'^(?:export\s+)?class\s+([A-Z][a-zA-Z0-9]*)\s+extends\s+(?:React\.)?(?:Component|PureComponent)',
        re.MULTILINE
    )

    HOOK_PATTERN = re.compile(r'use([A-Z][a-zA-Z0-9]*)\s*\(')
    PROPS_PATTERN = re.compile(r'(?:props\.|{\s*([^}]+)\s*}\s*=\s*props|:\s*([A-Z][a-zA-Z0-9]*Props))')
    CONTEXT_PATTERN = re.compile(r'useContext\s*\(|\.Provider|\.Consumer')
    EFFECT_PATTERN = re.compile(r'useEffect\s*\(|useLayoutEffect\s*\(')
    STATE_PATTERN = re.compile(r'useState\s*\(|useReducer\s*\(|this\.state')
    CALLBACK_PATTERN = re.compile(r'on[A-Z][a-zA-Z]*\s*[=:]|handle[A-Z][a-zA-Z]*\s*[=:]')

    def __init__(self, source_path: Path, verbose: bool = False):
        self.source_path = source_path
        self.verbose = verbose
        self.components: List[ComponentInfo] = []

    def scan(self) -> List[ComponentInfo]:
        """Scan the source path for React components"""
        extensions = {'.tsx', '.jsx', '.ts', '.js'}

        for root, dirs, files in os.walk(self.source_path):
            # Skip node_modules and test directories
            dirs[:] = [d for d in dirs if d not in {'node_modules', '__tests__', 'test', 'tests', '.git'}]

            for file in files:
                if Path(file).suffix in extensions:
                    file_path = Path(root) / file
                    self._scan_file(file_path)

        return self.components

    def _scan_file(self, file_path: Path):
        """Scan a single file for components"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not read {file_path}: {e}")
            return

        # Skip test files
        if '.test.' in file_path.name or '.spec.' in file_path.name:
            return

        # Skip files without JSX indicators
        if 'return' not in content or ('<' not in content and 'jsx' not in content.lower()):
            # Could still be a hook
            if not self.HOOK_PATTERN.search(content):
                return

        # Find functional components
        for match in self.FUNCTIONAL_COMPONENT.finditer(content):
            name = match.group(1)
            self._add_component(name, file_path, content, 'functional')

        # Find plain function declarations (export function Button(props) { ... })
        for match in self.FUNCTION_DECLARATION.finditer(content):
            self._add_component(match.group(1), file_path, content, 'functional')

        # Find arrow function components
        for match in self.ARROW_COMPONENT.finditer(content):
            name = match.group(1)
            component_type = 'functional'
            if 'memo(' in content:
                component_type = 'memo'
            elif 'forwardRef(' in content:
                component_type = 'forwardRef'
            self._add_component(name, file_path, content, component_type)

        # Find class components
        for match in self.CLASS_COMPONENT.finditer(content):
            name = match.group(1)
            self._add_component(name, file_path, content, 'class')

    def _add_component(self, name: str, file_path: Path, content: str, component_type: str):
        """Add a component to the list if not already present"""
        # Check if already added
        for comp in self.components:
            if comp.name == name and comp.file_path == str(file_path):
                return

        # Extract hooks used
        hooks = list(set(self.HOOK_PATTERN.findall(content)))

        # Extract prop names (simplified)
        props = []
        props_match = self.PROPS_PATTERN.search(content)
        if props_match:
            props_str = props_match.group(1) or ''
            props = [p.strip().split(':')[0].strip() for p in props_str.split(',') if p.strip()]

        prop_types = extract_prop_types(content)
        props = props or list(prop_types)

        # Extract imports
        imports = re.findall(r"import\s+(?:{[^}]+}|[^;]+)\s+from\s+['\"]([^'\"]+)['\"]", content)

        # Extract exports
        exports = re.findall(r"export\s+(?:default\s+)?(?:const|function|class)\s+(\w+)", content)

        component = ComponentInfo(
            name=name,
            file_path=str(file_path),
            component_type=component_type,
            has_props=bool(props) or 'props' in content.lower(),
            props=props[:10],  # Limit props
            has_hooks=hooks[:10],  # Limit hooks
            has_context=bool(self.CONTEXT_PATTERN.search(content)),
            has_effects=bool(self.EFFECT_PATTERN.search(content)),
            has_state=bool(self.STATE_PATTERN.search(content)),
            has_callbacks=bool(self.CALLBACK_PATTERN.search(content)),
            exports=exports[:5],
            imports=imports[:10],
            prop_types=prop_types,
        )

        self.components.append(component)

        if self.verbose:
            print(f"  Found: {name} ({component_type}) in {file_path.name}")


class TestGenerator:
    """Generates Jest + React Testing Library test files"""

    def __init__(self, include_a11y: bool = False, template: Optional[str] = None):
        self.include_a11y = include_a11y
        self.template = template

    def generate(self, component: ComponentInfo) -> TestFile:
        """Generate a test file for a component"""
        test_file = TestFile(component=component)

        # Build imports
        test_file.imports.add("import { render, screen } from '@testing-library/react';")

        if component.has_callbacks:
            test_file.imports.add("import userEvent from '@testing-library/user-event';")

        if component.has_effects or component.has_state:
            test_file.imports.add("import { waitFor } from '@testing-library/react';")

        if self.include_a11y:
            test_file.imports.add("import { axe, toHaveNoViolations } from 'jest-axe';")

        # Add component import
        relative_path = self._get_relative_import(component.file_path)
        test_file.imports.add(f"import {{ {component.name} }} from '{relative_path}';")

        # Generate test cases
        test_file.test_cases.append(self._generate_render_test(component))

        if component.has_props:
            test_file.test_cases.append(self._generate_props_test(component))

        if component.has_callbacks:
            test_file.test_cases.append(self._generate_interaction_test(component))

        if component.has_state:
            test_file.test_cases.append(self._generate_state_test(component))

        if self.include_a11y:
            test_file.test_cases.append(self._generate_a11y_test(component))

        return test_file

    def _get_relative_import(self, file_path: str) -> str:
        """Get the relative import path for a component"""
        path = Path(file_path)
        # Remove extension
        stem = path.stem
        if stem == 'index':
            return f"../{path.parent.name}"
        return f"../{path.parent.name}/{stem}"

    def _generate_render_test(self, component: ComponentInfo) -> TestCase:
        """Generate a basic render test"""
        props_str = self._get_mock_props(component)

        code = f'''  it('renders without crashing', () => {{
    render(<{component.name}{props_str} />);
  }});

  it('renders expected content', () => {{
    render(<{component.name}{props_str} />);
    // TODO: Add specific content assertions
    // expect(screen.getByRole('...')).toBeInTheDocument();
  }});'''

        return TestCase(
            name='render',
            description='Basic render tests',
            test_type='render',
            code=code
        )

    def _generate_props_test(self, component: ComponentInfo) -> TestCase:
        """Generate props-related tests"""
        props = component.props[:3] if component.props else ['prop1']

        prop_tests = []
        spread = ' {...mockProps}' if component.has_props else ''
        for prop in props:
            ts_type = component.prop_types.get(prop, ('string', False))[0]
            value = self._mock_value(prop, ts_type)
            prop_tests.append(f'''  it('renders with {prop} prop', () => {{
    render(<{component.name}{spread} {prop}={{{value}}} />);
    // TODO: Assert that {prop} affects rendering
  }});''')

        code = '\n\n'.join(prop_tests)

        return TestCase(
            name='props',
            description='Props handling tests',
            test_type='props',
            code=code
        )

    def _generate_interaction_test(self, component: ComponentInfo) -> TestCase:
        """Generate user interaction tests"""
        code = f'''  it('handles user interaction', async () => {{
    const user = userEvent.setup();
    const handleClick = jest.fn();

    render(<{component.name} onClick={{handleClick}} />);

    // TODO: Find the interactive element
    const button = screen.getByRole('button');
    await user.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  }});

  it('handles keyboard navigation', async () => {{
    const user = userEvent.setup();
    render(<{component.name} />);

    // TODO: Add keyboard interaction tests
    // await user.tab();
    // expect(screen.getByRole('...')).toHaveFocus();
  }});'''

        return TestCase(
            name='interaction',
            description='User interaction tests',
            test_type='interaction',
            code=code
        )

    def _generate_state_test(self, component: ComponentInfo) -> TestCase:
        """Generate state-related tests"""
        code = f'''  it('updates state correctly', async () => {{
    const user = userEvent.setup();
    render(<{component.name} />);

    // TODO: Trigger state change
    // await user.click(screen.getByRole('button'));

    // TODO: Assert state change is reflected in UI
    await waitFor(() => {{
      // expect(screen.getByText('...')).toBeInTheDocument();
    }});
  }});'''

        return TestCase(
            name='state',
            description='State management tests',
            test_type='state',
            code=code
        )

    def _generate_a11y_test(self, component: ComponentInfo) -> TestCase:
        """Generate accessibility test"""
        props_str = self._get_mock_props(component)

        code = f'''  it('has no accessibility violations', async () => {{
    const {{ container }} = render(<{component.name}{props_str} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  }});'''

        return TestCase(
            name='accessibility',
            description='Accessibility tests',
            test_type='a11y',
            code=code
        )

    @staticmethod
    def _mock_value(name: str, ts_type: str) -> str:
        """Pick a minimal valid value for a TypeScript prop type."""
        t = ts_type.replace(' ', '')
        if '=>' in t or t.startswith('Function'):
            return 'jest.fn()'
        if t.endswith('[]') or t.startswith('Array<'):
            return '[]'
        if t == 'boolean':
            return 'false'
        if t == 'number':
            return '1'
        if t == 'string':
            return f"'test-{name}'"
        if t.startswith(("'", '"')):
            return t.split('|')[0]
        if 'ReactNode' in t or 'ReactElement' in t or t == 'JSX.Element':
            return "'content'"
        return f'{{}} as never /* TODO: real {ts_type} */'

    def _mock_props_block(self, component: ComponentInfo) -> List[str]:
        """Typed mockProps with a value for every required prop."""
        required = {n: t for n, (t, optional) in component.prop_types.items() if not optional}
        if not required:
            return ['const mockProps = {};']
        lines = ['const mockProps = {']
        lines += [f'  {name}: {self._mock_value(name, t)},' for name, t in required.items()]
        lines.append('};')
        return lines

    def _get_mock_props(self, component: ComponentInfo) -> str:
        """Generate mock props string for a component"""
        if not component.has_props or not component.props:
            return ''

        # Return empty for simplicity, user should fill in
        return ' {...mockProps}'

    def format_test_file(self, test_file: TestFile) -> str:
        """Format the complete test file content"""
        lines = []

        # Imports
        lines.append("import '@testing-library/jest-dom';")
        for imp in sorted(test_file.imports):
            lines.append(imp)

        lines.append('')

        # A11y setup if needed
        if self.include_a11y:
            lines.append('expect.extend(toHaveNoViolations);')
            lines.append('')

        # Mock props if component has props
        if test_file.component.has_props:
            if test_file.component.prop_types:
                lines.append('// Minimal valid values for the required props; adjust per test')
                lines.extend(self._mock_props_block(test_file.component))
            else:
                lines.append('// TODO: Define mock props (no Props interface was found to infer them)')
                lines.append('const mockProps = {};')
            lines.append('')

        # Describe block
        lines.append(f"describe('{test_file.component.name}', () => {{")

        # Test cases grouped by type
        test_types = {}
        for test_case in test_file.test_cases:
            if test_case.test_type not in test_types:
                test_types[test_case.test_type] = []
            test_types[test_case.test_type].append(test_case)

        for test_type, cases in test_types.items():
            for case in cases:
                lines.append('')
                lines.append(f'  // {case.description}')
                lines.append(case.code)

        lines.append('});')
        lines.append('')

        return '\n'.join(lines)


class TestSuiteGenerator:
    """Main class for generating test suites"""

    def __init__(
        self,
        source_path: str,
        output_path: Optional[str] = None,
        include_a11y: bool = False,
        scan_only: bool = False,
        verbose: bool = False,
        template: Optional[str] = None
    ):
        self.source_path = Path(source_path)
        self.output_path = Path(output_path) if output_path else None
        self.include_a11y = include_a11y
        self.scan_only = scan_only
        self.verbose = verbose
        self.template = template
        self.results = {
            'status': 'success',
            'source': str(self.source_path),
            'components': [],
            'generated_files': [],
            'summary': {}
        }

    def run(self) -> Dict:
        """Execute the test suite generation"""
        print(f"Scanning: {self.source_path}")

        # Validate source path
        if not self.source_path.exists():
            raise ValueError(f"Source path does not exist: {self.source_path}")

        # Scan for components
        scanner = ComponentScanner(self.source_path, self.verbose)
        components = scanner.scan()

        print(f"Found {len(components)} React components")

        if self.scan_only:
            self._report_scan_results(components)
            return self.results

        # Generate tests
        if not self.output_path:
            # Default to __tests__ in source directory
            self.output_path = self.source_path / '__tests__'

        self.output_path.mkdir(parents=True, exist_ok=True)

        generator = TestGenerator(self.include_a11y, self.template)

        total_tests = 0
        for component in components:
            test_file = generator.generate(component)
            content = generator.format_test_file(test_file)

            # Write test file
            test_filename = f"{component.name}.test.tsx"
            test_path = self.output_path / test_filename

            test_path.write_text(content, encoding='utf-8')

            test_count = len(test_file.test_cases)
            total_tests += test_count

            self.results['generated_files'].append({
                'component': component.name,
                'path': str(test_path),
                'test_cases': test_count
            })

            print(f"  {test_filename} ({test_count} test cases)")

        # Store component info
        self.results['components'] = [asdict(c) for c in components]

        # Summary
        self.results['summary'] = {
            'total_components': len(components),
            'total_files': len(self.results['generated_files']),
            'total_test_cases': total_tests,
            'output_directory': str(self.output_path)
        }

        print('')
        print(f"Summary: {len(components)} test files, {total_tests} test cases")

        return self.results

    def _report_scan_results(self, components: List[ComponentInfo]):
        """Report scan results without generating tests"""
        print('')
        print("=" * 60)
        print("COMPONENT SCAN RESULTS")
        print("=" * 60)

        # Group by type
        by_type = {}
        for comp in components:
            comp_type = comp.component_type
            if comp_type not in by_type:
                by_type[comp_type] = []
            by_type[comp_type].append(comp)

        for comp_type, comps in sorted(by_type.items()):
            print(f"\n{comp_type.upper()} COMPONENTS ({len(comps)}):")
            for comp in comps:
                hooks_str = f" [hooks: {', '.join(comp.has_hooks[:3])}]" if comp.has_hooks else ""
                state_str = " [stateful]" if comp.has_state else ""
                print(f"  - {comp.name}{hooks_str}{state_str}")
                print(f"    {comp.file_path}")

        print('')
        print("=" * 60)
        print(f"Total: {len(components)} components")
        print("=" * 60)

        self.results['components'] = [asdict(c) for c in components]
        self.results['summary'] = {
            'total_components': len(components),
            'by_type': {k: len(v) for k, v in by_type.items()}
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate Jest + React Testing Library test stubs for React components",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan and generate tests
  python test_suite_generator.py src/components/ --output __tests__/

  # Scan only (don't generate)
  python test_suite_generator.py src/components/ --scan-only

  # Include accessibility tests
  python test_suite_generator.py src/ --include-a11y --output tests/

  # Verbose output
  python test_suite_generator.py src/components/ -v
        """
    )
    parser.add_argument(
        'source',
        help='Source directory containing React components'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output directory for test files (default: <source>/__tests__/)'
    )
    parser.add_argument(
        '--include-a11y',
        action='store_true',
        help='Include accessibility tests using jest-axe'
    )
    parser.add_argument(
        '--scan-only',
        action='store_true',
        help='Scan and report components without generating tests'
    )
    parser.add_argument(
        '--template',
        help='Custom template file for test generation'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    try:
        generator = TestSuiteGenerator(
            args.source,
            output_path=args.output,
            include_a11y=args.include_a11y,
            scan_only=args.scan_only,
            verbose=args.verbose,
            template=args.template
        )

        results = generator.run()

        if args.json:
            print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
