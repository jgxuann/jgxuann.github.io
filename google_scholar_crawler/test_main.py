import unittest

from google_scholar_crawler.main import parse_profile_page


PROFILE_HTML = """
<html><body>
  <div id="gsc_prf_in">Example Author</div>
  <table id="gsc_rsb_st"><tbody><tr><td>Citations</td><td class="gsc_rsb_std">1,234</td></tr></tbody></table>
  <table>
    <tr class="gsc_a_tr">
      <td><a class="gsc_a_at">First &amp; Best Paper</a></td>
      <td class="gsc_a_c"><a class="gsc_a_ac">56</a></td>
    </tr>
    <tr class="gsc_a_tr">
      <td><a class="gsc_a_at">Uncited Paper</a></td>
      <td class="gsc_a_c"><a class="gsc_a_ac"></a></td>
    </tr>
  </table>
</body></html>
"""


class ProfileParserTests(unittest.TestCase):
    def test_parses_total_and_publication_citations(self):
        total, papers = parse_profile_page(PROFILE_HTML)
        self.assertEqual(total, 1234)
        self.assertEqual(papers, {"First & Best Paper": 56, "Uncited Paper": 0})

    def test_rejects_non_profile_page(self):
        with self.assertRaisesRegex(RuntimeError, "refusing to overwrite"):
            parse_profile_page("<html><body>Our systems detected unusual traffic</body></html>")


if __name__ == "__main__":
    unittest.main()
