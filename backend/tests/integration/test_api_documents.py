"""Integration tests for document API endpoints."""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
import io

from app.models.document import DocumentStatus


@pytest.mark.integration
class TestTemplatesEndpoint:
    """Tests for GET /api/v1/documents/templates endpoint."""

    @pytest.mark.asyncio
    async def test_get_templates_success(self, client: AsyncClient):
        """Test successful retrieval of templates."""
        response = await client.get("/api/v1/documents/templates")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 2

        # Check structure
        for template in data:
            assert 'name' in template
            assert 'description' in template
            assert 'font' in template
            assert 'font_size' in template
            assert 'line_spacing' in template

        # Check specific templates
        template_names = [t['name'] for t in data]
        assert 'gost_vkr' in template_names
        assert 'gost_coursework' in template_names


@pytest.mark.integration
class TestUploadEndpoint:
    """Tests for POST /api/v1/documents/upload endpoint."""

    @pytest.mark.asyncio
    async def test_upload_document_success(self, client: AsyncClient, sample_docx_path):
        """Test successful document upload."""
        with open(sample_docx_path, 'rb') as f:
            files = {'file': ('test.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {'template': 'gost_vkr'}

            with patch('app.tasks.document_tasks.process_document_task.delay') as mock_task:
                mock_task.return_value = AsyncMock(id='test-task-id')

                response = await client.post(
                    "/api/v1/documents/upload",
                    files=files,
                    data=data
                )

        assert response.status_code == 200
        response_data = response.json()

        assert 'id' in response_data
        assert response_data['original_filename'] == 'test.docx'
        assert response_data['template_name'] == 'gost_vkr'
        assert response_data['status'] == DocumentStatus.UPLOADED.value

    @pytest.mark.asyncio
    async def test_upload_document_wrong_extension(self, client: AsyncClient):
        """Test upload with wrong file extension."""
        file_content = b'test content'
        files = {'file': ('test.txt', io.BytesIO(file_content), 'text/plain')}
        data = {'template': 'gost_vkr'}

        response = await client.post(
            "/api/v1/documents/upload",
            files=files,
            data=data
        )

        assert response.status_code == 400
        assert 'только файлы формата .docx' in response.json()['detail'].lower()

    @pytest.mark.asyncio
    async def test_upload_document_invalid_template(self, client: AsyncClient, sample_docx_path):
        """Test upload with invalid template."""
        with open(sample_docx_path, 'rb') as f:
            files = {'file': ('test.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {'template': 'invalid_template'}

            response = await client.post(
                "/api/v1/documents/upload",
                files=files,
                data=data
            )

        assert response.status_code == 400
        assert 'не найден' in response.json()['detail'].lower()

    @pytest.mark.asyncio
    async def test_upload_document_default_template(self, client: AsyncClient, sample_docx_path):
        """Test upload with default template (no template specified)."""
        with open(sample_docx_path, 'rb') as f:
            files = {'file': ('test.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}

            with patch('app.tasks.document_tasks.process_document_task.delay') as mock_task:
                mock_task.return_value = AsyncMock(id='test-task-id')

                response = await client.post(
                    "/api/v1/documents/upload",
                    files=files
                )

        assert response.status_code == 200
        response_data = response.json()

        # Should default to gost_vkr
        assert response_data['template_name'] == 'gost_vkr'


@pytest.mark.integration
class TestGetDocumentStatus:
    """Tests for GET /api/v1/documents/documents/{document_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_document_status_not_found(self, client: AsyncClient):
        """Test getting status of non-existent document."""
        response = await client.get("/api/v1/documents/documents/99999")

        assert response.status_code == 404
        assert 'не найден' in response.json()['detail'].lower()

    @pytest.mark.asyncio
    async def test_get_document_status_success(self, client: AsyncClient, test_db, sample_docx_path):
        """Test successful document status retrieval."""
        from app.models.document import Document

        # Create a document in the database
        document = Document(
            original_filename='test.docx',
            original_file_path=str(sample_docx_path),
            template_name='gost_vkr',
            status=DocumentStatus.PROCESSING
        )
        test_db.add(document)
        await test_db.commit()
        await test_db.refresh(document)

        response = await client.get(f"/api/v1/documents/documents/{document.id}")

        assert response.status_code == 200
        response_data = response.json()

        assert response_data['id'] == document.id
        assert response_data['original_filename'] == 'test.docx'
        assert response_data['template_name'] == 'gost_vkr'
        assert response_data['status'] == DocumentStatus.PROCESSING.value


@pytest.mark.integration
class TestListDocuments:
    """Tests for GET /api/v1/documents/documents endpoint."""

    @pytest.mark.asyncio
    async def test_list_documents_empty(self, client: AsyncClient):
        """Test listing documents when database is empty."""
        response = await client.get("/api/v1/documents/documents")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_documents_with_data(self, client: AsyncClient, test_db, sample_docx_path):
        """Test listing documents with data."""
        from app.models.document import Document

        # Create multiple documents
        for i in range(3):
            document = Document(
                original_filename=f'test_{i}.docx',
                original_file_path=str(sample_docx_path),
                template_name='gost_vkr' if i % 2 == 0 else 'gost_coursework',
                status=DocumentStatus.COMPLETED
            )
            test_db.add(document)

        await test_db.commit()

        response = await client.get("/api/v1/documents/documents")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 3
        assert all('id' in doc for doc in data)
        assert all('template_name' in doc for doc in data)

    @pytest.mark.asyncio
    async def test_list_documents_pagination(self, client: AsyncClient, test_db, sample_docx_path):
        """Test listing documents with pagination."""
        from app.models.document import Document

        # Create 5 documents
        for i in range(5):
            document = Document(
                original_filename=f'test_{i}.docx',
                original_file_path=str(sample_docx_path),
                template_name='gost_vkr',
                status=DocumentStatus.COMPLETED
            )
            test_db.add(document)

        await test_db.commit()

        # Test with limit
        response = await client.get("/api/v1/documents/documents?limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

        # Test with skip
        response = await client.get("/api/v1/documents/documents?skip=3")
        assert response.status_code == 200
        assert len(response.json()) == 2

        # Test with skip and limit
        response = await client.get("/api/v1/documents/documents?skip=1&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2


@pytest.mark.integration
class TestDownloadDocument:
    """Tests for GET /api/v1/documents/documents/{document_id}/download endpoint."""

    @pytest.mark.asyncio
    async def test_download_document_not_found(self, client: AsyncClient):
        """Test downloading non-existent document."""
        response = await client.get("/api/v1/documents/documents/99999/download")

        assert response.status_code == 404
        assert 'не найден' in response.json()['detail'].lower()

    @pytest.mark.asyncio
    async def test_download_document_not_completed(self, client: AsyncClient, test_db, sample_docx_path):
        """Test downloading document that is not yet completed."""
        from app.models.document import Document

        document = Document(
            original_filename='test.docx',
            original_file_path=str(sample_docx_path),
            template_name='gost_vkr',
            status=DocumentStatus.PROCESSING
        )
        test_db.add(document)
        await test_db.commit()
        await test_db.refresh(document)

        response = await client.get(f"/api/v1/documents/documents/{document.id}/download")

        assert response.status_code == 400
        assert 'не обработан' in response.json()['detail'].lower()

    @pytest.mark.asyncio
    async def test_download_document_success(self, client: AsyncClient, test_db, sample_docx_path):
        """Test successful document download."""
        from app.models.document import Document

        document = Document(
            original_filename='test.docx',
            original_file_path=str(sample_docx_path),
            formatted_file_path=str(sample_docx_path),  # Using same file for test
            template_name='gost_vkr',
            status=DocumentStatus.COMPLETED
        )
        test_db.add(document)
        await test_db.commit()
        await test_db.refresh(document)

        response = await client.get(f"/api/v1/documents/documents/{document.id}/download")

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
