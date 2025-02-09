Goals and Non-Goals:
Goal: Improve user engagement through an interactive diff experience
SnickerSync aims to enhance the merge process by providing users with a visually engaging and entertaining way to resolve diffs, leading to better retention and adoption of GiggleGit.

Non-Goal: Automatic merge conflict resolution using AI
While SnickerSync aims to improve the diffing experience, it does not intend to automatically resolve complex merge conflicts without user intervention. The focus is on user interaction and decision-making.


NFRS:
NFR 1: Role-Based Access Control for PMs and Developers
Different user roles (PMs, developers, team leads) should have appropriate permissions within SnickerSync to ensure the correct level of access to maintain snickering concepts.

NFR 2: Controlled Random Assignment in User Studies
Users participating in SnickerSync user studies must be randomly assigned to either a control group or a variant group to ensure valid testing.


FRS:
FRs for NFR 1: Role-Based Access Control
FR 1.1: Implement User Roles in the System
The system must support at least three roles: PMs, Developers, and Team Leads, with appropriate access levels.
FR 1.2: Restrict Snickering Concept Modifications
Only PMs should have the ability to modify and update SnickerSync’s snickering concepts, while developers can only use pre-defined concepts.

FRs for NFR 2: Controlled Random Assignment in User Studies
FR 2.1: Implement Automated User Group Assignment
When a new user joins a SnickerSync study, they must be automatically assigned to either the control or variant group based on a predefined randomization algorithm.
FR 2.2: Track & Log User Group Assignment
Each user’s group assignment must be stored in a database, allowing user study results to be properly analyzed.