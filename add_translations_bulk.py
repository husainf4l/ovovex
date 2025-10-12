#!/usr/bin/env python3
import re
import sys

def add_i18n_tags(content):
    """Add {% load i18n %} and wrap text with {% trans %} tags"""
    
    # Add {% load i18n %} after {% extends %}
    if '{% load i18n %}' not in content:
        content = content.replace(
            "{% extends 'base.html' %}",
            "{% extends 'base.html' %}\n{% load i18n %}"
        )
    
    # Patterns to wrap with {% trans %}
    patterns = [
        # h1-h6 headers
        (r'<h([1-6])[^>]*>([^<{]+)</h\1>', r'<h\1\2>{% trans "\3" %}</h\1>'),
        # p tags with simple text
        (r'<p([^>]*)>([^<{]+)</p>', r'<p\1>{% trans "\2" %}</p>'),
        # Button text
        (r'<button([^>]*)>([^<{]+)</button>', r'<button\1>{% trans "\2" %}</button>'),
        # Link text (not containing {% url %})
        (r'<a([^>]*href="[^"]*signup[^"]*"[^>]*)>([^<{]+)</a>', r'<a\1>{% trans "\2" %}</a>'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    return content

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python add_translations_bulk.py <file1> <file2> ...")
        sys.exit(1)
    
    for filepath in sys.argv[1:]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add translations
            translated_content = add_i18n_tags(content)
            
            # Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            print(f"✓ Processed: {filepath}")
        except Exception as e:
            print(f"✗ Error processing {filepath}: {e}")

