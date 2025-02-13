                                                                                 Agile
Theme: Get GiggleGit demo into a stable enough alpha to start onboarding some adventurous clients

Epic: Onboarding experience 

 Complete the following tasks:

Complete these user stories:
Story 1: As a vanilla git power-user that has never seen GiggleGit before, I want to know why it is better to use GiggleGit than git so I have a reason to use rather than Git
    Task: Provide a tutorial explaining differences between GiggleGit and vanilla git

        Ticket 1: make a creative and broad introduction or tutorial for GiggleGit
            keep it short and explain the key features of GiggleGit as compared to Git

        Ticket 2: Allow  user customizability
            let users add their own memes so it feels personalized which is something that Git does not provide


Story 2: As a team lead onboarding an experienced GiggleGit user, I want to give people different access types so they can access different repositories and work on different projects basically
    Task: Implement a access managing system

        Ticket 1: Create a role dependent accessibility
            Allow the repository owner to assign different roles

        Ticket 2: Develop a request portal as well
            Let different users request for more permissions so they can access more repositories than their current role

Story 3: As someone who commits a lot, can I see which files are being added and commmitted currently and the previous ones
    Task: Implement a system which shows which files are currently being added and something to show previous commits

        Ticket 1: Implement a feature which shows the current files being added
            Show the files in text after doing the add command

        Ticket 2: Implement a command that shows previous commits
            Shows all previous commits in a list form 

Why is it not a User Story? 
My Response: The user doesn't tell WHY they need this change to be made or WHY this feature needs to be added which is important



                                                                             Formal Requirements
Goal: To provide  a fun way of syncing files through a fun new diff tool and improve user to user interactions
Non Goal: As mentioned before, this is exclusively for GiggleGit and will have no effect on Git or any other softwares  

Non-functional Requirement 1: Access Management
    Functional Requirements: 
        Let only admins configure the diff tool and the users who can manipulate it 

        Let users submit requests for a change in their role so they can also get admin

Non-functional Requirement 2: User Reviews 
    Functional Requirements: 
        Let users review the tools they have used after some time of using it 

        Let users also rate it in stars to get a brief general consensus in terms of how it stands