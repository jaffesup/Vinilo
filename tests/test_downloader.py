import unittest
from pathlib import Path

from downloader import (
    Kind, build_command, extract_urls, resolve_kind, video_format
)


class DownloaderTests(unittest.TestCase):
    def test_extract_urls_keeps_order_and_deduplicates(self):
        text = "https://example.com/a https://example.com/a\nhttps://example.org/b"
        self.assertEqual(extract_urls(text), [
            "https://example.com/a", "https://example.org/b"
        ])

    def test_video_format_quality(self):
        self.assertEqual(video_format("720p"), "bv*[height<=720]+ba/b[height<=720]/b")
        self.assertEqual(video_format("Mejor disponible"), "bv*+ba/b")

    def test_auto_detects_music_category(self):
        info = {"_type": "video", "categories": ["Music"], "title": "Track"}
        self.assertEqual(resolve_kind("https://youtube.com/watch?v=abc", info), Kind.SONG)

    def test_auto_playlist_defaults_to_audio(self):
        info = {"_type": "playlist", "entries": []}
        self.assertEqual(resolve_kind("https://youtube.com/playlist?list=abc", info), Kind.PLAYLIST)

    def test_video_mode_keeps_playlist_as_video_playlist(self):
        info = {"_type": "playlist", "entries": []}
        self.assertEqual(resolve_kind("https://youtube.com/playlist?list=abc", info, "video"),
                         Kind.VIDEO_PLAYLIST)

    def test_download_command_requests_thumbnail(self):
        cmd = build_command(Kind.VIDEO, "https://example.com/video", Path("ffmpeg"),
                            Path("downloads"), "1080p")
        self.assertIn("--write-thumbnail", cmd)
        self.assertIn("--embed-thumbnail", cmd)
        self.assertIn("--merge-output-format", cmd)
        self.assertIn("mp4", cmd)


if __name__ == "__main__":
    unittest.main()
