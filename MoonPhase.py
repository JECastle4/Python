from astropy.coordinates import get_sun, get_body
import numpy as np

def moon_phase(time, location=None):
    """Compute Moon illumination fraction (0=new, 1=full)."""
    sun = get_sun(time)
    moon = get_body("moon", time, location=location) if location is not None else get_body("moon", time)
    
    # Elongation angle (Sun-Moon separation as seen from Earth)
    elongation = sun.separation(moon)
    
    # Illumination fraction
    # elongation=0° → new moon (illum=0), elongation=180° → full moon (illum=1)
    illum = 0.5 * (1 - np.cos(elongation.rad))
    return illum

def moon_phase_name(time, location=None):
    """Get textual moon phase name."""
  
    sun = get_sun(time)
    moon = get_body("moon", time, location=location) if location is not None else get_body("moon", time)
    
    # Elongation angle (0 to 180 degrees from separation)
    elongation_deg = sun.separation(moon).deg
    
    # Determine if waxing or waning by checking Sun's position relative to Moon
    # Calculate ecliptic longitudes
    sun_lon = sun.geocentrictrueecliptic.lon.deg
    moon_lon = moon.geocentrictrueecliptic.lon.deg
    
    # Phase angle (0-360, measures Moon ahead of Sun in ecliptic)
    phase_angle = (moon_lon - sun_lon) % 360
    
    # Illumination
    illum = 0.5 * (1 - np.cos(np.radians(elongation_deg)))
    illum_pct = illum * 100
    
    # Determine phase name
    if phase_angle < 180:  # Waxing
        if illum_pct < 3:
            return "New Moon"
        elif illum_pct < 47:
            return "Waxing Crescent"
        elif illum_pct < 53:
            return "First Quarter"
        elif illum_pct < 97:
            return "Waxing Gibbous"
        else:
            return "Full Moon"
    else:  # Waning
        if illum_pct > 97:
            return "Full Moon"
        elif illum_pct > 53:
            return "Waning Gibbous"
        elif illum_pct > 47:
            return "Last Quarter"
        elif illum_pct > 3:
            return "Waning Crescent"
        else:
            return "New Moon"