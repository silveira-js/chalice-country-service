import pytest
from unittest.mock import Mock, patch
from chalicelib.rate_limiter import RateLimiter
from botocore.exceptions import ClientError


class TestRateLimiter:
    @pytest.fixture
    def rate_limiter(self):
        mock_redis = Mock()
        mock_rate_limites = {'default': {'limit': 5, 'period': 60}}
        with patch('chalicelib.rate_limiter.Redis'), patch('chalicelib.rate_limiter.boto3.client'):
            return RateLimiter(mock_redis, mock_rate_limites)

    def test_request_is_limited_first_request(self, rate_limiter):
        rate_limiter.redis_client.get.return_value = None
        
        result = rate_limiter.request_is_limited("test_key", 5, 60)
        
        assert result == False
        rate_limiter.redis_client.set.assert_called_once_with("test_key", 1, ex=60)

    def test_request_is_limited_under_limit(self, rate_limiter):
        rate_limiter.redis_client.get.return_value = "3"
        
        result = rate_limiter.request_is_limited("test_key", 5, 60)
        
        assert result == False
        rate_limiter.redis_client.incr.assert_called_once_with("test_key")

    def test_request_is_limited_over_limit(self, rate_limiter):
        rate_limiter.redis_client.get.return_value = "5"
        
        result = rate_limiter.request_is_limited("test_key", 5, 60)
        
        assert result == True
