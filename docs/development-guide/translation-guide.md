---
layout: default
title: Translation Contribution Guidelines
nav_order: 4
parent: Development Guide
permalink: development-guide/translation-contribution-guidelines
---

# Translation Contribution Guide
{: .no_toc}

This guide explains how to contribute translations to RimSort. The project uses PySide6's Qt internationalization (i18n) system with QTranslator.

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

## Translation System Overview

RimSort uses Qt's translation system with the following components:
- **`.ts` files**: Source translation files (XML format) that translators edit
- **`.qm` files**: Compiled binary translation files used by the application
- **QTranslator**: Qt's translation engine that loads and applies translations

## Project Structure

```
RimSort/
├── locales/           # Translation files directory
│   ├── en_US.ts      # English (source language)
│   ├── zh_CN.ts      # Simplified Chinese
│   ├── fr_FR.ts      # French
│   ├── de_DE.ts      # German
│   ├── es_ES.ts      # Spanish
│   └── ja_JP.ts      # Japanese
└── app/
    └── controllers/
        └── language_controller.py  # Language management
```

## Currently Supported Languages

| Language Code | Language Name | Status |
|---------------|---------------|--------|
| `en_US` | English | Complete (source) |
| `zh_CN` | 简体中文 (Simplified Chinese) | Partial |
| `fr_FR` | Français (French) | Needs translation |
| `de_DE` | Deutsch (German) | Needs translation |
| `es_ES` | Español (Spanish) | Needs translation |
| `ja_JP` | 日本語 (Japanese) | Needs translation |

## Translation Helper Tool

The project provides a `translation_helper.py` script to assist with translation work.

**Important Note**: This tool is implemented using PySide6 commands and requires a properly configured development environment. Please refer to the [Development Setup Guide](development-setup.md) to set up your environment before using this tool.

```bash
# Check translation completeness for a specific language
python translation_helper.py check en_US

# Show translation statistics for all languages
python translation_helper.py stats

# Validate translation file
python translation_helper.py validate en_US

# Update translation files
python translation_helper.py update-ts en_US

# Compile translation file
python translation_helper.py compile en_US

# Compile all translation files
python translation_helper.py compile-all
```

## How to Contribute Translations

### Prerequisites

1. **Development Environment**
   - **Required**: Set up the project development environment following the [Development Setup Guide](development-setup.md)
   - This includes installing Python 3.12, PySide6, and project dependencies

2. **Translation Editor Choice**
   - **Recommended**: Any text editor with XML syntax highlighting (VS Code, Sublime Text, Notepad++, etc.)
   - **Optional**: Qt Linguist (if you already have Qt development environment installed)

3. **Git** for version control
4. **GitHub account** for contributing

### Step 1: Set Up Your Environment

1. Fork the RimSort repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/RimSort.git
   cd RimSort
   ```

3. Create a new branch for your translation:
   ```bash
   git checkout -b translation-LANGUAGE_CODE
   # Example: git checkout -b translation-pt_BR
   ```

### Step 2: Choose Your Contribution Type

#### Option A: Improve Existing Translation
{: .no_toc}

1. Navigate to the `locales/` directory
2. Open the existing `.ts` file for your language (e.g., `en_US.ts`)
3. Look for entries marked as `type="unfinished"` or empty `<translation>` tags

#### Option B: Create New Language Translation
{: .no_toc}

1. Use PySide6 tools to generate new translation file:
   ```bash
   # For Unix-like systems (Linux/macOS)
   pyside6-lupdate $(find app -name "*.py") -ts locales/NEW_LANGUAGE_CODE.ts -no-obsolete
   # Example:
   pyside6-lupdate $(find app -name "*.py") -ts locales/pt_BR.ts -no-obsolete
   ```

   ```powershell
   # For Windows PowerShell
   pyside6-lupdate @(Get-ChildItem -Recurse -Filter *.py -Path app | ForEach-Object { $_.FullName }) -ts locales\NEW_LANGUAGE_CODE.ts -no-obsolete
   # Example:
   pyside6-lupdate @(Get-ChildItem -Recurse -Filter *.py -Path app | ForEach-Object { $_.FullName }) -ts locales\pt_BR.ts -no-obsolete
   ```

2. Update the language attribute in the file:
   ```xml
   <TS version="2.1" language="pt_BR">
   ```

3. Add your language to the supported languages map in `app/controllers/language_controller.py`:
   ```python
   language_map = {
       "en_US": "English",
       "es_ES": "Español",
       "fr_FR": "Français",
       "de_DE": "Deutsch",
       "zh_CN": "简体中文",
       "ja_JP": "日本語",
       "pt_BR": "Português (Brasil)",  # Add your language here
   }
   ```

### Step 3: Translation Process

#### Using Text Editor (Recommended)
{: .no_toc}

1. Open the `.ts` file in your preferred text editor
2. Find `<message>` blocks that need translation:
   ```xml
   <message>
       <location filename="../app/views/settings_dialog.py" line="896"/>
       <source>Select Language (Restart required to apply changes)</source>
       <translation type="unfinished"></translation>
   </message>
   ```

3. Replace the empty translation with your text and remove `type="unfinished"`:
   ```xml
   <message>
       <location filename="../app/views/settings_dialog.py" line="896"/>
       <source>Select Language (Restart required to apply changes)</source>
       <translation>Selecionar Idioma (Reinicialização necessária para aplicar as alterações)</translation>
   </message>
   ```

#### Using Qt Linguist (Optional)
{: .no_toc}

If you already have Qt Linguist installed, you can also use it:

1. Open Qt Linguist
2. File → Open → Select your `.ts` file
3. Translate each string:
   - Select an untranslated item from the list
   - Enter your translation in the "Translation" field
   - Mark as "Done" when satisfied
   - Add translator comments if needed

4. Save your work: File → Save

### Step 4: Translation Guidelines

#### Context Understanding
{: .no_toc}

Each translatable string has context information:
- **Filename**: Shows which file contains the string
- **Line number**: Exact location in the source code
- **Context name**: Usually the class name (e.g., "SettingsDialog", "ModInfo")

#### Translation Best Practices
{: .no_toc}

1. **Preserve formatting**:
   - Keep `\n` for line breaks
   - Maintain `%s`, `%d`, `{0}`, `{variable_name}` placeholders
   - Preserve HTML tags if present

2. **UI considerations**:
   - Keep translations concise for button labels
   - Consider text expansion (some languages need more space)
   - Maintain the tone consistent with the application

3. **Technical terms**:
   - "Mod" → Usually kept as "Mod" in most languages
   - "Workshop" → May translate or keep as "Workshop"
   - Software-specific terms should be consistent

#### Example Translation
{: .no_toc}

```xml
<!-- English source -->
<source>Sort mods</source>
<translation>Organizar mods</translation>

