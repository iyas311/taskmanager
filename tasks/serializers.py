from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed = [c[0] for c in Task.STATUS_CHOICES]
        self.fields['status'] = serializers.ChoiceField(
            choices=Task.STATUS_CHOICES,
            error_messages={
                'invalid_choice': (
                    "Invalid status '{input}'. "
                    f"Allowed values: {', '.join(allowed)}."
                ),
            }
        )

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'assigned_to', 'title', 'description', 'due_date'
        ]

    def validate_worked_hours(self, value):
        """Ensure worked_hours is positive if provided."""
        if value is None:
            return value
        try:
            val = float(value)
            if val <= 0:
                raise serializers.ValidationError("Worked hours must be a positive number.")
        except (TypeError, ValueError):
            raise serializers.ValidationError("Worked hours must be a valid number.")
        return value

    def validate(self, attrs):
        # Determine final values considering partial updates
        status_val = attrs.get('status')
        if status_val is None and self.instance is not None:
            status_val = getattr(self.instance, 'status', None)

        completion_report = attrs.get('completion_report')
        if completion_report is None and self.instance is not None:
            completion_report = getattr(self.instance, 'completion_report', None)

        worked_hours = attrs.get('worked_hours')
        if worked_hours is None and self.instance is not None:
            worked_hours = getattr(self.instance, 'worked_hours', None)

        if status_val == 'completed':
            if not completion_report or (isinstance(completion_report, str) and not completion_report.strip()):
                raise serializers.ValidationError({
                    'completion_report': 'This field is required when completing a task.'
                })
            if worked_hours in (None, ''):
                raise serializers.ValidationError({
                    'worked_hours': 'This field is required when completing a task.'
                })
            # Also validate numeric and positive hours here for PATCH/PUT consistency
            try:
                if float(worked_hours) <= 0:
                    raise serializers.ValidationError({
                        'worked_hours': 'Worked hours must be a positive number.'
                    })
            except (TypeError, ValueError):
                raise serializers.ValidationError({
                    'worked_hours': 'Worked hours must be a valid number.'
                })

        return attrs

    # Ensure model-level ValidationError is surfaced as DRF 400 response
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except DjangoValidationError as e:
            # Prefer field-wise error mapping if available
            detail = getattr(e, 'message_dict', None) or getattr(e, 'messages', None) or str(e)
            raise serializers.ValidationError(detail)

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except DjangoValidationError as e:
            detail = getattr(e, 'message_dict', None) or getattr(e, 'messages', None) or str(e)
            raise serializers.ValidationError(detail)


class TaskReportSerializer(serializers.ModelSerializer):
    assigned_to_id = serializers.IntegerField(source='assigned_to.id', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_by_id = serializers.IntegerField(source='assigned_by.id', read_only=True, allow_null=True)
    assigned_by_username = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'due_date',
            'completion_report', 'worked_hours',
            'assigned_to_id', 'assigned_to_username',
            'assigned_by_id', 'assigned_by_username',
            'created_at', 'updated_at',
        ]

    def get_assigned_by_username(self, obj):
        return getattr(obj.assigned_by, 'username', None)
