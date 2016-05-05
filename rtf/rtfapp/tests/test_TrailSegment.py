from django.test import TestCase
from rtfapp.models import TrailSegment


class TrailSegmentTests(TestCase):
	""" Test cases for creating Trail Segment """
	fixtures = ["test_trail_segment.json"]

	def test_loadTrailSegmentFixures(self):
		""" Test using a fixture for a Maintenance Request by checking that data can be loaded """
		request = TrailSegment.objects.get(pk=1)
		self.assertEquals(request.description, "trail segment near UVA")
