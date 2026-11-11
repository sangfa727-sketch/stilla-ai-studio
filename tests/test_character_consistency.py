import json
from pathlib import Path

import pytest

from stilla.characters.consistency import build_generation_plan
from stilla.characters.schema import (
    CharacterProfile,
    CharacterProfileError,
    CharacterReference,
    ComedyPersonality,
    VisualIdentity,
)
from stilla.characters.storage import (
    CharacterStorageError,
    load_character,
    save_character,
)


def sample_character() -> CharacterProfile:
    return CharacterProfile(
        id="pogo_01",
        name="Pogo",
        species_or_type="small round forest creature",
        visual=VisualIdentity(
            silhouette="pear-shaped body with short legs",
            body_proportions="head and torso form one rounded shape; short arms",
            face_shape="wide soft oval",
            eyes="large amber eyes with dark pupils and thick upper eyelids",
            nose="tiny triangular dark-brown nose",
            mouth="wide flexible smile with one visible tooth",
            primary_colors=("warm teal", "cream", "coral"),
            surface_or_skin_detail="fine soft fur",
            hairstyle_or_head_shape="two small leaf-like tufts",
            outfit="coral vest with two brass buttons",
            accessories=("tiny canvas satchel on left hip",),
            distinguishing_marks=("cream crescent patch above right eye",),
            art_style="original handcrafted 3D family cartoon",
            fixed_features=("left ear tip folds forward",),
        ),
        personality=ComedyPersonality(
            archetype="overconfident little inventor",
            core_traits=("curious", "loyal", "easily distracted"),
            strength="finds unusual solutions",
            comic_flaw="celebrates before checking whether the invention works",
            humor_mechanics=("visual misunderstanding", "delayed reaction", "harmless slapstick"),
            speech_pattern="fast explanations that trail into a whisper",
            catchphrase="I planned that. Mostly.",
            reaction_style="freezes, blinks twice, then pretends it was intentional",
            relationship_dynamic="competes playfully with a cautious best friend",
            running_gag="his inventions solve a tiny problem but create a sillier one",
        ),
        references=(CharacterReference("pogo_master", "characters/pogo/front.png", "front"),),
    )


def test_character_profile_round_trip_and_fingerprint() -> None:
    original = sample_character()
    loaded = CharacterProfile.from_dict(original.to_dict())
    assert loaded == original
    assert loaded.identity_fingerprint == original.identity_fingerprint


def test_fingerprint_changes_when_visual_anchor_changes() -> None:
    original = sample_character()
    changed_visual = VisualIdentity(
        silhouette="tall narrow body", body_proportions="long legs", face_shape="square",
        eyes="small blue eyes",
    )
    changed = CharacterProfile(id=original.id, name=original.name,
                               species_or_type=original.species_or_type, visual=changed_visual)
    assert changed.identity_fingerprint != original.identity_fingerprint


def test_generation_plan_locks_visual_identity_but_allows_scene_pose_and_expression() -> None:
    character = sample_character()
    plan = build_generation_plan(character, "Pogo slips on a leaf beside a garden gate.",
                                  pose="arms windmilling", expression="surprised")
    assert "pear-shaped body with short legs" in plan.prompt
    assert "coral vest with two brass buttons" in plan.prompt
    assert "arms windmilling" in plan.prompt
    assert "surprised" in plan.prompt
    assert plan.reference_paths == ("characters/pogo/front.png",)
    assert "changed costume" in plan.negative_prompt
    assert "outfit" in plan.locked_fields


def test_costume_change_requires_explicit_permission() -> None:
    character = sample_character()
    with pytest.raises(CharacterProfileError, match="explicit"):
        build_generation_plan(character, "At a winter festival", outfit_override="blue coat")
    plan = build_generation_plan(character, "At a winter festival",
                                 outfit_override="blue coat", allow_costume_change=True)
    assert "Outfit: blue coat." in plan.prompt


def test_scene_changes_do_not_change_identity_fingerprint() -> None:
    character = sample_character()
    first = build_generation_plan(character, "At the beach", pose="standing")
    second = build_generation_plan(character, "In a bakery", pose="sitting")
    assert first.identity_fingerprint == second.identity_fingerprint
    assert first.consistency_key != second.consistency_key


def test_rejects_reference_path_traversal_and_invalid_digest() -> None:
    with pytest.raises(CharacterProfileError):
        CharacterReference("ref_1", "../outside.png")
    with pytest.raises(CharacterProfileError):
        CharacterReference("ref_1", "characters/ref.png", sha256="not-a-digest")


def test_rejects_unknown_profile_fields_and_duplicate_references() -> None:
    data = sample_character().to_dict()
    data["execute"] = "not allowed"
    with pytest.raises(CharacterProfileError):
        CharacterProfile.from_dict(data)
    original = sample_character()
    with pytest.raises(CharacterProfileError, match="unique"):
        CharacterProfile(id="x", name="X", species_or_type="creature",
                         visual=original.visual,
                         references=(original.references[0], original.references[0]))


def test_save_and_load_character_atomically(tmp_path: Path) -> None:
    original = sample_character()
    path = save_character(tmp_path, original)
    assert path.name == "pogo_01.character.json"
    assert load_character(tmp_path, "pogo_01") == original


def test_storage_rejects_symlink_target(tmp_path: Path) -> None:
    original = sample_character()
    real = save_character(tmp_path, original)
    alias = tmp_path / "alias.character.json"
    try:
        alias.symlink_to(real)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable")
    with pytest.raises(CharacterStorageError, match="symbolic-link"):
        load_character(tmp_path, "alias")


def test_storage_rejects_malformed_json_without_leaking_contents(tmp_path: Path) -> None:
    (tmp_path / "broken.character.json").write_text('{"private":"do not disclose"', encoding="utf-8")
    with pytest.raises(CharacterStorageError, match="schema validation") as exc:
        load_character(tmp_path, "broken")
    assert "do not disclose" not in str(exc.value)
