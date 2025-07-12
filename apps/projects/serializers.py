from rest_framework import serializers
from .models import Project, Drawing, ApprovalHistory

class DrawingSerializer(serializers.ModelSerializer):
    added_by_name = serializers.CharField(source='added_by.get_full_name', read_only=True)
    
    class Meta:
        model = Drawing
        fields = [
            'id', 'drawing_no', 'drawing_title', 'drawing_description',
            'drawing_list_link', 'discipline', 'drawing_type', 'status',
            'date_added', 'added_by', 'added_by_name'
        ]
        read_only_fields = ['id', 'date_added', 'added_by', 'added_by_name']

class ApprovalHistorySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    
    class Meta:
        model = ApprovalHistory
        fields = [
            'id', 'action', 'performed_by', 'performed_by_name', 'performed_at',
            'comments', 'previous_status', 'new_status', 'version'
        ]

class ProjectSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    version_display = serializers.CharField(read_only=True)
    drawings = DrawingSerializer(many=True, read_only=True)
    approval_history = ApprovalHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'project_name', 'project_description', 'version', 'version_display',
            'submitted_by', 'submitted_by_name', 'reviewed_by', 'reviewed_by_name',
            'date_created', 'date_submitted', 'date_reviewed', 'no_of_drawings',
            'status', 'review_comments', 'revision_notes',
            'project_priority', 'deadline_date', 'drawings', 'approval_history'
        ]
        read_only_fields = [
            'id', 'version', 'version_display', 'submitted_by', 'submitted_by_name',
            'reviewed_by', 'reviewed_by_name', 'date_created', 'date_submitted',
            'date_reviewed', 'no_of_drawings', 'drawings', 'approval_history'
        ]