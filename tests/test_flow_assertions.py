import pytest

from specs.models import FlowAssertion


@pytest.mark.django_db
class TestFlowAssertionModel:
    def test_create_assertion(self):
        a = FlowAssertion.objects.create(
            assertion_id="TEST001",
            title="Test assertion",
            assertion_type="table_invariant",
            entity_types=["1120S"],
            definition={"table_name": "MACRS_200DB_HY", "check": "sum_equals_one"},
        )
        assert a.assertion_id == "TEST001"
        assert a.status == "active"

    def test_seed_creates_every_starter_assertion(self):
        """Every authored starter assertion reaches the DB, with the type mix intact.

        The count assertion reads the authored list rather than a literal, because a
        literal is what rotted here: `FA-K1-ROUND` was added in 05cbe72 and this test
        went red on every run afterwards, asserting 20 against a seeder that creates 21.
        A permanently-red test is one nobody reads. The TYPE counts stay literal on
        purpose — those are the tripwire, and moving one should be a deliberate edit.
        """
        from django.core.management import call_command

        from specs.management.commands.seed_flow_assertions import ASSERTIONS

        call_command("seed_flow_assertions")
        assert FlowAssertion.objects.count() == len(ASSERTIONS)
        assert FlowAssertion.objects.filter(assertion_type="table_invariant").count() == 4
        assert FlowAssertion.objects.filter(assertion_type="flow_assertion").count() == 9
        assert FlowAssertion.objects.filter(assertion_type="reconciliation").count() == 8
