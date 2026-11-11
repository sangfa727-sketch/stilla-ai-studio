"""Deterministic character-lock prompt compilation for compatible image/video providers."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from stilla.characters.schema import CharacterProfile, CharacterProfileError

MAX_SCENE_TEXT = 8_000


def _scene_text(value: str, field: str) -> str:
    if not isinstance(value, str) or len(value) > MAX_SCENE_TEXT:
        raise CharacterProfileError(f"{field} must be text within the supported limit")
    return value.strip()


@dataclass(frozen=True, slots=True)
class CharacterGenerationPlan:
    prompt: str
    negative_prompt: str
    reference_paths: tuple[str, ...]
    identity_fingerprint: str
    consistency_key: str
    seed: int | None
    locked_fields: tuple[str, ...]


def build_generation_plan(
    character: CharacterProfile,
    scene_description: str,
    *,
    pose: str = "",
    expression: str = "",
    outfit_override: str = "",
    allow_costume_change: bool = False,
    seed: int | None = None,
) -> CharacterGenerationPlan:
    """Compile identity + scene direction without asking users to write lock prompts.

    Only pose and expression are scene-variable by default. Costume changes require
    an explicit application-level choice. A seed is advisory and only used if the
    selected provider supports it; reference-image conditioning is the stronger signal.
    """
    if not isinstance(character, CharacterProfile):
        raise CharacterProfileError("character must be a validated CharacterProfile")
    scene = _scene_text(scene_description, "scene_description")
    if not scene:
        raise CharacterProfileError("scene_description must not be empty")
    pose_text = _scene_text(pose, "pose")
    expression_text = _scene_text(expression, "expression")
    override = _scene_text(outfit_override, "outfit_override")
    if override and not allow_costume_change:
        raise CharacterProfileError("costume change requires explicit allow_costume_change=True")
    selected_seed = character.canonical_seed if seed is None else seed
    if selected_seed is not None and (
        isinstance(selected_seed, bool) or not isinstance(selected_seed, int)
        or not 0 <= selected_seed <= 2**32 - 1
    ):
        raise CharacterProfileError("seed must be an unsigned 32-bit integer")

    visual = character.visual
    fixed = [
        f"Character identity: {character.name}, {character.species_or_type}.",
        f"Silhouette: {visual.silhouette}.",
        f"Body proportions: {visual.body_proportions}.",
        f"Face shape: {visual.face_shape}.",
        f"Eyes: {visual.eyes}.",
    ]
    for label, value in (
        ("Nose", visual.nose), ("Mouth", visual.mouth),
        ("Surface details", visual.surface_or_skin_detail),
        ("Hair or head shape", visual.hairstyle_or_head_shape),
        ("Primary colors", ", ".join(visual.primary_colors)),
        ("Outfit", override or visual.outfit),
        ("Accessories", ", ".join(visual.accessories)),
        ("Distinguishing marks", ", ".join(visual.distinguishing_marks)),
        ("Fixed features", ", ".join(visual.fixed_features)),
    ):
        if value:
            fixed.append(f"{label}: {value}.")
    fixed.append(f"Art direction: {visual.art_style}.")
    fixed.append("Preserve the exact same established character design and proportions; "
                 "do not redesign, age, recolor, or reinterpret the character.")
    if pose_text:
        fixed.append(f"Scene pose (variable only): {pose_text}.")
    if expression_text:
        fixed.append(f"Facial expression (variable only): {expression_text}.")
    fixed.append(f"Scene: {scene}")

    personality = character.personality
    behavior = []
    if personality.archetype:
        behavior.append("Personality archetype: " + personality.archetype + ".")
    if personality.core_traits:
        behavior.append("Character behavior: " + ", ".join(personality.core_traits) + ".")
    if personality.strength:
        behavior.append("Character strength: " + personality.strength + ".")
    if personality.catchphrase:
        behavior.append("Catchphrase: " + personality.catchphrase + ".")
    if personality.humor_mechanics:
        behavior.append("Original comedy mechanics: " + ", ".join(personality.humor_mechanics) + ".")
    for label, value in (
        ("Comic flaw", personality.comic_flaw),
        ("Speech pattern", personality.speech_pattern),
        ("Reaction style", personality.reaction_style),
        ("Relationship dynamic", personality.relationship_dynamic),
        ("Running gag", personality.running_gag),
    ):
        if value:
            behavior.append(f"{label}: {value}.")
    if personality.avoid:
        behavior.append("Avoid these behavior patterns: " + ", ".join(personality.avoid) + ".")
    if character.voice_description:
        behavior.append("Voice design: " + character.voice_description + ".")
    behavior.append("Dialogue language: " + character.language + ".")
    prompt = " ".join(fixed + behavior)
    negative = (
        "character redesign, different face, different eye shape, altered silhouette, "
        "changed body proportions, inconsistent colors, changed costume, missing accessories, "
        "extra accessories, altered distinguishing marks, duplicate character, identity drift, "
        "unintended age change, unintended species change, low-detail face"
    )
    refs = tuple(ref.relative_path for ref in character.references)
    key_material = "|".join((character.identity_fingerprint, scene, pose_text, expression_text,
                             override, str(selected_seed if selected_seed is not None else "")))
    consistency_key = hashlib.sha256(key_material.encode("utf-8")).hexdigest()
    locked = ("silhouette", "body_proportions", "face_shape", "eyes", "primary_colors",
              "outfit", "accessories", "distinguishing_marks", "art_style")
    return CharacterGenerationPlan(
        prompt=prompt, negative_prompt=negative, reference_paths=refs,
        identity_fingerprint=character.identity_fingerprint,
        consistency_key=consistency_key, seed=selected_seed, locked_fields=locked,
    )
