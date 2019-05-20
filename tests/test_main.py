
from tank.main import MixbytesTankTest

def test_tank(tmp):
    with MixbytesTankTest() as app:
        res = app.run()
        print(res)
        raise Exception

def test_cluster(tmp):
    argv = ['cluster']
    with MixbytesTankTest(argv=argv) as app:
        app.run()
