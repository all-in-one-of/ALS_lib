call "\\Projects\tools\bin\maya2016-x64_env.cmd"
call "\\Projects\tools\bin\mentalray3131-x64_env.cmd"

rem start %MAYA_LOCATION%\bin\maya.exe -file %1
start %MAYA_LOCATION%\bin\maya.exe -command "file -open -force \"%1\""