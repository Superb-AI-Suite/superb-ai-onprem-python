from typing import Union, Optional

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.graphql import build_query


def get_exports_params(
    dataset_id: str,
    filter_params: Union[
        UndefinedType,
        dict
    ] = Undefined,
    order_by: Union[
        UndefinedType,
        dict
    ] = Undefined,
    cursor: Union[
        UndefinedType,
        str
    ] = Undefined,
    length: Union[
        UndefinedType,
        int
    ] = Undefined,
):
    """Create parameters for getting exports.
    
    Args:
        dataset_id (str): The ID of the dataset to get exports for.
        filter_params (Optional[dict]): The filter to apply to the exports.
        order_by (Optional[dict]): The order to return the exports in.
        cursor (Optional[str]): The cursor to use for pagination.
        length (Optional[int]): The number of exports to return.
        
    Returns:
        dict: Parameters for getting exports
    """
    params = {
        "datasetId": dataset_id,
    }

    if filter_params is not Undefined:
        params["filter"] = filter_params
    if order_by is not Undefined:
        params["orderBy"] = order_by
    if cursor is not Undefined:
        params["cursor"] = cursor
    if length is not Undefined:
        params["length"] = length

    return params


def get_exports_query(params: dict) -> str:
    """Build GraphQL query for getting exports.
    
    Args:
        params (dict): Parameters for the query
        
    Returns:
        str: GraphQL query
    """
    query = """
        query GetExports(
            $datasetId: String!
            $filter: ExportFilter
            $orderBy: ExportOrderBy
            $cursor: String
            $length: Int
        ) {
            exports(
                datasetId: $datasetId
                filter: $filter
                orderBy: $orderBy
                cursor: $cursor
                length: $length
            ) {
                exports {
                    id
                    name
                    location
                    status
                    dataFilter
                    dataCount
                    frameCount
                    annotationCount
                    meta
                    createdAt
                    completedAt
                }
                next
                totalCount
            }
        }
    """
    
    return build_query(query, params) 