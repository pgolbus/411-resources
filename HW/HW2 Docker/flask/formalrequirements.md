1. goal: develop a sync interface compatible with base GiggleGit packages so that when a user sync their code a humorous message would generate

2. nongoal: incorporate ai or somesort of api to create messages/audios/videos/images when syncing. 

* nonfunctional requirement 1: Security
- functional requirement 1: data and information about the user should be encrypted and secured
- functional requirement 2: feature does not have customization/manipulation, ensuring consistentcy

* nonfunctional requirement 2: Non-Repeatability
- functional requirement 1: use database to store previous messages, a user should not obtain the same message more than once per 3 days
- functional requirement 2: messages build off of one another/tailored to a user humor
