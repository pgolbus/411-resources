Project Description: 
This project will develop the demo for CodeChuckle's GiggleGit product - a version control system that uses memes to manage merge 
conflicts. My goal within this project will be to ensure that GiggleGit is able to effectively cater to both new and experienced users.
The overall goal is to implement core version control functionalities, such as managing branches and commits and resolving merge con-
flicts with an interactive meme-based system.

Agile Tasks:
Theme: Get GiggleGit demo into a stable enough alpha to start onboarding some adventurous clients.
Epic: Onboarding Experience

User Stories:

User Story 1: As a vanilla git power-user that has never seen GiggleGit before, I want to be able to use the product effectively so 
that I can catch up with more experienced users in my team and feel confident in implementing the product's features for my team.
Tasks:
Task 1: Develop a learning manual that is both user-friendly and interactive in order to ensure that new users are able to succesfully
develop proficiency in the product in a timely manner. Ticket 1: Create a beginner-friendly GiggleGit user guide. In accomplishing this,
we need to ensure that our documentation is both simple yet detailed enough to enable the vanilla git power user to understand basic
operations, such as cloning a repository or merging branches with meme-based conflict resolution. We should also ensure that the user 
guide has screenshots and examples to enable to user to visualize various processes. Ticket 2: Implementing onboarding tips for these
new users. These tooltips should strive to fully guide the beginner user through tasks like making a repository or making a first com-
mit in a very clear step by step manner.

User Story 2: As a team lead onboarding an experienced GiggleGit user, I want to learn how to access more advanced tools and then 
tailor these tools to the specific needs and workflows of my team. 
Tasks:
Task 1: Create an onboarding experience that effectively gives the team lead power to give permissions to various configurations. Ticket 1:
Provide a web interface so that team leads can set up integrations and permission. In doing this, we need to implement specific metho-
dologies that allow the team lead to give users varying levels of permissions and also manage the reading and merging of branches.
Ticket 2: Developed a personalized onboarding experience that allows the user to skip specific steps based on their level of profici-
ency. Onboarding should be split into various sections, allowing users to select which sections they'd like to learn more about. It 
should also allow users to select from the start any advanced features they require in order to customize the experience to the nec-
essities of their team.


User Story 3: As a developer, I need a visual depiction of my Git branches so that I can quickly follow the history and progress of my
projects.
Tasks:
Task 1: Create a tool for being able to visualize the branches of Git. Ticket 1: Develop branches as a tree so that they can be visua-
lized in consecutive order in an effective manner. This tree should be able to show the branches in a simple format for clarity and 
then distinguish between the types of different branches (active, merged, etc). Ticket 2: As these branches could become large depen-
ding on the breadth of a certain project, we should develop a filtration/search system. This will enable people using the platform to 
search for different branches and get real time updates when filtering. 

"As a user, I want to be able to authenticate on a new machine". The preceding statement is not a user story as it details just a 
technical specification rather than a feature that makes the life of the user easier. It's simply a technical requirement.

Formal Requirements:
Goal: Enable users to merge repositories with SnickerSync in an interactive, effective, and fun manner.
Non-Goal:Beyond simple synchronizing features, the program won't try to replace conventional Git tools.

Non-Functional Requirements and their Associated Functional Requirements:
1. Permission Settings - based on their level of seniority or role within the team, only some users should have access to Snicker Sync
Based on this non-functional requirement, our functional requirements could be that we add an authenticator or password to ensure only
some users get acess to SnickerSync. The second functional requirement for this would be a way to restrict the permission of access
to only team leads and administrators.
2. Bolstering the effectiveness of user studies - users should be assigned randomly in order to test different features of Snicker-
Sync. The first associated functional requirment is that a system should be developed to ensure that there will be no bias in the 
comprehensive evaluation of different setups by randomly assigning users to distinct testing groups. The second is that we need a 
platform for viewing the results of each test and acquiring user feedback so that it can be used to improve the product. 
