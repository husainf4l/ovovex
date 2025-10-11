# Django Internationalization (i18n) Setup Guide
## English & Arabic Support with RTL Layout

This guide explains the complete internationalization setup for your Django project supporting English (default) and Arabic with right-to-left (RTL) layout.

---

## 📋 What Was Configured

### 1. **settings.py Changes**

#### ✅ Enabled i18n System
```python
USE_I18N = True  # Enable Django's translation system
USE_L10N = True  # Enable localized formatting of numbers and dates
```

**What it does:** Activates Django's built-in internationalization framework to handle translations.

---

#### ✅ Added LocaleMiddleware
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # ← Added here
    'django.middleware.common.CommonMiddleware',
    # ... rest of middleware
]
```

**What it does:** 
- Detects the user's preferred language from browser settings, cookies, or session
- Must be placed AFTER `SessionMiddleware` and BEFORE `CommonMiddleware`
- Automatically activates the correct language for each request

---

#### ✅ Configured Supported Languages
```python
LANGUAGE_CODE = 'en'  # Default language

LANGUAGES = [
    ('en', 'English'),
    ('ar', 'العربية'),  # Arabic
]
```

**What it does:** 
- Sets English as the default language
- Defines only English and Arabic as supported languages
- The tuple format: (language_code, human_readable_name)

---

#### ✅ Set Translation File Path
```python
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
```

**What it does:** Tells Django where to look for translation files (.po and .mo files)

---

#### ✅ Added i18n Context Processor
```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... other processors
                'django.template.context_processors.i18n',  # ← Added
            ],
        },
    },
]
```

**What it does:** Makes language-related variables available in all templates (like LANGUAGE_CODE, LANGUAGE_BIDI)

---

### 2. **urls.py Changes**

#### ✅ Wrapped URLs with i18n_patterns
```python
from django.conf.urls.i18n import i18n_patterns

# URLs without language prefix (admin, health checks)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", views.health_check, name="health_check"),
    path('i18n/', include('django.conf.urls.i18n')),  # Language switcher
]

# URLs WITH language prefix (/en/ or /ar/)
urlpatterns += i18n_patterns(
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    # ... all other user-facing URLs
)
```

**What it does:**
- Adds language prefix to URLs: `/en/` for English, `/ar/` for Arabic
- Example: `example.com/en/login/` or `example.com/ar/login/`
- Admin and API endpoints don't need translation, so they stay outside i18n_patterns
- The `/i18n/` endpoint is required for the language switcher to work

---

### 3. **base.html Template Changes**

#### ✅ Added Language and Direction Detection
```django
{% load i18n %}
{% get_current_language as LANGUAGE_CODE %}
{% get_current_language_bidi as LANGUAGE_BIDI %}
<html lang="{{ LANGUAGE_CODE }}" dir="{% if LANGUAGE_BIDI %}rtl{% else %}ltr{% endif %}">
```

**What it does:**
- Loads i18n template tags
- Gets current language code (en/ar)
- Detects if current language is RTL (Right-to-Left)
- Sets `dir="rtl"` for Arabic, `dir="ltr"` for English
- Automatically flips the entire layout for Arabic

---

#### ✅ Added Arabic Font Support
```html
{% if LANGUAGE_BIDI %}
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
    body, html {
        font-family: 'Cairo', 'Inter', sans-serif;
    }
</style>
{% endif %}
```

**What it does:** Loads Cairo font (beautiful Arabic font) when Arabic is active

---

### 4. **navbar.html - Language Switcher**

#### ✅ Added Translation Tags
```django
{% load i18n %}
<a href="/">{% trans "Home" %}</a>
<a href="{% url 'pricing' %}">{% trans "Pricing" %}</a>
```

**What it does:** Marks text for translation. The `{% trans %}` tag will be replaced with the translated version.

---

#### ✅ Added Language Dropdown
```django
<div class="relative group">
    {% get_current_language as LANGUAGE_CODE %}
    <button>
        <i class="fas fa-globe"></i>
        {% if LANGUAGE_CODE == 'ar' %}العربية{% else %}English{% endif %}
    </button>
    <div class="dropdown">
        <form action="{% url 'set_language' %}" method="post">
            {% csrf_token %}
            <input name="next" type="hidden" value="{{ request.path }}" />
            <button type="submit" name="language" value="en">English</button>
            <button type="submit" name="language" value="ar">العربية</button>
        </form>
    </div>
</div>
```

**What it does:**
- Shows current language with globe icon
- Provides dropdown to switch between English/Arabic
- Uses Django's built-in `set_language` view
- Reloads the current page in the selected language
- Stores language preference in session/cookie

---

## 🔧 Required Commands

### Step 1: Create Translation Files for Arabic

Run this command from your project root:

```bash
python manage.py makemessages -l ar
```

**What it does:**
- Scans all your templates and Python files
- Finds all `{% trans %}` tags and `_()` functions
- Creates `/locale/ar/LC_MESSAGES/django.po` file
- This .po file contains all translatable strings

**Output:** You'll see a file created at `locale/ar/LC_MESSAGES/django.po`

---

### Step 2: Edit the Translation File

Open `locale/ar/LC_MESSAGES/django.po` and add Arabic translations:

```po
# Example content
msgid "Home"
msgstr "الرئيسية"

msgid "Pricing"
msgstr "الأسعار"

