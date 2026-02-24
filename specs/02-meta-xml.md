# Spec 02: Meta XML Files

## Scope
version.xml, settings.xml, container.xml, manifest.xml, container.rdf, and content.hpf must match the reference HWPX structure.

## Acceptance Criteria
1. `version.xml`: Root `<hv:HCFVersion>` with attrs `tagetApplication="WORDPROCESSOR"`, `major="5"`, `minor="1"`, `micro="1"`, `buildNumber="0"`, `os="1"`, `xmlVersion="1.5"`, `application="Hancom Office Hangul"`, `appVersion="12.0.0.1"`
2. `settings.xml`: Root `<ha:HWPApplicationSetting>` with `CaretPosition` and `PrintInfo` config items
3. `container.xml`: Must reference `Contents/content.hpf`, `Preview/PrvText.txt`, `META-INF/container.rdf`
4. `container.rdf`: Must declare `Contents/header.xml` as HeaderFile and `Contents/section0.xml` as SectionFile
5. `content.hpf`: Must list `header`, `section0`, and `settings` in manifest and spine

## Test
`tests/validate_xml.py`
