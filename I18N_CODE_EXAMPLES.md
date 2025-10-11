# Django i18n Code Examples

## Template Examples

### Basic Translation
```django
{% load i18n %}

<h1>{% trans "Welcome" %}</h1>
<p>{% trans "This is a test" %}</p>
```

### Translation with Variables
```django
{% load i18n %}

{% blocktrans with name=user.first_name %}
Hello, {{ name }}!
{% endblocktrans %}

{% blocktrans count counter=items|length %}
You have {{ counter }} item.
{% plural %}
You have {{ counter }} items.
{% endblocktrans %}
```

### Context-Specific Translation (same word, different meaning)
```django
{% load i18n %}

{# "May" as the month #}
{% trans "May" context "month name" %}

{# "May" as permission #}
{% trans "may" context "permission" %}
```

---

## Python/Views Examples

### Basic Translation
```python
from django.utils.translation import gettext as _

def my_view(request):
    message = _("Welcome to Ovovex")
    return render(request, 'template.html', {'message': message})
```

### Lazy Translation (for module-level constants)
```python
from django.utils.translation import gettext_lazy as _

# Use lazy when defining constants or class attributes
class MyModel(models.Model):
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
    ]
```

### Translation with Variables
```python
from django.utils.translation import gettext

def my_view(request):
    count = 5
    message = gettext('You have %(count)d messages') % {'count': count}
    return render(request, 'template.html', {'message': message})
```

### Plural Forms
```python
from django.utils.translation import ngettext

def my_view(request):
    count = items.count()
    message = ngettext(
        'You have %d item',    # singular
        'You have %d items',   # plural
        count
    ) % count
```

---

## Models with Translation

```python
from django.db import models
from django.utils.translation import gettext_lazy as _

class Product(models.Model):
    name = models.CharField(_('product name'), max_length=100)
    description = models.TextField(_('description'))
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
```

---

## Forms with Translation

```python
from django import forms
from django.utils.translation import gettext_lazy as _

class ContactForm(forms.Form):
    name = forms.CharField(
        label=_('Your name'),
        max_length=100,
        help_text=_('Enter your full name')
    )
    email = forms.EmailField(
        label=_('Email address'),
        help_text=_('We will never share your email')
    )
    message = forms.CharField(
        label=_('Message'),
        widget=forms.Textarea
    )
```

---

## URL Translation

```python
# urls.py
from django.urls import path
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path(_('about/'), views.about, name='about'),
    path(_('contact/'), views.contact, name='contact'),
]

# This creates:
# English: /en/about/
# Arabic: /ar/حول/  (if translated)
```

---

## JavaScript Translation

### Setup in template
```django
{% load i18n %}

<script src="{% url 'javascript-catalog' %}"></script>
<script>
    const message = gettext('Hello world');
    const plural = ngettext('%(count)s item', '%(count)s items', count);
</script>
```

### Configure in urls.py
```python
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]
```

---

## RTL CSS Examples

### Using CSS Logical Properties (Best Practice)
```css
/* ❌ Don't use: */
.button {
    margin-left: 10px;
    padding-right: 20px;
    text-align: left;
}

/* ✅ Do use: */
.button {
    margin-inline-start: 10px;      /* Auto-adapts to LTR/RTL */
    padding-inline-end: 20px;       /* Auto-adapts to LTR/RTL */
    text-align: start;              /* Auto-adapts to LTR/RTL */
}
```

### Conditional RTL Styles in Template
```django
{% load i18n %}
{% get_current_language_bidi as LANGUAGE_BIDI %}

<style>
    .container {
        padding: 20px;
        {% if LANGUAGE_BIDI %}
        direction: rtl;
        text-align: right;
        {% else %}
        direction: ltr;
        text-align: left;
        {% endif %}
    }
</style>
```

---

## Language Switcher Examples

### Dropdown Switcher (As implemented)
```django
{% load i18n %}
{% get_current_language as LANGUAGE_CODE %}

<div class="language-switcher">
    <button>
        <i class="fas fa-globe"></i>
        {% if LANGUAGE_CODE == 'ar' %}العربية{% else %}English{% endif %}
    </button>
    <form action="{% url 'set_language' %}" method="post">
        {% csrf_token %}
        <input name="next" type="hidden" value="{{ request.path }}" />
        <button type="submit" name="language" value="en">English</button>
        <button type="submit" name="language" value="ar">العربية</button>
    </form>
</div>
```

### Simple Toggle Buttons
```django
{% load i18n %}
{% get_current_language as LANGUAGE_CODE %}

<form action="{% url 'set_language' %}" method="post" class="inline">
    {% csrf_token %}
    <input name="next" type="hidden" value="{{ request.path }}" />
    
    <button type="submit" name="language" value="en" 
            class="{% if LANGUAGE_CODE == 'en' %}active{% endif %}">
        EN
    </button>
    
    <button type="submit" name="language" value="ar"
            class="{% if LANGUAGE_CODE == 'ar' %}active{% endif %}">
        عر
    </button>
</form>
```