msgid "Login"
msgstr "تسجيل الدخول"

msgid "Sign Up"
msgstr "إنشاء حساب"

msgid "Dashboard"
msgstr "لوحة التحكم"

msgid "Welcome back"
msgstr "مرحباً بعودتك"
```

**Format:**
- `msgid`: Original English text
- `msgstr`: Your Arabic translation (add it here)

---

### Step 3: Compile Translation Files

After editing the .po file, run:

```bash
python manage.py compilemessages
```

**What it does:**
- Converts the human-readable .po file into a binary .mo file
- Django uses .mo files for fast translation lookup
- Creates `locale/ar/LC_MESSAGES/django.mo`

**Important:** You MUST run this command every time you edit the .po file!

---

### Step 4: Update Translations (When You Add New Text)

When you add new `{% trans %}` tags or modify existing ones:

```bash
# 1. Update the .po file with new strings
python manage.py makemessages -l ar

# 2. Edit locale/ar/LC_MESSAGES/django.po and add translations

# 3. Compile the updated translations
python manage.py compilemessages
```

---

## 📝 How to Use in Templates

### Basic Translation
```django
{% load i18n %}

<!-- Translate simple text -->
<h1>{% trans "Welcome" %}</h1>

<!-- Translate with variables (use blocktrans) -->
{% blocktrans with name=user.first_name %}
Hello, {{ name }}!
{% endblocktrans %}
```

---

### Translation in Python Code
```python
from django.utils.translation import gettext as _

def my_view(request):
    message = _("Welcome to Ovovex")  # Will be translated
    return render(request, 'template.html', {'message': message})
```

---

## 🎨 RTL CSS Considerations

When Arabic is active, the entire layout flips automatically. However, you may need to adjust some CSS:

### Option 1: Conditional CSS in Template
```django
{% if LANGUAGE_BIDI %}
<style>
    .navbar { padding-right: 20px; padding-left: 0; }
    .button { margin-left: 10px; margin-right: 0; }
</style>
{% endif %}
```

### Option 2: CSS with Logical Properties (Modern Approach)
```css
/* Instead of margin-left, use margin-inline-start */
.button {
    margin-inline-start: 10px;  /* Adapts to LTR/RTL automatically */
    padding-inline: 20px;       /* Same as padding-left and padding-right */
}
```

---

## 🌐 Testing the Setup

### Test in Browser

1. **Start the server:**
   ```bash
   python manage.py runserver
   ```

2. **Access English version:**
   ```
   http://127.0.0.1:8000/en/
   ```

3. **Access Arabic version:**
   ```
   http://127.0.0.1:8000/ar/
   ```

4. **Use the language switcher:** Click the globe icon in the navbar to switch languages

---

### Expected Behavior

✅ **When you switch to Arabic:**
- URL changes to `/ar/...`
- Layout flips to right-to-left
- Arabic font (Cairo) loads
- All translated strings appear in Arabic
- Navbar, buttons, forms all flip direction

✅ **When you switch to English:**
- URL changes to `/en/...`
- Layout returns to left-to-right
- English font (Inter) is used
- All text appears in English

---

## 🚀 Production Checklist

Before deploying:

- [ ] All important text has `{% trans %}` tags
- [ ] Translation file `django.po` is fully translated
- [ ] Compiled translations with `compilemessages`
- [ ] Tested both English and Arabic versions
- [ ] RTL layout looks good (no broken UI)
- [ ] Language switcher works on all pages
- [ ] Language preference persists across pages

---

## 📚 Common Issues & Solutions

### Issue: Translations not appearing
**Solution:** Make sure you ran `compilemessages` after editing the .po file

### Issue: Layout breaks in RTL
**Solution:** Use CSS logical properties or add RTL-specific styles

### Issue: Language switcher not working
**Solution:** Check that `path('i18n/', include('django.conf.urls.i18n'))` is in urlpatterns

### Issue: Some pages don't have language prefix
**Solution:** Make sure URLs are inside `i18n_patterns()` in urls.py

---

## 🎓 Summary

| Component | Purpose | Required? |
|-----------|---------|-----------|
| `USE_I18N = True` | Enable translation system | ✅ Yes |
| `LocaleMiddleware` | Detect user's language | ✅ Yes |
| `LANGUAGES` setting | Define supported languages | ✅ Yes |
| `LOCALE_PATHS` | Where translation files live | ✅ Yes |
| `i18n_patterns()` | Add language prefix to URLs | ✅ Yes |
| `{% load i18n %}` | Load translation tags in templates | ✅ Yes |
| `{% trans %}` | Mark text for translation | ✅ Yes |
| `makemessages` | Create .po files | ✅ Yes |
| `compilemessages` | Create .mo files | ✅ Yes |
| Language switcher | Let users change language | ✅ Recommended |
| RTL CSS | Fix layout for Arabic | ⚠️ As needed |

---

## 🔗 Next Steps

1. Add `{% trans %}` tags to all templates (start with important pages)
2. Run `makemessages -l ar`
3. Translate all strings in `django.po`
4. Run `compilemessages`
5. Test thoroughly in both languages
6. Deploy!

---

**Need help?** Check Django's official i18n documentation:
https://docs.djangoproject.com/en/5.2/topics/i18n/

---

*Setup completed successfully! Your Django project now supports English and Arabic with full RTL support.* 🎉
