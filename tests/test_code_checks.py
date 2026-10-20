"""Static checks over the SDK source."""
import ast
import builtins
from pathlib import Path

import pytest

from spb_onprem.data.service import DataService
from spb_onprem.exceptions import BadParameterError

SOURCE = Path(__file__).resolve().parent.parent / "spb_onprem"


def test_no_none_check_on_a_builtin_name():
    """`if id is None` on a function without an `id` parameter checks the builtin, never None."""
    found = []
    for path in SOURCE.rglob("*.py"):
        tree = ast.parse(path.read_text())
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            args = fn.args
            names = {a.arg for a in args.args + args.kwonlyargs + args.posonlyargs}
            names |= {a.arg for a in (args.vararg, args.kwarg) if a}
            names |= {
                node.id for node in ast.walk(fn)
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
            }
            for node in ast.walk(fn):
                if (
                    isinstance(node, ast.Compare)
                    and isinstance(node.left, ast.Name)
                    and any(isinstance(op, (ast.Is, ast.IsNot)) for op in node.ops)
                    and hasattr(builtins, node.left.id)
                    and node.left.id not in names
                ):
                    found.append(f"{path.relative_to(SOURCE.parent)}:{node.lineno} {fn.name}: {node.left.id}")
    assert found == []


def test_update_slice_annotation_version_requires_version_id():
    service = DataService()
    service.request_gql = lambda *args: pytest.fail("must not send")
    with pytest.raises(BadParameterError, match="version_id is required"):
        service.update_slice_annotation_version(
            dataset_id="d1", data_id="x", slice_id="s1", version_id=None, meta={},
        )


def test_delete_slice_annotation_version_requires_id():
    """Its parameter is named `id`, so this check was right."""
    service = DataService()
    service.request_gql = lambda *args: pytest.fail("must not send")
    with pytest.raises(BadParameterError, match="id is required"):
        service.delete_slice_annotation_version(dataset_id="d1", data_id="x", slice_id="s1", id=None)
