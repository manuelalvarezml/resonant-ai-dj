from pathlib import Path

from prompt_to_playlist.adapters import load_catalog
from prompt_to_playlist.desktop import criteria_summary, describe_run, match_summary, result_notice, catalog_coverage
from prompt_to_playlist.models import TagEvidence
from prompt_to_playlist.service import build_playlist
from prompt_to_playlist.translators import RulesTranslator
from prompt_to_playlist.vocabulary import load_vocabulary

DEMO = Path(__file__).parents[1] / 'examples/demo-catalog.json'


def test_preferred_energy_gap_does_not_obscure_required_house_matches():
    catalog = load_catalog(DEMO)
    for track in catalog.tracks:
        track.tags = [e for e in track.tags if not e.tag.startswith('energy:')]
    run = build_playlist('require house; prefer high energy', catalog, load_vocabulary(), RulesTranslator())
    assert run.status == 'matched'
    assert all('genre:house' in match.matched_tags for match in run.result.matches)
    assert 'Must match  ·  House' in criteria_summary(run)
    assert 'Prefer  ·  High energy' in criteria_summary(run)
    assert 'Not evidenced in this library: High energy.' in result_notice(run, catalog)
    assert 'required filters' in result_notice(run, catalog)
    assert '%' not in match_summary(run.result.matches[0])


def test_missing_hard_constraint_is_not_claimed_absent_from_audio():
    catalog = load_catalog(DEMO)
    for track in catalog.tracks:
        track.tags = [e for e in track.tags if not e.tag.startswith('energy:')]
    run = build_playlist('require high energy', catalog, load_vocabulary(), RulesTranslator())
    assert run.status == 'no_matches'
    notice = result_notice(run, catalog)
    assert 'Not evidenced' in notice and 'No tracks satisfy every required filter' in notice
    assert 'no energetic' not in notice.lower()


def test_known_low_energy_is_not_mislabeled_as_unknown():
    catalog = load_catalog(DEMO)
    for track in catalog.tracks:
        track.tags = [e for e in track.tags if not e.tag.startswith('energy:')]
        track.tags.append(TagEvidence(tag='energy:low', authority='user_verified', source='review'))
    run = build_playlist('require house; prefer high energy', catalog, load_vocabulary(), RulesTranslator())
    summary = match_summary(run.result.matches[0])
    assert 'Not evidenced: High energy' in summary
    assert 'unknown' not in summary.lower()


def test_unresolved_constraints_remain_visible_with_details_closed():
    catalog = load_catalog(DEMO)
    run = build_playlist('require house; 45 minutes', catalog, load_vocabulary(), RulesTranslator())
    assert 'Please clarify:' in result_notice(run, catalog)
    assert '45 minutes' in result_notice(run, catalog)
    assert run.result is None


def test_unusable_tag_annotations_do_not_count_as_available_evidence():
    catalog = load_catalog(DEMO)
    for track in catalog.tracks:
        for evidence in track.tags:
            evidence.status = 'rejected'
    run = build_playlist('prefer high energy', catalog, load_vocabulary(), RulesTranslator())
    assert '0 tracks with genre tags' in catalog_coverage(catalog)
    assert 'Not evidenced in this library: High energy.' in result_notice(run, catalog)
    assert 'Matched:' not in match_summary(run.result.matches[0])


def test_rejected_duplicate_evidence_keeps_its_status_in_expanded_details():
    catalog = load_catalog(DEMO)
    house = next(track for track in catalog.tracks if any(e.tag == 'genre:house' for e in track.tags))
    house.tags.append(TagEvidence(tag='genre:house', authority='user_verified', source='rejected duplicate', status='rejected'))
    run = build_playlist('require house', catalog, load_vocabulary(), RulesTranslator())
    assert 'user_verified · rejected · rejected duplicate' in describe_run(run)


def test_negative_filter_gap_is_explained_without_suggesting_missing_tags_prove_absence():
    catalog = load_catalog(DEMO)
    for track in catalog.tracks:
        track.complete_tag_axes = []
    run = build_playlist('exclude vocal', catalog, load_vocabulary(), RulesTranslator())
    assert run.status == 'no_matches'
    assert 'cannot verify the requested exclusions' in result_notice(run, catalog)


def test_unrestricted_candidates_do_not_claim_descriptor_or_tempo_matching():
    catalog = load_catalog(DEMO)
    run = build_playlist('count 5', catalog, load_vocabulary(), RulesTranslator())
    notice = result_notice(run, catalog)
    assert 'No style or tempo filters requested' in notice
    assert 'Matched using' not in notice


def test_overview_is_bounded_without_truncating_full_evidence():
    from prompt_to_playlist.desktop import compact_text
    catalog = load_catalog(DEMO)
    run = build_playlist('require house; ' + 'unsupported ' * 80, catalog, load_vocabulary(), RulesTranslator())
    compact = compact_text(result_notice(run, catalog))
    assert len(compact) < 350
    assert 'See details' in compact
    assert ('unsupported ' * 80).strip() in describe_run(run)
