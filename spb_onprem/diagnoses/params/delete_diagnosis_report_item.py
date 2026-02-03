def delete_diagnosis_report_item_params(
    dataset_id: str,
    diagnosis_id: str,
    diagnosis_report_item_id: str,
):
    return {
        "dataset_id": dataset_id,
        "diagnosis_id": diagnosis_id,
        "diagnosis_report_item_id": diagnosis_report_item_id,
    }
