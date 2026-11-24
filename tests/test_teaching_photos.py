import sys
import unittest
from pathlib import Path
from io import BytesIO
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from acpa_msmda.teaching_photos import clean_photo
from acpa_msmda.pdf import scenario_pdf
from acpa_msmda import i18n

class TeachingPhotoTests(unittest.TestCase):
    def test_invalid_file(self):
        with self.assertRaises(ValueError):
            clean_photo(b"not an image")

    def test_photo_metadata_removed_and_pdf(self):
        raw = BytesIO()
        im = Image.new("RGB", (1800, 900), "green")
        exif = im.getexif()
        exif[270] = "private information"
        im.save(raw, format="JPEG", exif=exif)
        result = clean_photo(raw.getvalue())
        with Image.open(BytesIO(result)) as out:
            self.assertEqual(out.size, (1600, 800))
            self.assertFalse(out.getexif())
        i18n.use("fr")
        pdf = scenario_pdf({"APS":"Endurance"}, [{"Phase":"Apprentissage","Durée (min)":15}], {"balanced":True,"available_minutes":15}, [], photo=result)
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertIn(b"/Subtype /Image", pdf)