### Flag-based Switcher
```django
{% load i18n %}
{% get_current_language as LANGUAGE_CODE %}

<form action="{% url 'set_language' %}" method="post">
    {% csrf_token %}
    <input name="next" type="hidden" value="{{ request.path }}" />
    
    <button type="submit" name="language" value="en" title="English">
        <img src="{% static 'flags/en.png' %}" alt="English" />
    </button>
    
    <button type="submit" name="language" value="ar" title="العربية">
        <img src="{% static 'flags/ar.png' %}" alt="العربية" />
    </button>
</form>
```

---

## Translation File Format (.po)

```po
# locale/ar/LC_MESSAGES/django.po

# Simple translation
msgid "Home"
msgstr "الرئيسية"

# With context
msgctxt "navigation menu"
msgid "Home"
msgstr "الصفحة الرئيسية"

# With variables
msgid "Hello, %(name)s!"
msgstr "مرحباً، %(name)s!"

# Plural forms
msgid "%(count)d item"
msgid_plural "%(count)d items"
msgstr[0] "لا توجد عناصر"           # zero
msgstr[1] "عنصر واحد"              # one
msgstr[2] "عنصران"                 # two
msgstr[3] "%(count)d عناصر"        # few (3-10)
msgstr[4] "%(count)d عنصراً"       # many (11-99)
msgstr[5] "%(count)d عنصر"         # other (100+)
```

---

## Middleware Order (IMPORTANT!)

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Must be BEFORE LocaleMiddleware
    'django.middleware.locale.LocaleMiddleware',             # Language detection here
    'django.middleware.common.CommonMiddleware',             # Must be AFTER LocaleMiddleware
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

---

## Testing Translations

### In Python Shell
```python
python manage.py shell

from django.utils.translation import activate, gettext as _

# Test English
activate('en')
print(_('Home'))  # Output: Home

# Test Arabic
activate('ar')
print(_('Home'))  # Output: الرئيسية
```

### In Views/Tests
```python
from django.test import TestCase
from django.utils.translation import activate, gettext as _

class TranslationTests(TestCase):
    def test_arabic_translation(self):
        activate('ar')
        self.assertEqual(_('Home'), 'الرئيسية')
    
    def test_english_translation(self):
        activate('en')
        self.assertEqual(_('Home'), 'Home')
```

---

## Common Patterns

### Date/Time Translation
```django
{% load i18n %}

{# Automatic localization #}
{{ post.created_at|date:"SHORT_DATE_FORMAT" }}

{# Manual format #}
{{ post.created_at|date:"d M Y" }}
```

### Number Formatting
```django
{% load l10n %}

{# Auto-format based on locale #}
{{ price|localize }}

{# Force unlocalized #}
{{ price|unlocalize }}
```

### Email Translation
```python
from django.core.mail import send_mail
from django.utils.translation import gettext as _

def send_welcome_email(user):
    subject = _('Welcome to Ovovex!')
    message = _('Dear %(name)s, thank you for signing up!') % {'name': user.first_name}
    send_mail(subject, message, 'noreply@ovovex.com', [user.email])
```

---

## Admin Translation

```python
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'status']
    
    # Translate admin texts
    verbose_name = _('Product')
    verbose_name_plural = _('Products')
    
    # Translate fieldsets
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description')
        }),
        (_('Pricing'), {
            'fields': ('price', 'discount')
        }),
    )
```

---

## Best Practices

### ✅ DO:
- Use `{% trans %}` for simple text
- Use `{% blocktrans %}` for text with variables
- Use `gettext_lazy` in models/forms
- Always run `compilemessages` after editing .po
- Test both languages thoroughly
- Use CSS logical properties for RTL

### ❌ DON'T:
- Don't translate technical terms (API, URL, etc.)
- Don't translate user-generated content
- Don't forget to compile translations
- Don't hardcode "left/right" in CSS
- Don't mix `gettext` and `gettext_lazy` incorrectly

---

## Full Example: Login Form

```python
# forms.py
from django import forms
from django.utils.translation import gettext_lazy as _

class LoginForm(forms.Form):
    username = forms.CharField(
        label=_('Username'),
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': _('Enter username')})
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Enter password')})
    )
    remember_me = forms.BooleanField(
        label=_('Remember me'),
        required=False
    )
```

```django
{# login.html #}
{% load i18n %}

<h1>{% trans "Login" %}</h1>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">{% trans "Sign in" %}</button>
</form>

<p>
    {% blocktrans %}
    Don't have an account? <a href="/signup/">Sign up here</a>
    {% endblocktrans %}
</p>
```

---

*This file contains all common patterns and examples for Django i18n!*
