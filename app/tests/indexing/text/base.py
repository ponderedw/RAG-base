import pytest

from datetime import datetime

from app.indexing.metadata import DocumentMetadata


class IndexingBase:


    @pytest.fixture
    def metadata(self) -> DocumentMetadata:
        return DocumentMetadata(
            source_id='source_id',
            source_name='source_name',
            modified_at=datetime(2021, 10, 20),
            payload={'k1': 'v1'},
        )
    
    @pytest.fixture
    def text(self) -> str:
        return ' '.join([
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            'Curabitur finibus ultricies augue, a lobortis elit lobortis nec.',
            'Donec sodales mauris a ultrices vehicula. Phasellus eget arcu leo.',
            'Morbi a arcu maximus, ultricies ipsum condimentum, vulputate tortor.',
            'Sed vel nibh ac quam tincidunt vehicula. Quisque semper leo eget ',
            'lacus pellentesque eleifend. Quisque vel purus sodales, efficitur lectus',
            'ac, ornare risus. Quisque ante elit, blandit sit amet tortor ut, tincidunt',
            'ornare dolor. Donec vel imperdiet magna. Mauris porta porta sagittis. Nam',
            'lacus nisl, sagittis mollis scelerisque vitae, scelerisque eu nisi. Vivamus',
            'arcu dolor, sollicitudin a pretium non, convallis at massa. Sed eu dui',
            'elementum, maximus ex lobortis, feugiat odio. Nulla finibus pretium ipsum,',
            'a finibus ex ultrices at.',
            '\n\n',
            'The quick brown fox jumps over the lazy dog. Then the lazy dog barks at the fox.',
            'Said the fox to the dog: "Why are you barking at me? I am just passing by."',
        ])
