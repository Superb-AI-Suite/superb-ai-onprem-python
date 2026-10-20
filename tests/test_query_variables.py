"""Every GraphQL variable the SDK sends is declared by its query, and the other way round.

A mismatch fails on the server: a required variable that is never sent gives
HTTP 400 ("Variable $x ... was not provided"), and a sent variable that the
query does not declare is silently dropped.
"""
import enum
import importlib
import inspect
import pkgutil
import re
import typing

import pytest
from pydantic import BaseModel

import spb_onprem
from spb_onprem.activities.entities import ActivityStatus
from spb_onprem.base_types import Undefined
from spb_onprem.contents.entities import BaseContent
from spb_onprem.data.entities import AnnotationVersion, Data, DataMeta, Scene
from spb_onprem.data.enums import DataMetaTypes, DataType, SceneType

DECLARED = re.compile(r"\$(\w+)\s*:\s*([\[\]\w!]+)")

_VERSION = AnnotationVersion(content=BaseContent(id="content-1"), meta={}, channels=["rgb"], version="v1")

#: Arguments for the variable builders that need more than plain strings.
OVERRIDES = {
    ("activities", "GET_ACTIVITY"): {"activity_id": "activity-1"},
    ("activities", "START_ACTIVITY"): {"activity_type": "DELETE_DATA", "slice_id": "slice-1"},
    ("activities", "UPDATE_ACTIVITY_HISTORY"): {"status": ActivityStatus.RUNNING},
    ("datasets", "DATASET"): {"dataset_id": "dataset-1"},
    ("slices", "GET_SLICE"): {"slice_id": "slice-1"},
    ("data", "CREATE"): {"data": Data(
        dataset_id="dataset-1", key="key-1", type=DataType.SUPERB_IMAGE,
        scene=[Scene(type=SceneType.IMAGE, content=BaseContent(id="content-1"))],
    )},
    ("data", "INSERT_ANNOTATION_VERSION"): {"version": _VERSION},
    ("data", "INSERT_SLICE_ANNOTATION_VERSION"): {"version": _VERSION},
    ("data", "UPDATE_SCENE"): {"scene": Scene(id="scene-1", type=SceneType.IMAGE, content=BaseContent(id="c"))},
    # UPDATE is used only without expected_caption (UPDATE_WITH_EXPECTED_CAPTION otherwise).
    ("data", "UPDATE"): {"meta": [DataMeta(key="k", type=DataMetaTypes.STRING, value="v")],
                         "expected_caption": Undefined},
    ("data", "UPDATE_WITH_EXPECTED_CAPTION"): {"meta": [DataMeta(key="k", type=DataMetaTypes.STRING, value="v")]},
    ("models", "CREATE"): {"contents": {"weights": "01ARZ3NDEKTSV4RRFFQ69G5FAV"}},
    ("models", "UPDATE"): {"contents": {"weights": "01ARZ3NDEKTSV4RRFFQ69G5FAV"}},
    ("vlm_settings", "CREATE_DATASET_VLM_SETTINGS"): {"settings": {"questions": []}},
    ("vlm_settings", "UPDATE_DATASET_VLM_SETTINGS"): {"settings": {"questions": []}},
    ("vlm_settings", "CREATE_SLICE_VLM_SETTINGS"): {"settings": {"questions": []}},
    ("vlm_settings", "UPDATE_SLICE_VLM_SETTINGS"): {"settings": {"questions": []}},
}

#: Sent but not declared, on purpose or harmless. The server's jobs/job/updateJob take no
#: datasetId, so the value is ignored there (kept for compatibility; not a name mismatch).
IGNORED_EXTRA = {
    ("activities", "GET_ACTIVITIES"): {"datasetId"},
    ("activities", "GET_ACTIVITY"): {"datasetId"},
    ("activities", "UPDATE_ACTIVITY"): {"datasetId"},
}


def _model(cls):
    try:
        return cls()
    except Exception:  # noqa: BLE001 - a model with required fields
        return cls.model_construct()


def _dummy_for(annotation):
    origin = getattr(annotation, "__origin__", None)
    args = getattr(annotation, "__args__", ())
    if origin in (list, typing.List):
        item = args[0] if args else str
        if isinstance(item, type) and issubclass(item, BaseModel):
            return [_model(item)]
        return ["x"]
    for candidate in (annotation, *args):
        if isinstance(candidate, type) and issubclass(candidate, enum.Enum):
            return list(candidate)[0]
        if isinstance(candidate, type) and issubclass(candidate, BaseModel):
            return _model(candidate)
        if getattr(candidate, "__origin__", None) in (list, typing.List):
            return _dummy_for(candidate)
    text = str(annotation)
    if "dict" in text.lower():
        return {"k": "v"}
    if "bool" in text and "str" not in text:
        return True
    if ("int" in text or "float" in text) and "str" not in text:
        return 1
    return "x"


def _dummy(param):
    return _dummy_for(param.annotation)


def _queries():
    for module in pkgutil.iter_modules(spb_onprem.__path__):
        if not module.ispkg:
            continue
        try:
            queries = importlib.import_module(f"spb_onprem.{module.name}.queries")
        except ModuleNotFoundError:
            continue
        holder = getattr(queries, "Queries", None)
        for key, value in vars(holder or object).items():
            if isinstance(value, dict) and "query" in value and callable(value.get("variables")):
                yield module.name, key, value


ALL_QUERIES = sorted(_queries(), key=lambda item: (item[0], item[1]))


@pytest.mark.parametrize("module,key,query", ALL_QUERIES, ids=[f"{m}.{k}" for m, k, _ in ALL_QUERIES])
def test_variables_match_the_query(module, key, query):
    declared = dict(DECLARED.findall(query["query"]))
    required = {name for name, kind in declared.items() if kind.endswith("!")}
    overrides = OVERRIDES.get((module, key), {})
    signature = inspect.signature(query["variables"])
    kwargs = {
        name: overrides.get(name, _dummy(param))
        for name, param in signature.parameters.items()
        if param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD)
    }
    try:
        sent = query["variables"](**kwargs)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"cannot build the variables of {module}.{key} ({exc!r}); add an OVERRIDES entry")

    extra = set(sent) - set(declared) - IGNORED_EXTRA.get((module, key), set())
    assert not extra, f"{module}.{key} sends undeclared variables {sorted(extra)}"
    missing = required - set(sent)
    assert not missing, f"{module}.{key} never sends required variables {sorted(missing)}"


def test_the_scan_covers_the_known_broken_ones():
    keys = {(m, k) for m, k, _ in ALL_QUERIES}
    assert {("datasets", "UPDATE_DATASET"), ("data", "DELETE_ANNOTATION_VERSION"),
            ("data", "UPDATE_SLICE_ANNOTATION_VERSION")} <= keys
    assert len(ALL_QUERIES) > 50
