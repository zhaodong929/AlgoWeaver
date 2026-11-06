# Reproduction planning and template artifacts

`ReproductionPlanner` converts a validated capability card and optional retrieval hits into a structured `ReproductionPlan`. The plan records objective, required inputs, expected outputs, dependencies, ordered steps, acceptance checks and evidence IDs. Missing core fields or provenance make the plan `blocked`.

`TemplateArtifactWriter` writes deterministic demo artifacts for the moving-average example. It never imports or executes the generated source, and every artifact is explicitly `unverified`. Runtime validation and promotion to a verified capability belong to the later sandbox workflow.
