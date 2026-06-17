import json
import subprocess
import sys

from ai_automation_kit.core.adapter_artifacts import build_adapter_blueprint, write_adapter_artifacts


def test_write_adapter_artifacts_creates_blueprint_and_runnable_starter(tmp_path):
    candidate = {
        "full_name": "example/strong",
        "url": "https://github.com/example/strong",
        "score": 94,
        "license": "MIT",
        "language": "Python",
        "business_area": "operations",
    }

    artifacts = write_adapter_artifacts(tmp_path, candidate, business_area="operations")

    blueprint = json.loads((tmp_path / "adapter_blueprint.json").read_text())
    assert {"kind": "adapter_blueprint", "path": "adapter_blueprint.md"} in artifacts
    assert blueprint["candidate"]["full_name"] == "example/strong"
    assert blueprint["contract"]["mode"] == "adapter_only"
    smoke_result = subprocess.run(
        [sys.executable, str(tmp_path / "adapter_starter" / "smoke_test.py")],
        cwd=tmp_path,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "adapter smoke test passed" in smoke_result.stdout


def test_build_adapter_blueprint_defaults_to_candidate_business_area():
    blueprint = build_adapter_blueprint(
        {
            "full_name": "example/support",
            "url": "https://github.com/example/support",
            "score": 90,
            "license": "Apache-2.0",
            "language": "TypeScript",
            "business_area": "support",
        },
        business_area=None,
    )

    assert blueprint["candidate"]["business_area"] == "support"
    assert blueprint["candidate"]["deployment_shape"] == "node_adapter"
