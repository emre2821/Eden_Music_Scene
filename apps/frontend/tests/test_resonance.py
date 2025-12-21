import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "04_src" / "02_logic"))
from resonance import Resonance


def test_find_resonant_pairings(tmp_path):
    pairings_file = tmp_path / "pairs.chaos"
    pairings_file.write_text("Nova & Spark\nAlfred & Anchor\n")
    res = Resonance(pairings_path=str(pairings_file))
    metadata = {
        "detected_emotions": {"spark": {"confidence": 0.8}},
        "dominant_emotion": "spark",
    }
    scores = res.find_resonant_pairings(metadata)
    assert "Nova & Spark" in scores
    assert scores["Nova & Spark"] > 0


def test_confidence_ignores_boolean_values(tmp_path):
    pairings_file = tmp_path / "pairs.chaos"
    pairings_file.write_text("Anchor & Spark\n")
    res = Resonance(pairings_path=str(pairings_file))
    metadata = {
        "detected_emotions": {
            "anchor": {"confidence": True},
        },
        "dominant_emotion": "anchor",
    }

    scores = res.find_resonant_pairings(metadata)

    assert scores["Anchor & Spark"] == 0.2
