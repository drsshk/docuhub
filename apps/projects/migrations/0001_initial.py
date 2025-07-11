# Generated by Django 4.2.7 on 2025-06-24 05:59

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("project_name", models.CharField(max_length=255)),
                ("project_description", models.TextField(blank=True)),
                ("version", models.IntegerField()),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_submitted", models.DateTimeField(blank=True, null=True)),
                ("date_reviewed", models.DateTimeField(blank=True, null=True)),
                ("no_of_drawings", models.IntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Draft", "Draft"),
                            ("Pending_Approval", "Pending Approval"),
                            ("Approved", "Approved"),
                            ("Rejected", "Rejected"),
                            ("Revise_and_Resubmit", "Revise and Resubmit"),
                            ("Obsolete", "Obsolete"),
                        ],
                        default="Draft",
                        max_length=30,
                    ),
                ),
                ("review_comments", models.TextField(blank=True)),
                ("revision_notes", models.TextField(blank=True)),
                ("client_department", models.CharField(blank=True, max_length=100)),
                (
                    "project_priority",
                    models.CharField(
                        choices=[
                            ("Low", "Low"),
                            ("Normal", "Normal"),
                            ("High", "High"),
                            ("Urgent", "Urgent"),
                        ],
                        default="Normal",
                        max_length=20,
                    ),
                ),
                ("deadline_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reviewed_projects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submitted_projects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "projects",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Drawing",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "drawing_no",
                    models.CharField(
                        max_length=20,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Drawing number must be exactly 4 alphanumeric characters (e.g., A001, M001)",
                                regex="^[A-Za-z0-9]{4}$",
                            )
                        ],
                    ),
                ),
                ("drawing_title", models.CharField(blank=True, max_length=255)),
                ("drawing_description", models.TextField(blank=True)),
                ("drawing_list_link", models.URLField(blank=True, max_length=500)),
                ("drawing_type", models.CharField(blank=True, max_length=50)),
                (
                    "discipline",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Architectural", "Architectural"),
                            ("Structural", "Structural"),
                            ("Mechanical", "Mechanical"),
                            ("Electrical", "Electrical"),
                            ("Plumbing", "Plumbing"),
                            ("Civil", "Civil"),
                            ("Other", "Other"),
                        ],
                        max_length=50,
                    ),
                ),
                ("scale_ratio", models.CharField(blank=True, max_length=20)),
                ("sheet_size", models.CharField(blank=True, max_length=10)),
                ("revision_number", models.IntegerField(default=0)),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Active", "Active"),
                            ("Inactive", "Inactive"),
                            ("Replaced", "Replaced"),
                            ("Obsolete", "Obsolete"),
                        ],
                        default="Active",
                        max_length=20,
                    ),
                ),
                ("sort_order", models.IntegerField(default=0)),
                (
                    "added_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="drawings",
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "db_table": "drawings",
                "ordering": ["sort_order", "drawing_no"],
            },
        ),
        migrations.CreateModel(
            name="ApprovalHistory",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("version", models.IntegerField()),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("Created", "Created"),
                            ("Submitted", "Submitted"),
                            ("Approved", "Approved"),
                            ("Rejected", "Rejected"),
                            ("Resubmitted", "Resubmitted"),
                            ("Status_Changed", "Status Changed"),
                            ("Obsoleted", "Obsoleted"),
                        ],
                        max_length=50,
                    ),
                ),
                ("performed_at", models.DateTimeField(auto_now_add=True)),
                ("comments", models.TextField(blank=True)),
                ("previous_status", models.CharField(blank=True, max_length=30)),
                ("new_status", models.CharField(blank=True, max_length=30)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                (
                    "performed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approval_history",
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "db_table": "approval_history",
                "ordering": ["-performed_at"],
            },
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(
                fields=["submitted_by"], name="projects_submitt_55b9bb_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["status"], name="projects_status_6303d7_idx"),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(
                fields=["date_submitted"], name="projects_date_su_104f56_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="drawing",
            index=models.Index(fields=["project"], name="drawings_project_957782_idx"),
        ),
        migrations.AddIndex(
            model_name="drawing",
            index=models.Index(fields=["added_by"], name="drawings_added_b_7a0238_idx"),
        ),
        migrations.AddIndex(
            model_name="drawing",
            index=models.Index(fields=["status"], name="drawings_status_53dbc8_idx"),
        ),
        migrations.AlterUniqueTogether(
            name="drawing",
            unique_together={("project", "drawing_no")},
        ),
        migrations.AddIndex(
            model_name="approvalhistory",
            index=models.Index(
                fields=["project"], name="approval_hi_project_e4cf47_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="approvalhistory",
            index=models.Index(
                fields=["performed_by"], name="approval_hi_perform_cac482_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="approvalhistory",
            index=models.Index(
                fields=["performed_at"], name="approval_hi_perform_98f597_idx"
            ),
        ),
    ]
