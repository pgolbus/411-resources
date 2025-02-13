Goal: Improve user conversion rate to the new tool SnickerSync; SnickerSync provides its users with a more interesting process of handling syncs, which may
lead to the tool gaining popularity.

Nongoal: Automate processes of complex merge conflicts; This is not the goal of the
tool, since it does not allow users to use GiggleGit to its fullest.

Nonfunctional Requirements: Secure User Authentication; Different users of ranks
should be granted separate permissions as to what actions they can take within
the SnickerSync system.

Functional Req: Role based access system; The system must define different
rankings for roles, and assign permissions to each role. Users with admin roles
should have access to more actions, while lower roles should have fewer powers.

Functional Req: The system must require 2 Factor authentication at all times when accessing an administrative action, such as viewing study results. This will ensure
that only the authorized users have access to certain actions.

Nonfunctional Requirements: Randomness in user assignment for studies; Users should
be randomly assigned to an experimental or a control group to eliminate inherent biases and ensure in true results.

Functional Req: Automated assignment for users; The system must automatically assign users to either experimental or control groups using a secure random generator. This process should result in unbiased testing. 

Functional Req: Logging user assignments; The system must track the users of each group, and this data should be given to the research team to ensure transparency in the user study.



