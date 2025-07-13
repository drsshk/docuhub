from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.projects.models import Project
import uuid

User = get_user_model()

class ProjectCreationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.client.login(username='testuser', password='password123')
        self.create_url = reverse('projects:create')

    def test_project_creation_success(self):
        response = self.client.post(self.create_url, {
            'project_name': 'Test Project 1',
            'project_description': 'This is a test description.',
            'project_priority': 'High',
            'deadline_date': '2025-12-31',
            'drawing_set-TOTAL_FORMS': 1,
            'drawing_set-INITIAL_FORMS': 0,
            'drawing_set-MIN_NUM_FORMS': 0,
            'drawing_set-MAX_NUM_FORMS': 1000,
            'drawing_set-0-drawing_no': 'D001',
            'drawing_set-0-drawing_title': 'Test Drawing',
            'drawing_set-0-drawing_description': 'Description',
            'drawing_set-0-scale_ratio': '1:100',
            'drawing_set-0-sheet_size': 'A1',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        self.assertTrue(Project.objects.filter(project_name='Test Project 1', submitted_by=self.user).exists())
        project = Project.objects.get(project_name='Test Project 1')
        self.assertEqual(project.status, 'Draft')
        self.assertEqual(project.version, 1)
        self.assertIsNotNone(project.project_group_id)

    def test_project_creation_duplicate_name_case_insensitive(self):
        # Create a project with a name
        Project.objects.create(
            project_name='Existing Project',
            project_description='Desc',
            project_priority='Normal', # Changed to 'Normal' as 'Medium' might not be a valid choice
            version=1, # Explicitly set version
            submitted_by=self.user,
            project_group_id=uuid.uuid4()
        )

        # Try to create another project with the same name but different case
        response = self.client.post(self.create_url, {
            'project_name': 'existing project',  # Different case
            'project_description': 'This is a test description.',
            'project_priority': 'High',
            'deadline_date': '2025-12-31',
            'drawing_set-TOTAL_FORMS': 0,
            'drawing_set-INITIAL_FORMS': 0,
            'drawing_set-MIN_NUM_FORMS': 0,
            'drawing_set-MAX_NUM_FORMS': 1000,
        })
        self.assertEqual(response.status_code, 200)  # Should render form with error
        self.assertContains(response, 'You already have an active project with this name. Please choose a different name.')
        self.assertEqual(Project.objects.filter(submitted_by=self.user, project_name__iexact='existing project').count(), 1)

    def test_project_name_sanitization(self):
        malicious_name = "<script>alert('xss');</script>My Project"
        response = self.client.post(self.create_url, {
            'project_name': malicious_name,
            'project_description': 'Description',
            'project_priority': 'Low',
            'deadline_date': '2025-12-31'
        })
        self.assertEqual(response.status_code, 302)
        # After bleach.clean(), script tags are removed but content remains
        expected_name = "alert('xss');My Project"
        project = Project.objects.get(submitted_by=self.user, project_name=expected_name)
        self.assertEqual(project.project_name, expected_name) # Script tags should be stripped

    def test_project_description_sanitization(self):
        malicious_description = "Normal description with <img src=x onerror=alert('xss')> malicious content."
        response = self.client.post(self.create_url, {
            'project_name': 'Another Project',
            'project_description': malicious_description,
            'project_priority': 'Low',
            'deadline_date': '2025-12-31'
        })
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(submitted_by=self.user, project_name='Another Project')
        # After bleach.clean(), img tag is removed but text content remains with extra space
        expected_description = 'Normal description with  malicious content.'
        self.assertEqual(project.project_description, expected_description) # Image tag should be stripped
