"""
Data Transfer Objects (DTOs) for UiPath Orchestrator API responses.
Pydantic models for type-safe API responses.
"""

from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BaseDTO(BaseModel):
    """Base DTO with common configuration."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class OAuthTokenDTO(BaseDTO):
    """OAuth token response from UiPath Orchestrator."""

    access_token: str = Field(description="OAuth access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(description="Token expiration in seconds")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    scope: Optional[str] = Field(None, description="Token scope")


class RobotDTO(BaseDTO):
    """UiPath Robot information."""

    id: int = Field(description="Robot ID")
    name: str = Field(description="Robot name")
    type: str = Field(description="Robot type (Attended/Unattended)")
    machine_name: Optional[str] = Field(None, description="Machine name")
    username: Optional[str] = Field(None, description="Robot username")
    enabled: bool = Field(default=True, description="Robot enabled status")
    execution_target: Optional[str] = Field(None, description="Execution target")
    release_id: Optional[int] = Field(None, description="Release ID")
    execution_sessions: Optional[int] = Field(None, description="Active execution sessions")
    license_key: Optional[str] = Field(None, description="License key")
    status: Optional[str] = Field(None, description="Robot status")
    version: Optional[str] = Field(None, description="Robot version")


class QueueDTO(BaseDTO):
    """UiPath Queue information."""

    id: int = Field(description="Queue ID")
    name: str = Field(description="Queue name")
    description: Optional[str] = Field(None, description="Queue description")
    account_id: int = Field(description="Account ID")
    max_retries: int = Field(default=0, description="Maximum retries")
    accept_orphaned_items: bool = Field(
        default=False,
        description="Accept orphaned items"
    )


class QueueItemDTO(BaseDTO):
    """UiPath Queue Item information."""

    id: int = Field(description="Item ID")
    queue_id: int = Field(description="Queue ID")
    queue_name: Optional[str] = Field(None, description="Queue name")
    status: str = Field(description="Item status")
    creation_time: Optional[datetime] = Field(None, description="Item creation time")
    start_processing_time: Optional[datetime] = Field(
        None,
        description="Processing start time"
    )
    end_processing_time: Optional[datetime] = Field(
        None,
        description="Processing end time"
    )
    retry_number: int = Field(default=0, description="Retry count")
    reference: Optional[str] = Field(None, description="Item reference")
    type: Optional[str] = Field(None, description="Item type")
    data: Optional[dict[str, Any]] = Field(None, description="Item data")
    priority: Optional[str] = Field(None, description="Item priority")


class ReleaseDTO(BaseDTO):
    """UiPath Release information."""

    id: int = Field(description="Release ID")
    name: str = Field(description="Release name")
    description: Optional[str] = Field(None, description="Release description")
    state: str = Field(description="Release state (Published/Draft/Deprecated)")
    version: str = Field(description="Release version")
    publish_date: Optional[datetime] = Field(None, description="Publish date")
    is_latest: bool = Field(default=False, description="Is latest version")
    auto_upgrade: bool = Field(default=False, description="Auto upgrade enabled")
    
    # Process information
    process_id: Optional[int] = Field(None, description="Process ID")
    process_name: Optional[str] = Field(None, description="Process name")
    key: Optional[str] = Field(None, description="Release key")


class JobDTO(BaseDTO):
    """UiPath Job information."""

    id: int = Field(description="Job ID")
    release_id: Optional[int] = Field(None, description="Release ID")
    release_name: Optional[str] = Field(None, description="Release name")
    state: str = Field(description="Job state (New/Pending/Running/Completed/etc)")
    input_arguments: Optional[dict[str, Any]] = Field(
        None,
        description="Job input arguments"
    )
    output_arguments: Optional[dict[str, Any]] = Field(
        None,
        description="Job output arguments"
    )
    status: Optional[str] = Field(None, description="Job status (Successful/Failed/etc)")
    reason_for_failure: Optional[str] = Field(None, description="Failure reason")
    robot_id: Optional[int] = Field(None, description="Robot ID")
    robot_name: Optional[str] = Field(None, description="Robot name")
    machine_name: Optional[str] = Field(None, description="Machine name")
    creation_time: Optional[datetime] = Field(None, description="Creation time")
    start_time: Optional[datetime] = Field(None, description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")
    execution_duration: Optional[int] = Field(None, description="Duration in milliseconds")
    execution_target: Optional[str] = Field(None, description="Execution target")
    priority: Optional[str] = Field(None, description="Job priority")
    has_schedules: bool = Field(default=False, description="Has associated schedules")


class TriggerDTO(BaseDTO):
    """UiPath Trigger information."""

    id: int = Field(description="Trigger ID")
    name: str = Field(description="Trigger name")
    trigger_type: str = Field(description="Trigger type (Schedule/FileTrigger/etc)")
    enabled: bool = Field(default=True, description="Trigger enabled status")
    process_id: Optional[int] = Field(None, description="Process ID")
    release_id: Optional[int] = Field(None, description="Release ID")
    
    # Schedule trigger fields
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    timezone_id: Optional[str] = Field(None, description="Timezone ID")
    base_time: Optional[str] = Field(None, description="Base time")
    
    # Additional properties
    parameters: Optional[dict[str, Any]] = Field(None, description="Trigger parameters")


class LogDTO(BaseDTO):
    """UiPath Job Log entry."""

    id: int = Field(description="Log ID")
    job_id: int = Field(description="Job ID")
    message: str = Field(description="Log message")
    level: str = Field(description="Log level (Trace/Debug/Info/Warn/Error/Fatal)")
    timestamp: Optional[datetime] = Field(None, description="Log timestamp")
    robot_name: Optional[str] = Field(None, description="Robot name")
    robot_id: Optional[int] = Field(None, description="Robot ID")
    process_name: Optional[str] = Field(None, description="Process name")


class ErrorDTO(BaseDTO):
    """Error response from Orchestrator API."""

    message: str = Field(description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[str] = Field(None, description="Error details")
    exception_type: Optional[str] = Field(None, description="Exception type")


class PaginatedResponseDTO(BaseDTO):
    """Generic paginated response from Orchestrator API."""

    value: list[dict[str, Any]] = Field(description="Data items")
    offset: int = Field(default=0, description="Offset")
    total_count: int = Field(description="Total count")


class JobStartRequestDTO(BaseModel):
    """Request DTO for starting a job."""

    release_id: int = Field(description="Release ID to execute")
    robot_ids: Optional[list[int]] = Field(None, description="Specific robot IDs")
    input_arguments: Optional[str] = Field(None, description="JSON input arguments")
    strategy: Optional[str] = Field(
        default="Specific",
        description="Execution strategy (Specific/RobotCount/etc)"
    )
    no_of_robots: Optional[int] = Field(None, description="Number of robots to use")
    priority: Optional[str] = Field(None, description="Job priority")


class QueueItemAddRequestDTO(BaseModel):
    """Request DTO for adding queue item."""

    reference: Optional[str] = Field(None, description="Item reference")
    priority: Optional[str] = Field(None, description="Item priority")
    due_date: Optional[datetime] = Field(None, description="Due date")
    data: Optional[dict[str, Any]] = Field(None, description="Item data/payload")
    defer_date: Optional[datetime] = Field(None, description="Defer date")
    analytics_data: Optional[dict[str, Any]] = Field(None, description="Analytics data")


class HealthCheckDTO(BaseDTO):
    """Health check response from Orchestrator."""

    is_available: bool = Field(description="Service availability")
    version: Optional[str] = Field(None, description="Service version")
    timestamp: Optional[datetime] = Field(None, description="Check timestamp")
