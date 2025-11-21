# 🎨 BizBooks Design System

**Created:** November 21, 2025  
**Purpose:** Centralized styling system for consistent, maintainable UI

---

## 📁 Files

1. **`modular_app/static/css/forms.css`** - Core CSS design system
2. **`modular_app/templates/_form_macros.html`** - Reusable Jinja components
3. **`modular_app/templates/base_sidebar.html`** - Automatically includes forms.css

---

## 🎯 Quick Start

### Using CSS Classes (Recommended)

```html
<!-- BEFORE (inline styles ❌) -->
<div style="display: flex; gap: 16px; margin-bottom: 16px;">
    <div style="flex: 1;">
        <label style="margin-bottom: 4px; font-weight: 500;">Name *</label>
        <input type="text" name="name" required>
        <small style="color: #7f8c8d;">Required field</small>
    </div>
</div>

<!-- AFTER (CSS classes ✅) -->
<div class="form-row">
    <div class="form-group">
        <label class="field-label field-label--required">Name</label>
        <input type="text" name="name" required>
        <small class="help-text">Required field</small>
    </div>
</div>
```

### Using Jinja Macros (Advanced)

```jinja
{% from "_form_macros.html" import text_field, number_field, select_field %}

<!-- Simple text input -->
{{ text_field('email', 'Email Address', required=true, placeholder='you@example.com') }}

<!-- Number input with help text -->
{{ number_field('price', 'Price (₹)', required=true, help_text='Enter selling price', min='0', step='0.01') }}

<!-- Dropdown with options -->
{{ select_field('status', 'Status', [('active', 'Active'), ('inactive', 'Inactive')], required=true) }}
```

---

## 📦 Available CSS Classes

### Layout

| Class | Purpose | Example |
|-------|---------|---------|
| `.form-row` | 2-column flex layout | `<div class="form-row">` |
| `.form-row--three-cols` | 3-column grid layout | For Unit/Category/Group |
| `.form-group` | Single form field container | Wrap each input |
| `.form-group--full` | Full-width field | For textareas |
| `.form-group--half` | 50% width | Rare, auto-handled |

### Labels & Text

| Class | Purpose | Example |
|-------|---------|---------|
| `.field-label` | Standard label | `<label class="field-label">` |
| `.field-label--required` | Adds red asterisk (*) | For required fields |
| `.label-row` | Flex row for label + checkbox | SKU with "Auto-generate" |
| `.help-text` | Small gray hint text | `<small class="help-text">` |

### Sections

| Class | Purpose | Example |
|-------|---------|---------|
| `.section-title` | Section headings | Sales Info, Purchase Info |
| `.collapsible-section` | Collapsible wrapper | Advanced Options |

### Radio/Checkbox

| Class | Purpose | Example |
|-------|---------|---------|
| `.radio-group` | Horizontal radio buttons | Goods/Service |
| `.checkbox-group` | Checkbox with label | Track Inventory |
| `.inline-checkbox` | Small inline checkbox | "Auto-generate" SKU |

### Buttons

| Class | Purpose | Example |
|-------|---------|---------|
| `.btn` | Base button | All buttons |
| `.btn-primary` | Blue action button | Save, Submit |
| `.btn-secondary` | Gray button | Cancel, Back |
| `.btn-success` | Green button | Approve |
| `.btn-danger` | Red button | Delete |

### Actions

| Class | Purpose | Example |
|-------|---------|---------|
| `.form-actions` | Button row at bottom | Save/Cancel buttons |

### Utility

| Class | Purpose | Example |
|-------|---------|---------|
| `.mb-0` to `.mb-3` | Margin bottom (0/8/16/24px) | Spacing control |
| `.mt-0` to `.mt-3` | Margin top (0/8/16/24px) | Spacing control |
| `.text-muted` | Gray text | `#7f8c8d` |
| `.text-danger` | Red text | Errors |
| `.text-success` | Green text | Success |
| `.w-full` | 100% width | Full-width elements |

---

## 🛠️ Common Patterns

### Two-Column Form Row

```html
<div class="form-row">
    <div class="form-group">
        <label class="field-label field-label--required">First Name</label>
        <input type="text" name="first_name" required>
    </div>
    <div class="form-group">
        <label class="field-label field-label--required">Last Name</label>
        <input type="text" name="last_name" required>
    </div>
</div>
```

### Three-Column Row

```html
<div class="form-row">
    <div class="form-group">
        <label class="field-label">Unit</label>
        <select name="unit">...</select>
    </div>
    <div class="form-group">
        <label class="field-label">Category</label>
        <select name="category">...</select>
    </div>
    <div class="form-group">
        <label class="field-label">Group</label>
        <select name="group">...</select>
    </div>
</div>
```

### Full-Width Textarea

```html
<div class="form-row">
    <div class="form-group form-group--full">
        <label class="field-label">Description</label>
        <textarea name="description" rows="3"></textarea>
        <small class="help-text">Optional description</small>
    </div>
</div>
```

### Section with Title

```html
<h3 class="section-title">
    💰 Sales Information
</h3>

<div class="form-row">
    <!-- fields -->
</div>
```

### Radio Group

```html
<div class="form-group">
    <label class="field-label field-label--required">Type</label>
    <div class="radio-group">
        <label>
            <input type="radio" name="type" value="goods" checked required>
            <span>Goods</span>
        </label>
        <label>
            <input type="radio" name="type" value="service" required>
            <span>Service</span>
        </label>
    </div>
</div>
```

