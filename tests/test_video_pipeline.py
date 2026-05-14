from pathlib import Path

from src.video.video_assembler import VideoAssembler


def test_render_plan_wires_expected_paths(tmp_path: Path) -> None:
    assembler = VideoAssembler()
    plan = assembler.build_plan(
        script_path=tmp_path / "script.txt",
        narration_path=tmp_path / "audio.mp3",
        image_paths=[tmp_path / "frame_1.png"],
        output_path=tmp_path / "video.mp4",
    )
    assert plan.output_path.name == "video.mp4"
    assert len(plan.image_paths) == 1
