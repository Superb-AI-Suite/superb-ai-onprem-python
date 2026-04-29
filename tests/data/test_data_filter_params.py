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
