---
layout: default
title: 翻译贡献指南
nav_order: 4
parent: Development Guide
---

# 翻译贡献指南

本指南说明如何为 RimSort 贡献翻译。项目使用 PySide6 的 Qt 国际化 (i18n) 系统和 QTranslator。

## 翻译系统概述

RimSort 使用 Qt 翻译系统，包含以下组件：
- **`.ts` 文件**：源翻译文件（XML 格式），供翻译者编辑
- **`.qm` 文件**：编译后的二进制翻译文件，供应用程序使用
- **QTranslator**：Qt 的翻译引擎，加载和应用翻译

## 项目结构

```
RimSort/
├── locales/           # 翻译文件目录
│   ├── en_US.ts      # 英语（源语言）
│   ├── zh_CN.ts      # 简体中文
│   ├── fr_FR.ts      # 法语
│   ├── de_DE.ts      # 德语
│   ├── es_ES.ts      # 西班牙语
│   └── ja_JP.ts      # 日语
└── app/
    └── controllers/
        └── language_controller.py  # 语言管理
```

## 当前支持的语言

| 语言代码 | 语言名称 | 状态 |
|----------|----------|------|
| `en_US` | English | 完整（源语言） |
| `zh_CN` | 简体中文 | 部分完成 |
| `fr_FR` | Français（法语） | 需要翻译 |
| `de_DE` | Deutsch（德语） | 需要翻译 |
| `es_ES` | Español（西班牙语） | 需要翻译 |
| `ja_JP` | 日本語（日语） | 需要翻译 |

## 如何贡献翻译

### 先决条件

