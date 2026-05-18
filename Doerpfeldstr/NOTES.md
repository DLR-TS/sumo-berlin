# Findings when mapping real data to a SUMO network
- Map matching is the important thing
- you can give additional info to randomTrips concerning
  - streets to avoid for routing (see preferences.xml)
  - defining fringe junctions
- you can give additional info to routeSampler concerning
  - turn probabilities (see turn_probabilities.xml)
  - major routes driven (see main_relations.xml)
- in the end if the inputs are not correctly matched it will not help
- if you see unusual lane usgae, check connectivity and also priority of connections
- avoid stops close to junctions if it is possible that the stopping vehicle needs to change lanes before the junction (e.g. to turn left)
- if long vehicles brake to early for oncoming traffic, try to set keepclear to false
- do not look only at teleports, cars may also be stuck in the insertion backlog
- enable edgedata, color by live edgedata teleports and look at the live teleport increasement
- does it have any effect if I connect the streets to the bike lanes and vice versa?


# Improvement ideas
- routeSampler should use the preferences and maybe routing costs in general to weight the alternatives


# Bugs
- when loading edge data with different attributes and switching coloring and then back to edge data, sumo-gui crashes with "Error: String 'intermediate' not found."