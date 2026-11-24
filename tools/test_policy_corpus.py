import re
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
POLICY_DIR = ROOT_DIR / "data" / "policies"
QUESTION_FILE = ROOT_DIR / "evals" / "rag" / "no_policy_questions.md"

EXPECTED_POLICY_IDS = [f"SD-{number:03d}" for number in range(1, 21)]
EXPECTED_QUESTION_IDS = [f"NP-{number:03d}" for number in range(1, 11)]
INTENTIONAL_CONFLICT_PAIRS = (
    ("SD-002", "SD-003"),
    ("SD-004", "SD-005"),
    ("SD-010", "SD-011"),
    ("SD-014", "SD-015"),
)
CONFLICT_INDEX_STATEMENTS = (
    "**Escalation:** SD-002 and SD-003 set different manager-review day thresholds.",
    "**Grace period:** SD-004 allows five calendar days; SD-005 says no grace period applies.",
    "**Contact cadence:** SD-010 allows contact every three business days; SD-011 sets five business days.",
    "**Balance review:** SD-014 sets a threshold above EGP 50,000; SD-015 says only balances above EGP 100,000 qualify.",
)
CONFLICT_STATEMENTS = {
    "SD-002": (
        "In this sample, an invoice more than 15 calendar days overdue requires Finance Manager review before a collector proceeds with a new collection recommendation.",
        "في هذه العينة، تتطلب الفاتورة التي تجاوز تأخرها 15 يومًا تقويميًا مراجعة المدير المالي قبل أن يتابع المحصّل توصية تحصيل جديدة.",
    ),
    "SD-003": (
        "In this sample, Finance Manager review is required only when an invoice is 30 or more calendar days overdue. This document does not identify itself as replacing another sample.",
        "في هذه العينة، تلزم مراجعة المدير المالي فقط عندما يبلغ تأخر الفاتورة 30 يومًا تقويميًا أو أكثر. ولا تنص هذه الوثيقة على أنها تحل محل عينة أخرى.",
    ),
    "SD-004": (
        "For this sample, an invoice has a grace period of five calendar days after its due date. It is treated as overdue only after that period ends.",
        "لأغراض هذه العينة، تتمتع الفاتورة بمهلة سماح مدتها خمسة أيام تقويمية بعد تاريخ الاستحقاق، ولا تُعامل على أنها متأخرة إلا بعد انتهاء المهلة.",
    ),
    "SD-005": (
        "For this sample, no grace period applies. An invoice is overdue starting on the calendar day after its due date.",
        "لأغراض هذه العينة، لا توجد مهلة سماح. تُعد الفاتورة متأخرة بدءًا من اليوم التقويمي التالي لتاريخ استحقاقها.",
    ),
    "SD-010": (
        "For this sample, do not make more than one collection contact attempt to the same account within any three-business-day period.",
        "لأغراض هذه العينة، لا تُجرَ أكثر من محاولة تواصل تحصيلي واحدة مع الحساب نفسه خلال أي فترة من ثلاثة أيام عمل.",
    ),
    "SD-011": (
        "For this sample, do not make more than one collection contact attempt to the same account within any five-business-day period.",
        "لأغراض هذه العينة، لا تُجرَ أكثر من محاولة تواصل تحصيلي واحدة مع الحساب نفسه خلال أي فترة من خمسة أيام عمل.",
    ),
    "SD-014": (
        "In this sample, balances above EGP 50,000 require Finance Manager review. This sample uses EGP 50,000 as its sole review threshold.",
        "في هذه العينة، تتطلب الأرصدة التي تتجاوز 50,000 جنيه مصري مراجعة المدير المالي. ويُستخدم مبلغ 50,000 جنيه مصري وحده كحد للمراجعة في هذه العينة.",
    ),
    "SD-015": (
        "In this sample, only balances above EGP 100,000 require Finance Manager review; balances at or below EGP 100,000 do not require it under this rule.",
        "في هذه العينة، تتطلب الأرصدة التي تتجاوز 100,000 جنيه مصري فقط مراجعة المدير المالي؛ أما الأرصدة التي تساوي هذا المبلغ أو تقل عنه فلا تتطلبها بموجب هذه القاعدة.",
    ),
}


class PolicyCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy_files = sorted(POLICY_DIR.glob("SD-*.md"))
        cls.policy_texts = {
            path.name: path.read_text(encoding="utf-8") for path in cls.policy_files
        }
        cls.policy_index = (POLICY_DIR / "README.md").read_text(encoding="utf-8")
        cls.question_text = QUESTION_FILE.read_text(encoding="utf-8")
        cls.question_lines = [
            line
            for line in cls.question_text.splitlines()
            if re.match(r"^\|\s*NP-", line)
        ]

    def test_exactly_20_policy_documents_exist(self):
        self.assertEqual(len(self.policy_files), 20)

    def test_policy_ids_are_unique_and_sequential(self):
        policy_ids = []
        for path in self.policy_files:
            match = re.fullmatch(r"(SD-\d{3})-[a-z0-9-]+\.md", path.name)
            self.assertIsNotNone(match, path.name)
            if match is not None:
                policy_ids.append(match.group(1))

        self.assertEqual(len(policy_ids), len(set(policy_ids)))
        self.assertEqual(policy_ids, EXPECTED_POLICY_IDS)

    def test_policy_ids_match_filenames_headings_and_citations(self):
        for path in self.policy_files:
            with self.subTest(document=path.name):
                filename_match = re.match(r"(SD-\d{3})-", path.name)
                self.assertIsNotNone(filename_match)
                if filename_match is None:
                    continue
                policy_id = filename_match.group(1)
                text = self.policy_texts[path.name]
                heading_ids = re.findall(r"^# (SD-\d{3})(?=\s|$)", text, re.MULTILINE)
                citations = re.findall(
                    r"^\*\*Type:\*\* [^\r\n]*\*\*Citation:\*\* "
                    r"(SD-\d{3}), §(\d+\.\d+)$",
                    text,
                    re.MULTILINE,
                )

                self.assertEqual(heading_ids, [policy_id])
                self.assertEqual(len(citations), 1)
                if citations:
                    self.assertEqual(citations[0][0], policy_id)

    def test_each_policy_has_english_and_arabic_sections(self):
        for path in self.policy_files:
            with self.subTest(document=path.name):
                text = self.policy_texts[path.name]
                self.assertRegex(text, r"(?m)^## English$")
                self.assertRegex(text, r"(?m)^## العربية$")

    def test_policy_section_numbers_match_citation_metadata(self):
        for path in self.policy_files:
            with self.subTest(document=path.name):
                text = self.policy_texts[path.name]
                citations = re.findall(
                    r"^\*\*Type:\*\* [^\r\n]*\*\*Citation:\*\* "
                    r"SD-\d{3}, §(\d+\.\d+)$",
                    text,
                    re.MULTILINE,
                )
                section_numbers = re.findall(r"^### §(\d+\.\d+)\s", text, re.MULTILINE)

                self.assertEqual(len(citations), 1)
                self.assertEqual(len(section_numbers), 2)
                if citations:
                    self.assertEqual(section_numbers, [citations[0]] * 2)

    def test_every_policy_has_synthetic_label(self):
        for path in self.policy_files:
            with self.subTest(document=path.name):
                self.assertRegex(self.policy_texts[path.name], r"\bSYNTHETIC\b")

    def test_exactly_10_no_policy_questions_exist(self):
        self.assertEqual(len(self.question_lines), 10)

    def test_question_ids_are_unique_and_sequential(self):
        question_ids = [self._question_cells(line)[0] for line in self.question_lines]

        self.assertEqual(len(question_ids), len(set(question_ids)))
        self.assertEqual(question_ids, EXPECTED_QUESTION_IDS)

    def test_every_question_has_language_text_and_no_citation(self):
        self.assertIn(
            "| ID | Language | Question | Expected citation |", self.question_text
        )
        for line in self.question_lines:
            with self.subTest(row=line):
                cells = self._question_cells(line)
                self.assertEqual(len(cells), 4)
                if len(cells) == 4:
                    self.assertIn(cells[1], {"English", "Arabic"})
                    self.assertTrue(cells[2])
                    self.assertEqual(cells[3], "None")

    def test_intentional_conflicts_remain_unchanged(self):
        self.assertIn("## Deliberate conflicts", self.policy_index)
        for statement in CONFLICT_INDEX_STATEMENTS:
            self.assertIn(statement, self.policy_index)

        for first_id, second_id in INTENTIONAL_CONFLICT_PAIRS:
            with self.subTest(pair=(first_id, second_id)):
                for policy_id, other_id in (
                    (first_id, second_id),
                    (second_id, first_id),
                ):
                    path = next(
                        path
                        for path in self.policy_files
                        if path.name.startswith(f"{policy_id}-")
                    )
                    text = self.policy_texts[path.name]
                    self.assertIn(f"deliberately conflicts with {other_id}", text)
                    for statement in CONFLICT_STATEMENTS[policy_id]:
                        self.assertIn(statement, text)

    @staticmethod
    def _question_cells(line):
        return [cell.strip() for cell in line.strip().strip("|").split("|")]


if __name__ == "__main__":
    unittest.main()
