
from freezegun import freeze_time

from leadrouter.publisher import DebugPublisher

def setup_function(f):
    global freezer
    freezer = freeze_time('2014-01-01 08:15:20')
    freezer.start()

def teardown_function(f):
    global freezer
    freezer.stop()


def test_debug_publisher_creating(tmpdir):
    filepath = tmpdir.join('debug.txt')

    DebugPublisher(filepath=str(filepath))

    content = filepath.read().split('\n')

    assert content[0] == '-------------------Wed,  1 Jan 2014 08:15:20 -------------------'
    assert content[1] == '__init__()'


def test_debug_publisher_connect_close(tmpdir):
    filepath = tmpdir.join('debug.txt')

    p = DebugPublisher(filepath=str(filepath))
    p.connect()
    p.close()

    content = filepath.read().split('\n')

    assert content[2] == 'connect()'
    assert content[3] == 'close()'


def test_debug_publisher_lead_methods(tmpdir):
    filepath = tmpdir.join('debug.txt')

    p = DebugPublisher(filepath=str(filepath))
    p.create_lead('id-123', {'email': 'lead@gmail.com'})
    p.update_lead('id-123', 'ld-455', {'email': 'lead@gmail.com'})
    p.add_activities('id-123', 'ld-455', [{'type': 'contact_emailed'}])

    content = filepath.read().split('\n')

    assert content[2] == '''create_lead("id-123", {'email': 'lead@gmail.com'})'''
    assert content[3] == '''create_lead("id-123", "ld-455", {'email': 'lead@gmail.com'})'''
    assert content[4] == '''create_lead("id-123", "ld-455", [{'type': 'contact_emailed'}])'''
