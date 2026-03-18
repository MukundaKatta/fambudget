"""Tests for Fambudget."""
from src.core import Fambudget
def test_init(): assert Fambudget().get_stats()["ops"] == 0
def test_op(): c = Fambudget(); c.process(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Fambudget(); [c.process() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Fambudget(); c.process(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Fambudget(); r = c.process(); assert r["service"] == "fambudget"
