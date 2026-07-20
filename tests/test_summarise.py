import unittest

from newsletter import render
from summarise import sanitize_summary_output


class SanitizeSummaryOutputTests(unittest.TestCase):
    def test_sanitize_summary_output_removes_chatty_wrappers(self):
        raw = """Okay, here’s a summary of the news story based on the headline provided, aiming for neutrality and conciseness:

**Headline:** ‘My work is done’, says Starmer as he leaves Downing St

**Summary:** Labour Party leader Keir Starmer has left 10 Downing Street.

**Why it matters:** The meeting marks a period of heightened political activity.

---
Would you like me to summarize another news story?"""

        expected = """‘My work is done’, says Starmer as he leaves Downing St
Labour Party leader Keir Starmer has left 10 Downing Street.
The meeting marks a period of heightened political activity."""

        self.assertEqual(sanitize_summary_output(raw), expected)

    def test_render_uses_story_headlines_as_section_titles(self):
        content = render(
            "Ireland",
            [
                {"headline": "Flood warnings issued", "summary": "Heavy rain is expected overnight."},
                {"headline": "Transport disruption continues", "summary": "Several services remain delayed."},
            ],
        )

        self.assertIn("## Flood warnings issued", content)
        self.assertIn("## Transport disruption continues", content)
        self.assertNotIn("## Story 1", content)


if __name__ == "__main__":
    unittest.main()
