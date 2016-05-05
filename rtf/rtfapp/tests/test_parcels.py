from django.test import TestCase
from rtfapp.models import Parcel
from django.test.client import Client

import os
import json
from os import path

class Parcel_Tests(TestCase):
    """ Test cases for creating Parcels """
    fixtures = ["test_parcel.json"]

    def test_pid(self):
        """ Test using a fixture for parcel data """
        request = Parcel.objects.get(pk=1)
        self.assertEquals(request.pid, "0parcel0")
        
    def test_pid_invalid(self):
        request = Parcel.objects.get(pk=1)
        self.assertNotEquals(request.pid, "PARCEL")
    
    def test_owner(self):
        """ Testing Owner of parcel"""
        request = Parcel.objects.get(pk=1)
        self.assertEquals(request.owner, "John Smith")
        
    def test_owner_invalid(self):
        request = Parcel.objects.get(pk=1)
        self.assertNotEquals(request.owner, "Pocahontas")
            
    def test_parcel_type(self):
        """ Testing GIS PATH of parcel"""
        request = Parcel.objects.get(pk=1)
        self.assertEquals(request.parcel_type, "Private Property")
        
    def test_parcel_type_invalid(self):
        request = Parcel.objects.get(pk=1)
        self.assertNotEquals(request.parcel_type, "Public Property")
        
    def test_size_valid(self):
        request = Parcel.objects.get(pk=1)
        valid = True
        if request.size < 0:
            valid = False
        self.assertEquals(valid, True)
        
    def test_size_invalid(self):
        request = Parcel.objects.get(pk=2)
        valid = True
        if request.size < 0:
            valid = False
        self.assertEquals(valid, False)
        
    def test_points_string_invalid(self):
        """ Testing validity of points data"""
        request = Parcel.objects.get(pk=2)
        valid = True
        coordinates = []
        coordinates2 = []
        for t in request.points_string.split():
            coordinates.append(t);
        for t in coordinates:
            for u in t.split(','):
                try:
                    coordinates2.append(float(u))
                except ValueError:
                    pass
        for t in coordinates2:
            if t > 180 or t < -180:
                valid = False
        self.assertEquals(valid, False)
        
        
    def test_points_string_valid(self):
        """ Testing validity of points data"""
        request = Parcel.objects.get(pk=1)
        valid = True
        coordinates = []
        coordinates2 = []
        for t in request.points_string.split():
            coordinates.append(t);
        for t in coordinates:
            for u in t.split(','):
                try:
                    coordinates2.append(float(u))
                except ValueError:
                    pass
        for t in coordinates2:
            if t > 180 or t < -180:
                valid = False

        self.assertEquals(valid, True)
        
     
c = Client()        

class Parcel_View_Tests(TestCase):
    fixtures = ["test_parcel.json"]

    def test_parcels_get_no_filter(self):
        response = c.get('/parcels/')
        parcels = json.loads(response.content)
        self.assertEquals(len(parcels), 2)
        self.assertEquals(parcels[0]["owner"], "John Smith")

    def test_parcels_get_ontrail_filter(self):
        response = c.get('/parcels/?filter=onTrail')
        parcels = json.loads(response.content)        
        self.assertEquals(len(parcels), 1)

    def test_parcels_get_within_filter(self):
        response = c.get('/parcels/?filter=within&within=400')
        parcels = json.loads(response.content)        
        self.assertEquals(len(parcels), 0)
        response = c.get('/parcels/?filter=within&within=550')
        parcels = json.loads(response.content)        
        self.assertEquals(len(parcels), 1)
        response = c.get('/parcels/?filter=within&within=700')
        parcels = json.loads(response.content)        
        self.assertEquals(len(parcels), 2)

    def test_parcels_get_invalid_filter(self):
        response = c.get('/parcels/?filter=nonsense')
        parcels = json.loads(response.content)
        self.assertEquals(len(parcels), 2)
        self.assertEquals(parcels[0]["owner"], "John Smith")