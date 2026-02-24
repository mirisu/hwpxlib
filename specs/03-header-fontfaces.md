# Spec 03: Header — Font Faces

## Scope
The `<hh:fontfaces>` section in header.xml defines available fonts for each language group.

## Acceptance Criteria
1. Exactly 7 fontface elements for languages: HANGUL, LATIN, HANJA, JAPANESE, OTHER, SYMBOL, USER
2. Each fontface has `fontCnt="2"` and contains 2 font elements
3. Font id=0: face="나눔고딕", type="TTF", isEmbedded="0"
4. Font id=1: face="나눔고딕코딩", type="TTF", isEmbedded="0"
5. Order must be HANGUL → LATIN → HANJA → JAPANESE → OTHER → SYMBOL → USER

## Test
`tests/test_header_xml.py::TestFontFaces`
