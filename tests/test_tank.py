
from pytest import raises
from tank.main import MixbytesTankTest

def test_tank():
    # test tank without any subcommands or arguments
    with MixbytesTankTest() as app:
        app.run()
        assert app.exit_code == 0


def test_tank_debug():
    # test that debug mode is functional
    argv = ['--debug']
    with MixbytesTankTest(argv=argv) as app:
        app.run()
        assert app.debug is True


def test_cluster():
    # test command1 without arguments
    argv = ['cluster']
    with MixbytesTankTest(argv=argv) as app:
        app.run()
        data,output = app.last_rendered
#        assert data['foo'] == 'bar'
        assert output.find('Manipulating of cluster')


    # test command1 with arguments
    argv = ['cluster', '--debug']
    with MixbytesTankTest(argv=argv) as app:
        app.run()
        data,output = app.last_rendered
#        assert data['foo'] == 'not-bar'
        assert output.find('Foo => not-bar')
