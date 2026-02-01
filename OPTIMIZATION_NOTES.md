# Batch API Optimization Analysis

## Current Performance (Partial Results)

| Test Scenario | Frames | Total Time | Time/Frame | Frames/Sec |
|--------------|--------|------------|------------|------------|
| 1 day hourly | 24 | 3.024s | 126ms | 7.94 |
| 1 week hourly | 169 | 6.384s | 37.78ms | 26.47 |

**Observation:** Time per frame decreases with more frames (126ms → 37.78ms), showing overhead amortization.

## Current Architecture - Duplicate Calculations

For each frame in the batch, we make **3 service calls**:

```python
# In api/services/batch_earth_observations.py (lines 38-51)
sun_data = calculate_sun_position(...)      # Calculates sun position
moon_data = calculate_moon_position(...)     # Calculates moon position  
moon_phase_data = calculate_moon_phase(...)  # Calculates sun AND moon again!
```

### Breakdown of Astronomical Calculations Per Frame:

1. **`calculate_sun_position()`** ([sun.py](api/services/sun.py#L9-L60)):
   - Creates `Time` object
   - Creates `EarthLocation` object
   - Creates `AltAz` frame
   - Calls `get_sun(t)` → **SUN CALCULATION #1**
   - Transforms to AltAz coordinates

2. **`calculate_moon_position()`** ([moon.py](api/services/moon.py#L8-L57)):
   - Creates `Time` object
   - Creates `EarthLocation` object
   - Creates `AltAz` frame
   - Calls `get_body("moon", time, location)` → **MOON CALCULATION #1**
   - Transforms to AltAz coordinates

3. **`calculate_moon_phase()`** ([moon_phase.py](api/services/moon_phase.py#L9-L94)):
   - Creates `Time` object
   - Creates `EarthLocation` object
   - Calls `get_sun(time)` → **SUN CALCULATION #2** (duplicate!)
   - Calls `get_body("moon", time, location)` → **MOON CALCULATION #2** (duplicate!)
   - Calculates elongation angle (sun.separation(moon))
   - Calculates ecliptic longitude difference

### Total Per Frame:
- **2× sun position calculations** (redundant)
- **2× moon position calculations** (redundant)
- **3× Time object creation** (redundant)
- **3× EarthLocation object creation** (redundant)
- **2× AltAz frame creation** (redundant)

## Proposed Optimization Strategy

### Option 1: Single Calculation Function (Recommended)
Create a new service `calculate_all_observations()` that:
1. Creates Time/Location/AltAz objects **once**
2. Gets sun position **once**
3. Gets moon position **once**
4. Calculates all derived values (altitude, azimuth, phase, illumination)
5. Returns all data in one go

**Estimated improvement:** ~50-60% reduction in computation time (eliminating 2 of 3 sun/moon calls)

### Option 2: Batch-Aware Services
Modify existing services to accept pre-calculated sun/moon positions:
```python
def calculate_moon_phase(
    date_str, time_str, lat, lon, elevation,
    sun_pos=None,  # Optional pre-calculated
    moon_pos=None  # Optional pre-calculated
)
```

**Pros:** Backward compatible, minimal refactoring
**Cons:** More complex API, parameter passing overhead

### Option 3: Caching Layer
Add memoization/caching for identical time/location combinations.

**Pros:** No code changes to services
**Cons:** Memory overhead, cache invalidation complexity, less effective for batch with unique times

## Recommendation

**Implement Option 1** with a new `calculate_complete_frame()` function used exclusively by the batch API:

```python
def calculate_complete_frame(
    datetime_str: str,
    latitude: float,
    longitude: float,
    elevation: float = 0.0
) -> dict:
    """
    Calculate sun position, moon position, and moon phase in a single pass.
    Eliminates duplicate astronomical calculations.
    """
    # Create objects once
    time = Time(datetime_str, format="isot", scale="utc")
    location = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg, height=elevation * u.m)
    altaz_frame = AltAz(obstime=time, location=location, pressure=0.0)
    
    # Get positions once
    sun = get_sun(time)
    moon = get_body("moon", time, location)
    
    # Transform once
    sun_altaz = sun.transform_to(altaz_frame)
    moon_altaz = moon.transform_to(altaz_frame)
    
    # Calculate all values
    # ... sun altitude, azimuth, visibility
    # ... moon altitude, azimuth, visibility
    # ... moon phase (illumination, phase_angle, phase_name)
    
    return {
        "sun": {...},
        "moon": {...},
        "moon_phase": {...}
    }
```

Keep existing individual services unchanged for single-request endpoints.

## Next Steps

1. ✅ Complete benchmark testing (interrupted)
2. ⬜ Implement `calculate_complete_frame()` in new file `api/services/complete_observation.py`
3. ⬜ Update `batch_earth_observations.py` to use new function
4. ⬜ Re-run benchmark to measure improvement
5. ⬜ Ensure all existing tests still pass
6. ⬜ Update integration tests if needed

## Performance Goals

- Target: **<20ms per frame** for 100+ frame batches (current: ~37ms)
- Ideal: **<15ms per frame** (would enable 1000+ frame batches in <15 seconds)
