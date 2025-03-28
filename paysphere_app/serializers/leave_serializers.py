from rest_framework import serializers
from paysphere_app.models.leave_models import LeaveRequest
from datetime import date

class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['employee_id', 'leave_type', 'start_date', 'end_date', 'reason', 'status', 'applied_on']
        read_only_fields = ['status', 'applied_on']

    def validate(self, data):
        user = self.context['request'].user  
        start_date = data['start_date']
        end_date = data['end_date']

        if start_date > end_date:
            raise serializers.ValidationError("Start date must be before end date.")

        if start_date < date.today():
            raise serializers.ValidationError("You cannot request leave for past dates.")

        existing_leave = LeaveRequest.objects.filter(
            employee=user,
            start_date=start_date,
            end_date=end_date
        ).exists()
        
        if existing_leave:
            raise serializers.ValidationError("You have already applied for leave on these dates.")

        overlapping_leave = LeaveRequest.objects.filter(
            employee=user,
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists()

        if overlapping_leave:
            raise serializers.ValidationError("You already have an approved leave overlapping this period.")


        return data

    def create(self, validated_data):
        validated_data['employee'] = self.context['request'].user  
        return super().create(validated_data)
    