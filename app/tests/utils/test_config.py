import os
import pytest

from unittest.mock import patch

from app.utils.config import Config


class TestConfig:

    @pytest.mark.parametrize('deploy_env,expected_deploy_env', [
        ('local', 'LOCAL'),
        ('DEV', 'DEV'),
        ('stAGinG', 'STAGING'),
        ('PROD', 'PROD'),
    ])
    def test_get_deploy_env(self, deploy_env: str, expected_deploy_env: str):
        """`get_deploy_env` should return the deployment environment in al caps."""
        # Setup
        with patch.dict(os.environ, {'DEPLOY_ENV': deploy_env}):

            # Run + Validate
            assert Config.get_deploy_env() == expected_deploy_env


    def test_get_deploy_env_default(self):
        """Test the default value for the deployment environment."""

        # Setup
        with patch.dict(os.environ) as env_mock:
            del env_mock['DEPLOY_ENV']

            # Run + Validate
            assert Config.get_deploy_env() == 'PROD'
