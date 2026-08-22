# Data Model

## User
- `id`
- `username`
- `email`
- `password_hash`
- `role`
- `created_at`

## Room
- `id`
- `name`
- `subject`
- `description`
- `invite_code`
- `is_private`
- `capacity`
- `created_by_id`
- `created_at`

## RoomMember
- `id`
- `user_id`
- `room_id`
- `joined_at`

## Message
- `id`
- `room_id`
- `user_id`
- `content`
- `created_at`

## SharedFile
- `id`
- `room_id`
- `user_id`
- `original_filename`
- `stored_filename`
- `uploaded_at`

## Task
- `id`
- `user_id`
- `room_id`
- `title`
- `is_completed`
- `created_at`

## StudySession
- `id`
- `user_id`
- `room_id`
- `duration_minutes`
- `started_at`
- `ended_at`

## Notification
- `id`
- `user_id`
- `message`
- `is_read`
- `created_at`
