from app.dynamic.matcher import EndpointMatcher


def test_matcher_supports_method_and_path_parameters():
    matcher = EndpointMatcher([
        {
            "api_id": "11111111-1111-1111-1111-111111111111",
            "api_version_id": "22222222-2222-2222-2222-222222222222",
            "owner_id": "33333333-3333-3333-3333-333333333333",
            "name": "Users",
            "base_path": "/users/{id}",
            "http_method": "GET",
            "version": "v1",
            "is_private": False,
            "is_active": True,
        }
    ])
    result = matcher.match(method="GET", path="/users/42")
    assert result.path_parameters == {"id": "42"}
