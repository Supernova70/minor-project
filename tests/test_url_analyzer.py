import pytest
from unittest.mock import patch, MagicMock
from app.engines.url_analyzer import UrlAnalyzer

class TestUrlAnalyzer:
    @patch("app.engines.url_analyzer.get_redis")
    @patch("app.engines.url_analyzer.httpx.Client")
    def test_heuristic_checks(self, mock_client, mock_redis):
        analyzer = UrlAnalyzer()
        analyzer._vt_keys = ["mock"]
        
        # Mock HTTPX for VT
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_client.return_value.__enter__.return_value.get.return_value = mock_resp
        
        # Check 2: IP
        res = analyzer.analyze("http://192.168.1.1/login", "")
        flags = res.per_url_results[0].heuristic_flags
        assert any("IP address" in f for f in flags)
        
        # Check 4: Shortener
        res = analyzer.analyze("http://bit.ly/xyz", "")
        flags = res.per_url_results[0].heuristic_flags
        assert any("shortener" in f for f in flags)
        
        # Check 5: Brand
        res = analyzer.analyze("http://paypa1.com/login", "")
        flags = res.per_url_results[0].heuristic_flags
        assert any("Brand impersonation" in f for f in flags)
        
        # Brand false positive
        res = analyzer.analyze("http://paypal.com/login", "")
        flags = res.per_url_results[0].heuristic_flags if res.per_url_results else []
        assert not any("Brand impersonation" in f for f in flags)

    @patch("app.engines.url_analyzer.get_redis")
    @patch("app.engines.url_analyzer.httpx.Client")
    def test_vt_responses(self, mock_client, mock_redis):
        analyzer = UrlAnalyzer()
        analyzer._vt_keys = ["mock"]
        
        # 200 OK
        mock_resp_200 = MagicMock()
        mock_resp_200.status_code = 200
        mock_resp_200.json.return_value = {
            "data": {"attributes": {"last_analysis_stats": {"malicious": 5, "suspicious": 2, "harmless": 50}}}
        }
        mock_client.return_value.__enter__.return_value.get.side_effect = [mock_resp_200]
        res = analyzer.analyze("http://evil.com", "")
        assert res.per_url_results[0].vt_malicious == 5
        
        # 429
        mock_resp_429 = MagicMock()
        mock_resp_429.status_code = 429
        mock_client.return_value.__enter__.return_value.get.side_effect = [mock_resp_429]
        res = analyzer.analyze("http://busy.com", "")
        assert "rate limit" in res.per_url_results[0].vt_error
