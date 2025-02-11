**Project Description:** 
This project will create a version control system where merges are managed by memes -- a product called GiggleGit from CodeChuckle. The objective is to allow users to merge branches while interacting with a meme-based suggestion system. The system should work well alongside Git and provide a good onboarding experience. 

**Agile**
- *Theme*: Get GiggleGit demo into a stable enough alpha to start onboarding some adventurous clients
- *Epic*: Onboarding experience 
- User Story 1: As a vanilla git power-user that has never seen GiggleGit before, I want to understand how meme-based merging works right away, so that I can get started on my work without having to learn a lot of new things. 
    - Task: Provide a concise tutorial/guide document for new users.
        - Ticket 1: Create onboarding documentation for GiggleGit.
        *Guide users through a simulation of the basic features of GiggleGit (i.e. "How to merge", "How to pull", etc).*
        - Ticket 2: Include text links (hyperlinks) at the top of the document that acts as a "Table of Contents".
        *When users click on the text links (i.e. "How to push code changes"), direct the user to that section of the document.*
- User Story 2: As a team lead onboarding an experienced GiggleGit user, I want to be able to set up my team with appropriate permissions/workflows so that they can collaborate efficiently.
    - Task: Implement a system to designate/manage user permissions.
        - Ticket 1: Have an team lead/admin dashboard.
        *A GUI that allows team leads to manage settings and user permissions.*
        - Ticket 2: Create a role-system for users.
        *Allow team leads to create assignable roles which have specific permissions attached to them [the roles].*
- User Story 3: As a developer working on a project on GiggleGit, I want to be able to undo/revert merges that went wrong so that I can recover from bad decisions.
    - Task: Establish a process for reversing changes.
        - Ticket 1: Store a history of all the merges including information about those merges.
        *Allow users to review past merges.* 
        - Ticket 2: Create an "Undo Merge" button for recent merges.
- Point/Question 3: This is not a user story. Why not? What is it? *"As a user I want to be able to authenticate on a new machine".*
    - My response: The user story does not mention why that user wants to authenticate on a new machine. Why should this feature be implemented?

**Formal Requirements**
- Goal: Ensure SnickerSync improves user experience by providing a reliable and efficient diff tool that aligns with GiggleGit's meme-based version control.
- Non-Goal: SnickerSync is not designed to run on mobile devices.
    - Non-functional requirement 1: Team permissions and accessibility settings
        - Functional requirements:
            - Allow team leads/admins to set different permission levels for contributors/reviewers as well as PMs.
            - Implement authentication functions to restrict access based on the users' roles.
    - Non-functional requirement 2: User study/testing
        - Functional requirements:
            - Use a testing framework where users are randomly assigned to either control groups or variant groups (users are assigned different variations of SnickerSync).
            - Use analytic tools to track user data (user engagement, user actions, etc) between the different versions.


