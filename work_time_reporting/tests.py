from django.test import TestCase
from django.urls import reverse

from work_time_reporting.models import WorkTime
from datetime import datetime


class WorkTimeTest(TestCase):
    def test_add_work_time(self):
        entry = {
            'date': '2023-12-31',
            'hours': 8,
        }

        url = reverse('add_work_time')
        response = self.client.post(url, entry)

        self.assertTrue(response.status_code == 200)
        self.assertEqual(WorkTime.objects.count(), 1)
        self.assertContains(response, f"Entry added: ({entry['date']}: {entry['hours']})")

        new_entry = WorkTime.objects.first()
        self.assertEqual(new_entry.date, datetime.strptime(entry['date'], '%Y-%m-%d').date())
        self.assertEqual(new_entry.hours, entry['hours'])

    def test_generate_summary_no_date_range(self):
        entry1 = {'date': '2023-12-31', 'hours': 8}
        entry2 = {'date': '2023-12-28', 'hours': 4.5}

        WorkTime(date=datetime.strptime(entry1['date'], '%Y-%m-%d').date(), hours=entry1['hours']).save()
        WorkTime(date=datetime.strptime(entry2['date'], '%Y-%m-%d').date(), hours=entry2['hours']).save()

        self.assertEqual(WorkTime.objects.count(), 2)

        url = reverse('generate_summary')
        response = self.client.get(url)

        self.assertTrue(response.status_code == 200)
        self.assertEquals(response.context['date_range'], "None")
        self.assertEquals(response.context['total_hours'], 12.5)
        self.assertEquals(response.context['entries'][0].date.strftime("%Y-%m-%d"), "2023-12-28")
        self.assertEquals(response.context['entries'][1].date.strftime("%Y-%m-%d"), "2023-12-31")
        

    def test_generate_summary_only_start_date(self):
        entry1 = {'date': '2023-12-31', 'hours': 8}
        entry2 = {'date': '2023-12-28', 'hours': 4.5}

        WorkTime(date=datetime.strptime(entry1['date'], '%Y-%m-%d').date(), hours=entry1['hours']).save()
        WorkTime(date=datetime.strptime(entry2['date'], '%Y-%m-%d').date(), hours=entry2['hours']).save()

        self.assertEqual(WorkTime.objects.count(), 2)

        url = reverse('generate_summary')
        response = self.client.get(url, {'start_date': '2023-12-29'})

        self.assertTrue(response.status_code == 200)
        self.assertEquals(response.context['date_range'], "after 2023-12-29")
        self.assertEquals(response.context['total_hours'], 8)
        self.assertTrue(len(response.context['entries']), 1)
        self.assertEquals(response.context['entries'][0].date.strftime("%Y-%m-%d"), "2023-12-31")

    def test_generate_summary_only_end_date(self):
        entry1 = {'date': '2023-12-31', 'hours': 8}
        entry2 = {'date': '2023-12-28', 'hours': 4.5}

        WorkTime(date=datetime.strptime(entry1['date'], '%Y-%m-%d').date(), hours=entry1['hours']).save()
        WorkTime(date=datetime.strptime(entry2['date'], '%Y-%m-%d').date(), hours=entry2['hours']).save()

        self.assertEqual(WorkTime.objects.count(), 2)

        url = reverse('generate_summary')
        response = self.client.get(url, {'end_date': '2023-12-29'})

        self.assertTrue(response.status_code == 200)
        self.assertEquals(response.context['date_range'], "before 2023-12-29")
        self.assertEquals(response.context['total_hours'], 4.5)
        self.assertTrue(len(response.context['entries']), 1)
        self.assertEquals(response.context['entries'][0].date.strftime("%Y-%m-%d"), "2023-12-28")

    def test_generate_summary_within_range(self):
        entry1 = {'date': '2023-12-31', 'hours': 8}
        entry2 = {'date': '2023-12-28', 'hours': 4.5}
        entry3 = {'date': '2024-01-01', 'hours': 7}

        WorkTime(date=datetime.strptime(entry1['date'], '%Y-%m-%d').date(), hours=entry1['hours']).save()
        WorkTime(date=datetime.strptime(entry2['date'], '%Y-%m-%d').date(), hours=entry2['hours']).save()
        WorkTime(date=datetime.strptime(entry3['date'], '%Y-%m-%d').date(), hours=entry3['hours']).save()

        self.assertEqual(WorkTime.objects.count(), 3)

        url = reverse('generate_summary')
        response = self.client.get(url, {'start_date': '2023-12-27', 'end_date': '2023-12-31'})

        self.assertTrue(response.status_code == 200)
        self.assertEquals(response.context['date_range'], "2023-12-27 - 2023-12-31")
        self.assertEquals(response.context['total_hours'], 12.5)
        self.assertTrue(len(response.context['entries']), 2)
        self.assertEquals(response.context['entries'][0].date.strftime("%Y-%m-%d"), "2023-12-28")
        self.assertEquals(response.context['entries'][1].date.strftime("%Y-%m-%d"), "2023-12-31")
