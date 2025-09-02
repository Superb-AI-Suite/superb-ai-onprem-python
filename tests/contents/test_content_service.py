import pytest
from unittest.mock import Mock, patch

from spb_onprem.contents.service import ContentService
from spb_onprem.contents.queries import Queries


class TestContentService:
    """Test cases for ContentService with new delete_content method."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.content_service = ContentService()
        self.content_service.request_gql = Mock()

    def test_delete_content_success(self):
        """Test successful content deletion."""
        # Arrange
        content_id = "test-content-123"
        mock_response = {"deleteContent": True}
        self.content_service.request_gql.return_value = mock_response

        # Act
        result = self.content_service.delete_content(content_id)

        # Assert
        assert result is True
        self.content_service.request_gql.assert_called_once_with(
            query=Queries.DELETE,
            variables=Queries.DELETE["variables"](content_id)
        )

    def test_delete_content_failure(self):
        """Test content deletion failure."""
        # Arrange
        content_id = "nonexistent-content"
        mock_response = {"deleteContent": False}
        self.content_service.request_gql.return_value = mock_response

        # Act
        result = self.content_service.delete_content(content_id)

        # Assert
        assert result is False
        self.content_service.request_gql.assert_called_once_with(
            query=Queries.DELETE,
            variables=Queries.DELETE["variables"](content_id)
        )

    def test_delete_content_missing_response(self):
        """Test content deletion with missing response field."""
        # Arrange
        content_id = "test-content-456"
        mock_response = {}  # No deleteContent field
        self.content_service.request_gql.return_value = mock_response

        # Act
        result = self.content_service.delete_content(content_id)

        # Assert
        assert result is False
        self.content_service.request_gql.assert_called_once_with(
            query=Queries.DELETE,
            variables=Queries.DELETE["variables"](content_id)
        )

    def test_delete_content_query_structure(self):
        """Test that DELETE query has correct structure."""
        # Arrange & Act
        query_structure = Queries.DELETE

        # Assert
        assert query_structure["name"] == "deleteContent"
        assert "mutation DeleteContent($id: ID!)" in query_structure["query"]
        assert "deleteContent(id: $id)" in query_structure["query"]
        assert callable(query_structure["variables"])

    def test_delete_content_variables_function(self):
        """Test that variables function generates correct parameters."""
        # Arrange
        content_id = "test-content-789"

        # Act
        variables = Queries.DELETE["variables"](content_id)

        # Assert
        assert variables == {"id": content_id}

    def test_delete_content_exception_handling(self):
        """Test content deletion exception handling."""
        # Arrange
        content_id = "test-content-error"
        self.content_service.request_gql.side_effect = Exception("Network error")

        # Act & Assert
        with pytest.raises(Exception, match="Network error"):
            self.content_service.delete_content(content_id)

        self.content_service.request_gql.assert_called_once()