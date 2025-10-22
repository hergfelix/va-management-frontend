#!/usr/bin/env python3
"""
Content Template Generator
Creates text variations from viral slideshow content
Examples:
- "Top 5 Snacks" → "Top 5 Trucks" (same structure, different topic)
- Text pattern variations while keeping proven hooks
"""

import json
import re
from pathlib import Path
from collections import defaultdict
import pandas as pd

class ContentVariationGenerator:
    def __init__(self, ocr_data_dir, repost_candidates_file):
        self.ocr_data_dir = Path(ocr_data_dir)
        self.repost_candidates_file = Path(repost_candidates_file)

        # Load repost candidates
        with open(self.repost_candidates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.candidates = data['candidates']

        print(f"✅ Loaded {len(self.candidates)} repost candidates")

        # Filter to ones with OCR text
        self.text_candidates = [c for c in self.candidates if c['has_text'] and c['ocr_text']]
        print(f"✅ {len(self.text_candidates)} candidates have OCR text")

    def extract_patterns(self):
        """
        Extract common text patterns from viral content

        Patterns to detect:
        1. List format: "Top 5 X", "Best 10 X", "X things to Y"
        2. Question format: "Would you X?", "Can you Y?"
        3. Statement format: "X never Y", "X always Z"
        4. Call-to-action: "Follow for X", "Save this for Y"
        """

        patterns = {
            'list_patterns': [],
            'question_patterns': [],
            'statement_patterns': [],
            'cta_patterns': []
        }

        for candidate in self.text_candidates:
            text = candidate['ocr_text'].lower()

            # List patterns
            if re.search(r'top\s+\d+|best\s+\d+|\d+\s+(things|ways|tips)', text, re.IGNORECASE):
                patterns['list_patterns'].append({
                    'original_text': candidate['ocr_text'],
                    'views': candidate['views'],
                    'pattern_type': 'list',
                    'account': candidate['account'],
                    'post_url': candidate['post_url']
                })

            # Question patterns
            if re.search(r'\?|would you|can you|do you|have you', text, re.IGNORECASE):
                patterns['question_patterns'].append({
                    'original_text': candidate['ocr_text'],
                    'views': candidate['views'],
                    'pattern_type': 'question',
                    'account': candidate['account'],
                    'post_url': candidate['post_url']
                })

            # Call-to-action patterns
            if re.search(r'follow|save|like|comment|share|tag', text, re.IGNORECASE):
                patterns['cta_patterns'].append({
                    'original_text': candidate['ocr_text'],
                    'views': candidate['views'],
                    'pattern_type': 'cta',
                    'account': candidate['account'],
                    'post_url': candidate['post_url']
                })

            # Statement patterns (catch-all)
            if not any([
                re.search(r'top\s+\d+|best\s+\d+', text, re.IGNORECASE),
                re.search(r'\?', text),
                re.search(r'follow|save', text, re.IGNORECASE)
            ]):
                patterns['statement_patterns'].append({
                    'original_text': candidate['ocr_text'],
                    'views': candidate['views'],
                    'pattern_type': 'statement',
                    'account': candidate['account'],
                    'post_url': candidate['post_url']
                })

        # Sort each by views
        for key in patterns:
            patterns[key].sort(key=lambda x: x['views'], reverse=True)

        return patterns

    def generate_variations(self, original_text, num_variations=3):
        """
        Generate text variations from a proven template

        Example:
        "Top 5 Snacks to Try" →
        - "Top 5 Trucks You'll Love"
        - "Top 5 Places to Visit"
        - "Top 5 Hacks for Success"
        """

        variations = []

        # Extract pattern structure
        text_lower = original_text.lower()

        # List number variation
        if match := re.search(r'top\s+(\d+)', text_lower):
            number = match.group(1)
            variations.append(f"Top {number} Things You Need")
            variations.append(f"Best {number} Secrets Revealed")
            variations.append(f"{number} Must-Try Ideas")

        # Question variation
        elif '?' in original_text:
            variations.append("Would you try this?")
            variations.append("Can you guess the answer?")
            variations.append("Have you seen this before?")

        # CTA variation
        elif re.search(r'follow|save', text_lower):
            variations.append("Follow for more content like this")
            variations.append("Save this for later")
            variations.append("Tag someone who needs to see this")

        # Generic variations
        else:
            # Keep first few words, change rest
            words = original_text.split()
            if len(words) > 3:
                prefix = ' '.join(words[:3])
                variations.append(f"{prefix} will surprise you")
                variations.append(f"{prefix} you must try")
                variations.append(f"{prefix} everyone loves")

        # Ensure we have at least num_variations
        while len(variations) < num_variations:
            variations.append(f"Variation inspired by: {original_text[:30]}...")

        return variations[:num_variations]

    def create_templates(self):
        """Create reusable content templates from top performers"""

        print(f"""
╔════════════════════════════════════════════════════════════════╗
║          📝 CONTENT TEMPLATE GENERATOR                        ║
╚════════════════════════════════════════════════════════════════╝
        """)

        # Extract patterns
        patterns = self.extract_patterns()

        print(f"\n📊 Pattern Analysis:")
        print(f"  List Patterns:      {len(patterns['list_patterns'])}")
        print(f"  Question Patterns:  {len(patterns['question_patterns'])}")
        print(f"  CTA Patterns:       {len(patterns['cta_patterns'])}")
        print(f"  Statement Patterns: {len(patterns['statement_patterns'])}")

        # Generate templates
        templates = []

        # Top 10 from each category
        for pattern_type, pattern_list in patterns.items():
            for i, pattern in enumerate(pattern_list[:10], 1):
                # Generate 3 variations
                variations = self.generate_variations(pattern['original_text'], num_variations=3)

                template = {
                    'rank': i,
                    'pattern_type': pattern['pattern_type'],
                    'original_text': pattern['original_text'],
                    'original_views': pattern['views'],
                    'original_account': pattern['account'],
                    'original_url': pattern['post_url'],
                    'variation_1': variations[0] if len(variations) > 0 else '',
                    'variation_2': variations[1] if len(variations) > 1 else '',
                    'variation_3': variations[2] if len(variations) > 2 else '',
                    'avg_views_expected': pattern['views']  # Use original as baseline
                }

                templates.append(template)

        # Sort by expected views
        templates.sort(key=lambda x: x['original_views'], reverse=True)

        print(f"\n✅ Generated {len(templates)} content templates")

        return templates

    def generate_report(self, templates):
        """Save content templates report"""

        report = {
            'generated_at': pd.Timestamp.now().isoformat(),
            'total_templates': len(templates),
            'templates': templates,
            'breakdown': {
                'list': sum(1 for t in templates if t['pattern_type'] == 'list'),
                'question': sum(1 for t in templates if t['pattern_type'] == 'question'),
                'cta': sum(1 for t in templates if t['pattern_type'] == 'cta'),
                'statement': sum(1 for t in templates if t['pattern_type'] == 'statement')
            }
        }

        # Save JSON
        report_dir = Path('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports')
        report_file = report_dir / "06_CONTENT_TEMPLATES.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Report saved: {report_file}")

        # Save CSV
        df = pd.DataFrame(templates)
        csv_file = report_dir / "06_CONTENT_TEMPLATES.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')

        print(f"💾 CSV export: {csv_file}")

        # Print summary
        print("\n" + "="*70)
        print("CONTENT TEMPLATE SUMMARY")
        print("="*70)
        print(f"Total Templates: {report['total_templates']}")
        print(f"\nBreakdown by Type:")
        print(f"  List Format:    {report['breakdown']['list']}")
        print(f"  Questions:      {report['breakdown']['question']}")
        print(f"  CTAs:           {report['breakdown']['cta']}")
        print(f"  Statements:     {report['breakdown']['statement']}")

        # Show top 10
        print("\n" + "="*70)
        print("TOP 10 TEMPLATES")
        print("="*70)
        print(f"{'Rank':<6} {'Views':<12} {'Type':<12} {'Original Text':<40}")
        print("-" * 70)

        for i, t in enumerate(templates[:10], 1):
            text_preview = t['original_text'][:37] + "..." if len(t['original_text']) > 40 else t['original_text']
            print(f"{i:<6} {t['original_views']:>10,}  {t['pattern_type']:<12} {text_preview:<40}")

        print("\n" + "="*70)
        print("EXAMPLE VARIATIONS (Top Template)")
        print("="*70)

        if templates:
            top = templates[0]
            print(f"Original: {top['original_text']}")
            print(f"\nVariations:")
            print(f"  1. {top['variation_1']}")
            print(f"  2. {top['variation_2']}")
            print(f"  3. {top['variation_3']}")

        return report


def main():
    """Generate content templates"""

    generator = ContentVariationGenerator(
        ocr_data_dir='/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/october_ocr_data',
        repost_candidates_file='/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/05_REPOST_CANDIDATES.json'
    )

    # Create templates
    templates = generator.create_templates()

    # Generate report
    report = generator.generate_report(templates)

    print("\n✅ Content template generation complete!\n")


if __name__ == "__main__":
    main()
