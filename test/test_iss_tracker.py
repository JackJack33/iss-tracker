#!/usr/bin/env python3

import pytest
import math
from iss_tracker import fetch_data, format_data, calculate_data_range, find_closest_epoch, calculate_average_speed, calculate_instantaneous_speed
from iss_tracker import format_header, format_metadata, format_comment, cartesian_to_geo

import requests
from flask import Flask, request
from iss_tracker import get_epochs, get_epoch, get_epoch_speed, get_now
from iss_tracker import get_header, get_comment, get_metadata, get_epoch_location
from iss_tracker import app


test_data_dict = {
    'ndm': {
        'oem': {
            'header': {
                'TEST1': 'TEST1 VALUE',
                'TEST2': 'TEST2 VALUE'
            },
            'body': {
                'segment': {
                    'metadata': {
                        'TEST1': 'TEST1 VALUE',
                        'TEST2': 'TEST2 VALUE'
                    },
                    'data': {
                        'COMMENT': [
                        'COMMENT LINE 1',
                        'COMMENT LINE 2'
                        ],
                        'stateVector': [
                            {
                                'EPOCH': '1000-001T00:00:00.000Z',
                                'X': {'#text': '1'},
                                'Y': {'#text': '-2'},
                                'Z': {'#text': '3'},
                                'X_DOT': {'#text': '4'},
                                'Y_DOT': {'#text': '-5'},
                                'Z_DOT': {'#text': '6'}
                            },
                            {
                                'EPOCH': '1000-002T00:00:00.000Z',
                                'X': {'#text': '-7'},
                                'Y': {'#text': '8'},
                                'Z': {'#text': '-9'},
                                'X_DOT': {'#text': '10'},
                                'Y_DOT': {'#text': '-11'},
                                'Z_DOT': {'#text': '12'}
                            },
                            {
                                'EPOCH': '1000-003T00:00:00.000Z',
                                'X': {'#text': '13'},
                                'Y': {'#text': '-14'},
                                'Z': {'#text': '15'},
                                'X_DOT': {'#text': '16'},
                                'Y_DOT': {'#text': '-17'},
                                'Z_DOT': {'#text': '18'}
                            },
                            {
                                'EPOCH': '1000-004T00:00:00.000Z',
                                'X': {'#text': '-19'},
                                'Y': {'#text': '20'},
                                'Z': {'#text': '-21'},
                                'X_DOT': {'#text': '22'},
                                'Y_DOT': {'#text': '-23'},
                                'Z_DOT': {'#text': '24'}
                            }
                        ]
                    }
                }
            }
        }
    }
}

test_formatted_data = [
    {
        'timestamp': '1000-01-01 00:00:00.000000',
        'x': 1.0,
        'y': -2.0,
        'z': 3.0,
        'dx': 4.0,
        'dy': -5.0,
        'dz': 6.0
    },
    {
        'timestamp': '1000-01-02 00:00:00.000000',
        'x': -7.0,
        'y': 8.0,
        'z': -9.0,
        'dx': 10.0,
        'dy': -11.0,
        'dz': 12.0
    },
    {
        'timestamp': '1000-01-03 00:00:00.000000',
        'x': 13.0,
        'y': -14.0,
        'z': 15.0,
        'dx': 16.0,
        'dy': -17.0,
        'dz': 18.0
    },
    {
        'timestamp': '1000-01-04 00:00:00.000000',
        'x': -19.0,
        'y': 20.0,
        'z': -21.0,
        'dx': 22.0,
        'dy': -23.0,
        'dz': 24.0
    }
    ]

# Part 1

def test_fetch_data():
    data_dict = fetch_data()
    assert isinstance(data_dict, dict)
    assert len(data_dict) > 0

def test_format_data():
    formatted_data = format_data(test_data_dict)
    assert isinstance(formatted_data, list)
    assert all(isinstance(item, dict) for item in formatted_data)
    assert formatted_data == test_formatted_data

def test_calculate_data_range():
    formatted_data = format_data(test_data_dict)
    first_epoch, last_epoch = calculate_data_range(formatted_data)
    assert isinstance(first_epoch, str)
    assert isinstance(last_epoch, str)
    assert first_epoch == '1000-01-01 00:00:00.000000'
    assert last_epoch == '1000-01-04 00:00:00.000000'

def test_find_closest_epoch():
    formatted_data = format_data(test_data_dict)
    closest_epoch = find_closest_epoch(formatted_data)
    assert isinstance(closest_epoch, dict)
    assert closest_epoch['timestamp'] == '1000-01-04 00:00:00.000000'

