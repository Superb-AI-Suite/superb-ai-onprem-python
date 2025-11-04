def delete_analytics_report_item_params(
    item_id: str,
    report_id: str,
    dataset_id: str,
):
    """Get parameters for deleting an analytics report item.
    
    Args:
        item_id: The item ID
        report_id: The report ID
        dataset_id: The dataset ID
        
    Returns:
        dict: Parameters for deleting an analytics report item
    """
    return {
        "itemId": item_id,
        "reportId": report_id,
        "datasetId": dataset_id,
    }
