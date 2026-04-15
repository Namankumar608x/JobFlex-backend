from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Application
from .serializers import ApplicationSerializer
from django.db.models import Count

@api_view(['GET'])
def dashboard_summary(request):
    try:
        user = request.user
        data = Application.objects.filter(U_ID=user)

        total = data.count()

        status_counts = data.values('status').annotate(count=Count('status'))

        status_dict = {
            "applied": 0,
            "accepted": 0,
            "rejected": 0
        }

        for item in status_counts:
            key = item['status'].lower()
            if key in status_dict:
                status_dict[key] = item['count']
      
        return Response({
            "total": total,
            "status": status_dict
        })

    except Exception as e:
        print("ERROR:", e)
        return Response({"error": str(e)}, status=500)

from django.db.models.functions import TruncDate
@api_view(['GET'])
def platform_stats(request):
    user_id = request.GET.get('user_id')
    user=request.user
    data = (
        Application.objects
        .filter(U_ID=user)
        .values('platform')
        .annotate(count=Count('id'))
    )

    return Response(data)
@api_view(['GET'])
def applications_timeline(request):
    user_id = request.GET.get('user_id')
    user=request.user
    data = (
        Application.objects
        .filter(U_ID=user)
        .annotate(date=TruncDate('changed_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    return Response(data) 

@api_view(['GET'])
def recent_applications(request):
    user_id = request.GET.get('user_id')
    user=request.user
    data = (
        Application.objects
        .filter(U_ID=user)
        .order_by('-changed_at')[:5]
        .values('APP_ID', 'company', 'jobrole', 'status', 'changed_at')
    )

    return Response(data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def application_list(request):
    # print("USER:", request.user)  # add this line temporarily
    # print("AUTH:", request.auth)
    if request.method == 'GET':
        apps = Application.objects.filter(U_ID=request.user).order_by('-changed_at')
        serializer = ApplicationSerializer(apps, many=True)
        return Response({'success': True, 'applications': serializer.data})

    if request.method == 'POST':
        data = request.data.copy()
        serializer = ApplicationSerializer(data=data)
        if serializer.is_valid():
            serializer.save(U_ID=request.user)
            return Response({'success': True, 'application': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def application_detail(request, app_id):

    try:
        app = Application.objects.get(APP_ID=app_id, U_ID=request.user)
    except Application.DoesNotExist:
        return Response({'success': False, 'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = ApplicationSerializer(app, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'application': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        app.delete()
        return Response({'success': True, 'message': 'Deleted'})