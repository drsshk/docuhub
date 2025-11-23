from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.projects.models import Project, Document, ProjectGroup, ProjectHistory, ApprovalHistory
from apps.projects.services import ProjectVersionService, ProjectSubmissionService
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


class ProjectVersionServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='password123'
        )
        self.project_group = uuid.uuid4()
        self.original_project = Project.objects.create(
            project_group_id=self.project_group,
            project_name='Release 1',
            project_description='Baseline release',
            version=1,
            submitted_by=self.user,
            status='Approved_Endorsed',
            project_priority='High'
        )
        # Seed history + drawings that mimic a real approved project.
        ProjectHistory.objects.create(
            project=self.original_project,
            version=1,
            submitted_by=self.user,
            date_submitted=timezone.now(),
            submission_link='/projects/1/',
            drawing_qty=2,
            drawing_numbers='D001, D002',
            receipt_id='rcpt-123',
            approval_status='Approved_Endorsed'
        )
        Drawing.objects.create(
            project=self.original_project,
            drawing_no='D001',
            drawing_title='Draft Layout',
            drawing_description='In-progress layout',
            scale_ratio='1:10',
            sheet_size='A1',
            revision_number=0,
            added_by=self.user,
            status='Draft',
            sort_order=1
        )
        Drawing.objects.create(
            project=self.original_project,
            drawing_no='D002',
            drawing_title='Approved Detail',
            drawing_description='Final detail sheet',
            scale_ratio='1:5',
            sheet_size='A2',
            revision_number=2,
            added_by=self.user,
            status='Approved_Endorsed',
            sort_order=2
        )

    def test_clone_preserves_original_release_state(self):
        new_project = ProjectVersionService.create_new_version(self.original_project, self.user)

        self.original_project.refresh_from_db()
        history = ProjectHistory.objects.get(project=self.original_project, version=1)

        self.assertEqual(self.original_project.status, 'Approved_Endorsed')
        self.assertEqual(history.approval_status, 'Approved_Endorsed')
        self.assertEqual(new_project.status, 'Draft')
        self.assertEqual(new_project.version, 2)

    def test_clone_copies_all_drawings_as_draft_and_updates_count(self):
        new_project = ProjectVersionService.create_new_version(self.original_project, self.user)
        new_project.refresh_from_db()

        drawings = list(new_project.drawings.order_by('drawing_no'))
        self.assertEqual(len(drawings), 2)
        self.assertTrue(all(d.status == 'Draft' for d in drawings))
        # Each drawing should move forward one revision number.
        original_revisions = {d.drawing_no: d.revision_number for d in Drawing.objects.filter(project=self.original_project)}
        for drawing in drawings:
            self.assertEqual(drawing.revision_number, original_revisions[drawing.drawing_no] + 1)
        self.assertEqual(new_project.no_of_drawings, 2)

    def test_clone_does_not_generate_placeholder_history(self):
        new_project = ProjectVersionService.create_new_version(self.original_project, self.user)
        self.assertFalse(ProjectHistory.objects.filter(project=new_project).exists())


class ProjectSubmissionServiceTests(TestCase):
    def setUp(self):
        self.submitter = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='password123'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            is_staff=True,
            is_superuser=True
        )
        self.group = uuid.uuid4()

        self.previous_project = Project.objects.create(
            project_group_id=self.group,
            project_name='Release 1',
            project_description='Original release',
            version=1,
            submitted_by=self.submitter,
            status='Approved_Endorsed',
            project_priority='Normal'
        )

        ProjectHistory.objects.create(
            project=self.previous_project,
            version=1,
            submitted_by=self.submitter,
            date_submitted=timezone.now(),
            submission_link='/projects/1/',
            drawing_qty=1,
            drawing_numbers='D100',
            receipt_id='rcpt-001',
            approval_status='Approved_Endorsed'
        )

        self.pending_project = Project.objects.create(
            project_group_id=self.group,
            project_name='Release 2',
            project_description='Next release',
            version=2,
            submitted_by=self.submitter,
            status='Pending_Approval',
            project_priority='High'
        )

        ProjectHistory.objects.create(
            project=self.pending_project,
            version=2,
            submitted_by=self.submitter,
            date_submitted=timezone.now(),
            submission_link='/projects/2/',
            drawing_qty=1,
            drawing_numbers='D200',
            receipt_id='rcpt-002',
            approval_status='Pending_Approval'
        )

        self.service = ProjectSubmissionService()

    def test_approve_project_obsoletes_previous_version(self):
        self.assertTrue(self.service.approve_project(self.pending_project, self.admin))

        self.previous_project.refresh_from_db()
        self.pending_project.refresh_from_db()

        self.assertEqual(self.pending_project.status, 'Approved_Endorsed')
        self.assertEqual(self.previous_project.status, 'Obsolete')

        previous_history = ProjectHistory.objects.get(project=self.previous_project, version=1)
        self.assertEqual(previous_history.approval_status, 'Obsolete')

        self.assertTrue(
            ApprovalHistory.objects.filter(
                project=self.previous_project,
                action='Obsoleted'
            ).exists()
        )

    def test_approve_project_when_no_previous_version(self):
        other_group = uuid.uuid4()
        lone_project = Project.objects.create(
            project_group_id=other_group,
            project_name='Solo Release',
            project_description='First release only',
            version=1,
            submitted_by=self.submitter,
            status='Pending_Approval',
            project_priority='Normal'
        )
        ProjectHistory.objects.create(
            project=lone_project,
            version=1,
            submitted_by=self.submitter,
            date_submitted=timezone.now(),
            submission_link='/projects/solo/',
            drawing_qty=1,
            drawing_numbers='S100',
            receipt_id='rcpt-003',
            approval_status='Pending_Approval'
        )

        self.assertTrue(self.service.approve_project(lone_project, self.admin))
        lone_project.refresh_from_db()
        self.assertEqual(lone_project.status, 'Approved_Endorsed')
        self.assertFalse(
            ApprovalHistory.objects.filter(project=lone_project, action='Obsoleted').exists()
        )
