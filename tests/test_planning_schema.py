import math

import pytest

from stilla.planning.schema import (
    CreativeBrief,
    PlanningValidationError,
    ScriptDocument,
    ScriptSegment,
    Shot,
    ShotPlan,
    StoryboardDocument,
    StoryboardFrame,
)


def test_creative_brief_round_trip_and_defaults():
    brief = CreativeBrief(
        title="Launch video", audience="New customers", objective="Explain the product",
        constraints=("No unlicensed assets", "Use clear captions"),
    )
    assert CreativeBrief.from_dict(brief.to_dict()) == brief
    assert brief.target_duration_seconds == 60
    assert brief.aspect_ratio == "16:9"


@pytest.mark.parametrize("duration", [0, -1, 86401, True, 1.5])
def test_brief_rejects_invalid_duration(duration):
    with pytest.raises(PlanningValidationError):
        CreativeBrief("Title", "Audience", "Objective", target_duration_seconds=duration)


def test_brief_rejects_unknown_fields_and_invalid_aspect_ratio():
    with pytest.raises(PlanningValidationError, match="unsupported fields"):
        CreativeBrief.from_dict({"title": "T", "audience": "A", "objective": "O", "secret": "x"})
    with pytest.raises(PlanningValidationError, match="aspect_ratio"):
        CreativeBrief("T", "A", "O", aspect_ratio="cinema")


def test_script_round_trip_and_duplicate_ids_are_rejected():
    script = ScriptDocument("script1", "Intro", "en", (
        ScriptSegment("seg1", "Hello", narration="Welcome", estimated_duration_seconds=2.5),
    ))
    assert ScriptDocument.from_dict(script.to_dict()) == script
    with pytest.raises(PlanningValidationError, match="unique"):
        ScriptDocument("script1", "Intro", "en", (
            ScriptSegment("seg1", "One"), ScriptSegment("seg1", "Two"),
        ))


def test_storyboard_and_shot_plan_round_trip():
    storyboard = StoryboardDocument("board1", "Intro", (
        StoryboardFrame("frame1", "seg1", "A bright studio", "Welcome", "wide shot"),
    ))
    assert StoryboardDocument.from_dict(storyboard.to_dict()) == storyboard
    plan = ShotPlan("plan1", "Intro", (
        Shot("shot1", "frame1", "Camera moves toward presenter", 3.0, "slow dolly"),
    ))
    assert ShotPlan.from_dict(plan.to_dict()) == plan


def test_rejects_bad_nested_shapes_and_unsafe_ids():
    with pytest.raises(PlanningValidationError):
        ScriptDocument.from_dict({"id": "bad/id", "title": "T", "language": "en"})
    with pytest.raises(PlanningValidationError):
        StoryboardDocument.from_dict({"id": "b", "title": "T", "frames": [{"id": "f"}]})
    with pytest.raises(PlanningValidationError):
        ShotPlan.from_dict({"id": "p", "title": "T", "shots": "not-an-array"})


def test_rejects_wrong_item_types_and_excessive_text():
    with pytest.raises(PlanningValidationError, match="ScriptSegment"):
        ScriptDocument("s", "Title", "en", ("not a segment",))
    with pytest.raises(PlanningValidationError, match="character limit"):
        ScriptSegment("s1", "x" * 100_001)


def test_rejects_nonfinite_shot_duration():
    with pytest.raises(PlanningValidationError):
        Shot("shot1", "frame1", "Description", math.nan)



@pytest.mark.parametrize(
    ("factory", "data"),
    [
        (CreativeBrief.from_dict, {"audience": "A", "objective": "O"}),
        (ScriptDocument.from_dict, {"id": "s1", "title": "T"}),
        (ScriptDocument.from_dict, {
            "id": "s1", "title": "T", "language": "en",
            "segments": [{"id": "seg1"}],
        }),
        (ShotPlan.from_dict, {
            "id": "p1", "title": "T",
            "shots": [{"id": "shot1", "storyboard_frame_id": "f1"}],
        }),
        (ShotPlan.from_dict, {"id": "p1"}),
    ],
)
def test_from_dict_missing_required_fields_uses_validation_error(factory, data):
    with pytest.raises(PlanningValidationError, match="missing required fields"):
        factory(data)



def test_rejects_extremely_large_integer_script_duration():
    with pytest.raises(PlanningValidationError):
        ScriptSegment("seg1", "Hello", estimated_duration_seconds=10**1000)
