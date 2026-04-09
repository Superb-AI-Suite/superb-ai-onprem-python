from typing import List, Optional, Tuple, Union

from spb_onprem.base_service import BaseService
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError

from .entities import WorkflowDefinition, WorkflowNodeDefinition, WorkflowRun


class WorkflowService(BaseService):
    """Workflow API 서비스 스켈레톤.

    Day 1 범위에서는 workflow 모듈 구조와 데이터 모델을 먼저 고정합니다.
    실제 GraphQL operation 문자열과 request wiring은 sunrise API contract가
    확정되는 Day 2 작업에서 연결합니다.
    """

    def create_workflow_definition(
        self,
        key: str,
        name: str,
        start_node_key: str,
        nodes: List[Union[WorkflowNodeDefinition, dict]],
        description: Optional[str] = None,
        trigger_schema: Optional[dict] = None,
    ) -> WorkflowDefinition:
        self._raise_contract_pending("create_workflow_definition")

    def update_workflow_definition(
        self,
        workflow_definition_id: str,
        name: Union[Optional[str], UndefinedType] = Undefined,
        description: Union[Optional[str], UndefinedType] = Undefined,
        start_node_key: Union[Optional[str], UndefinedType] = Undefined,
        nodes: Union[Optional[List[Union[WorkflowNodeDefinition, dict]]], UndefinedType] = Undefined,
        trigger_schema: Union[Optional[dict], UndefinedType] = Undefined,
    ) -> WorkflowDefinition:
        self._raise_contract_pending("update_workflow_definition")

    def activate_workflow_definition(
        self,
        workflow_definition_id: str,
    ) -> WorkflowDefinition:
        if workflow_definition_id is None:
            raise BadParameterError("workflow_definition_id is required.")
        self._raise_contract_pending("activate_workflow_definition")

    def get_workflow_definitions(
        self,
        cursor: Optional[str] = None,
        length: int = 10,
    ) -> Tuple[List[WorkflowDefinition], Optional[str], int]:
        if length < 1 or length > 50:
            raise BadParameterError("length must be between 1 and 50.")
        self._raise_contract_pending("get_workflow_definitions")

    def get_workflow_definition(
        self,
        workflow_definition_id: str,
    ) -> Optional[WorkflowDefinition]:
        if workflow_definition_id is None:
            raise BadParameterError("workflow_definition_id is required.")
        self._raise_contract_pending("get_workflow_definition")

    def start_workflow_run(
        self,
        workflow_definition_id: str,
        trigger_input: Optional[dict] = None,
    ) -> WorkflowRun:
        if workflow_definition_id is None:
            raise BadParameterError("workflow_definition_id is required.")
        self._raise_contract_pending("start_workflow_run")

    def stop_workflow_run(
        self,
        workflow_run_id: str,
        reason: Union[Optional[str], UndefinedType] = Undefined,
    ) -> WorkflowRun:
        if workflow_run_id is None:
            raise BadParameterError("workflow_run_id is required.")
        self._raise_contract_pending("stop_workflow_run")

    def get_workflow_runs(
        self,
        cursor: Optional[str] = None,
        length: int = 10,
    ) -> Tuple[List[WorkflowRun], Optional[str], int]:
        if length < 1 or length > 50:
            raise BadParameterError("length must be between 1 and 50.")
        self._raise_contract_pending("get_workflow_runs")

    def get_workflow_run(
        self,
        workflow_run_id: str,
    ) -> Optional[WorkflowRun]:
        if workflow_run_id is None:
            raise BadParameterError("workflow_run_id is required.")
        self._raise_contract_pending("get_workflow_run")

    def _raise_contract_pending(self, method_name: str):
        raise NotImplementedError(
            f"WorkflowService.{method_name} will be wired after the sunrise workflow API contract is finalized."
        )
