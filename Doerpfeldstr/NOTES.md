# Findings when mapping real data to a SUMO network
- Map matching is the important thing
- you can give additional info to randomTrips concerning
  - streets to avoid for routing (see preferences.xml)
  - defining fringe junctions
- you can give additional info to routeSampler concerning
  - turn probabilities (see turn_probabilities.xml)
  - major routes driven (see main_relations.xml)
- in the end if the inputs are not correctly matched it will not help
