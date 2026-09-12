from pythermalcomfort.models import utci
result = utci(tdb=30, tr=30, v=1, rh=50)
print(type(result))
print(dir(result))
print(result)
