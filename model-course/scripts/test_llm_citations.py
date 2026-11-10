"""Citation contracts with synthetic documents; not evidence of model quality."""
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "book/llm/examples/assistant/assistant.py"
spec = importlib.util.spec_from_file_location("course_assistant", SCRIPT)
assistant = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = assistant
spec.loader.exec_module(assistant)


def chunk(text, start=0, doc_id="sample", index=0):
    return assistant.Chunk(
        chunk_id=f"{doc_id}#{index}", doc_id=doc_id, title=doc_id, version="test",
        sha256=hashlib.sha256(text.encode()).hexdigest(), start=start,
        end=start + len(text), text=text,
    )


def extract(source, quote):
    return assistant.validate_extract_payload(
        {"status": "answered", "claims": [{"chunk_id": source.chunk_id, "quote": quote}]},
        {source.chunk_id: source},
    )


def engine(docs_path):
    return assistant.AssistantEngine(
        docs_path=docs_path, chunk_chars=100, chunk_overlap=20, provider="local",
        model_dir=None, embedding_dir=None, max_new_tokens=192, api_timeout=15,
        price_input=None, price_output=None,
    )


class CitationSpanTests(unittest.TestCase):
    def test_extract_system_example_matches_the_active_output_validator(self):
        source = chunk("资料中的连续原文片段")
        messages = assistant.build_fixed_messages([(source, 1.0)], "查找依据", "extract")
        example = next(line for line in messages[0]["content"].splitlines() if line.startswith("{"))
        payload = json.loads(example)
        payload["claims"][0]["chunk_id"] = source.chunk_id
        status, answer, claims = assistant.validate_extract_payload(payload, {source.chunk_id: source})
        self.assertEqual(status, "answered")
        self.assertEqual(answer, source.text)
        self.assertEqual(claims[0]["citations"][0]["quote"], source.text)
        # Copy retains its own schema; a copy example must not be accepted by extract.
        copy = assistant.build_fixed_messages([(source, 1.0)], "查找依据")
        copy_example = next(line for line in copy[0]["content"].splitlines() if line.startswith("{"))
        with self.assertRaises(assistant.AssistantFailure):
            assistant.validate_extract_payload(json.loads(copy_example), {source.chunk_id: source})

    def test_unicode_and_collapsed_whitespace_map_to_document_characters(self):
        prefix = "上一段\n\n"
        body = "  ## 🛰️ 记录\n温度\t\u00a0  4.2\n米每秒  \n结束。"
        quoted = "\t温度 4.2 米每秒\n"
        source = chunk(body, len(prefix))
        status, answer, claims = extract(source, quoted)
        citation = claims[0]["citations"][0]
        text = prefix + body
        self.assertEqual(status, "answered")
        self.assertEqual(answer, "温度 4.2 米每秒")
        self.assertEqual(citation["quote"], quoted)
        self.assertEqual(citation["quote_start"], text.index("温度"))
        self.assertEqual(citation["quote_end"], text.index("米每秒") + len("米每秒"))
        self.assertEqual((citation["start"], citation["end"]), (source.start, source.end))
        self.assertEqual(text[citation["quote_start"]:citation["quote_end"]], "温度\t\u00a0  4.2\n米每秒")

    def test_repeated_quote_uses_first_match_in_selected_chunk(self):
        source = chunk("  风速\t4.2。风速 4.2。", start=31)
        citation = extract(source, "风速 4.2")[2][0]["citations"][0]
        self.assertEqual((citation["quote_start"], citation["quote_end"]), (33, 39))

    def test_overlapping_chunks_locate_the_same_document_span(self):
        document = "第一段\n\n第二段 风速\t4.2 米每秒。\n\n第三段"
        second_start = document.index("第二段")
        sources = [chunk(document[:document.index("第三段")], 0, index=0),
                   chunk(document[second_start:], second_start, index=1)]
        positions = []
        for source in sources:
            citation = extract(source, "风速 4.2 米每秒")[2][0]["citations"][0]
            positions.append((citation["quote_start"], citation["quote_end"]))
        self.assertEqual(positions[0], positions[1])
        self.assertEqual(document[slice(*positions[0])], "风速\t4.2 米每秒")

    def test_bom_and_crlf_use_decoded_lf_text_but_hash_original_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = ("\ufeff" + "前置说明。" * 24 + "\r\n\r\n## 🛰️\r\n风速\t4.2 米每秒。\r结束。").encode()
            (root / "source.md").write_bytes(data)
            (root / "documents.json").write_text(json.dumps({
                "schema": "assistant-documents/1", "documents": [
                    {"id": "sample", "path": "source.md", "version": "test", "readers": ["student"]}
                ],
            }), encoding="utf-8")
            workspace = assistant.load_workspace(root / "documents.json", "student", 100, 20)
            document = workspace.documents[0]
            source = next(c for c in workspace.chunks if "风速" in c.text)
            citation = extract(source, "风速 4.2 米每秒")[2][0]["citations"][0]
            self.assertGreater(source.start, 0)
            self.assertEqual(document.sha256, hashlib.sha256(data).hexdigest())
            self.assertEqual(document.text[citation["quote_start"]:citation["quote_end"]], "风速\t4.2 米每秒")
            self.assertNotIn("\r", document.text)
            self.assertFalse(document.text.startswith("\ufeff"))

    def test_heading_removed_only_from_display_not_citation_span(self):
        source = chunk("\n## 记录\n风速 4.2\n")
        status, answer, claims = extract(source, "## 记录 风速 4.2")
        citation = claims[0]["citations"][0]
        self.assertEqual(answer, "记录 风速 4.2")
        self.assertEqual(source.text[citation["quote_start"]:citation["quote_end"]], "## 记录\n风速 4.2")

    def test_matching_does_not_fold_case_unicode_or_punctuation(self):
        for text, quoted in [("ABC 42", "abc 42"), ("编号ＡＢ", "编号AB"), ("café", "cafe\u0301"), ("甲，乙", "甲,乙")]:
            with self.subTest(text=text):
                self.assertIsNone(assistant.find_quote_span(text, quoted))

    def test_whitespace_variants_map_without_shifting_characters(self):
        for separator in (" ", "\t", "\n\n", "\r\n", "\u2003\u00a0", " \t\n"):
            with self.subTest(separator=separator):
                source = "\t🛰️甲" + separator + "乙。\n"
                span = assistant.find_quote_span(source, "🛰️甲 乙。")
                self.assertEqual(span, (1, len(source)-1))
                self.assertEqual(assistant.normalize_text(source[slice(*span)]), "🛰️甲 乙。")

    def test_missing_discontinuous_negated_and_invalid_length_quotes_fail(self):
        source = chunk("地点尚未确定。甲方负责，乙方核验。" + "长" * 301)
        for quoted in ("地点已确定。", "甲方乙方", "不存在的文本", "", "\t\n", "甲", "长" * 301):
            with self.subTest(quote=quoted), self.assertRaises(assistant.AssistantFailure) as caught:
                extract(source, quoted)
            self.assertEqual(caught.exception.status, "citation-failed")

    def test_model_supplied_offsets_or_claim_text_are_rejected(self):
        source = chunk("地点尚未确定。")
        for extra in ({"quote_start": 0}, {"text": "地点已确定。"}):
            with self.subTest(extra=extra), self.assertRaises(assistant.AssistantFailure) as caught:
                assistant.validate_extract_payload({"status":"answered", "claims":[{
                    "chunk_id":source.chunk_id, "quote":source.text, **extra,
                }]}, {source.chunk_id:source})
            self.assertEqual(caught.exception.status, "invalid-response")

    def test_conflict_requires_two_documents_and_preserves_both_spans(self):
        sources = [chunk("闭站 17:30", 14, "policy"), chunk("闭站 18:00", 28, "notice")]
        payload = {"status":"conflict", "claims":[{"chunk_id":s.chunk_id,"quote":s.text} for s in sources]}
        status, _, claims = assistant.validate_extract_payload(payload, {s.chunk_id:s for s in sources})
        self.assertEqual(status, "conflict")
        self.assertEqual([c["citations"][0]["quote_start"] for c in claims], [14,28])
        payload["claims"][1] = payload["claims"][0].copy()
        with self.assertRaises(assistant.AssistantFailure) as caught:
            assistant.validate_extract_payload(payload, {s.chunk_id:s for s in sources})
        self.assertEqual(caught.exception.status, "invalid-response")

    def test_insufficient_has_no_citations_and_cannot_smuggle_claims(self):
        result = assistant.validate_extract_payload({"status":"insufficient","claims":[]}, {})
        self.assertEqual(result, ("insufficient-evidence", "资料不足，无法回答。", []))
        source = chunk("风速 4.2")
        with self.assertRaises(assistant.AssistantFailure):
            assistant.validate_extract_payload({"status":"insufficient","claims":[{
                "chunk_id":source.chunk_id,"quote":source.text,
            }]}, {source.chunk_id:source})

    def test_default_copy_retains_fields_and_rejects_opposite_claim(self):
        source = chunk("地点尚未确定。")
        payload = {"status":"answered","answer":"尚未确定","claims":[{
            "text":"尚未确定","citations":[{"chunk_id":source.chunk_id,"quote":source.text}],
        }]}
        citation = assistant.validate_fixed_payload(payload,{source.chunk_id:source},[])[2][0]["citations"][0]
        self.assertEqual(set(citation), {"kind","chunk_id","doc_id","title","version","sha256","start","end","quote"})
        payload["answer"] = payload["claims"][0]["text"] = "地点已经确定。"
        with self.assertRaises(assistant.AssistantFailure) as caught:
            assistant.validate_fixed_payload(payload,{source.chunk_id:source},[])
        self.assertEqual(caught.exception.status, "citation-failed")

    def test_incompatible_mode_stops_before_document_or_model_access(self):
        runtime = engine(Path("must-not-be-read.json"))
        with patch.object(runtime,"workspace",side_effect=AssertionError("document access")), patch.object(runtime,"_get_chat_model",side_effect=AssertionError("model access")):
            report = assistant.run_pipeline(runtime, assistant.RunSettings("student","风速",mode="agent",claim_mode="extract"))
        self.assertEqual(report["status"], "invalid-request")
        self.assertEqual(report["config"]["claim_contract"], "source-extract/2")
        self.assertEqual(report["usage"]["calls"], 0)
        self.assertEqual(report["documents"], [])
        self.assertEqual(report["diagnostics"]["first_failure"]["stage"], "config")

    def test_markdown_displays_precise_span_and_accepts_legacy_reports(self):
        source = chunk("风速\t4.2", 10)
        claims = extract(source,"风速 4.2")[2]
        report = {"status":"answered","claims":claims}
        self.assertIn("[10, 16)", assistant.render_report_markdown(report))
        del claims[0]["citations"][0]["quote_start"]
        del claims[0]["citations"][0]["quote_end"]
        self.assertNotIn("摘录位置", assistant.render_report_markdown(report))


if __name__ == "__main__":
    unittest.main()
