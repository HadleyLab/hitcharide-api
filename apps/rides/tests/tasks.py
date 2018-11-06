from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from apps.rides.factories import RideFactory, RideBookingFactory, \
    RideComplaintFactory
from apps.rides.models import RideBookingStatus, RideStatus
from apps.rides.tasks import complete_rides


class TasksTest(TestCase):
    def setUp(self):
        super(TasksTest, self).setUp()
        now = timezone.now()
        previous_datetime = now - timedelta(days=2)

        self.ride1 = RideFactory.create(date_time=previous_datetime)
        self.booking1 = RideBookingFactory.create(
            ride=self.ride1,
            status=RideBookingStatus.PAYED)
        self.booking2 = RideBookingFactory.create(ride=self.ride1)

    @mock.patch('apps.rides.tasks.ride_payout', autospec=True)
    def test_complete_rides_without_complaints(
            self, mock_ride_payout):
        complete_rides()
        self.ride1.refresh_from_db()

        self.assertEqual(mock_ride_payout.call_count, 1)
        mock_ride_payout.assert_called_with(self.ride1)
        self.assertEqual(self.ride1.status, RideStatus.COMPLETED)

    @mock.patch('apps.rides.tasks.ride_payout', autospec=True)
    def test_complete_rides_without_payed_booking_without_complaints(
            self, mock_ride_payout):
        self.booking1.status = RideBookingStatus.CANCELED
        self.booking1.save()
        complete_rides()
        self.ride1.refresh_from_db()

        self.assertEqual(mock_ride_payout.call_count, 0)
        self.assertEqual(self.ride1.status, RideStatus.OBSOLETE)

    @mock.patch('apps.rides.tasks.ride_payout', autospec=True)
    def test_complete_rides_with_complaints(
            self, mock_ride_payout):
        RideComplaintFactory.create(ride=self.ride1)
        complete_rides()
        self.ride1.refresh_from_db()

        self.assertEqual(mock_ride_payout.call_count, 0)
        self.assertEqual(self.ride1.status, RideStatus.CREATED)
