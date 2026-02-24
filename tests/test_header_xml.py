"""Tests for header.xml structure.

Compares hwpxlib-generated header.xml against reference XML.
Spec: specs/03 through specs/07
"""
from xml.etree import ElementTree as ET

import pytest
from tests import NS


class TestFontFaces:
    """Spec: specs/03-header-fontfaces.md"""

    def test_fontface_count(self, ref_header_tree, generated_header_tree):
        ref_ff = ref_header_tree.findall(".//hh:fontface", NS)
        gen_ff = generated_header_tree.findall(".//hh:fontface", NS)
        assert len(gen_ff) == len(ref_ff) == 7

    def test_fontface_langs(self, ref_header_tree, generated_header_tree):
        ref_langs = [ff.get("lang") for ff in ref_header_tree.findall(".//hh:fontface", NS)]
        gen_langs = [ff.get("lang") for ff in generated_header_tree.findall(".//hh:fontface", NS)]
        assert gen_langs == ref_langs

    def test_font_count_per_face(self, ref_header_tree, generated_header_tree):
        for ref_ff, gen_ff in zip(
            ref_header_tree.findall(".//hh:fontface", NS),
            generated_header_tree.findall(".//hh:fontface", NS),
        ):
            ref_fonts = ref_ff.findall("hh:font", NS)
            gen_fonts = gen_ff.findall("hh:font", NS)
            lang = ref_ff.get("lang")
            assert len(gen_fonts) == len(ref_fonts), \
                f"Font count mismatch for {lang}: {len(gen_fonts)} vs {len(ref_fonts)}"

    def test_font_names(self, ref_header_tree, generated_header_tree):
        ref_fonts = ref_header_tree.findall(".//hh:fontface/hh:font", NS)
        gen_fonts = generated_header_tree.findall(".//hh:fontface/hh:font", NS)
        for ref_f, gen_f in zip(ref_fonts, gen_fonts):
            assert gen_f.get("face") == ref_f.get("face"), \
                f"Font face mismatch: {gen_f.get('face')} vs {ref_f.get('face')}"


class TestBorderFills:
    """Spec: specs/04-header-borderfills.md"""

    def test_borderfill_count(self, ref_header_tree, generated_header_tree):
        ref_bf = ref_header_tree.findall(".//hh:borderFill", NS)
        gen_bf = generated_header_tree.findall(".//hh:borderFill", NS)
        assert len(gen_bf) == len(ref_bf) == 6

    def test_borderfill_ids_are_1_based(self, generated_header_tree):
        bfs = generated_header_tree.findall(".//hh:borderFill", NS)
        ids = [int(bf.get("id")) for bf in bfs]
        assert ids == list(range(1, 7))

    def test_borderfill_attributes_match(self, ref_header_tree, generated_header_tree):
        ref_bfs = ref_header_tree.findall(".//hh:borderFill", NS)
        gen_bfs = generated_header_tree.findall(".//hh:borderFill", NS)
        for ref_bf, gen_bf in zip(ref_bfs, gen_bfs):
            bf_id = ref_bf.get("id")
            for attr in ["threeD", "shadow", "centerLine", "breakCellSeparateLine"]:
                assert gen_bf.get(attr) == ref_bf.get(attr), \
                    f"borderFill {bf_id} attr {attr}: {gen_bf.get(attr)} vs {ref_bf.get(attr)}"


