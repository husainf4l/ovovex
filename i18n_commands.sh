#!/bin/bash
# Django i18n Quick Commands
# Run these commands from your project root directory

echo "================================"
echo "Django i18n Commands Reference"
echo "================================"
echo ""

# Create Arabic translation files
echo "1. Create/Update Arabic translation files:"
echo "   python manage.py makemessages -l ar"
echo ""

# Compile translation files
echo "2. Compile translation files (run after editing .po files):"
echo "   python manage.py compilemessages"
echo ""

# Update all translations
echo "3. Update translations after adding new {% trans %} tags:"
echo "   python manage.py makemessages -l ar"
echo "   # Edit locale/ar/LC_MESSAGES/django.po"
echo "   python manage.py compilemessages"
echo ""

# Force recreate translations
echo "4. Force recreate all translation files:"
echo "   python manage.py makemessages -l ar --no-obsolete"
echo "   python manage.py compilemessages"
echo ""

# Check for untranslated strings
echo "5. Check for missing translations:"
echo "   msgfmt --check locale/ar/LC_MESSAGES/django.po"
echo ""

# Ignore specific directories
echo "6. Create messages ignoring certain directories:"
echo "   python manage.py makemessages -l ar --ignore=venv/* --ignore=staticfiles/*"
echo ""

echo "================================"
echo "Quick Workflow:"
echo "================================"
echo "1. Add {% trans %} tags to templates"
echo "2. Run: python manage.py makemessages -l ar"
echo "3. Edit: locale/ar/LC_MESSAGES/django.po"
echo "4. Run: python manage.py compilemessages"
echo "5. Restart server and test!"
echo ""

# To run this workflow automatically, uncomment below:
# python manage.py makemessages -l ar
# echo "✓ Translation files updated"
# echo "Now edit locale/ar/LC_MESSAGES/django.po and add your translations"
# echo "Then run: python manage.py compilemessages"
