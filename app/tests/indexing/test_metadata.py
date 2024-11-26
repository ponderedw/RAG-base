import pytest

from datetime import datetime
from app.indexing.metadata import DocumentMetadata


class TestDocumentMetadata:

    @pytest.mark.parametrize('init_kwargs', [
        {
            'source_id': '1',
            'source_name': 'test',
            'modified_at': datetime(2021, 1, 1),
            'payload': {'key': 'value'}
        },
        {
            'source_id': 'asdfsa381-3921-1231',
            'source_name': 'my_source_382',
            'modified_at': datetime(2024, 8, 30),
            'payload': {
                'k48': 'v1',
                'k029': 48912,
                'k3': {'inner': 'value'},
            },
        },

        # No payload
        {'source_id': '1', 'source_name': 'test', 'modified_at': datetime(2021, 1, 1)},
    ])
    def test_successful_initialization(self, init_kwargs: dict):
        metadata = DocumentMetadata(**init_kwargs)

        assert metadata.source_id == init_kwargs['source_id']
        assert metadata.source_name == init_kwargs['source_name']
        assert metadata.modified_at == init_kwargs['modified_at']
        assert metadata.payload == init_kwargs.get('payload', {})

    @pytest.mark.parametrize('init_kwargs', [
        # source_id is missing
        {'source_name': 'test', 'modified_at': datetime(2021, 1, 1), 'payload': {}},

        # source_name is missing
        {'source_id': '1', 'modified_at': datetime(2021, 1, 1)},

        # modified_at is missing
        {'source_id': '1', 'source_name': 'test'},
    ])
    def test_failed_initialization(self, init_kwargs: dict):
        with pytest.raises(TypeError):
            DocumentMetadata(**init_kwargs)

    def test_to_dict(self):
        metadata = DocumentMetadata(
            source_id='1',
            source_name='test',
            modified_at=datetime(2021, 1, 21, 19, 30, 0),
            payload={'key': 'value34'},
        )

        assert metadata.to_dict() == {
            'source_id': '1',
            'source_name': 'test',
            'modified_at': '2021-01-21T19:30:00',
            'payload': {'key': 'value34'},
        }
