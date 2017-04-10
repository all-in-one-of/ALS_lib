# import os, re
# dir = r'\\POST\film\RenderCompose\seq012\seq012_sh034\VFX\mutagen_render.v01\mutagen'
# for f in os.listdir( dir ):
# 	if re.search('\.-\d+\.', f) :
# 		os.remove("{}/{}".format( dir, f ) )
# 		print f

# (bbox('../transform1',D_YMIN) - bbox(opinputpath('.',0),D_YMAX))


dir = r'\\POST\film\RenderCompose\seq012\seq012_sh034\VFX\mutagen_render.v01\mutagen'
print dir.split('\\')[0:-1]