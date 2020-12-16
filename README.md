# NagBot
SD&amp;D project

Hello! We are NagBot, a project dedicated to helping our users be productive. Our Windows application allows users to schedule Work and Break Blocks and denylist certain sites during Work blocks. Not only will users be notified when they are entering a Block, but if they visit a denylisted site during a Work Block, out app will "nag" the user and politely remind them to stay on task.

While the main features have all been implemented there are still some special features that have yet to be fully implemented. If you are a developer looking to extend our project, visit the CODE directory to take a look at the Python code. A README there will tell you a bit about the files and what dependecies you will need to get started

If you'd like to use our app without having to install the dependencies, visit the DIST directory to download the latest build. Download the entire folder (currently "NagBot_v1") and run the NagBot.exe to run the app. Note that the app will take a few seconds to lauch (a debug cmd line will also launch since we are still in beta) and also a few seconds to close (it will need to check all data is saved)

## UI Flowchart (UI may differ a bit since we are still in beta)
![](images/GUI_Flowchart.svg)