from rest_framework import viewsets, permissions, serializers
from paysphere_app.models.leave_models import LeaveRequest
from paysphere_app.serializers.leave_serializers import LeaveRequestSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.utils import timezone

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all().order_by('-applied_on')  
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.group == "HR":
            return LeaveRequest.objects.filter(status = "PENDING").order_by('-applied_on')
        return LeaveRequest.objects.filter(employee=user)

    def perform_create(self, serializer):
        employee = self.request.user

        if LeaveRequest.objects.filter(employee=employee, status="PENDING").exists():
            raise serializers.ValidationError({"error": "You have a pending leave request. Please wait for approval before submitting a new one."})
            
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        
        leave_days = (end_date - start_date).days + 1

        if employee.remaining_leaves < leave_days:
            raise serializers.ValidationError({"error": "You do not have enough leave balance."})

        serializer.save(employee=employee)
        return Response({"message": "Leave request created successfully!"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='status')
    def approve_leave(self, request, pk=None):
        user = request.user

        try:
            leave_request = self.get_queryset().get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "You are not authorized to update this leave request."}, status=status.HTTP_403_FORBIDDEN)

        if leave_request.employee == user:
            return Response({"error": "You cannot approve your own leave requests."}, status=status.HTTP_400_BAD_REQUEST)

        if user.group != "HR":
            return Response({"error": "Only HR can approve or reject leave requests."}, status=status.HTTP_403_FORBIDDEN)

        status_value = request.data.get("status")
        if status_value not in ["APPROVED", "REJECTED"]:
            return Response({"error": "Invalid status. Use 'APPROVED' or 'REJECTED'."}, status=status.HTTP_400_BAD_REQUEST)

        if status_value == "APPROVED":
            employee = leave_request.employee
            leave_days = (leave_request.end_date - leave_request.start_date).days + 1

            employee.leaves_taken += leave_days
            employee.remaining_leaves -= leave_days
            employee.save()

        leave_request.status = status_value
        leave_request.reviewed_by = user
        leave_request.reviewed_on = timezone.now()
        leave_request.save()

        return Response({"message": f"Leave request {status_value.lower()} successfully!"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='history')
    def leave_history(self, request):
        user = request.user
        
        if user.group == "HR":
            past_leaves = LeaveRequest.objects.filter(status="APPROVED").order_by('-applied_on')
        else:
            past_leaves = LeaveRequest.objects.filter(employee=user, status="APPROVED").order_by('-applied_on')

        serializer = LeaveRequestSerializer(past_leaves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='all-requests')
    def all_leave_requests(self, request):
        user = request.user

        if user.group != "HR":
            return Response({"error": "Only HR can view all leave requests."}, status=status.HTTP_403_FORBIDDEN)

        all_leaves = LeaveRequest.objects.all().order_by('-applied_on')
        serializer = LeaveRequestSerializer(all_leaves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)