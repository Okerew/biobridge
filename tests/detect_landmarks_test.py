from biobridge.tools.bpa import BodyPartAnalyzer


def test_detect_landmarks():
    analyzer = BodyPartAnalyzer()
    analyzer.detect_landmarks('image_examples/head.jpg')


test_detect_landmarks()
