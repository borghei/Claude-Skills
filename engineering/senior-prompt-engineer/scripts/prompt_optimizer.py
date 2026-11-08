#!/usr/bin/env python3
"""
Prompt Optimizer - Static analysis tool for prompt engineering

Features:
- Token estimation (character-ratio approximation; not a real tokenizer)
- Prompt structure analysis
- Clarity scoring
- Few-shot example extraction and management
- Optimization suggestions

Usage:
    python prompt_optimizer.py prompt.txt --analyze
    python prompt_optimizer.py prompt.txt --tokens --model claude-sonnet-5-5 --price-per-1k 0.003  # example price

Scores are heuristics (regex checks for vague wording, structure, output format, reasoning
scaffolding and shouted emphasis), useful for spotting issues, not a measure of quality.
Costs are only shown when you pass --price-per-1k from the provider's current pricing page.
Exit codes: 0 analysis ran, 2 bad input (missing or empty prompt file).
    python prompt_optimizer.py prompt.txt --optimize --output optimized.txt
    python prompt_optimizer.py prompt.txt --extract-examples --output examples.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


# Characters per token by model family (rough; real tokenizers differ by language and content)
TOKEN_RATIOS = {
    'claude': 3.5,
    'default': 4.0
}
# No price table on purpose: prices change. Pass --price-per-1k from the provider's pricing page.

# Explicit chain-of-thought scaffolding. Reasoning models think before answering, so these
# phrases mostly add tokens; keep them only when targeting a non-reasoning model.
REASONING_SCAFFOLD = [
    r"\b(let'?s|please)?\s*think (it through )?step[- ]by[- ]step\b",
    r'\bchain[- ]of[- ]thought\b',
    r'\breason (carefully|step by step) before\b',
    r'\bexplain your reasoning before\b',
    r'\bshow your (work|reasoning)\b',
    r'^\s*Thought\s*:',
]
SHOUTED = r'\b(MUST|NEVER|ALWAYS|CRITICAL|IMPORTANT|DO NOT|REQUIRED)\b'


@dataclass
class PromptAnalysis:
    """Results of prompt analysis"""
    token_count: int
    estimated_cost: Optional[float]
    model: str
    clarity_score: int
    structure_score: int
    issues: List[Dict[str, str]]
    suggestions: List[str]
    sections: List[Dict[str, any]]
    has_examples: bool
    example_count: int
    has_output_format: bool
    word_count: int
    line_count: int


@dataclass
class FewShotExample:
    """A single few-shot example"""
    input_text: str
    output_text: str
    index: int


def estimate_tokens(text: str, model: str = 'default') -> int:
    """Estimate token count based on a per-family character ratio"""
    family = 'claude' if model.lower().startswith('claude') else 'default'
    return int(len(text) / TOKEN_RATIOS[family])


def estimate_cost(token_count: int, price_per_1k: Optional[float] = None) -> Optional[float]:
    """Input cost for the given price per 1K tokens, or None when no price was supplied"""
    if price_per_1k is None:
        return None
    return round((token_count / 1000) * price_per_1k, 6)


def find_reasoning_scaffolding(text: str) -> List[Dict[str, str]]:
    """Flag forced chain-of-thought phrasing and heavy ALL-CAPS emphasis"""
    issues = []
    for i, line in enumerate(text.split('\n'), 1):
        for pattern in REASONING_SCAFFOLD:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                issues.append({'type': 'reasoning_scaffold', 'line': i, 'text': match.group().strip(),
                               'message': 'Forced chain-of-thought: reasoning models already think. State the goal, '
                                          'constraints and output contract instead (keep only for non-reasoning models)',
                               'context': line.strip()[:80]})
                break
    shouted = [(i, m.group()) for i, line in enumerate(text.split('\n'), 1) for m in re.finditer(SHOUTED, line)]
    if len(shouted) >= 3:
        line, word = shouted[0]
        issues.append({'type': 'emphasis', 'line': line, 'text': word,
                       'message': f'{len(shouted)} ALL-CAPS imperatives: heavy emphasis makes current models '
                                  'over-apply rules. Use calm wording and give the reason instead',
                       'context': ''})
    return issues


def find_ambiguous_instructions(text: str) -> List[Dict[str, str]]:
    """Find vague or ambiguous instructions"""
    issues = []

    # Vague verbs that need specificity
    vague_patterns = [
        (r'\b(analyze|process|handle|deal with)\b', 'Vague verb - specify the exact action'),
        (r'\b(good|nice|appropriate|suitable)\b', 'Subjective term - define specific criteria'),
        (r'\b(etc\.|and so on|and more)\b', 'Open-ended list - enumerate all items explicitly'),
        (r'\b(if needed|as necessary|when appropriate)\b', 'Conditional without criteria - specify when'),
        (r'\b(some|several|many|few|various)\b', 'Vague quantity - use specific numbers'),
    ]

    lines = text.split('\n')
    for i, line in enumerate(lines, 1):
        for pattern, message in vague_patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                issues.append({
                    'type': 'ambiguity',
                    'line': i,
                    'text': match.group(),
                    'message': message,
                    'context': line.strip()[:80]
                })

    return issues


def find_redundant_content(text: str) -> List[Dict[str, str]]:
    """Find potentially redundant content"""
    issues = []
    lines = text.split('\n')

    # Check for repeated phrases (3+ words)
    seen_phrases = {}
    for i, line in enumerate(lines, 1):
        words = line.split()
        for j in range(len(words) - 2):
            phrase = ' '.join(words[j:j+3]).lower()
            phrase = re.sub(r'[^\w\s]', '', phrase)
            if phrase and len(phrase) > 10:
                if phrase in seen_phrases:
                    issues.append({
                        'type': 'redundancy',
                        'line': i,
                        'text': phrase,
                        'message': f'Phrase repeated from line {seen_phrases[phrase]}',
                        'context': line.strip()[:80]
                    })
                else:
                    seen_phrases[phrase] = i

    return issues


def check_output_format(text: str) -> Tuple[bool, List[str]]:
    """Check if prompt specifies output format"""
    suggestions = []

    format_indicators = [
        r'respond\s+(in|with)\s+(json|xml|csv|markdown)',
        r'output\s+format',
        r'return\s+(only|just)',
        r'format:\s*\n',
        r'\{["\']?\w+["\']?\s*:',  # JSON-like structure
        r'```\w*\n',  # Code block
    ]

    has_format = any(re.search(p, text, re.IGNORECASE) for p in format_indicators)

    if not has_format:
        suggestions.append('Add explicit output format specification (e.g., "Respond in JSON with keys: ...")')

    return has_format, suggestions


def extract_sections(text: str) -> List[Dict[str, any]]:
    """Extract logical sections from prompt"""
    sections = []

    # Common section patterns
    section_patterns = [
        r'^#+\s+(.+)$',  # Markdown headers
        r'^([A-Z][A-Za-z\s]+):\s*$',  # Title Case Label:
        r'^(Instructions|Context|Examples?|Input|Output|Task|Role|Format)[:.]',
    ]

    lines = text.split('\n')
    current_section = {'name': 'Introduction', 'start': 1, 'content': []}

    for i, line in enumerate(lines, 1):
        is_header = False
        for pattern in section_patterns:
            match = re.match(pattern, line.strip(), re.IGNORECASE)
            if match:
                if current_section['content']:
                    current_section['end'] = i - 1
                    current_section['line_count'] = len(current_section['content'])
                    sections.append(current_section)
                current_section = {
                    'name': match.group(1).strip() if match.groups() else line.strip(),
                    'start': i,
                    'content': []
                }
                is_header = True
                break

        if not is_header:
            current_section['content'].append(line)

    # Add last section
    if current_section['content']:
        current_section['end'] = len(lines)
        current_section['line_count'] = len(current_section['content'])
        sections.append(current_section)

    return sections


def extract_few_shot_examples(text: str) -> List[FewShotExample]:
    """Extract few-shot examples from prompt"""
    examples = []

    # Pattern 1: "Example N:" or "Example:" blocks
    example_pattern = r'Example\s*\d*:\s*\n(Input:\s*(.+?)\n(?:Output:\s*(.+?)(?=\n\nExample|\n\n[A-Z]|\Z)))'

    matches = re.finditer(example_pattern, text, re.DOTALL | re.IGNORECASE)
    for i, match in enumerate(matches, 1):
        examples.append(FewShotExample(
            input_text=match.group(2).strip() if match.group(2) else '',
            output_text=match.group(3).strip() if match.group(3) else '',
            index=i
        ))

    # Pattern 2: Input/Output pairs without "Example" label
    if not examples:
        io_pattern = r'Input:\s*["\']?(.+?)["\']?\s*\nOutput:\s*(.+?)(?=\nInput:|\Z)'
        matches = re.finditer(io_pattern, text, re.DOTALL)
        for i, match in enumerate(matches, 1):
            examples.append(FewShotExample(
                input_text=match.group(1).strip(),
                output_text=match.group(2).strip(),
                index=i
            ))

    return examples


def calculate_clarity_score(text: str, issues: List[Dict]) -> int:
    """Calculate clarity score (0-100)"""
    score = 100

    # Deduct for issues
    score -= len([i for i in issues if i['type'] == 'ambiguity']) * 5
    score -= len([i for i in issues if i['type'] == 'redundancy']) * 3
    score -= len([i for i in issues if i['type'] in ('reasoning_scaffold', 'emphasis')]) * 5

    # Check for structure
    if not re.search(r'^#+\s|^[A-Z][a-z]+:', text, re.MULTILINE):
        score -= 10  # No clear sections

    # Check for instruction clarity
    if not re.search(r'(you (should|must|will)|please|your task)', text, re.IGNORECASE):
        score -= 5  # No clear directives

    return max(0, min(100, score))


def calculate_structure_score(sections: List[Dict], has_format: bool, has_examples: bool) -> int:
    """Calculate structure score (0-100)"""
    score = 50  # Base score

    # Bonus for clear sections
    if len(sections) >= 2:
        score += 15
    if len(sections) >= 4:
        score += 10

    # Bonus for output format
    if has_format:
        score += 15

    # Bonus for examples
    if has_examples:
        score += 10

    return min(100, score)


def generate_suggestions(analysis: PromptAnalysis) -> List[str]:
    """Generate optimization suggestions"""
    suggestions = []

    if not analysis.has_output_format:
        suggestions.append('Add explicit output format: "Respond in JSON with keys: ..."')

    if analysis.example_count == 0:
        suggestions.append('Consider adding 2-3 few-shot examples for consistent outputs')
    elif analysis.example_count == 1:
        suggestions.append('Add 1-2 more examples to improve consistency')
    elif analysis.example_count > 5:
        suggestions.append(f'Consider reducing examples from {analysis.example_count} to 3-5 to save tokens')

    if analysis.clarity_score < 70:
        suggestions.append('Improve clarity: replace vague terms with specific instructions')

    if analysis.token_count > 2000:
        suggestions.append(f'Prompt is {analysis.token_count} tokens - consider condensing for cost efficiency')

    if any(i['type'] == 'reasoning_scaffold' for i in analysis.issues):
        suggestions.append('Remove "think step by step" style scaffolding for reasoning models; '
                           'use the platform\'s reasoning effort / thinking budget setting if you need more depth')

    # Context beats a generic persona
    if not re.search(r'\b(audience|used (for|by)|so that|because|the goal|purpose)\b', analysis.raw_text, re.IGNORECASE):
        suggestions.append('Say who the output is for and why it is needed; that context helps more than '
                           '"You are an expert..."')

    return suggestions


def analyze_prompt(text: str, model: str = 'generic', price_per_1k: Optional[float] = None) -> PromptAnalysis:
    """Perform comprehensive prompt analysis"""

    # Basic metrics
    token_count = estimate_tokens(text, model)
    cost = estimate_cost(token_count, price_per_1k)
    word_count = len(text.split())
    line_count = len(text.split('\n'))

    # Find issues
    ambiguity_issues = find_ambiguous_instructions(text)
    redundancy_issues = find_redundant_content(text)
    all_issues = ambiguity_issues + redundancy_issues + find_reasoning_scaffolding(text)

    # Extract structure
    sections = extract_sections(text)
    examples = extract_few_shot_examples(text)
    has_format, format_suggestions = check_output_format(text)

    # Calculate scores
    clarity_score = calculate_clarity_score(text, all_issues)
    structure_score = calculate_structure_score(sections, has_format, len(examples) > 0)

    analysis = PromptAnalysis(
        token_count=token_count,
        estimated_cost=cost,
        model=model,
        clarity_score=clarity_score,
        structure_score=structure_score,
        issues=all_issues,
        suggestions=[],
        sections=[{'name': s['name'], 'lines': f"{s['start']}-{s.get('end', s['start'])}"} for s in sections],
        has_examples=len(examples) > 0,
        example_count=len(examples),
        has_output_format=has_format,
        word_count=word_count,
        line_count=line_count
    )

    analysis.raw_text = text
    # Both sources suggest adding an output format; keep the first of each topic
    suggestions, topics = [], set()
    for text_ in generate_suggestions(analysis) + format_suggestions:
        topic = 'output format' if 'output format' in text_.lower() else text_
        if topic not in topics:
            topics.add(topic)
            suggestions.append(text_)
    analysis.suggestions = suggestions
    del analysis.raw_text

    return analysis


def optimize_prompt(text: str) -> str:
    """Generate optimized version of prompt"""
    optimized = text

    # Remove redundant whitespace
    optimized = re.sub(r'\n{3,}', '\n\n', optimized)
    optimized = re.sub(r' {2,}', ' ', optimized)

    # Trim lines
    lines = [line.rstrip() for line in optimized.split('\n')]
    optimized = '\n'.join(lines)

    return optimized.strip()


def format_report(analysis: PromptAnalysis) -> str:
    """Format analysis as human-readable report"""
    report = []
    report.append("=" * 50)
    report.append("PROMPT ANALYSIS REPORT")
    report.append("=" * 50)
    report.append("")

    report.append("📊 METRICS")
    report.append(f"  Token count:     {analysis.token_count:,}")
    if analysis.estimated_cost is None:
        report.append(f"  Estimated cost:  n/a (pass --price-per-1k)")
    else:
        report.append(f"  Estimated cost:  ${analysis.estimated_cost:.4f} input ({analysis.model})")
    report.append(f"  Word count:      {analysis.word_count:,}")
    report.append(f"  Line count:      {analysis.line_count}")
    report.append("")

    report.append("📈 SCORES (heuristic)")
    report.append(f"  Clarity:    {analysis.clarity_score}/100 {'✅' if analysis.clarity_score >= 70 else '⚠️'}")
    report.append(f"  Structure:  {analysis.structure_score}/100 {'✅' if analysis.structure_score >= 70 else '⚠️'}")
    report.append("")

    report.append("📋 STRUCTURE")
    report.append(f"  Sections:      {len(analysis.sections)}")
    report.append(f"  Examples:      {analysis.example_count} {'✅' if analysis.has_examples else '❌'}")
    report.append(f"  Output format: {'✅ Specified' if analysis.has_output_format else '❌ Missing'}")
    report.append("")

    if analysis.sections:
        report.append("  Detected sections:")
        for section in analysis.sections:
            report.append(f"    - {section['name']} (lines {section['lines']})")
        report.append("")

    if analysis.issues:
        report.append(f"⚠️ ISSUES FOUND ({len(analysis.issues)})")
        for issue in analysis.issues[:10]:  # Limit to first 10
            report.append(f"  Line {issue['line']}: {issue['message']}")
            report.append(f"    Found: \"{issue['text']}\"")
        if len(analysis.issues) > 10:
            report.append(f"  ... and {len(analysis.issues) - 10} more issues")
        report.append("")

    if analysis.suggestions:
        report.append("💡 SUGGESTIONS")
        for i, suggestion in enumerate(analysis.suggestions, 1):
            report.append(f"  {i}. {suggestion}")
        report.append("")

    report.append("=" * 50)

    return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Prompt Optimizer - Analyze and optimize prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s prompt.txt --analyze
  %(prog)s prompt.txt --tokens --model claude-sonnet-5-5 --price-per-1k 0.003  # example price
  %(prog)s prompt.txt --optimize --output optimized.txt
  %(prog)s prompt.txt --extract-examples --output examples.json
        """
    )

    parser.add_argument('prompt', help='Prompt file to analyze')
    parser.add_argument('--analyze', '-a', action='store_true', help='Run full analysis')
    parser.add_argument('--tokens', '-t', action='store_true', help='Count tokens only')
    parser.add_argument('--optimize', '-O', action='store_true', help='Generate optimized version')
    parser.add_argument('--extract-examples', '-e', action='store_true', help='Extract few-shot examples')
    parser.add_argument('--model', '-m', default='generic',
                       help='Model id, used for the token ratio (claude* ~3.5 chars/token, others ~4)')
    parser.add_argument('--price-per-1k', type=float,
                       help="Input price per 1K tokens from the provider's pricing page (enables cost output)")
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--compare', '-c', help='Compare with baseline analysis JSON')

    args = parser.parse_args()

    # Read prompt file
    prompt_path = Path(args.prompt)
    if not prompt_path.is_file():
        print(f"error: file not found: {args.prompt}", file=sys.stderr)
        sys.exit(2)
    try:
        text = prompt_path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: cannot read {args.prompt}: {exc}", file=sys.stderr)
        sys.exit(2)
    if not text.strip():
        print(f"error: {args.prompt} is empty", file=sys.stderr)
        sys.exit(2)

    # Tokens only
    if args.tokens:
        token_count = estimate_tokens(text, args.model)
        cost = estimate_cost(token_count, args.price_per_1k)
        if args.json:
            print(json.dumps({
                'tokens': token_count,
                'cost': cost,
                'model': args.model
            }, indent=2))
        else:
            print(f"Tokens: {token_count:,}")
            print(f"Estimated cost: ${cost:.4f} input ({args.model})" if cost is not None
                  else "Estimated cost: n/a (pass --price-per-1k)")
        sys.exit(0)

    # Extract examples
    if args.extract_examples:
        examples = extract_few_shot_examples(text)
        output = [asdict(ex) for ex in examples]

        if args.output:
            Path(args.output).write_text(json.dumps(output, indent=2))
            print(f"Extracted {len(examples)} examples to {args.output}")
        else:
            print(json.dumps(output, indent=2))
        sys.exit(0)

    # Optimize
    if args.optimize:
        optimized = optimize_prompt(text)

        if args.output:
            Path(args.output).write_text(optimized)
            print(f"Optimized prompt written to {args.output}")

            # Show comparison
            orig_tokens = estimate_tokens(text, args.model)
            new_tokens = estimate_tokens(optimized, args.model)
            saved = orig_tokens - new_tokens
            print(f"Tokens: {orig_tokens:,} -> {new_tokens:,} (saved {saved:,})")
        else:
            print(optimized)
        sys.exit(0)

    # Default: full analysis
    analysis = analyze_prompt(text, args.model, args.price_per_1k)

    # Compare with baseline
    if args.compare:
        baseline_path = Path(args.compare)
        if baseline_path.exists():
            baseline = json.loads(baseline_path.read_text())
            print("\n📊 COMPARISON WITH BASELINE")
            print(f"  Tokens: {baseline.get('token_count', 0):,} -> {analysis.token_count:,}")
            print(f"  Clarity: {baseline.get('clarity_score', 0)} -> {analysis.clarity_score}")
            print(f"  Issues: {len(baseline.get('issues', []))} -> {len(analysis.issues)}")
            print()

    if args.json:
        print(json.dumps(asdict(analysis), indent=2))
    else:
        print(format_report(analysis))

    # Write to output file
    if args.output:
        output_data = asdict(analysis)
        Path(args.output).write_text(json.dumps(output_data, indent=2))
        print(f"\nAnalysis saved to {args.output}")


if __name__ == "__main__":
    main()
