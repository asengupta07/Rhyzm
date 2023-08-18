import pytest
from project import list_artists, make_url, get_top, get_tracks, get_headers


def test_list_artists():
    artists = [{"name": "Sophia"}, {"name": "John"}, {"name": "Adam"}]
    assert list_artists(artists=artists) == "Sophia, John and Adam"
    artists = [
        {"name": "Sophia", "type": "Lead Singer"},
        {"name": "John", "type": "Drummer"},
        {"status": "Reserved", "name": "Adam", "type": "Guitarist"},
    ]
    assert list_artists(artists=artists) == "Sophia, John and Adam"
    artists = [
        {"stagename": "Sophia", "type": "Lead Singer"},
        {"stagename": "John", "type": "Drummer"},
        {"status": "Reserved", "name": "Adam", "type": "Guitarist"},
    ]
    with pytest.raises(KeyError):
        assert list_artists(artists=artists)


def test_make_url():
    assert make_url("SF3sgsjh454S") == "https://youtu.be/SF3sgsjh454S"
    assert make_url("HelloWorld") == "https://youtu.be/HelloWorld"
    assert make_url("1234345324") == "https://youtu.be/1234345324"


def test_get_top():
    tracks = get_top()
    for item in tracks:
        assert "track" in item
        assert "album" in item
        assert "image" in item
        assert "artists" in item


def test_get_tracks():
    tracks = get_tracks(query="Hello", N="5")
    for item in tracks:
        assert "track" in item
        assert "album" in item
        assert "image" in item
        assert "artists" in item


def test_get_headers():
    headers = get_headers()
    assert "Authorization" in headers
