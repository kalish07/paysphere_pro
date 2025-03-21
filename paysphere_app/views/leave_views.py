from rest_framework import viewsets, permissions
from paysphere_app.models.leave_models import LeaveRequest
from paysphere_app.serializers.leave_serializers import LeaveRequestSerializer
from rest_framework.response import Response
from rest_framework import status

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all().order_by('-applied_on')  
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LeaveRequest.objects.filter(employee=self.request.user)

    def perform_create(self, serializer):
        employee = self.request.user
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        overlapping_leave = LeaveRequest.objects.filter(
            employee=employee,
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists()

        if overlapping_leave:
            return Response(
                {"error": "You already have an approved leave overlapping this period."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(employee=employee)