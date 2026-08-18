import pytest

from tests.support.case import ModuleCase

pytestmark = [
    pytest.mark.skip_unless_on_freebsd,
    pytest.mark.usefixtures("bridge_pytest_and_runtests"),
]


class SysrcModuleTest(ModuleCase):
    def setUp(self):
        super().setUp()
        ret = self.run_function("cmd.has_exec", ["sysrc"])
        if not ret:
            self.skipTest("sysrc not found")

    def test_show(self):
        ret = self.run_function("sysrc.get")
        assert isinstance(ret, dict), "sysrc.get returned wrong type, expecting dictionary"
        assert "/etc/rc.conf" in ret, "sysrc.get should have an rc.conf key in it."

    @pytest.mark.destructive_test
    def test_set(self):
        ret = self.run_function("sysrc.set", ["test_var", "1"])
        assert isinstance(ret, dict), "sysrc.get returned wrong type, expecting dictionary"
        assert "/etc/rc.conf" in ret, "sysrc.set should have an rc.conf key in it."
        assert "1" in ret["/etc/rc.conf"]["test_var"], "sysrc.set should return the value it set."
        ret = self.run_function("sysrc.remove", ["test_var"])
        assert "test_var removed" == ret

    @pytest.mark.destructive_test
    def test_set_bool(self):
        ret = self.run_function("sysrc.set", ["test_var", True])
        assert isinstance(ret, dict), "sysrc.get returned wrong type, expecting dictionary"
        assert "/etc/rc.conf" in ret, "sysrc.set should have an rc.conf key in it."
        assert "YES" in ret["/etc/rc.conf"]["test_var"], "sysrc.set should return the value it set."
        ret = self.run_function("sysrc.remove", ["test_var"])
        assert "test_var removed" == ret
