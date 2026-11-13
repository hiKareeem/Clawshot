"""Darunia's Joy follows its own cutscene source; the Fire quest only moves forward.

Invented flows on the native contracts of plans/03-game-data.md section 48, never extracted game content.
The runner follows state-changing events only; engine animation, timing and save behavior still need play.
"""

import pytest

from clawshot.formats import evfl
from clawshot.patch import darunia
from clawshot.patch.plan import PatchError

# Native Get_StoneOfFire step order (the Challenge row); IsAfter_X holds strictly after X.
STEPS = (
    "NotReady",
    "Ready",
    "KakarikoVillageNpc",
    "KakarikoVillageLetter",
    "DeathMtTrailIn",
    "DeathMtTrailNpc",
    "GoronCityIn",
    "GoronCityDarniaroomNpcTalk01",
    "GoronCityDarniaroomOpen",
    "GoronCityDarniaTalk",
    "DarniaRoomKokiriTalk",
    "KokiriForestNPCTalk",
    "KokiriForestFire",
    "KokiriForestIn",
    "SariaMelodyGet",
    "SariaMelodyPlay",
    "DodongoCavernOpne",
    "DungeonStart",
    "BossBattle",
    "EscapeDungeon",
    "Complete",
)
OPENED = STEPS.index("DodongoCavernOpne")
FIRST = ("SariaMelodyGet", "SariaMelodyPlay")  # Saria's Song learned before the cavern opens
LATE = ("DungeonStart", "BossBattle", "EscapeDungeon", "Complete")  # boulder, boss entry, defeat, blue warp
PLAY = "Get_StoneOfFire_PlayOcarina"
BRACELET = "Item_Gauntlet_Goron"
BRACELET_OWNED = "Armor_Child_Gauntlet_Goron"
STEP = "Step_Get_StoneOfFire"
GET_IN = ("Dm_SY_GetInEvent", "GetInEvent_Goron")
# Unchanged native helpers a played song passes through; their presentation is not executed here.
PRESENTATION = {
    ("Dm_SY_Ocarina", "PlayOcarinaFree"),
    ("Dm_SY_Ocarina", "PlayOcarinaSequence_NpcBeginningTalk"),
    ("NpcCommon", "NpcCommon_PlayOcarina_BeginningTalk"),
    ("InitTalk", "InitTalk_OnEvent"),
    ("Common_Camera_Pln", "CameraDoF_Default"),
}


def transition(scene):
    return {"IsWaitEnd": True, "SpecialEventActionType": 1, "FadeInTypeEventEnd": 0, "EventName": scene}


def stone_flow():
    """Darunia's song reaction: presentation by quest step, the recommended-melody check, the dance, Event39."""
    talk = 3
    return evfl.EventFlowFile(
        "DaruniaSongTest",
        evfl.Flowchart(
            "Get_StoneOfFire",
            [
                evfl.Actor(
                    "GameDataActor",
                    actions=[darunia.SET_BOOL],
                    queries=[darunia.READ_EXPRESSION, darunia.READ_BOOL],
                ),
                evfl.Actor("EventSystemActor", actions=["EventTransition"]),
                evfl.Actor("GameSystemActor", queries=["EventQueryIsRecommendedMelody"]),
                evfl.Actor("Npc_Goron_Darunia_Child", actions=["EventTalk"]),
            ],
            [
                evfl.SwitchEvent("Event82", 0, 0, [(0, 1), (1, 2)], {"GameDataName": darunia.CUTOFF}),
                evfl.ActionEvent("FreePlay", talk, 0, 3, {"MessageId": "Test:FreePlay"}),
                evfl.ActionEvent("BeginningTalk", talk, 0, 3, {"MessageId": "Test:Beginning"}),
                evfl.SwitchEvent("Event35", 2, 0, [(0, 4), (1, 7)]),
                evfl.ActionEvent("Event185", 1, 0, 5, transition("Dm_Goron_0025")),
                evfl.SwitchEvent("Event39", 0, 0, [(0, 6), (1, 8)], {"GameDataName": darunia.CUTOFF}),
                evfl.ActionEvent("Event42", talk, 0, evfl.NONE, {"MessageId": "Test:Repeat"}),
                evfl.ActionEvent("Event147", talk, 0, evfl.NONE, {"MessageId": "Test:WrongSong"}),
                evfl.ActionEvent("Event31", 1, 0, evfl.NONE, transition("Dm_Goron_0030")),
            ],
            [evfl.EntryPoint(PLAY, 0)],
        ),
    )


