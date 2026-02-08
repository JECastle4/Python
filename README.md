# Python
John's python code - probably astronomy related

# To start the app
## PowerShell terminal 1
cd frontend
npm run dev
## Powershell terminal 2
uvicorn api.main:app --reload --port 8000

Day 1
HelloWorld
Julian Date + Day of the Week
Sun and Moon Position
Plot Sun and Moon longitude over 12 months

Day 2
Sun rise and set
Moon rise and set
Moon phase
Sun and moon animation
# Test commit to verify branch protection

## Phase 1
Building to two Open GL animations:
SunAndMoonAnimation - Earth bound
SolarSystemAnimation - Sun centered

## 1/2/2026
Initial API layer
- Dates
- Sun position
- Moon position
- Moon phase
Enough for 1 frame on the Earth bound animation.

## 4/2/2026
E2E test

## 5/2/2026
Windows size changes affects the canvas sizing.
Sizes of objects and default view settings updated.
Visibility of objects on the parameters and animation views corrected.

## 6/2/2026 - 7/2/2026
Parameter input UX
- Use a map for coordinates
- Date range picker, defaulting to today
- Slider for frames per day

## 7/2/2026
Progress bar for long running API call
-- SSE to send each frame as an event
-- Progress bar that show progress and only times out if any frame takes too long