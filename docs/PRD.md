# Virtual Study Hall PRD

## Product Summary
Virtual Study Hall is a Flask-based web platform where students can join focused online study rooms, communicate in real time, manage study sessions, share materials, and build accountability with peers.

## Target Users
- Students studying remotely or preparing for exams.
- Small peer groups that need a shared study space.
- Admins or coordinators who manage rooms, users, and shared resources.

## Problem
Students often lose focus when studying alone, and normal video meeting tools do not provide study-specific workflows such as synchronized focus timers, study goals, material sharing, and study tracking.

## Goals
- Help students study together from different locations.
- Provide real-time communication through chat and video.
- Improve productivity using focus timers and task tracking.
- Allow easy sharing of notes, PDFs, PPTs, and images.
- Give admins basic control over rooms, users, and uploaded content.

## Non-Goals For MVP
- Native mobile apps.
- Payment subscriptions.
- AI tutoring.
- Fully custom multi-party WebRTC infrastructure.
- Advanced analytics dashboards.

## Core Features

### Authentication
- User registration and login.
- Password hashing.
- Logout.
- User roles: student and admin.

### Dashboard
- Show rooms joined by the user.
- Show public rooms.
- Quick room creation.
- Display basic personal productivity stats.

### Study Rooms
- Create public or private rooms.
- Join by room list or invite code.
- Leave rooms.
- Show active members and room metadata.
- Room capacity limit.

### Real-Time Chat
- Room-specific live chat using Flask-SocketIO.
- Message history stored in database.
- Join/leave system messages.
- Timestamps and sender names.

### Focus Timer
- Pomodoro presets and custom duration.
- Shared room timer controls.
- Timer events synced with room members.
- Study sessions recorded when completed.

### Tasks
- Personal tasks linked to a room.
- Add, complete, and delete tasks.
- Support room goals later.

### File Sharing
- Upload study resources to a room.
- Download shared files.
- Restrict file types and store metadata.
- Keep files private unless the requester is a room member.

### Video Study Room
- Use Jitsi Meet embed for MVP.
- One video meeting per study room using room invite code.
- Keep video optional so low-bandwidth users can still study through chat and timer.

### Admin
- Admin dashboard.
- View users and rooms.
- Delete rooms and unsafe uploads.
- Basic activity counts.

## MVP Acceptance Criteria
- A user can register, log in, and log out.
- A user can create a room and join existing rooms.
- A room page shows chat, members, timer, tasks, files, and video area.
- Chat updates live for all connected room members.
- Files can be uploaded and downloaded.
- Timer can be started, paused, and reset in a room.
- Admin can view platform activity and manage rooms/users.

## Commercial Direction
The first commercial version should use Jitsi because it is reliable, fast to integrate, and supports video/audio/screen sharing without requiring custom media infrastructure. If video becomes the main product differentiator, the platform can later migrate to a dedicated SFU stack such as LiveKit, Jitsi Videobridge, Janus, or mediasoup.