def movie_flow(reward=BRACELET):
    """The gift cutscene: cut C10 hands the reward over beside a wait, cut C11 steps Fire and resets the camera."""
    return evfl.EventFlowFile(
        "DaruniaMovieTest",
        evfl.Flowchart(
            "Dm_Goron_0030",
            [
                evfl.Actor("GameSystemActor", actions=["EventWait"], params=dict(darunia.SYSTEM_ACTOR_PARAMS)),
                evfl.Actor(
                    "ChallengeSystemActor",
                    actions=["EventExecuteProgressChallengeStep", "EventTriggerShowChallengeProgressUI"],
                    params=dict(darunia.SYSTEM_ACTOR_PARAMS),
                ),
                evfl.Actor("Player_Event", actions=["EventTriggerPlayerLookAtObject"]),
                evfl.Actor("EventCamera", actions=["EventTriggerSendReserveCameraResetMessageToPlayerCamera"]),
            ],
            [
                evfl.SubFlowEvent("Event183", "", "C10", 1),
                evfl.SubFlowEvent("Event219", "", "C11"),
                evfl.ForkEvent("Event186", 3, [4, 5]),
                evfl.JoinEvent("Event193"),
                evfl.SubFlowEvent("Event127", *GET_IN, evfl.NONE, {"ActorName": reward}),
                evfl.ActionEvent("Event200", 0, 0, evfl.NONE, {"IsWaitEnd": True, "Frames": 12}),
                evfl.ActionEvent("Event130", 2, 0, 7, {"ActorName": "Npc_Goron_Darunia_Child"}),
                evfl.ActionEvent("Event121", 1, 0, 8, dict(darunia.STEP_WRITE)),
                evfl.ActionEvent("Event128", 1, 1, 9, dict(darunia.STEP_NOTICE)),
                evfl.ActionEvent("Event202", 3, 0, 10, {"CameraResetPolicy": 0}),
                evfl.SubFlowEvent("Event149", "Common_Camera_Pln", "CameraDoF_Default"),
            ],
            [
                evfl.EntryPoint("EntryPoint0", 0, [0, 1]),
                evfl.EntryPoint("C10", 2, [4]),
                evfl.EntryPoint("C11", 6, [10]),
            ],
        ),
    )


def patched(stone, movie):
    return (
        evfl.read(darunia.gift_gate(evfl.write(stone))),
        evfl.read(darunia.source_once(evfl.write(movie))),
    )


class UnregisteredCall(AssertionError):
    pass


