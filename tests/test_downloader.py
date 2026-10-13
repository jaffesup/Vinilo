import unittest
from pathlib import Path

from downloader import (
    DownloadQueue, Kind, Status, build_command, extract_urls, resolve_kind, video_format
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

    def test_advanced_options_add_subtitles_chapters_and_metadata(self):
        options = {
            "write_subtitles": True,
            "write_auto_subtitles": True,
            "embed_subtitles": True,
            "subtitle_languages": "es,en",
            "split_chapters": True,
            "export_description": True,
            "write_info_json": True,
            "video_container": "webm",
            "preferred_frame_rate": "60",
        }
        cmd = build_command(Kind.VIDEO, "https://example.com/video", Path("ffmpeg"),
                            Path("downloads"), "1080p", options=options)
        for flag in ("--write-subs", "--write-auto-subs", "--embed-subs",
                     "--sub-langs", "--split-chapters", "--write-description",
                     "--write-info-json"):
            self.assertIn(flag, cmd)
        self.assertIn("es,en", cmd)
        self.assertIn("webm", cmd)
        self.assertIn("fps:60", cmd)

    def test_advanced_options_can_disable_metadata_and_thumbnail(self):
        cmd = build_command(
            Kind.SONG, "https://example.com/audio", Path("ffmpeg"), Path("downloads"),
            options={"embed_metadata": False, "embed_thumbnail": False},
        )
        self.assertNotIn("--embed-metadata", cmd)
        self.assertNotIn("--embed-thumbnail", cmd)
        self.assertNotIn("--write-thumbnail", cmd)

    def test_invalid_video_container_falls_back_to_mp4(self):
        cmd = build_command(
            Kind.VIDEO, "https://example.com/video", Path("ffmpeg"), Path("downloads"),
            options={"video_container": "not-a-container"},
        )
        self.assertEqual(cmd[cmd.index("--merge-output-format") + 1], "mp4")

    def test_retry_failed_resets_job_to_pending(self):
        queue = DownloadQueue(lambda *_: None)
        job = queue.add("https://example.com/video", "720p")
        job.status = Status.ERROR
        job.progress = 63.0
        job.code = 1
        self.assertEqual(queue.retry_failed(), [job.id])
        self.assertEqual(job.status, Status.PENDING)
        self.assertEqual(job.progress, 0.0)
        self.assertIsNone(job.code)


if __name__ == "__main__":
    unittest.main()
