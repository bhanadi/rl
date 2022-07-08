import pytest
from solution import average_city_temps
from io import StringIO


@pytest.fixture
def empty_input():
    return StringIO('\n')


@pytest.fixture
def one_word_input():
    return StringIO('Boston\n\n')


@pytest.fixture
def bad_temp_input():
    return StringIO('Boston qq\n\n')


@pytest.fixture
def one_temp_report():
    return StringIO('Boston 10\n\n')


@pytest.fixture
def one_city_two_temps():
    return StringIO('Boston 10\nBoston 20\n\n')


@pytest.fixture
def two_cities_four_temps():
    return StringIO('Boston 10\nBoston 20\nNew York 15\nNew York 25\n\n')


def test_no_inputs(monkeypatch, capsys, empty_input):
    monkeypatch.setattr('sys.stdin', empty_input)
    result = average_city_temps()
    assert result == {}


def test_one_city_one_temp(monkeypatch, capsys, one_temp_report):
    monkeypatch.setattr('sys.stdin', one_temp_report)
    result = average_city_temps()
    assert result == {'Boston': 10}


def test_one_city_two_temps(monkeypatch, capsys, one_city_two_temps):
    monkeypatch.setattr('sys.stdin', one_city_two_temps)
    result = average_city_temps()
    assert result == {'Boston': 15}


def test_two_cities_four_temps(monkeypatch, capsys, two_cities_four_temps):
    monkeypatch.setattr('sys.stdin', two_cities_four_temps)
    result = average_city_temps()
    assert result == {'Boston': 15, 'New York': 20}


def test_no_whitespace(monkeypatch, capsys, one_word_input):
    monkeypatch.setattr('sys.stdin', one_word_input)
    average_city_temps()
    captured_out, captured_err = capsys.readouterr()
    assert 'No whitespace' in captured_out


def test_bad_temp(monkeypatch, capsys, bad_temp_input):
    monkeypatch.setattr('sys.stdin', bad_temp_input)
    average_city_temps()
    captured_out, captured_err = capsys.readouterr()
    assert 'not a valid temperature' in captured_out