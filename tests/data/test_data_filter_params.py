from spb_onprem.data.params import DataListFilter, get_data_id_list_params


def dump_filter(payload):
    data_filter = DataListFilter.model_validate(payload)
    return data_filter.model_dump(by_alias=True, exclude_unset=True)


def test_slice_id_exists_false_is_preserved_with_camel_case_alias():
    payload = {"must": {"sliceIdExists": False}}

    assert dump_filter(payload) == payload


def test_slice_id_exists_false_is_preserved_with_legacy_pascal_case_alias():
    data_filter = DataListFilter.model_validate({"must": {"SliceIdExists": False}})

    assert data_filter.model_dump(by_alias=True, exclude_unset=True) == {
        "must": {"sliceIdExists": False}
    }


def test_slice_id_exists_false_is_serialized_for_data_id_list_query():
    data_filter = DataListFilter.model_validate(
        {"must": {"sliceIdExists": False}}
    )

    assert get_data_id_list_params(
        dataset_id="dataset-1",
        data_filter=data_filter,
    )["filter"] == {"must": {"sliceIdExists": False}}


def test_slice_id_field_is_not_serialized_to_avoid_slice_filter_overlap():
    data_filter = DataListFilter.model_validate(
        {"must": {"sliceId": "slice-1", "sliceIdExists": False}}
    )

    assert get_data_id_list_params(
        dataset_id="dataset-1",
        data_filter=data_filter,
    )["filter"] == {"must": {"sliceIdExists": False}}


def test_caption_semantic_query_is_preserved():
    """Incident 2026-11-24: the filter lost captionSemanticQuery and became {"must": {}} (MOD2-99)."""
    payload = {"must": {"captionSemanticQuery": "blue"}}
    data_filter = DataListFilter.model_validate(payload)

    assert data_filter.model_dump(by_alias=True, exclude_none=True) == payload
    assert get_data_id_list_params(
        dataset_id="dataset-1",
        data_filter=data_filter,
    )["filter"] == payload


def test_fields_added_for_the_server_schema_round_trip():
    payload = {
        "must": {
            "captionExists": False,
            "createdAt": {"withinLast": {"amount": 7, "unit": "WEEK"}},
            "annotationCounts": {"type": [{"key": "box", "range": {"gte": 1}}]},
        },
        "frames": [{
            "conditions": {"counts": {"type": [{"key": "box"}]}},
            "matchingFrameCount": {"gte": 1},
        }],
        "slice": {"id": "slice-1", "must": {"labelingRound": {"gte": 2}}},
    }

    assert dump_filter(payload) == payload
