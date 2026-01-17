"""Factory for creating validated chart data for analytics reports."""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel


class CategoryValueData(BaseModel):
    """Data model for category-value based charts (PIE, BAR charts)."""
    category: str
    value: Union[int, float]


class HeatmapData(BaseModel):
    """Data model for heatmap charts."""
    y_category: str
    x_category: str
    value: Union[int, float]


class LineChartData(BaseModel):
    """Data model for line charts."""
    series: str
    x: Union[int, float, str]
    y: Union[int, float]


class ScatterPlotData(BaseModel):
    """Data model for scatter plot charts."""
    x: Union[int, float]
    y: Union[int, float]
    category: Optional[str] = None


class BinFrequencyData(BaseModel):
    """Data model for histogram charts."""
    bin: str
    frequency: Union[int, float]


class MetricData(BaseModel):
    """Data model for metrics charts."""
    key: str
    value: Union[str, int, float, Dict[str, Any]]


class DataIdsIndex(BaseModel):
    """Data model for data IDs indexed by a key."""
    index: str
    data_ids: List[str]


class XYDataIds(BaseModel):
    """Data model for data IDs indexed by x and y coordinates (used in heatmap and table charts)."""
    x: str
    y: str
    data_ids: List[str]


class LineChartDataIds(BaseModel):
    """Data model for line chart data IDs indexed by series and x."""
    series: str
    x: str
    data_ids: List[str]


class ChartDataResult(BaseModel):
    """DTO for chart data factory results."""
    reports_json: Dict[str, Any]
    data_ids_json: Optional[Dict[str, Any]] = None


