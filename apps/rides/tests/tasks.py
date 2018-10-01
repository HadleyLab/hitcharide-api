from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from apps.rides.factories import RideFactory, RideBookingFactory, \
    RideComplaintFactory
from apps.rides.models import RideBookingStatus
from apps.rides.tasks import create_payouts_for_rides


class TasksTest(TestCase):
    def setUp(self):
        super(TasksTest, self).setUp()
        now = timezone.now()
        previous_datetime = now - timedelta(days=2)

        self.ride1 = RideFactory.create(date_time=previous_datetime)
        self.ride2 = RideFactory.create(date_time=now)
        RideBookingFactory.create(
            ride=self.ride1,
            status=RideBookingStatus.PAYED)
        RideBookingFactory.create(ride=self.ride1)
        RideBookingFactory.create(
            ride=self.ride2,
            status=RideBookingStatus.PAYED)

    @mock.patch('apps.rides.tasks.ride_payout', autospec=True)
    def test_create_payouts_for_rides_without_complaints(
            self, mock_ride_payout):
        create_payouts_for_rides()
        self.ride1.refresh_from_db()

        self.assertEqual(mock_ride_payout.call_count, 1)
        mock_ride_payout.assert_called_with(self.ride1)
        self.assertTrue(self.ride1.completed)

    @mock.patch('apps.rides.tasks.ride_payout', autospec=True)
    def test_create_payouts_for_rides_with_complaints(
            self, mock_ride_payout):
        RideComplaintFactory.create(ride=self.ride1)
        create_payouts_for_rides()
        self.ride1.refresh_from_db()

        self.assertEqual(mock_ride_payout.call_count, 0)
        self.assertFalse(self.ride1.completed)
