Symptom Check Web app



Description
A web application that allows users to symptom check possible diseases. Users will be able to store household members` symptom check history.

Data Source / API
The data required for this app includes Infermedia API, a simple questionnaire on symptoms a person is having. 
The tech stack is a Python back end using Flask, with server rendered jinja pages. The database is handled through Flask-SQLAlchemy interfacing for PostgreSQL, and form validation through WTForms.

Functionality
Create user profile
Symptom check on certain person
Manage household members` symptom check history

User Flow:
Display homepage explaining the questionnaire and two buttons - one that says register and one that says login. 
After logging in display mainpage asking user to select who is the checkup for (different names and a new person selection)
After selecting, show the selected person`s profile (date of birth, gender) and previous results (these results can be deleted) and a start button to begin the symptom questionnaire. If a new person is selected, ask the user the new person's profile then begin the questionnaire. 
The result page shows the possible diseases and a button to save the result. 
