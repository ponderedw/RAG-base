import pytest

from datetime import datetime, timedelta

from app.utils.singleton import Singleton
from app.tests.test_utils.date_utils import patch_now


class TestSingleton:
    """Tests for the Singleton metaclass."""

    class TestClass(metaclass=Singleton):
        """A test class that uses the Singleton metaclass.
        
        Used throught the tests to test the Singleton metaclass.
        """
        MAX_INSTANCE_TTL = timedelta(seconds=30)


    def test_returns_same_instance(self):
        """Test that the Singleton metaclass returns the same instance for the same class."""

        # Run
        instance1 = self.TestClass()
        instance2 = self.TestClass()

        # Test - Make sure that the two instances are the same.
        assert instance1 is instance2

    def test_returns_different_instance_after_ttl(self):
        """Test that the Singleton metaclass returns a different instance after the TTL has passed."""

        # Setup
        instance1 = self.TestClass()
        org_now = datetime.now()
        
        # Run - "Move the time forward" by 31 seconds and create a new instance.
        with patch_now('app.utils.singleton.datetime', org_now + timedelta(seconds=31)):
            instance2 = self.TestClass()

        # Test - Make sure that the two instances are different.
        assert instance1 is not instance2

    @pytest.mark.parametrize('force_recreate', [True, False])
    def test_force_recreate(self, force_recreate: bool):
        """Test that the Singleton metaclass returns a different instance when `force_recreate` is set to `True`."""

        # Setup
        instance1 = self.TestClass()

        # Run - Create a new instance with `force_recreate`.
        instance2 = self.TestClass(force_recreate=force_recreate)

        # Test - Make sure that the two instances are different when `force_recreate` is set.
        assert (instance1 is not instance2) == force_recreate
