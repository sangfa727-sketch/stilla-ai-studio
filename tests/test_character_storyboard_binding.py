from __future__ import annotations

import pytest

from stilla.characters.schema import CharacterProfile, VisualIdentity
from stilla.characters.storyboard import (
    CharacterBoundShotPlan,
    CharacterRevisionSnapshot,
    ShotCharacterBinding,
    StoryboardBindingError,
    bind_character_to_shots,
)
from stilla.planning.schema import Shot, ShotPlan


def profile(character_id: str = "char_a", name: str = "Milo") -> CharacterProfile:
    return CharacterProfile(
        id=character_id,
        name=name,
        species_or_type="Original cartoon creature",
        visual=VisualIdentity(
            silhouette="round pear-shaped body",
            body_proportions="large head, short legs",
            face_shape="oval",
            eyes="large amber eyes",
            primary_colors=("teal", "cream"),
            outfit="orange vest",
            fixed_features=("one bent antenna",),
        ),
    )


def shot_plan() -> ShotPlan:
    return ShotPlan(
        id="plan_01",
        title="Morning mishap",
        shots=(
            Shot("shot_01", "frame_01", "A creature opens a bakery door."),
            Shot("shot_02", "frame_02", "The creature drops a tray of buns."),
        ),
    )


def empty_document() -> CharacterBoundShotPlan:
    return CharacterBoundShotPlan(shot_plan=shot_plan())


def test_bind_character_to_all_shots_and_compile_generation_plans() -> None:
    bound = bind_character_to_shots(empty_document(), profile(), revision=1)

    assert len(bound.bindings) == 2
    assert {item.shot_id for item in bound.bindings} == {"shot_01", "shot_02"}
    assert all(item.profile_revision == 1 for item in bound.bindings)
    plans = bound.compile_shot("shot_01")
    assert len(plans) == 1
    assert "Milo" in plans[0].prompt
    assert plans[0].identity_fingerprint == profile().identity_fingerprint


def test_binding_selected_shot_only_preserves_other_shots_unbound() -> None:
    bound = bind_character_to_shots(
        empty_document(), profile(), revision=2, shot_ids=["shot_02"]
    )

    assert [item.shot_id for item in bound.bindings] == ["shot_02"]
    assert bound.compile_shot("shot_01") == ()


def test_round_trip_preserves_exact_profile_snapshot_and_fingerprint() -> None:
    bound = bind_character_to_shots(empty_document(), profile(), revision=3)
    restored = CharacterBoundShotPlan.from_dict(bound.to_dict())

    assert restored == bound
    assert restored.character_revisions[0].identity_fingerprint == profile().identity_fingerprint
    assert restored.compile_shot("shot_02")[0].identity_fingerprint == profile().identity_fingerprint


def test_same_revision_cannot_be_overwritten_with_different_profile() -> None:
    bound = bind_character_to_shots(empty_document(), profile(), revision=1)
    changed = profile(name="Milo Changed")

    with pytest.raises(StoryboardBindingError, match="cannot be overwritten"):
        bind_character_to_shots(bound, changed, revision=1)


def test_new_revision_can_be_added_without_changing_old_shot_binding() -> None:
    bound = bind_character_to_shots(
        empty_document(), profile(), revision=1, shot_ids=["shot_01"]
    )
    changed = profile(name="Milo Updated")
    updated = bind_character_to_shots(
        bound, changed, revision=2, shot_ids=["shot_02"]
    )

    assert len(updated.character_revisions) == 2
    assert updated.compile_shot("shot_01")[0].identity_fingerprint == profile().identity_fingerprint
    assert updated.compile_shot("shot_02")[0].identity_fingerprint == changed.identity_fingerprint


def test_rebinding_selected_shot_replaces_only_same_character_binding() -> None:
    doc = bind_character_to_shots(empty_document(), profile(), revision=1)
    other = profile("char_b", "Pip")
    doc = bind_character_to_shots(doc, other, revision=1, shot_ids=["shot_01"])
    changed = profile(name="Milo v2")
    doc = bind_character_to_shots(doc, changed, revision=2, shot_ids=["shot_01"])

    shot_one = [item.character_id for item in doc.bindings if item.shot_id == "shot_01"]
    assert shot_one == ["char_b", "char_a"]
    assert doc.compile_shot("shot_01")[0].identity_fingerprint == other.identity_fingerprint
    assert doc.compile_shot("shot_01")[1].identity_fingerprint == changed.identity_fingerprint


@pytest.mark.parametrize("shot_ids", [[], ["missing"], ["shot_01", "shot_01"]])
def test_rejects_empty_unknown_or_duplicate_shot_selection(shot_ids: list[str]) -> None:
    with pytest.raises(StoryboardBindingError, match="selected shot IDs"):
        bind_character_to_shots(empty_document(), profile(), revision=1, shot_ids=shot_ids)


def test_rejects_binding_to_missing_revision_or_wrong_fingerprint() -> None:
    bad = ShotCharacterBinding(
        shot_id="shot_01",
        character_id="char_a",
        profile_revision=1,
        identity_fingerprint="0" * 64,
    )
    with pytest.raises(StoryboardBindingError, match="missing character revision"):
        CharacterBoundShotPlan(shot_plan(), (), (bad,))


def test_rejects_duplicate_character_binding_for_same_shot() -> None:
    snapshot = CharacterRevisionSnapshot(1, profile())
    binding = ShotCharacterBinding(
        "shot_01", "char_a", 1, snapshot.identity_fingerprint
    )
    with pytest.raises(StoryboardBindingError, match="only be bound once"):
        CharacterBoundShotPlan(shot_plan(), (snapshot,), (binding, binding))


def test_rejects_invalid_document_shape_and_unsupported_fields() -> None:
    with pytest.raises(StoryboardBindingError, match="invalid character-bound"):
        CharacterBoundShotPlan.from_dict({"schema_version": 1})
    payload = empty_document().to_dict()
    payload["execute"] = "not allowed"
    with pytest.raises(StoryboardBindingError, match="invalid character-bound"):
        CharacterBoundShotPlan.from_dict(payload)


def test_profile_revision_is_positive_and_bool_is_not_accepted() -> None:
    with pytest.raises(StoryboardBindingError, match="positive integer"):
        CharacterRevisionSnapshot(0, profile())
    with pytest.raises(StoryboardBindingError, match="positive integer"):
        CharacterRevisionSnapshot(True, profile())
