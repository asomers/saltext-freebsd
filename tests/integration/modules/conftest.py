"""
Pytest fixtures for integration module tests that need a running Salt master.

Master/minion factories are created in ``tests/conftest.py``. This module
overrides those fixtures to start the daemons and bridge their configuration
into ``RUNTIME_VARS`` for ``ModuleCase``-based tests. Fixtures are not
autouse; tests must request ``bridge_pytest_and_runtests`` (for example via
``pytest.mark.usefixtures``).
"""

import os

import pytest
import salt.config
from salt.utils.immutabletypes import freeze

from tests.support.runtests import RUNTIME_VARS


@pytest.fixture(scope="package")
def minion_config():  # pragma: no cover
    """
    ModuleCase targets the minion id ``minion`` by default.
    """
    return {"id": "minion", "minion_id": "minion"}


@pytest.fixture(scope="package")
def master(master):  # pragma: no cover
    with master.started():
        yield master


@pytest.fixture(scope="package")
def minion(minion):  # pragma: no cover
    with minion.started():
        salt_call_cli = minion.salt_call_cli()
        ret = salt_call_cli.run("saltutil.sync_all")
        assert ret.returncode == 0, ret
        yield minion


@pytest.fixture(scope="package")
def bridge_pytest_and_runtests(master, minion, salt_factories):  # pragma: no cover
    """
    Populate RUNTIME_VARS so ModuleCase and SaltClientTestCaseMixin can connect
    to the pytest-managed master/minion.
    """
    RUNTIME_VARS.RUNTIME_CONFIGS.pop("runtime_client", None)
    RUNTIME_VARS.RUNTIME_CONFIGS["master"] = freeze(master.config)
    RUNTIME_VARS.RUNTIME_CONFIGS["minion"] = freeze(minion.config)
    RUNTIME_VARS.RUNTIME_CONFIGS["client_config"] = freeze(
        salt.config.client_config(master.config["conf_file"])
    )

    RUNTIME_VARS.TMP_ROOT_DIR = str(salt_factories.root_dir.resolve())
    RUNTIME_VARS.TMP_CONF_DIR = os.path.dirname(master.config["conf_file"])
    RUNTIME_VARS.TMP_MINION_CONF_DIR = os.path.dirname(minion.config["conf_file"])
    yield