class ChartDataFactory:
    """Factory class for creating validated chart data for different analytics report types."""
    
    @staticmethod
    def create_pie_chart(
        category_name: str,
        value_name: str,
        data: List[CategoryValueData],
        data_ids: Optional[List[DataIdsIndex]] = None
    ) -> ChartDataResult:
        """Create validated PIE chart data.
        
        Args:
            category_name (str): Name of the category field
            value_name (str): Name of the value field
            data (List[CategoryValueData]): List of category-value data points
            data_ids (Optional[List[DataIdsIndex]]): List of data IDs indexed by category
        
        Returns:
            ChartDataResult: Chart data result object
        """
        reports_json = {
            "category_name": category_name,
            "value_name": value_name,
            "data": [item.model_dump() for item in data]
        }
        
        data_ids_json = None
        if data_ids:
            data_ids_json = {"data_ids": [item.model_dump() for item in data_ids]}
        
        return ChartDataResult(reports_json=reports_json, data_ids_json=data_ids_json)
    
    @staticmethod
    def create_horizontal_bar_chart(
        y_axis_name: str,
        x_axis_name: str,
        data: List[CategoryValueData],
        data_ids: Optional[List[DataIdsIndex]] = None
    ) -> ChartDataResult:
        """Create validated HORIZONTAL_BAR chart data.
        
        Args:
            y_axis_name (str): Name of the Y-axis (category)
            x_axis_name (str): Name of the X-axis (value)
            data (List[CategoryValueData]): List of category-value data points
            data_ids (Optional[List[DataIdsIndex]]): List of data IDs indexed by category
        
        Returns:
            ChartDataResult: Chart data result object
        """
        reports_json = {
            "y_axis_name": y_axis_name,
            "x_axis_name": x_axis_name,
            "data": [item.model_dump() for item in data]
        }
        
        data_ids_json = None
        if data_ids:
            data_ids_json = {"data_ids": [item.model_dump() for item in data_ids]}
        
        return ChartDataResult(reports_json=reports_json, data_ids_json=data_ids_json)
    
    @staticmethod
    def create_vertical_bar_chart(
        x_axis_name: str,
        y_axis_name: str,
        data: List[CategoryValueData],
        data_ids: Optional[List[DataIdsIndex]] = None
    ) -> ChartDataResult:
        """Create validated VERTICAL_BAR chart data.
        
        Args:
            x_axis_name (str): Name of the X-axis (category)
            y_axis_name (str): Name of the Y-axis (value)
            data (List[CategoryValueData]): List of category-value data points
            data_ids (Optional[List[DataIdsIndex]]): List of data IDs indexed by category
        
        Returns:
            ChartDataResult: Chart data result object
        """
        reports_json = {
            "x_axis_name": x_axis_name,
            "y_axis_name": y_axis_name,
            "data": [item.model_dump() for item in data]
        }
        
        data_ids_json = None
        if data_ids:
            data_ids_json = {"data_ids": [item.model_dump() for item in data_ids]}
        
        return ChartDataResult(reports_json=reports_json, data_ids_json=data_ids_json)
    
    @staticmethod
    def create_heatmap_chart(
        y_axis_name: str,
        x_axis_name: str,
        data: List[HeatmapData],
        data_ids: Optional[List[XYDataIds]] = None
    ) -> ChartDataResult:
        """Create validated HEATMAP chart data.
        
        Args:
            y_axis_name (str): Name of the Y-axis category
            x_axis_name (str): Name of the X-axis category
            data (List[HeatmapData]): List of heatmap data points
            data_ids (Optional[List[XYDataIds]]): List of data IDs indexed by x and y coordinates
        
        Returns:
            ChartDataResult: Chart data result object
        """
        reports_json = {
            "y_axis_name": y_axis_name,
            "x_axis_name": x_axis_name,
            "data": [item.model_dump() for item in data]
        }
        
        data_ids_json = None
        if data_ids:
            data_ids_json = {"data_ids": [item.model_dump() for item in data_ids]}
        
        return ChartDataResult(reports_json=reports_json, data_ids_json=data_ids_json)
    
    @staticmethod
    def create_table_chart(
        headers: List[str],
        rows: List[List[Any]],
        data_ids: Optional[List[XYDataIds]] = None
    ) -> ChartDataResult:
        """Create validated TABLE chart data.
        
        Args:
            headers (List[str]): Column headers
            rows (List[List]): Table rows
            data_ids (Optional[List[XYDataIds]]): List of data IDs for each cell (x=column, y=row)
        
        Returns:
            ChartDataResult: Chart data result object
        """
        if not headers:
            raise ValueError("Headers must not be empty")
        
        for row in rows:
            if len(row) != len(headers):
                raise ValueError(f"Row length {len(row)} does not match headers length {len(headers)}")
        
        reports_json = {
            "data": {
                "headers": headers,
                "rows": rows
            }
        }
        
        data_ids_json = None
        if data_ids:
            data_ids_json = {"data_ids": [item.model_dump() for item in data_ids]}
        
        return ChartDataResult(reports_json=reports_json, data_ids_json=data_ids_json)
    
    @staticmethod
    def create_line_chart(
        x_name: str,
        y_name: str,
        data: List[LineChartData],
        data_ids: Optional[List[LineChartDataIds]] = None
    ) -> ChartDataResult:
        """Create validated LINE_CHART data.
        
        Args:
            x_name (str): Name of the X-axis
            y_name (str): Name of the Y-axis
            data (List[LineChartData]): List of line chart data points with series
            data_ids (Optional[List[LineChartDataIds]]): List of data IDs indexed by series and x
        
        Returns:
            ChartDataResult: Chart data result object
        """
        reports_json = {
            "x_name": x_name,
            "y_name": y_name,
            "data": [item.model_dump() for item in data]
        }
        
        data_ids_json = None
        if data_ids:
            data_ids_json = {"data_ids": [item.model_dump() for item in data_ids]}
        
        return ChartDataResult(reports_json=reports_json, data_ids_json=data_ids_json)
    
    @staticmethod
    def create_scatter_plot_chart(
        x_name: str,
        y_name: str,
        data: List[ScatterPlotData],
        data_ids: Optional[List[DataIdsIndex]] = None
    ) -> ChartDataResult:
        """Create validated SCATTER_PLOT chart data.
        
        Args:
            x_name (str): Name of the X-axis
            y_name (str): Name of the Y-axis
            data (List[ScatterPlotData]): List of scatter plot data points with optional category
            data_ids (Optional[List[DataIdsIndex]]): List of data IDs indexed by category
        
        Returns:
            ChartDataResult: Chart data result object
        """
        reports_json = {
            "x_name": x_name,
            "y_name": y_name,
            "data": [item.model_dump(exclude_none=True) for item in data]
        }
        
        data_ids_json = None
        if data_ids:
            data_ids_json = {"data_ids": [item.model_dump() for item in data_ids]}
        
        return ChartDataResult(reports_json=reports_json, data_ids_json=data_ids_json)
    
    @staticmethod
    def create_histogram_chart(
        bin_name: str,
        frequency_name: str,
        data: List[BinFrequencyData],
        data_ids: Optional[List[DataIdsIndex]] = None
    ) -> ChartDataResult:
        """Create validated HISTOGRAM chart data.
        
        Args:
            bin_name (str): Name of the bin field
            frequency_name (str): Name of the frequency field
            data (List[BinFrequencyData]): List of bin-frequency data points
            data_ids (Optional[List[DataIdsIndex]]): List of data IDs indexed by bin
        
        Returns:
            ChartDataResult: Chart data result object
        """
        reports_json = {
            "bin_name": bin_name,
            "frequency_name": frequency_name,
            "data": [item.model_dump() for item in data]
        }
        
        data_ids_json = None
        if data_ids:
            data_ids_json = {"data_ids": [item.model_dump() for item in data_ids]}
        
        return ChartDataResult(reports_json=reports_json, data_ids_json=data_ids_json)
    
    @staticmethod
    def create_metrics_chart(
        metrics: List[MetricData],
        data_ids: Optional[List[str]] = None
    ) -> ChartDataResult:
        """Create validated METRICS chart data.
        
        Args:
            metrics (List[MetricData]): List of metric data with key-value pairs
            data_ids (Optional[List[str]]): List of data IDs
        
        Returns:
            ChartDataResult: Chart data result object
        """
        if not metrics:
            raise ValueError("Metrics must not be empty")
        
        reports_json = {
            "data": [item.model_dump() for item in metrics]
        }
        
        data_ids_json = None
        if data_ids:
            data_ids_json = {"data_ids": data_ids}
        
        return ChartDataResult(reports_json=reports_json, data_ids_json=data_ids_json)
