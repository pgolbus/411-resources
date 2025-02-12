# Formal Requirements

- Goal: Create a seamless and enjoyable merging experience with GiggleGit using SnickerSync.
- Non-Goal: SnickerSync will not generate snickers based on merge content.
    - Non-functional requirement 1: Security
        - Functional requirements:
            - Use OAuth authentication to allow authenticated users to use SnickerSync
            - PMs have access to maintain snickering concepts, while regular users can only initiate syncs
    - Non-functional requirement 2: Usability
        - Functional requirements:
            - A button will be implemented in the GiggleGit UI that allows users to trigger SnickerSync
            - Users should receive real-time notifications on sync success, failure, or conflicts