### Inline Checkbox (e.g., Auto-generate SKU)

```html
<div class="form-group">
    <div class="label-row">
        <label class="field-label">SKU</label>
        <label class="inline-checkbox">
            <input type="checkbox" id="autoSku" checked>
            <span>Auto-generate</span>
        </label>
    </div>
    <input type="text" id="skuInput" name="sku">
    <small class="help-text">Will be auto-generated</small>
</div>
```

### Form Actions (Bottom Buttons)

```html
<div class="form-actions">
    <a href="{{ url_for('items.index') }}" class="btn btn-secondary">
        Cancel
    </a>
    <button type="submit" class="btn btn-primary">
        💾 Save Item
    </button>
</div>
```

---

## 🔧 Available Jinja Macros

Import at the top of your template:

```jinja
{% from "_form_macros.html" import text_field, number_field, select_field, textarea_field, checkbox_field, radio_group, section_title %}
```

### Text Field

```jinja
{{ text_field(
    name='customer_name',
    label='Customer Name',
    required=true,
    placeholder='John Doe',
    help_text='Full legal name',
    value=''
) }}
```

### Number Field

```jinja
{{ number_field(
    name='price',
    label='Price (₹)',
    required=true,
    placeholder='0.00',
    help_text='Selling price',
    min='0',
    step='0.01'
) }}
```

### Select Field

```jinja
{{ select_field(
    name='status',
    label='Status',
    options=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending')
    ],
    required=true,
    help_text='Current status',
    selected='active'
) }}
```

### Textarea Field

```jinja
{{ textarea_field(
    name='description',
    label='Description',
    required=false,
    placeholder='Enter details...',
    help_text='Optional description',
    rows=3
) }}
```

### Checkbox Field

```jinja
{{ checkbox_field(
    name='is_active',
    label='Active',
    checked=true,
    help_text='Enable this item'
) }}
```

### Radio Group

```jinja
{{ radio_group(
    name='type',
    label='Type',
    options=[
        ('goods', 'Goods'),
        ('service', 'Service')
    ],
    required=true,
    selected='goods'
) }}
```

### Section Title

```jinja
{{ section_title('Sales Information', icon='💰') }}
```

---

## 📱 Mobile Responsive

The design system includes built-in responsive breakpoints:

- **Desktop (>768px)**: 2-3 column layouts
- **Mobile (≤768px)**: Single column, stacked layout

No extra work needed - it's automatic! 🎉

---

## 🚀 Migration Strategy

### DON'T:
- ❌ Refactor everything at once (too risky)
- ❌ Mix inline styles with classes (inconsistent)
- ❌ Create new inline styles (defeats the purpose)

### DO:
- ✅ Touch pages gradually as you work on them
- ✅ Use CSS classes for ALL new pages
- ✅ Convert old pages when editing them
- ✅ Document any custom additions

---

## 🎨 Color Palette

```css
Primary Blue:   #3498db
Dark Blue:      #2980b9
Dark Gray:      #2c3e50
Medium Gray:    #34495e
Light Gray:     #7f8c8d
Border Gray:    #dfe6e9
Background:     #f5f7fa
White:          #ffffff

Success Green:  #27ae60
Danger Red:     #e74c3c
Warning Yellow: #f39c12
```

---

## 💡 Best Practices

1. **Always use classes**, never inline styles
2. **Import macros** for complex forms
3. **Use semantic names** (`.field-label` not `.blue-text`)
4. **Keep spacing consistent** (use utility classes)
5. **Test on mobile** after changes
6. **Document custom classes** in forms.css

---

## 📝 Example: Creating a New Form

```jinja
{% extends "base_sidebar.html" %}
{% from "_form_macros.html" import text_field, number_field, section_title %}

{% block content %}
<form method="POST">
    <div class="card">
        {{ section_title('Basic Information', icon='📋') }}
        
        <div class="form-row">
            {{ text_field('name', 'Name', required=true) }}
            {{ text_field('email', 'Email', required=true) }}
        </div>
        
        <div class="form-row">
            {{ number_field('phone', 'Phone', required=true) }}
            {{ number_field('age', 'Age', min='0', step='1') }}
        </div>
        
        <div class="form-actions">
            <a href="{{ url_for('index') }}" class="btn btn-secondary">Cancel</a>
            <button type="submit" class="btn btn-primary">Save</button>
        </div>
    </div>
</form>
{% endblock %}
```

**That's it!** Clean, consistent, maintainable. 🎯

---

## 🆘 Troubleshooting

### Forms.css not loading?
- Check `base_sidebar.html` has the CSS link
- Clear browser cache (Ctrl+Shift+R)
- Check Vercel deployment includes `static/css/forms.css`

### Styles not applying?
- Make sure you're using exact class names
- Check for typos (`.form-group` not `.form-groups`)
- Use browser DevTools to inspect elements

### Macros not working?
- Import them at top: `{% from "_form_macros.html" import ... %}`
- Check macro name spelling
- Ensure _form_macros.html is in templates folder

---

## 🔮 Future Enhancements

- [ ] Add `.card` styles to forms.css
- [ ] Create table styling system
- [ ] Add animation utilities
- [ ] Create dashboard card components
- [ ] Add dark mode support
- [ ] Create icon system

---

**Questions?** Check `modular_app/templates/admin/items/add.html` for a complete, working example! ✨

