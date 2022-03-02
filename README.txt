

Steps to run the project:
    1. Clone or download and extract the zip file.

    2. Create the virtual environment using the following command,
        virtualenv -p python3 <virtual environment name>
        Note: This is a one time process, if you already have the virtual environment, skip this step.

    3. Activate the virtual environment,
        source <virtual environment name>/bin/activate

    4. Navigate to project directory(Blockchain).

    5. Create MySQL database specified in settings file, also do the changes for username and password

    6. Also add the email username and email password, for sending the emails.

    7. Do the necessary migrations using following command,
        python manage.py makemigrations user_registration ballot

    8. Migrate the changes,
        python manage.py migrate

Note:
    For Deleting the vote data, use the below command.
    python manage.py clear_vote_data