1. **Qt Linguist**（推荐）或任何 XML 编辑器
   - 从 [Qt 官方网站](https://www.qt.io/download-qt-installer) 下载
   - 替代方案：使用任何文本编辑器编辑 XML

2. **Git** 版本控制
3. **GitHub 账户** 用于贡献

### 步骤 1：设置环境

1. 在 GitHub 上 Fork RimSort 仓库
2. 克隆你的 fork：
   ```bash
   git clone https://github.com/YOUR_USERNAME/RimSort.git
   cd RimSort
   ```

3. 为你的翻译创建新分支：
   ```bash
   git checkout -b translation-LANGUAGE_CODE
   # 例如：git checkout -b translation-pt_BR
   ```

### 步骤 2：选择贡献类型

#### 选项 A：改进现有翻译

1. 导航到 `locales/` 目录
2. 打开你的语言的现有 `.ts` 文件（例如 `zh_CN.ts`）
3. 查找标记为 `type="unfinished"` 或空的 `<translation>` 标签的条目

#### 选项 B：创建新语言翻译

1. 复制 `en_US.ts` 文件作为模板：
   ```bash
   cp locales/en_US.ts locales/NEW_LANGUAGE_CODE.ts
   # 例如：cp locales/en_US.ts locales/pt_BR.ts
   ```

2. 更新文件中的语言属性：
   ```xml
   <TS version="2.1" language="pt_BR">
   ```

3. 在 `app/controllers/language_controller.py` 中的支持语言映射中添加你的语言：
   ```python
   language_map = {
       "en_US": "English",
       "es_ES": "Español",
       "fr_FR": "Français",
       "de_DE": "Deutsch",
       "zh_CN": "简体中文",
       "ja_JP": "日本語",
       "pt_BR": "Português (Brasil)",  # 在这里添加你的语言
   }
   ```

### 步骤 3：翻译过程

#### 使用 Qt Linguist（推荐）

1. 打开 Qt Linguist
2. 文件 → 打开 → 选择你的 `.ts` 文件
3. 翻译每个字符串：
   - 从列表中选择未翻译的项目
   - 在"翻译"字段中输入你的翻译
   - 满意时标记为"完成"
   - 如需要可添加翻译者注释

4. 保存工作：文件 → 保存

#### 使用文本编辑器

1. 在你喜欢的文本编辑器中打开 `.ts` 文件
2. 找到需要翻译的 `<message>` 块：
   ```xml
   <message>
       <location filename="../app/views/settings_dialog.py" line="896"/>
       <source>Select Language (Restart required to apply changes)</source>
       <translation type="unfinished"></translation>
   </message>
   ```

3. 用你的文本替换空翻译并删除 `type="unfinished"`：
   ```xml
   <message>
       <location filename="../app/views/settings_dialog.py" line="896"/>
       <source>Select Language (Restart required to apply changes)</source>
       <translation>选择语言（需要重启以应用更改）</translation>
   </message>
   ```

### 步骤 4：翻译指南

#### 上下文理解

每个可翻译字符串都有上下文信息：
- **文件名**：显示包含该字符串的文件
- **行号**：源代码中的确切位置
- **上下文名称**：通常是类名（例如"SettingsDialog"、"ModInfo"）

#### 翻译最佳实践

1. **保留格式**：
   - 保持 `\n` 换行符
   - 维护 `%s`、`%d`、`{0}`、`{variable_name}` 占位符
   - 如果存在，保留 HTML 标签

2. **UI 考虑**：
   - 按钮标签保持简洁
   - 考虑文本扩展（某些语言需要更多空间）
   - 保持与应用程序一致的语调

3. **技术术语**：
   - "Mod" → 在大多数语言中通常保持为"Mod"
   - "Workshop" → 可以翻译或保持为"Workshop"
   - 软件特定术语应保持一致

#### 翻译示例

```xml
<!-- 英语源 -->
<source>Sort mods</source>
<translation>排序模组</translation>

<!-- 带占位符 -->
<source>Found {count} mods</source>
<translation>找到 {count} 个模组</translation>

<!-- 带换行符 -->
<source>Click OK to save settings\nand restart the application</source>
<translation>点击确定保存设置\n并重启应用程序</translation>
```

### 步骤 5：测试翻译

1. **生成编译翻译**（测试可选）：
   ```bash
   # 如果已安装 Qt 工具
   lrelease locales/YOUR_LANGUAGE.ts
   ```

2. **在开发环境中测试**：
   - 按照[开发设置指南](development-setup.zh-cn.md)设置开发环境
   - 在 RimSort 设置中更改语言
   - 验证翻译正确显示
   - 检查文本溢出或布局问题

### 步骤 6：提交贡献

1. **提交更改**：
   ```bash
   git add locales/YOUR_LANGUAGE.ts
   # 如果添加了新语言，也提交语言控制器更改
   git add app/controllers/language_controller.py
   git commit -m "添加/更新 [语言名称] 翻译"
   ```

2. **推送到你的 fork**：
   ```bash
   git push origin translation-LANGUAGE_CODE
   ```

3. **创建 Pull Request**：
   - 转到 GitHub 上的 fork
   - 点击"新建 Pull Request"
   - 选择你的翻译分支
   - 提供清晰的更改描述

## 翻译状态跟踪

你可以通过查找以下内容检查翻译完整性：
- `type="unfinished"` 条目（需要翻译）
- 空的 `<translation></translation>` 标签
- `type="obsolete"` 条目（可能需要审查）

## 维护和更新

### 当源代码更改时

1. **更新源字符串**：当开发者添加新的可翻译字符串时，他们会更新 `.ts` 文件
2. **翻译者通知**：我们将通过 GitHub issues 通知翻译者更新
3. **增量更新**：你只需要翻译新的或更改的字符串

### 翻译文件格式

`.ts` 文件使用 XML 格式，结构如下：
```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="LANGUAGE_CODE">
<context>
    <name>ClassName</name>
    <message>
        <location filename="../path/to/file.py" line="123"/>
        <source>English text</source>
        <translation>翻译文本</translation>
    </message>
</context>
</TS>
```

## 获取帮助

- **翻译问题**：创建带有"translation"标签的 issue
- **技术问题**：查看[开发设置指南](development-setup.zh-cn.md)
- **协作**：参加翻译相关 issues 的讨论
- **上下文说明**：在 pull request 评论中询问

## 认可

贡献者将在以下地方得到认可：
- `ACKNOWLEDGEMENTS.md` 文件
- 包含其翻译的版本发布说明
- GitHub 贡献者列表

感谢你帮助让 RimSort 为全世界用户提供服务！🌍