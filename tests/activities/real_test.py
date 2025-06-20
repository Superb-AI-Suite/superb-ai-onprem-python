from spb_onprem import (
    DatasetService,
    Dataset,
    ActivityService,
    Activity,
    ActivityHistory,
    ActivityStatus,
    ActivitySchema,
    SchemaType,
)


def test_activity_service():
    dataset_service = DatasetService()
    dataset = dataset_service.get_dataset(
        dataset_id="01JPM6NR1APMBXJNC0YW72S1FN"
    )

    print(dataset)
    
    activity_service = ActivityService()
    cursor = None
    assign_data_slice_activity = None
    while True:
        (described_activities, cursor, _) = activity_service.get_activities(
            dataset_id=dataset.id,
            cursor=cursor,
            length=50
        )
        for activity in described_activities:
            if activity.activity_type == "ASSIGN_DATA_TO_SLICE":
                assign_data_slice_activity = activity
                break
        if cursor is None:
            break
    
    print(assign_data_slice_activity.parameter_schema)

    activity_history = activity_service.start_activity(
        dataset_id=dataset.id,
        activity_id=assign_data_slice_activity.id,
        parameters={
            "dataset_id": dataset.id,
            "slice_name": "sdk_test_slice",
            "slice_description": "sdk_test_slice_description",
            "filter": {
                "must": {
                    "keyContains": "validation_v5/87d37e96-0bab3a63.jpg"
                }
            },
            "filter_type": "DATA",
            "is_new_slice": True,
        }
    )
    print(activity_history)
    
    activity_service.update_activity_history_status(
        activity_history_id=activity_history.id,
        status=ActivityStatus.FAILED,
        meta={
            "sdk_test": "sdk_test_value"
        }
    )

if __name__ == "__main__":
    test_activity_service()