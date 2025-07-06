from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView as BaseTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from analytics.models import DataSet, Analysis, Insight
from dashboards.models import Dashboard
from analytics.tasks import run_analysis
from .serializers import (
    DataSetSerializer, AnalysisSerializer, InsightSerializer,
    DashboardSerializer, FileUploadSerializer, QuickAnalysisSerializer
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners to edit objects.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for owner
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'uploaded_by'):
            return obj.uploaded_by == request.user
        
        return False


class DataSetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing datasets
    """
    queryset = DataSet.objects.all()
    serializer_class = DataSetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return DataSet.objects.filter(uploaded_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        Get dataset preview data
        """
        dataset = self.get_object()
        # Implement preview logic
        return Response({'message': 'Preview data would be here'})
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """
        Start analysis on dataset
        """
        dataset = self.get_object()
        serializer = QuickAnalysisSerializer(data=request.data)
        if serializer.is_valid():
            analysis = Analysis.objects.create(
                dataset=dataset,
                name=f"API Analysis - {dataset.name}",
                analysis_type=serializer.validated_data['analysis_type'],
                selected_columns=serializer.validated_data.get('selected_columns', []),
                configuration=serializer.validated_data.get('configuration', {}),
                created_by=request.user
            )
            
            # Start analysis task
            run_analysis.delay(analysis.id)
            
            return Response({
                'analysis_id': analysis.id,
                'status': 'queued',
                'message': 'Analysis started successfully'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing analyses
    """
    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Analysis.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        Get analysis status
        """
        analysis = self.get_object()
        return Response({
            'id': analysis.id,
            'status': analysis.status,
            'execution_time': analysis.execution_time,
            'error_message': analysis.error_message
        })
    
    @action(detail=True, methods=['post'])
    def rerun(self, request, pk=None):
        """
        Rerun analysis
        """
        analysis = self.get_object()
        analysis.status = 'queued'
        analysis.save()
        
        # Start analysis task
        run_analysis.delay(analysis.id)
        
        return Response({
            'message': 'Analysis restarted successfully',
            'status': 'queued'
        })


class InsightViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing insights
    """
    queryset = Insight.objects.all()
    serializer_class = InsightSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Insight.objects.filter(
            analysis__created_by=self.request.user,
            is_hidden=False
        ).order_by('-importance_score')
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Verify insight
        """
        insight = self.get_object()
        insight.is_verified = True
        insight.save()
        return Response({'message': 'Insight verified successfully'})
    
    @action(detail=True, methods=['post'])
    def hide(self, request, pk=None):
        """
        Hide insight
        """
        insight = self.get_object()
        insight.is_hidden = True
        insight.save()
        return Response({'message': 'Insight hidden successfully'})


class DashboardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing dashboards
    """
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Dashboard.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """
        Export dashboard configuration
        """
        dashboard = self.get_object()
        serializer = self.get_serializer(dashboard)
        return Response(serializer.data)


class TokenObtainPairView(BaseTokenObtainPairView):
    """
    Custom token obtain pair view
    """
    pass


class TokenRefreshView(BaseTokenRefreshView):
    """
    Custom token refresh view
    """
    pass


class FileUploadView(APIView):
    """
    API view for file uploads
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            dataset = DataSet.objects.create(
                name=serializer.validated_data['name'],
                description=serializer.validated_data.get('description', ''),
                file=serializer.validated_data['file'],
                file_size=serializer.validated_data['file'].size,
                file_type=serializer.validated_data['file'].name.split('.')[-1].lower(),
                uploaded_by=request.user,
                tags=serializer.validated_data.get('tags', [])
            )
            
            return Response({
                'id': dataset.id,
                'message': 'File uploaded successfully',
                'status': 'processing'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuickAnalysisView(APIView):
    """
    API view for quick analysis
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        serializer = QuickAnalysisSerializer(data=request.data)
        if serializer.is_valid():
            dataset = get_object_or_404(
                DataSet, 
                id=serializer.validated_data['dataset_id'],
                uploaded_by=request.user
            )
            
            analysis = Analysis.objects.create(
                dataset=dataset,
                name=f"Quick Analysis - {dataset.name}",
                analysis_type=serializer.validated_data['analysis_type'],
                selected_columns=serializer.validated_data.get('selected_columns', []),
                configuration=serializer.validated_data.get('configuration', {}),
                created_by=request.user
            )
            
            # Start analysis task
            run_analysis.delay(analysis.id)
            
            return Response({
                'analysis_id': analysis.id,
                'status': 'queued',
                'message': 'Analysis started successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExportAnalysisView(APIView):
    """
    API view for exporting analysis results
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, analysis_id, format=None):
        analysis = get_object_or_404(
            Analysis,
            id=analysis_id,
            created_by=request.user
        )
        
        export_format = request.query_params.get('format', 'json')
        
        if export_format == 'json':
            serializer = AnalysisSerializer(analysis)
            return Response(serializer.data)
        
        elif export_format == 'csv':
            # Implement CSV export
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="analysis_{analysis.id}.csv"'
            # Add CSV export logic here
            return response
        
        elif export_format == 'pdf':
            # Implement PDF export
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="analysis_{analysis.id}.pdf"'
            # Add PDF export logic here
            return response
        
        return Response(
            {'error': 'Unsupported export format'},
            status=status.HTTP_400_BAD_REQUEST
        )


# API endpoints for template functionality

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def duplicate_dashboard(request, dashboard_id):
    """Duplicate a dashboard"""
    try:
        dashboard = get_object_or_404(Dashboard, id=dashboard_id, tenant=request.tenant)
        # Create a copy with new name
        new_dashboard = Dashboard.objects.create(
            tenant=dashboard.tenant,
            name=f"{dashboard.name} (Copy)",
            description=dashboard.description,
            layout=dashboard.layout,
            category=dashboard.category,
            is_public=False,
            created_by=request.user
        )
        # Copy widgets
        for widget in dashboard.widgets.all():
            widget.pk = None
            widget.dashboard = new_dashboard
            widget.save()
        
        return Response({
            'success': True,
            'dashboard_id': new_dashboard.id,
            'message': 'Dashboard duplicated successfully'
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def revoke_share(request, share_id):
    """Revoke a report share"""
    try:
        from reports.models import ReportShare
        share = get_object_or_404(ReportShare, id=share_id, report__tenant=request.tenant)
        share.delete()
        return Response({
            'success': True,
            'message': 'Share revoked successfully'
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def export_user_data(request):
    """Export user data"""
    try:
        import json
        from django.http import JsonResponse
        
        # Collect user data
        user_data = {
            'profile': {
                'name': request.user.get_full_name(),
                'email': request.user.email,
                'date_joined': request.user.date_joined.isoformat(),
            },
            'reports': list(request.user.created_reports.values('title', 'created_at')),
            'dashboards': list(request.user.created_dashboards.values('name', 'created_at')),
        }
        
        response = JsonResponse(user_data)
        response['Content-Disposition'] = 'attachment; filename="user_data.json"'
        return response
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_status(request, export_id):
    """Check export status"""
    try:
        from reports.models import ReportExport
        export = get_object_or_404(ReportExport, id=export_id, report__tenant=request.tenant)
        return Response({
            'progress': export.progress,
            'status': export.get_status_display(),
            'completed': export.status == 'completed',
            'download_url': export.file_url if export.status == 'completed' else None
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
