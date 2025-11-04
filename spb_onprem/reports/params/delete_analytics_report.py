def delete_analytics_report_params(
    report_id: str,
    dataset_id: str,
):
    """Get parameters for deleting an analytics report.
    
    Args:
        report_id: The report ID
        dataset_id: The dataset ID
        
    Returns:
        dict: Parameters for deleting an analytics report
    """
    return {
        "reportId": report_id,
        "datasetId": dataset_id,
    }