def play(stone, movie, *, step, source=False, song=True, owned=(), pouch=None):
    """Play a song to Darunia and follow both flows' state-changing events.

    ``owned`` contains canonical saved IsGet suffixes, not acquisition-actor names. The engine's own
    HavePlayedEvent bookkeeping is not modeled; only the flows' writes count. A step write is applied as
    written, so a backward write would step the quest back here."""
    flows = {"Get_StoneOfFire": stone.flowchart, "Dm_Goron_0030": movie.flowchart}
    if pouch is not None:
        flows["GetPouchContent"] = pouch.flowchart
    state = {STEP: step, darunia.SOURCE: source, **{f"IsGet.{item}": True for item in owned}}
    result = {"rewards": [], "writes": [], "notices": 0, "trace": []}
    budget = [5000]

    def query(fc, event, params):
        name = fc.actors[event.actor].queries[event.query]
        if name == "EventQueryIsRecommendedMelody":
            return 0 if song else 1
        if name == "EventQueryMelodyTypeForNormal":
            return 2 if song else 0  # Saria's Song is native MelodyType 2
        if name == darunia.READ_EXPRESSION:
            assert params == {"GameDataName": darunia.CUTOFF}, event
            return 0 if STEPS.index(state[STEP]) > STEPS.index("SariaMelodyPlay") else 1
        if name == darunia.READ_BOOL:
            assert params.get("Index") == -1, event
            return 0 if state.get(params["GameDataName"], False) else 1
        raise AssertionError(f"unmodeled query {name}: {event}")

    def run(fc, entry, index, stop=evfl.NONE, arguments=None):
        arguments = arguments or {}
        while index not in (evfl.NONE, stop):
            budget[0] -= 1
            assert budget[0] > 0, result["trace"]
            event = fc.events[index]
            result["trace"].append(event.name)
            params = getattr(event, "params", None) or {}
            if isinstance(event, evfl.SwitchEvent):
                index = dict(event.cases).get(query(fc, event, params), evfl.NONE)
            elif isinstance(event, evfl.ForkEvent):
                assert isinstance(fc.events[event.join], evfl.JoinEvent), event
                for fork in event.forks:
                    run(fc, entry, fork, event.join, arguments)
                index = event.join
            elif isinstance(event, evfl.JoinEvent):
                index = event.next
            elif isinstance(event, evfl.SubFlowEvent):
                if index not in entry.sub_flow_events:
                    raise UnregisteredCall(f"{fc.name}:{entry.name}: {event.name} not registered")
                if not event.flowchart:
                    child = fc.entry_point(event.entry_point)
                    run(fc, child, child.main_event, arguments=params)
                elif (event.flowchart, event.entry_point) == GET_IN:
                    reward = params["ActorName"]
                    if isinstance(reward, evfl.Argument):
                        reward = arguments[str(reward)]
                    result["rewards"].append(reward)
                    identity = BRACELET_OWNED if reward == BRACELET else reward
                    state[f"IsGet.{identity}"] = True
                elif event.flowchart in flows:
                    child_chart = flows[event.flowchart]
                    child = child_chart.entry_point(event.entry_point)
                    run(child_chart, child, child.main_event, arguments=params)
                else:
                    assert (event.flowchart, event.entry_point) in PRESENTATION, event
                index = event.next
            elif isinstance(event, evfl.ActionEvent):
                action = fc.actors[event.actor].actions[event.action]
                if action == darunia.SET_BOOL:
                    state[params["GameDataName"]] = params["Value"]
                elif action == "EventExecuteProgressChallengeStep":
                    assert params["ChallengeName"] == "Get_StoneOfFire", event
                    result["writes"].append((state[STEP], params["StepName"]))
                    state[STEP] = params["StepName"]
                elif action == "EventTriggerShowChallengeProgressUI":
                    result["notices"] += 1
                elif action == "EventTransition":
                    scene = params["EventName"]
                    if scene in flows:  # its event setting names no entry: the cutscene's EntryPoint0 plays
                        start = flows[scene].entry_point("EntryPoint0")
                        run(flows[scene], start, start.main_event, arguments=params)
                    else:
                        result["trace"].append(f"timeline {scene}")
                index = event.next
            else:
                raise AssertionError(f"unmodeled event {event}")

    start = stone.flowchart.entry_point(PLAY)
    run(stone.flowchart, start, start.main_event)
    return state, result


def native_path(trace):
    return [name for name in trace if not name.startswith("Clawshot")]


@pytest.mark.parametrize("step", FIRST)
def test_song_before_the_cavern_keeps_the_native_gift_and_step(step):
    original = (stone_flow(), movie_flow())
    before, native = play(*original, step=step)
    after, result = play(*patched(*original), step=step)
    assert native["rewards"] == result["rewards"] == [BRACELET]
    assert native["writes"] == result["writes"] == [(step, "DodongoCavernOpne")]
    assert native["notices"] == result["notices"] == 1
    assert native_path(result["trace"]) == native["trace"]
    assert after[STEP] == before[STEP] == "DodongoCavernOpne"
    assert after[darunia.SOURCE] is True
    assert result["trace"].index("Event127") < result["trace"].index(f"{darunia.PREFIX}SourceOnce")


@pytest.mark.parametrize("step", ("DodongoCavernOpne", *LATE))
def test_cavern_opened_another_way_still_gives_the_gift_without_stepping_back(step):
    original = (stone_flow(), movie_flow())
    _, native = play(*original, step=step)
    assert native["rewards"] == [] and "Event42" in native["trace"]  # the native missable branch
    after, result = play(*patched(*original), step=step)
    assert result["rewards"] == [BRACELET]
    assert after[darunia.SOURCE] is True
    assert after[STEP] == step
    assert result["writes"] == [] and result["notices"] == 0
    assert result["trace"][-2:] == ["Event202", "Event149"]  # the camera tail still runs


