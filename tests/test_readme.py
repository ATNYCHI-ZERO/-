import pathlib
import unittest


class TestReadmeStructure(unittest.TestCase):
    def setUp(self):
        self.readme_path = pathlib.Path(__file__).resolve().parents[1] / "README.md"
        self.content = self.readme_path.read_text(encoding="utf-8")

    def test_readme_exists(self):
        self.assertTrue(self.readme_path.exists(), "README.md should exist for DARPA audit compliance")

    def test_required_sections_present(self):
        required_sections = [
            "Abstract",
            "1. The Myth of the Perfect Circle",
            "2. The Harmonic Fingerprint of Matter",
            "3. A New Philosophy of Repair: Resonance Restoration",
            "4. Turning an Object into a Number, and Back Again",
            "5. What This Means for the Future",
            "Conclusion: A Universe of Echoes",
        ]
        for section in required_sections:
            with self.subTest(section=section):
                self.assertIn(section, self.content)


if __name__ == "__main__":
    unittest.main()