class TestCharProperties:
    """Spec: specs/05-header-char-properties.md"""

    def test_charpr_count(self, ref_header_tree, generated_header_tree):
        ref_cp = ref_header_tree.findall(".//hh:charPr", NS)
        gen_cp = generated_header_tree.findall(".//hh:charPr", NS)
        assert len(gen_cp) == len(ref_cp) == 14

    def test_charpr_attributes_match(self, ref_header_tree, generated_header_tree):
        ref_cps = ref_header_tree.findall(".//hh:charPr", NS)
        gen_cps = generated_header_tree.findall(".//hh:charPr", NS)
        for ref_cp, gen_cp in zip(ref_cps, gen_cps):
            cp_id = ref_cp.get("id")
            for attr in ["height", "textColor", "shadeColor", "borderFillIDRef"]:
                assert gen_cp.get(attr) == ref_cp.get(attr), \
                    f"charPr {cp_id} attr {attr}: {gen_cp.get(attr)} vs {ref_cp.get(attr)}"

    def test_charpr_bold_italic_presence(self, ref_header_tree, generated_header_tree):
        """Bold/italic elements must match reference for each charPr."""
        ref_cps = ref_header_tree.findall(".//hh:charPr", NS)
        gen_cps = generated_header_tree.findall(".//hh:charPr", NS)
        for ref_cp, gen_cp in zip(ref_cps, gen_cps):
            cp_id = ref_cp.get("id")
            ref_bold = ref_cp.find("hh:bold", NS) is not None
            gen_bold = gen_cp.find("hh:bold", NS) is not None
            assert gen_bold == ref_bold, f"charPr {cp_id} bold: {gen_bold} vs {ref_bold}"

            ref_italic = ref_cp.find("hh:italic", NS) is not None
            gen_italic = gen_cp.find("hh:italic", NS) is not None
            assert gen_italic == ref_italic, f"charPr {cp_id} italic: {gen_italic} vs {ref_italic}"

    def test_charpr_fontref_match(self, ref_header_tree, generated_header_tree):
        ref_cps = ref_header_tree.findall(".//hh:charPr", NS)
        gen_cps = generated_header_tree.findall(".//hh:charPr", NS)
        for ref_cp, gen_cp in zip(ref_cps, gen_cps):
            cp_id = ref_cp.get("id")
            ref_fr = ref_cp.find("hh:fontRef", NS)
            gen_fr = gen_cp.find("hh:fontRef", NS)
            for attr in ["hangul", "latin", "hanja", "japanese", "other", "symbol", "user"]:
                assert gen_fr.get(attr) == ref_fr.get(attr), \
                    f"charPr {cp_id} fontRef.{attr}: {gen_fr.get(attr)} vs {ref_fr.get(attr)}"


class TestParaProperties:
    """Spec: specs/06-header-para-properties.md"""

    def test_parapr_count(self, ref_header_tree, generated_header_tree):
        ref_pp = ref_header_tree.findall(".//hh:paraPr", NS)
        gen_pp = generated_header_tree.findall(".//hh:paraPr", NS)
        # Generated has more paraPrs than reference (ordered list added)
        assert len(gen_pp) >= len(ref_pp)
        assert len(gen_pp) == 11

    def test_parapr_attributes_match(self, ref_header_tree, generated_header_tree):
        ref_pps = ref_header_tree.findall(".//hh:paraPr", NS)
        gen_pps = generated_header_tree.findall(".//hh:paraPr", NS)
        for ref_pp, gen_pp in zip(ref_pps, gen_pps):
            pp_id = ref_pp.get("id")
            for attr in ["tabPrIDRef", "condense", "fontLineHeight", "snapToGrid"]:
                assert gen_pp.get(attr) == ref_pp.get(attr), \
                    f"paraPr {pp_id} attr {attr}: {gen_pp.get(attr)} vs {ref_pp.get(attr)}"

    def test_parapr_heading_match(self, ref_header_tree, generated_header_tree):
        ref_pps = ref_header_tree.findall(".//hh:paraPr", NS)
        gen_pps = generated_header_tree.findall(".//hh:paraPr", NS)
        for ref_pp, gen_pp in zip(ref_pps, gen_pps):
            pp_id = ref_pp.get("id")
            ref_h = ref_pp.find("hh:heading", NS)
            gen_h = gen_pp.find("hh:heading", NS)
            for attr in ["type", "idRef", "level"]:
                assert gen_h.get(attr) == ref_h.get(attr), \
                    f"paraPr {pp_id} heading.{attr}: {gen_h.get(attr)} vs {ref_h.get(attr)}"


class TestStyles:
    """Spec: specs/07-header-styles-numbering.md"""

    def test_style_count(self, ref_header_tree, generated_header_tree):
        ref_st = ref_header_tree.findall(".//hh:style", NS)
        gen_st = generated_header_tree.findall(".//hh:style", NS)
        assert len(gen_st) == len(ref_st) == 7

    def test_style_langid(self, ref_header_tree, generated_header_tree):
        gen_styles = generated_header_tree.findall(".//hh:style", NS)
        for st in gen_styles:
            assert st.get("langID") == "1042", \
                f"Style {st.get('id')} langID must be 1042, got {st.get('langID')}"

    def test_style_attributes_match(self, ref_header_tree, generated_header_tree):
        ref_sts = ref_header_tree.findall(".//hh:style", NS)
        gen_sts = generated_header_tree.findall(".//hh:style", NS)
        for ref_st, gen_st in zip(ref_sts, gen_sts):
            st_id = ref_st.get("id")
            for attr in ["type", "name", "engName", "paraPrIDRef",
                          "charPrIDRef", "nextStyleIDRef", "langID"]:
                assert gen_st.get(attr) == ref_st.get(attr), \
                    f"style {st_id} attr {attr}: {gen_st.get(attr)} vs {ref_st.get(attr)}"
