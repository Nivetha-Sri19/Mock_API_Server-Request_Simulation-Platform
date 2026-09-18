import pytest

from app.dynamic.scenario_handler import ScenarioHandler


def test_success_scenario_is_default():
    handler = ScenarioHandler()
    result = handler.select_template(
        responses=[
            {"scenario": "success", "status_code": 200, "body": {"ok": True}},
            {"scenario": "not_found", "status_code": 404, "body": {"ok": False}},
        ]
    )
    assert result["status_code"] == 200


@pytest.mark.parametrize("scenario,status", [("not_found", 404), ("server_error", 500)])
def test_requested_scenario(scenario, status):
    result = ScenarioHandler().select_template(
        responses=[
            {"scenario": "success", "status_code": 200},
            {"scenario": scenario, "status_code": status},
        ],
        scenario=scenario,
    )
    assert result["status_code"] == status
