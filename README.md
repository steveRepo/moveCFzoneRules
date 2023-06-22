# moveCFzoneRules
Moves CF zone rules from one zone to another

This script copies Zone Rulesets from one zone to another.
At the moment, it doesn't update managed rulesets. These will need to be updated manually on the target zone. 
This will added be in the next iteration, along with a confirmation plan and yes/no.
Before copying, it deletes any non-default rulesets that have been added.
Add your Auth below before use

To use, ensure you have python installed (https://docs.brew.sh/Homebrew-and-Python).
To run: $ python ruleset-transfer.py 
Script prompts for the source and target zones.
