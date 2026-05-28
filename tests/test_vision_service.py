import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from services.vision_service import VisionService


class FakeInsightFaceApp:
    def __init__(self, faces):
        self.faces = faces

    def get(self, image, max_num=1):
        if max_num == 0:
            return self.faces
        return self.faces[:max_num]


class VisionServiceTests(unittest.TestCase):
    def test_extract_face_embedding_uses_insightface_embedding(self):
        service = VisionService()
        image = np.zeros((120, 120, 3), dtype=np.uint8)
        face_crop = np.zeros((80, 80, 3), dtype=np.uint8)
        insightface_face = SimpleNamespace(
            bbox=np.array([0, 0, 80, 80]),
            normed_embedding=np.array([0.1, 0.2, 0.3], dtype=np.float32),
        )

        with (
            patch.object(service, "_decode_image", return_value=image),
            patch.object(
                service,
                "_detect_face",
                return_value={
                    "face_crop": face_crop,
                    "detector_used": "opencv-haar",
                    "faces_detected": 1,
                    "bounding_box": {"x1": 1, "y1": 2, "x2": 81, "y2": 82},
                },
            ),
            patch.object(
                service,
                "_get_insightface_app",
                return_value=FakeInsightFaceApp([insightface_face]),
            ),
        ):
            result = service.extract_face_embedding(b"image-bytes")

        self.assertTrue(result["success"])
        self.assertEqual(result["reason"], "face_detected")
        self.assertEqual(result["embedding_model"], "insightface")
        self.assertEqual(result["detector_used"], "opencv-haar+insightface")
        self.assertAlmostEqual(result["embedding"][0], 0.26726124, places=6)
        self.assertAlmostEqual(result["embedding"][1], 0.53452247, places=6)
        self.assertAlmostEqual(result["embedding"][2], 0.80178374, places=6)

    def test_extract_face_embedding_fails_when_insightface_has_no_embedding(self):
        service = VisionService()
        image = np.zeros((120, 120, 3), dtype=np.uint8)
        face_crop = np.zeros((80, 80, 3), dtype=np.uint8)

        with (
            patch.object(service, "_decode_image", return_value=image),
            patch.object(
                service,
                "_detect_face",
                return_value={
                    "face_crop": face_crop,
                    "detector_used": "opencv-haar",
                    "faces_detected": 1,
                    "bounding_box": {"x1": 1, "y1": 2, "x2": 81, "y2": 82},
                },
            ),
            patch.object(
                service,
                "_get_insightface_app",
                return_value=FakeInsightFaceApp([]),
            ),
        ):
            result = service.extract_face_embedding(b"image-bytes")

        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "face_embedding_failed")
        self.assertEqual(result["detector_used"], "opencv-haar+insightface")
        self.assertEqual(result["faces_detected"], 1)


if __name__ == "__main__":
    unittest.main()