@pytest.mark.parametrize("step", ("SariaMelodyPlay", "DodongoCavernOpne", *LATE))
def test_collected_source_repeats_the_dance_reaction(step):
    after, result = play(*patched(stone_flow(), movie_flow()), step=step, source=True)
    assert result["rewards"] == [] and result["writes"] == []
    assert "Event42" in result["trace"] and "Event31" not in result["trace"]
    assert after[STEP] == step


@pytest.mark.parametrize("step", ("SariaMelodyPlay", "DungeonStart"))
def test_a_reward_found_elsewhere_is_not_the_source(step):
    after, result = play(*patched(stone_flow(), movie_flow()), step=step, owned=(BRACELET_OWNED,))
    assert result["rewards"] == [BRACELET]
    assert after[darunia.SOURCE] is True


@pytest.mark.parametrize("step", ("SariaMelodyPlay", "DungeonStart"))
def test_another_song_changes_nothing(step):
    original = (stone_flow(), movie_flow())
    before, native = play(*original, step=step, song=False)
    after, result = play(*patched(*original), step=step, song=False)
    assert (after, result["rewards"], result["writes"]) == (before, [], [])
    assert result["trace"] == native["trace"]


@pytest.mark.parametrize("step", ("SariaMelodyPlay", "BossBattle"))
def test_shuffled_reward_completes_the_source_once(step):
    stone, movie = patched(stone_flow(), movie_flow("Item_DinFire"))
    after, result = play(stone, movie, step=step)
    assert result["rewards"] == ["Item_DinFire"]
    assert after[darunia.SOURCE] is True
    again, repeat = play(stone, movie, step=after[STEP], source=after[darunia.SOURCE])
    assert repeat["rewards"] == [] and again[STEP] == after[STEP]


def _named(document, name):
    return next(event for event in document.flowchart.events if event.name == name)


def _documents():
    return {"stone": stone_flow(), "movie": movie_flow()}


TRANSFORMS = {"stone": darunia.gift_gate, "movie": darunia.source_once}


@pytest.mark.parametrize(
    "flow, event, field, value, match",
    [
        ("stone", "Event39", "GameDataName", "Get_StoneOfFire_IsAfter_DungeonStart_Exp", "IsAfter_DungeonStart"),
        ("stone", "Event31", "EventName", "Dm_Goron_0040", "Dm_Goron_0040"),
        ("movie", "Event121", "StepName", "DungeonStart", "'StepName': 'DungeonStart'"),
        ("movie", "Event128", "ChallengeName", "Get_StoneOfWater", "Get_StoneOfWater"),
        ("movie", "Event127", "ActorName", evfl.Argument("ActorName"), "changed native hand-over"),
    ],
)
def test_changed_native_payloads_are_refused_with_the_actual_values(flow, event, field, value, match):
    documents = _documents()
    _named(documents[flow], event).params[field] = value
    with pytest.raises(PatchError, match=match):
        TRANSFORMS[flow](evfl.write(documents[flow]))


@pytest.mark.parametrize(
    "flow, event, target, match",
    [
        ("stone", "FreePlay", "Event39", r"callers \['FreePlay', 'Event185'\]"),
        ("movie", "Event200", "Event121", r"callers \['Event200', 'Event130'\]"),
        ("movie", "Event127", "Event200", "changed native hand-over"),
    ],
)
def test_changed_native_routes_are_refused_with_the_actual_callers(flow, event, target, match):
    documents = _documents()
    events = documents[flow].flowchart.events
    _named(documents[flow], event).next = next(i for i, e in enumerate(events) if e.name == target)
    with pytest.raises(PatchError, match=match):
        TRANSFORMS[flow](evfl.write(documents[flow]))


def test_a_second_application_is_refused():
    stone, movie = patched(stone_flow(), movie_flow())
    with pytest.raises(PatchError, match=r"changed native gift gate.*HavePlayedEvent\.Dm_Goron_0030"):
        darunia.gift_gate(evfl.write(stone))
    with pytest.raises(PatchError, match="already patched"):
        darunia.source_once(evfl.write(movie))
