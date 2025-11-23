from rest_framework import serializers
from .models import Project, Document, ProjectGroup, ApprovalHistory, ProjectHistory

class ProjectGroupSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    latest_project = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectGroup
        fields = [
            'id', 'code', 'name', 'client_name',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'latest_project'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'created_by_name', 'latest_project']
    
    def get_latest_project(self, obj):
        latest = obj.get_latest_project()
        if latest:
            return {
                'id': latest.id,
                'version_number': latest.version_number,
                'version_display': latest.version_display,
                'created_at': latest.created_at
            }
        return None

class DocumentSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'project', 'project_name', 'document_number', 'title', 'description', 
            'discipline', 'revision', 'file_path', 'status',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
            'updated_by', 'updated_by_name'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 'created_by_name', 
            'updated_by', 'updated_by_name', 'project_name'
        ]

class ApprovalHistorySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    document_number = serializers.CharField(source='document.document_number', read_only=True)
    
    class Meta:
        model = ApprovalHistory
        fields = [
            'id', 'project', 'project_name', 'document', 'document_number',
            'action', 'from_status', 'to_status', 
            'performed_by', 'performed_by_name', 'performed_at',
            'comment', 'ip_address', 'user_agent'
        ]
        read_only_fields = [
            'id', 'performed_at', 'performed_by', 'performed_by_name',
            'project_name', 'document_number'
        ]

class ProjectHistorySerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    
    class Meta:
        model = ProjectHistory
        fields = [
            'id', 'project', 'project_name', 'version', 'date_submitted',
            'submission_link', 'drawing_qty', 'drawing_numbers', 'receipt_id',
            'approval_status', 'submitted_by', 'submitted_by_name'
        ]
        read_only_fields = [
            'id', 'date_submitted', 'submitted_by', 'submitted_by_name',
            'project_name', 'receipt_id'
        ]

class ProjectSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    version_display = serializers.CharField(read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    approval_history = ApprovalHistorySerializer(many=True, read_only=True)
    history_logs = ProjectHistorySerializer(many=True, read_only=True)
    project_group_name = serializers.CharField(source='project_group.name', read_only=True)
    project_group_code = serializers.CharField(source='project_group.code', read_only=True)
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'project_group', 'project_group_name', 'project_group_code',
            'project_name', 'client_name', 'project_description', 
            'version_number', 'version_display', 'is_latest',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'reference_no', 'notes', 'project_priority', 'deadline_date', 
            'project_folder_link', 'documents', 'approval_history', 'history_logs', 'document_count'
        ]
        read_only_fields = [
            'id', 'version_display', 'created_by', 'created_by_name', 'created_at', 'updated_at',
            'documents', 'approval_history', 'history_logs', 'project_group_name', 'project_group_code',
            'document_count'
        ]
    
    def get_document_count(self, obj):
        return obj.documents.count()