# Spec 01: ZIP Container

## Scope
The HWPX file is a ZIP/OPC container with strict ordering and compression rules.

## Acceptance Criteria
1. The first ZIP entry MUST be `mimetype` with compression method STORED (not DEFLATED)
2. The `mimetype` entry content MUST be exactly `application/hwp+zip` (19 bytes, no newline)
3. All other entries MUST use DEFLATED compression
4. Required entries:
   - `mimetype`
   - `version.xml`
   - `settings.xml`
   - `META-INF/container.xml`
   - `META-INF/manifest.xml`
   - `META-INF/container.rdf`
   - `Contents/content.hpf`
   - `Contents/header.xml`
   - `Contents/section0.xml`
   - `Preview/PrvText.txt`

## Test
`tests/test_zip_container.py`
