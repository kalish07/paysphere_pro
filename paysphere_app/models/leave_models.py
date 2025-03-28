from django.db import models
from django.conf import settings

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    LEAVE_TYPES = [
        ('SICK', 'Sick Leave'),
        ('CASUAL', 'Casual Leave'),
        ('ANNUAL', 'Annual Leave'),
        ('OTHER', 'Other'),
    ]

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    applied_on = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_leaves")
    reviewed_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.email} - {self.leave_type} ({self.status})"