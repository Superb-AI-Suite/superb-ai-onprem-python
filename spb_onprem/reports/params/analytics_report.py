def analytics_report_params(
    report_id: str,
    dataset_id: str,
):
    """Get parameters for retrieving a single analytics report.
    
    Args:
        report_id: The report ID
        dataset_id: The dataset ID
        
    Returns:
        dict: Parameters for retrieving an analytics report
    """
    return {
        "reportId": report_id,
        "datasetId": dataset_id,
    }
