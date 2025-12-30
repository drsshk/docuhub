# Error Handling Documentation

## Overview

This document outlines the comprehensive error handling implemented throughout DocuHub to gracefully handle database schema mismatches, integrity errors, and other database-related issues.

## Error Handling Components

### 1. Signal Handlers (`apps/accounts/signals.py`)

**Purpose**: Handle user profile and notification preference creation with graceful error handling.

**Key Features**:
- Comprehensive try-catch blocks around all database operations
- Specific handling for `IntegrityError` (duplicate entries)
- Logging of all errors with user context
- Graceful fallback when profile creation fails
- Automatic session management with error recovery

**Example**:
```python
try:
    profile, profile_created = UserProfile.objects.get_or_create(
        user=instance,
        defaults={'role': default_role, 'department': '', 'phone_number': ''}
    )
    if profile_created:
        logger.info(f"Created UserProfile for user {instance.username}")
except IntegrityError as e:
    logger.warning(f"IntegrityError creating profile for user {instance.username}: {e}")
    # Profile already exists, continue gracefully
```

### 2. Form Error Handling (`apps/accounts/forms.py`, `apps/notifications/forms.py`)

**Purpose**: Handle database errors in form save operations.

**Key Features**:
- Override `save()` methods with error handling
- Convert database errors to user-friendly `ValidationError` messages
- Comprehensive logging for debugging
- Specific error messages for common issues

**Example**:
```python
def save(self, commit=True):
    try:
        return super().save(commit=commit)
    except IntegrityError as e:
        logger.error(f"IntegrityError saving notification preferences: {e}")
        raise ValidationError("There was an error saving your notification preferences. Please try again.")
```

### 3. Middleware Error Handling (`apps/accounts/middleware.py`)

**Purpose**: Global error handling for database-related exceptions.

#### DatabaseErrorMiddleware
- Catches `IntegrityError`, `OperationalError`, and `DatabaseError` globally
- Provides user-friendly error messages
- Handles schema mismatch errors specifically
- Redirects users gracefully or shows error page

#### UserProfileMiddleware
- Ensures authenticated users have required profile objects
- Creates missing profiles on-the-fly
- Handles missing notification preferences
- Prevents errors from missing user data

**Example Error Handling**:
```python
if isinstance(exception, IntegrityError):
    error_message = str(exception).lower()
    if 'duplicate entry' in error_message:
        if 'user_profiles.user_id' in error_message:
            messages.error(request, "User profile already exists. Please contact support if this persists.")
```

### 4. Error Template (`templates/error.html`)

**Purpose**: User-friendly error page for database issues.

**Features**:
- Clean, responsive design using Tailwind CSS
- Clear error messaging
- Navigation options (Go Back, Return to Home)
- Consistent with application styling

## Error Types Handled

### 1. IntegrityError
**Cause**: Duplicate entries, constraint violations
**Handling**: 
- Specific messages for duplicate usernames, emails, profiles
- Graceful fallback to existing records
- User-friendly error messages

### 2. OperationalError / DatabaseError
**Cause**: Schema mismatches, missing tables, connection issues
**Handling**:
- Detection of "Unknown column" errors (schema mismatch)
- Detection of missing table errors
- Generic database connection error messages
- Critical logging for admin attention

### 3. ValidationError
**Cause**: Form validation failures
**Handling**:
- Allow normal Django handling
- Log validation issues for monitoring

## Implementation Strategy

### 1. Layered Approach
1. **Signal Level**: Handle errors during automatic profile creation
2. **Form Level**: Handle errors during user input processing  
3. **Middleware Level**: Catch any remaining database errors globally
4. **Template Level**: Present friendly error messages to users

### 2. Logging Strategy
- **INFO**: Successful operations (profile creation, etc.)
- **WARNING**: Recoverable errors (duplicate creation attempts)
- **ERROR**: Database errors that affect functionality
- **CRITICAL**: Schema mismatches requiring admin attention

### 3. User Experience
- Never show raw database errors to users
- Provide actionable error messages
- Offer clear navigation options
- Maintain application functionality even during errors

## Testing Error Handling

### Test Cases Covered
1. **Normal Operation**: User creation with profile/preferences
2. **Duplicate Handling**: Multiple attempts to create same profile
3. **Schema Mismatches**: Graceful handling of missing fields/tables
4. **Form Validation**: Error handling in user input forms
5. **Session Management**: Error recovery during login/logout

### Testing Commands
```bash
# Test signal handlers
./venv/Scripts/python.exe -c "test_signal_handlers_script"

# Test Django system check
./venv/Scripts/python.exe manage.py check

# Test middleware and forms through UI
./venv/Scripts/python.exe manage.py runserver
```

## Benefits

1. **Stability**: Application continues to function even with database schema issues
2. **User Experience**: Clear, friendly error messages instead of technical errors
3. **Debugging**: Comprehensive logging helps identify and fix issues quickly
4. **Resilience**: Automatic recovery from common database problems
5. **Maintainability**: Centralized error handling makes updates easier

## Future Enhancements

1. **Email Notifications**: Alert admins of critical database errors
2. **Retry Mechanisms**: Automatic retry for transient database issues
3. **Health Checks**: Proactive monitoring of database schema alignment
4. **Error Analytics**: Track error patterns for proactive fixes