<!-- With placeholders -->
<source>Found {count} mods</source>
<translation>Encontrados {count} mods</translation>

<!-- With line breaks -->
<source>Click OK to save settings
and restart the application</source>
<translation>Clique em OK para salvar as configurações
e reiniciar a aplicação</translation>
```

### Step 5: Testing Your Translation

#### 5.1 Validate Translation File
{: .no_toc}

1. **Check translation completeness**:
   ```bash
   python translation_helper.py check YOUR_LANGUAGE
   # Example: python translation_helper.py check zh_CN
   ```

2. **Validate translation file**:
   ```bash
   python translation_helper.py validate YOUR_LANGUAGE
   # This checks for placeholder mismatches, HTML tag issues, etc.
   ```

3. **View overall statistics**:
   ```bash
   python translation_helper.py stats
   # Shows completion status for all languages
   ```

#### 5.2 Compile Translation
{: .no_toc}

1. **Using translation helper tool** (recommended):
   ```bash
   python translation_helper.py compile YOUR_LANGUAGE
   # Example: python translation_helper.py compile en_US
   ```

2. **Using PySide6 tools directly**:
   ```bash
   pyside6-lrelease locales/YOUR_LANGUAGE.ts
   ```

#### 5.3 Test in Application
{: .no_toc}

1. **Launch RimSort and switch language**:
   - Start the application
   - Go to Settings → Language
   - Select your language
   - Restart the application when prompted

2. **Basic UI testing**:
   - Check main interface menu items, buttons, tooltips
   - Verify settings dialog options are translated
   - Test mod listing, sorting, filtering labels

3. **Layout checks**:
   - Ensure translated text fits in UI elements
   - Check if buttons accommodate longer text
   - Verify dialog dimensions remain proper

### Step 6: Submit Your Contribution

1. **Commit your changes**:
   ```bash
   git add locales/YOUR_LANGUAGE.ts
   # If you added a new language, also commit the language controller changes
   git add app/controllers/language_controller.py
   git commit -m "Add/Update [Language Name] translation"
   ```

2. **Push to your fork**:
   ```bash
   git push origin translation-LANGUAGE_CODE
   ```

3. **Create Pull Request**:
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your translation branch
   - Provide a clear description of your changes

## Translation Status Tracking

You can check translation completeness by looking for:
- `type="unfinished"` entries (need translation)
- Empty `<translation></translation>` tags
- `type="obsolete"` entries (may need review)

## Maintenance and Updates

### When Source Code Changes

Translation files may need updates. You can:

1. **Self-update translation files**: Use the translation helper tool to generate updated translation files
   ```bash
   python translation_helper.py update-ts YOUR_LANGUAGE
   ```

2. **Incremental updates**: You only need to translate new or changed strings

### Translation File Format
{: .no_toc}

The `.ts` files use XML format with this structure:
```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="LANGUAGE_CODE">
<context>
    <name>ClassName</name>
    <message>
        <location filename="../path/to/file.py" line="123"/>
        <source>English text</source>
        <translation>Translated text</translation>
    </message>
</context>
</TS>
```

Thank you for helping make RimSort accessible to users worldwide! 🌍