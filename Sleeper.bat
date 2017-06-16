set sleeper=path\to\Sleeper.py
set sleeper_log=path\to\logFileToCreate\NO".log"AtEnd
set firstScript=path\to\script.py
set secondScript=path\to\script.py

Start /wait %sleeper% 09:16 0 %sleeper_log%

Start /wait %firstScript%

Start /wait %secondScript%