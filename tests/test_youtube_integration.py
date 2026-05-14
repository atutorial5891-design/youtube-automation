from src.api.youtube_api import YouTubeClient


def test_youtube_metadata_builder_sets_defaults() -> None:
    client = YouTubeClient(credentials_path="config/youtube-credentials.json")
    metadata = client.build_metadata("Demo", "Description")
    assert metadata.privacy_status == "private"
    assert metadata.tags == []
