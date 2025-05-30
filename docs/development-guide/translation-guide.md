---
layout: default
title: Translation Contribution Guide
nav_order: 4
parent: Development Guide
---

# Translation Contribution Guide

This guide explains how to contribute translations to RimSort. The project uses PySide6's Qt internationalization (i18n) system with QTranslator.

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

## How to Contribute Translations

### Prerequisites

1. **Qt Linguist** (recommended) or any XML editor
   - Download from [Qt official website](https://www.qt.io/download-qt-installer)
   - Alternative: Use any text editor for XML editing

2. **Git** for version control
3. **GitHub account** for contributing

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

1. Navigate to the `locales/` directory
2. Open the existing `.ts` file for your language (e.g., `zh_CN.ts`)
3. Look for entries marked as `type="unfinished"` or empty `<translation>` tags

#### Option B: Create New Language Translation

1. Copy the `en_US.ts` file as a template:
   ```bash
   cp locales/en_US.ts locales/NEW_LANGUAGE_CODE.ts
   # Example: cp locales/en_US.ts locales/pt_BR.ts
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

#### Using Qt Linguist (Recommended)

1. Open Qt Linguist
2. File → Open → Select your `.ts` file
3. Translate each string:
   - Select an untranslated item from the list
   - Enter your translation in the "Translation" field
   - Mark as "Done" when satisfied
   - Add translator comments if needed

4. Save your work: File → Save

#### Using Text Editor

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

### Step 4: Translation Guidelines

#### Context Understanding

Each translatable string has context information:
- **Filename**: Shows which file contains the string
- **Line number**: Exact location in the source code
- **Context name**: Usually the class name (e.g., "SettingsDialog", "ModInfo")

#### Translation Best Practices

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

```xml
<!-- English source -->
<source>Sort mods</source>
<translation>Organizar mods</translation>

<!-- With placeholders -->
<source>Found {count} mods</source>
<translation>Encontrados {count} mods</translation>

<!-- With line breaks -->
<source>Click OK to save settings\nand restart the application</source>
<translation>Clique em OK para salvar as configurações\ne reiniciar a aplicação</translation>
```

### Step 5: Testing Your Translation

1. **Generate compiled translation** (optional for testing):
   ```bash
   # If you have Qt tools installed
   lrelease locales/YOUR_LANGUAGE.ts
   ```

2. **Test in development environment**:
   - Set up the development environment following the [Development Setup Guide](development-setup.md)
   - Change the language in RimSort settings
   - Verify your translations appear correctly
   - Check for text overflow or layout issues

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

1. **Update source strings**: When developers add new translatable strings, they update the `.ts` files
2. **Translator notification**: We'll notify translators of updates via GitHub issues
3. **Incremental updates**: You only need to translate new or changed strings

### Translation File Format

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

## Getting Help

- **Questions about translation**: Open an issue with the "translation" label
- **Technical problems**: Check the [Development Setup Guide](development-setup.md)
- **Collaboration**: Join discussions in translation-related issues
- **Context clarification**: Ask in the pull request comments

## Recognition

Contributors will be acknowledged in:
- `ACKNOWLEDGEMENTS.md` file
- Release notes for versions containing their translations
- GitHub contributors list

Thank you for helping make RimSort accessible to users worldwide! 🌍