def test_calculate_average_speed():
    formatted_data = format_data(test_data_dict)
    average_speed = calculate_average_speed(formatted_data)
    assert isinstance(average_speed, float)
    assert math.isclose(average_speed, 24.31, rel_tol=1)

def test_calculate_instantaneous_speed():
    formatted_data = format_data(test_data_dict)
    closest_epoch = find_closest_epoch(formatted_data)
    instantaneous_speed = calculate_instantaneous_speed(closest_epoch)
    assert isinstance(instantaneous_speed, float)
    assert math.isclose(instantaneous_speed, 39.86, rel_tol=1)

def test_get_epochs():
    response0 = requests.get('http://localhost:5000/epochs?limit=5&offset=2')
    assert response0.status_code == 200
    response1 = requests.get('http://localhost:5000/epochs?limit=5')
    assert response1.status_code == 200
    assert len(response0.json()) == 5
    assert len(response1.json()) == 5

    assert response0.json()[4-2]['timestamp'] == response1.json()[4]['timestamp']

def test_get_epoch():
    response0 = requests.get('http://localhost:5000/epochs?limit=1')
    assert response0.status_code == 200
    timestamp = response0.json()[0]['timestamp'].replace(" ", "__").replace(":", "_")

    response1 = requests.get(f'http://localhost:5000/epochs/{timestamp}')
    assert response1.status_code == 200
    assert response0.json()[0]['timestamp'] == response1.json()['timestamp']

def test_get_epoch_speed():
    response0 = requests.get('http://localhost:5000/epochs?limit=1')
    assert response0.status_code == 200
    timestamp = response0.json()[0]['timestamp'].replace(" ", "__").replace(":", "_")

    response1 = requests.get(f'http://localhost:5000/epochs/{timestamp}/speed')
    assert response1.status_code == 200
    assert calculate_instantaneous_speed(response0.json()[0]) == response1.json()['speed']

def test_get_now():
    response0 = requests.get('http://localhost:5000/epochs')
    assert response0.status_code == 200

    response1 = requests.get('http://localhost:5000/now')
    assert response1.status_code == 200
    assert response1.json()['closest_epoch']['timestamp'] == find_closest_epoch(response0.json())['timestamp']


# Part 2


def test_format_header():
    header = format_header(test_data_dict)
    expected_header = {
        'TEST1': 'TEST1 VALUE',
        'TEST2': 'TEST2 VALUE'
    }
    assert header == expected_header

def test_format_metadata():
    metadata = format_metadata(test_data_dict)
    expected_metadata = {
        'TEST1': 'TEST1 VALUE',
        'TEST2': 'TEST2 VALUE'
    }
    assert metadata == expected_metadata

def test_format_comment():
    comment = format_comment(test_data_dict)
    expected_comment = [
        'COMMENT LINE 1',
        'COMMENT LINE 2'
    ]
    assert comment == expected_comment

def test_cartesian_to_geo():
    epoch = {
        'timestamp': '2024-03-17 12:00:00.000000',
        'x': 5000,
        'y': 2000,
        'z': 3000
    }

    geo = cartesian_to_geo(epoch)

    assert isinstance(geo[0]['lat'], float)
    assert isinstance(geo[0]['lon'], float)
    assert isinstance(geo[0]['alt'], float)
    assert isinstance(geo[0]['geoloc'], str)

def test_get_header():
    response0 = requests.get('http://localhost:5000/header')
    assert response0.status_code == 200
    assert len(response0.json()) > 0

def test_get_metadata():
    response0 = requests.get('http://localhost:5000/metadata')
    assert response0.status_code == 200
    assert len(response0.json()) > 0

def test_get_header():
    response0 = requests.get('http://localhost:5000/comment')
    assert response0.status_code == 200
    assert len(response0.json()) > 0


def test_get_epoch_location():
    response0 = requests.get('http://localhost:5000/now')
    assert response0.status_code == 200
    timestamp = response0.json()['closest_epoch']['timestamp'].replace(" ", "__").replace(":", "_")
    response1 = requests.get(f'http://localhost:5000/epochs/{timestamp}/location')
    assert response1.status_code == 200
    assert float(response1.json()[0]['alt']) > 0
    assert (float(response1.json()[0]['lat']) >= -90 and float(response1.json()[0]['lat']) <= 90)
    assert (float(response1.json()[0]['lon']) >= -180 and float(response1.json()[0]['lon']) <= 180)
