from PromptDate import prompt_date
from astropy.time import Time
from DayOfTheWeek import jd_to_weekday

# Example
t = prompt_date()
print("Parsed date:", t.iso)

print("ISO (UTC):", t.iso)
print("Julian Date (JD):", t.jd)
print("Modified Julian Date (MJD):", t.mjd)
weekday = jd_to_weekday(t.jd)
daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
print("Day of the week (0=Sun ... 6=Sat):", weekday)
print("Day of the week:", daysOfWeek[weekday])

